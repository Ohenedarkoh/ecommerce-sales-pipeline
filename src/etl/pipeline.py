from sqlalchemy import create_engine
import pandas as pd
import sys
from pathlib import Path

project_root = Path.cwd()
sys.path.append(str(project_root))

from src.utils.data_utils import load_csv, convert_type, convert_datetype,profile_col


# Database connection
  
connection_url = 'postgresql+psycopg2://postgres:password@host:port/db'
engine = create_engine(connection_url)


 
# Extraction

data_path = 'C:/Users/DELL/Projects/ecommerce-sales-pipeline/data/raw'

Customers = load_csv('Customers.csv', data_path)
Location = load_csv('Location.csv', data_path)
Products = load_csv('Products.csv', data_path)
Orders = load_csv('Orders.csv', data_path)


#transform customers

Customers = Customers.rename(columns={
    'Customer ID': 'customer_id',
    'Customer Name': 'customer_name'
})


# load customers
Customers.to_sql(
    name='customers',
    if_exists='append',
    con=engine,
    index=False
)



# Transform Locations

Location = Location.rename(columns={
    'Postal Code': 'postal_code',
    'City': 'city',
    'State': 'state',
    'Region': 'region',
    'Country/Region': 'country'
})

# Load locations 
Location.to_sql(
    name='locations',
    if_exists='append',
    con=engine,
    index=False
)


 
# Create location mapping

query = "SELECT location_id, postal_code FROM locations"

location_mapping = pd.read_sql(
    query,
    con=engine
)

# Normalize postal codes
location_mapping['postal_code'] = (
    location_mapping['postal_code']
    .astype(str)
    .str.replace('.0', '', regex=False)
)

# One location_id per postal code
location_mapping = location_mapping.drop_duplicates(
    subset='postal_code',
    keep='first'
)


 
# transform products

malformed_rows= (
    Products['Category'].isna() & 
    Products['Sub-Category'].isna() &
    Products['Product Name,,,,,'].isna())

Products.loc[malformed_rows,['Product ID', 'Category', 'Sub-Category', 'Product Name,,,,,']] = Products.loc[malformed_rows,'Product ID'].str.split(';', n=3, expand=True).values

Products['Product Name,,,,,'] = Products['Product Name,,,,,'].str.rstrip(',')

Products = Products.rename(columns={
    'Product ID': 'product_id',
    'Category': 'category',
    'Sub-Category':'sub_category',
    'Product Name,,,,,':'product_name'
})

print(profile_col(Products))


#load products to db
Products.to_sql(
    name='products',
    if_exists='append',
    con=engine,
    index=False
)

# Transform Orders

Orders['Postal Code'] = convert_type(
    Orders['Postal Code'],
    'str'
)

Orders = Orders.merge(
    location_mapping,
    left_on='Postal Code',
    right_on='postal_code',
    how='left'
)

print("Orders after location mapping:", Orders.shape)
print("Missing location IDs:", Orders['location_id'].isna().sum())

Orders = Orders.drop(
    columns=['Postal Code', 'postal_code']
)


  
# Rename and load Orders to db


Orders = Orders.rename(columns={
    'Row ID': 'row_id',
    'Order ID': 'order_id',
    'Order Date': 'order_date',
    'Ship Date': 'ship_date',
    'Ship Mode': 'ship_mode',
    'Customer ID': 'customer_id',
    'Segment': 'segment',
    'Product ID': 'product_id',
    'Sales': 'sales',
    'Quantity': 'quantity',
    'Discount': 'discount',
    'Profit': 'profit'
})

Orders['order_date']=convert_datetype(Orders['order_date'])
Orders['ship_date'] = convert_datetype(Orders['ship_date'])


print((Orders['ship_date']<Orders['order_date']).sum())

Orders.to_sql(
    name='orders',
    if_exists='append',
    con=engine,
    index=False
)



  
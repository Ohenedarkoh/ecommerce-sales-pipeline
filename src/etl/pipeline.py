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


data_path = 'C:/Users/DELL/Projects/ecommerce-sales-pipeline/data/raw'

files=['Customers.csv','Location.csv','Products.csv','Orders.csv']

#  validatiing whether files exist and are actual files
for filename in files:
    file_path = Path(data_path)/filename

    if file_path.exists() and file_path.is_file():
        print(f"{file_path} exists and is a file")
    else:
        raise FileNotFoundError(f"{file_path} does not exist or is not a file")


# Extraction
Customers = load_csv('Customers.csv', data_path)
Location = load_csv('Location.csv', data_path)
Products = load_csv('Products.csv', data_path)
Orders = load_csv('Orders.csv', data_path)

dataframes= {
    'Customers':Customers,
    'Location':Location,
    'Products':Products,
    'Orders':Orders
}


# validating whether files are not empty
for name, dataframe in dataframes.items(): 
    if dataframe.empty:
        raise ValueError(f"{name} is empty")
    else:
        print(f"{name} is not empty")



expected_cols={
    'Customers':['Customer ID',
    'Customer Name',
    ],

    'Location':['Postal Code',
    'City',
    'State',
    'Region',
    'Country/Region'],

    'Products':['Product ID',
    'Category',
    'Sub-Category',
    'Product Name,,,,,'],

    'Orders':[
        'Row ID',
        'Order ID',
        'Order Date',
        'Ship Date',
        'Ship Mode',
        'Customer ID',
        'Segment',
        'Postal Code',
        'Product ID',
        'Sales',
        'Quantity',
        'Discount',
        'Profit'

    ]


    }

#validating the expected columns across all datasets
for dataset,cols in expected_cols.items():
    dataframe = dataframes[dataset]
    missing_cols = set(cols) - set(dataframe.columns)

    if missing_cols:
        raise ValueError(
            f"Schema validation failed. Missing: {missing_cols}"
            )
    else:
        print(f"{dataset} schema validation passed")


#transform customers

Customers = Customers.rename(columns={
    'Customer ID': 'customer_id',
    'Customer Name': 'customer_name'
})


# Transform Locations

Location = Location.rename(columns={
    'Postal Code': 'postal_code',
    'City': 'city',
    'State': 'state',
    'Region': 'region',
    'Country/Region': 'country'
})


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



#Transform Orders

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


# print((Orders['ship_date']<Orders['order_date']).sum())


#validating whether datasets have missing values in fields that do not allow nulls
missing_customers=Customers[['customer_id','customer_name']].isna().sum()
missing_location= Location[['city','state','region','country']].isna().sum()
missing_products= Products[['product_id','category','sub_category','product_name']].isna().sum()
missing_orders= Orders[['row_id','order_id','order_date','ship_date','ship_mode','customer_id','segment','product_id','sales','quantity','discount','profit']].isna().sum()


missing_fields={
    'missing_customers':missing_customers,
    'missing_orders': missing_orders,
    'missing_location':missing_location,
    'missing_products':missing_products
}

if any(value.gt(0).any() for value in missing_fields.values()):
    raise ValueError(
        f" There are missing fields in the datasets."
    )

date_columns = ['order_date', 'ship_date']


#validating datetime type for date columns
for column in date_columns:
    if not pd.api.types.is_datetime64_any_dtype(Orders[column]):
        raise TypeError(
            f"{column} must be a datetime column"
        )
    else:
        print(f"{column} datatype validation passed")


# validating all order dates to be before ship dates
invalid_dates= (Orders['ship_date'] < Orders['order_date']).sum()
if invalid_dates>0 :
    raise ValueError(
        f" There are ship dates that come before order dates."
            )
else:
    print("Date relationship validation passed.")



# validation: customer_id must be unique
if Customers['customer_id'].nunique() != len(Customers):
    raise ValueError(
        "Customer ID contains duplicate values."
    )

# Orders: row_id must be unique
if Orders['row_id'].nunique() != len(Orders):
    raise ValueError(
        "Row ID contains duplicate values."
    )

print("Primary-key uniqueness validation passed")


#validation: referential integrity for customers
missing_customers = set(Orders['customer_id']) - set(Customers['customer_id'])

if missing_customers:
    raise ValueError(
        f"Orders contain customer IDs not found in Customers: {missing_customers}"
    )

print("Customer referential integrity validation passed")


#validation: referential integrity for location
if Orders['location_id'].isna().any():
    raise ValueError(
        "Some orders could not be mapped to a location."
    )

print("Location mapping validation passed")

#numeric/data-type validation
numeric_columns = [
    'sales',
    'quantity',
    'discount',
    'profit'
]

for column in numeric_columns:
    if not pd.api.types.is_numeric_dtype(Orders[column]):
        raise TypeError(
            f"{column} must be numeric"
        )

print("Numeric datatype validation passed")



if not pd.api.types.is_integer_dtype(Orders['quantity']):
    raise TypeError(
        "Quantity must be an integer"
    )

print("Quantity datatype validation passed")


#text type validation
text_columns = [
    'customer_id',
    'order_id',
    'product_id'
]

for column in text_columns:
    if not pd.api.types.is_string_dtype(Orders[column]):
        raise TypeError(
            f"{column} must be a string"
        )

print("Identifier datatype validation passed")


#pre-load constraint validation

required_orders = [
    'row_id',
    'order_id',
    'order_date',
    'ship_date',
    'ship_mode',
    'customer_id',
    'segment',
    'product_id',
    'sales',
    'quantity',
    'discount',
    'profit',
    'location_id'
]

null_constraints = Orders[required_orders].isna().sum()

if null_constraints.any():
    raise ValueError(
        f"Orders contain NULL values in required fields: "
        f"{null_constraints[null_constraints > 0].to_dict()}"
    )

print("Pre-load constraint validation passed")



    
# load customers to db
Customers.to_sql(
    name='customers',
    if_exists='append',
    con=engine,
    index=False
)
# Load locations to db 
Location.to_sql(
    name='locations',
    if_exists='append',
    con=engine,
    index=False
)

#load products to db
Products.to_sql(
    name='products',
    if_exists='append',
    con=engine,
    index=False
)
#load orders to db
Orders.to_sql(
    name='orders',
    if_exists='append',
    con=engine,
    index=False
)



  
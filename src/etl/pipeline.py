from sqlalchemy import create_engine
import os
import sys
from pathlib import Path

project_root = Path.cwd()
sys.path.append(str(project_root))
from src.utils.data_utils import load_csv


# Create engine: engine
connection_url = 'postgresql+psycopg2://postgres:password@localhost:5432/ecommerce'
engine = create_engine(connection_url)
    
#test connection to db
#  with engine.connect() as connection:
#     result = connection.execute(text("SELECT 1"))
#     print(result.scalar())

data_path = 'C:/Users/DELL/Projects/ecommerce-sales-pipeline/data/raw'

Customers = load_csv('Customers.csv',data_path)
Location= load_csv('Location.csv',data_path)
Products = load_csv('Products.csv',data_path)
Orders= load_csv('Orders.csv',data_path)


Location.to_sql(name='locations', con=engine, index=False)
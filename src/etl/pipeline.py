from sqlalchemy import create_engine, text
import pandas as pd
import sys
from pathlib import Path
import logging
import os
from dotenv import load_dotenv

project_root = Path.cwd()
sys.path.append(str(project_root))

from src.utils.data_utils import load_csv, convert_type, convert_datetype, profile_col

# create the logs directory automatically
log_dir = Path("logs")
log_dir.mkdir(parents=True, exist_ok=True)

# define the log file
filename = log_dir / "pipeline.log"

# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# create console handler and set level to info
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)


# create file handler and set level to debug
fh = logging.FileHandler(filename)
fh.setLevel(logging.DEBUG)


# create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# add formatter to ch and fh
ch.setFormatter(formatter)
fh.setFormatter(formatter)

# add ch and fh to logger
logger.addHandler(ch)
logger.addHandler(fh)



# Database connection
load_dotenv(override=True)


db_vars=['host','username','password','port','database']

for var in db_vars:
    if not os.getenv(var):
        sys.exit(f"Error: {var} is missing.")

        
host=os.getenv('host')
username=os.getenv('username')
password=os.getenv('password')
port=os.getenv('port')
database=os.getenv('database')
connection_url = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
engine = create_engine(connection_url)


data_path = "C:/Users/DELL/Projects/ecommerce-sales-pipeline/data/raw"

files = ["Customers.csv", "Location.csv", "Products.csv", "Orders.csv"]

#  validatiing whether files exist and are actual files
try:
    logger.info("Validating file existence and file types.")
    for filename in files:
        file_path = Path(data_path) / filename

        if file_path.exists() and file_path.is_file():
            logger.info(f"{file_path} exists and is a file")
        else:
            raise FileNotFoundError(f"{file_path} does not exist or is not a file")
except Exception:
    logger.exception("File existence validation failed.")
    raise

# Extraction
try:
    logger.info("Files extraction began")
    Customers = load_csv("Customers.csv", data_path)
    logger.info(f"Successfully extacted {len(Customers)} customers.")
except Exception:
    logger.exception("Customers extraction failed.")
    raise

try:
    Location = load_csv("Location.csv", data_path)
    logger.info(f"Successfully extacted {len(Location)} locations.")
except Exception:
    logger.exception("Locations extraction failed")
    raise

try:
    Products = load_csv("Products.csv", data_path)
    logger.info(f"Successfully extacted {len(Products)} products.")
except Exception:
    logger.exception("Products extraction failed.")
    raise

try:
    Orders = load_csv("Orders.csv", data_path)
    logger.info(f"Successfully extacted {len(Orders)} orders.")
except Exception:
    logger.exception("Orders extraction failed.")
    raise


dataframes = {
    "Customers": Customers,
    "Location": Location,
    "Products": Products,
    "Orders": Orders,
}

# validating whether files are not empty
try:
    logger.info("Validating whether files are not empty.")
    for name, dataframe in dataframes.items():
        if dataframe.empty:
            raise ValueError(f"{name} is empty")
        else:
            logger.info(f"{name} is not empty")
except Exception:
    logger.exception("Failed to validate whether files are not empty.")
    raise


expected_cols = {
    "Customers": [
        "Customer ID",
        "Customer Name",
    ],
    "Location": ["Postal Code", "City", "State", "Region", "Country/Region"],
    "Products": ["Product ID", "Category", "Sub-Category", "Product Name,,,,,"],
    "Orders": [
        "Row ID",
        "Order ID",
        "Order Date",
        "Ship Date",
        "Ship Mode",
        "Customer ID",
        "Segment",
        "Postal Code",
        "Product ID",
        "Sales",
        "Quantity",
        "Discount",
        "Profit",
    ],
}

# validating the expected columns across all datasets
try:
    logger.info("Validating expected columns across all datasets ")
    for dataset, cols in expected_cols.items():
        dataframe = dataframes[dataset]
        missing_cols = set(cols) - set(dataframe.columns)

        if missing_cols:
            raise ValueError(
                f"Schema validation failed for {dataset}. Missing: {missing_cols}"
            )
        else:
            logger.info(f"{dataset} schema validation passed")
except Exception:
    logger.exception("Failed to validate the expected columns across all datasets.")
    raise


# transform customers
try:
    logger.info("Renaming columns in customers data.")
    Customers = Customers.rename(
        columns={"Customer ID": "customer_id", "Customer Name": "customer_name"}
    )
    logger.info("Successfully renamed columns in customers data.")
except Exception:
    logger.exception("Failed to rename columns in customers data.")
    raise


# Transform Locations
try:
    logger.info("Initiated Locations data transformation.")
    Location = Location.rename(
        columns={
            "Postal Code": "postal_code",
            "City": "city",
            "State": "state",
            "Region": "region",
            "Country/Region": "country",
        }
    )
    logger.info("Successfully renamed locations columns.")
except Exception:
    logger.exception("Failed to rename locations columns.")
    raise


# transform products
try:
    logger.info("Grouping malformed rows")
    malformed_rows = (
        Products["Category"].isna()
        & Products["Sub-Category"].isna()
        & Products["Product Name,,,,,"].isna()
    )
    logger.info(f"Successfully grouped {malformed_rows.sum()} malformed rows.")
except Exception:
    logger.exception("Failed to group malformed rows.")
    raise


try:
    logger.info(f"Splitting {malformed_rows.sum()} malformed rows.")
    Products.loc[
        malformed_rows, ["Product ID", "Category", "Sub-Category", "Product Name,,,,,"]
    ] = (
        Products.loc[malformed_rows, "Product ID"]
        .str.split(";", n=3, expand=True)
        .values
    )
    logger.info(f"Successfully split {malformed_rows.sum()} malformed rows.")
except Exception:
    logger.exception("Failed to split malformed rows.")
    raise

try:
    logger.info("Removing trailing commas from product names.")
    Products["Product Name,,,,,"] = Products["Product Name,,,,,"].str.rstrip(",")
    logger.info("Successfully removed traling commas from product names.")
except Exception:
    logger.exception("Failed to remove trailing commas from product names.")
    raise


try:
    logger.info("Renaming product columns.")
    Products = Products.rename(
        columns={
            "Product ID": "product_id",
            "Category": "category",
            "Sub-Category": "sub_category",
            "Product Name,,,,,": "product_name",
        }
    )
    logger.info("Successfully renamed product columns.")
except Exception:
    logger.exception("Failed to rename product columns.")
    raise


# Transform Orders
try:
    logger.info("Converting data type of postal code to str.")
    Orders["Postal Code"] = convert_type(Orders["Postal Code"], "str")
    logger.info("Successfully converted data type of postal code in Order data.")
except Exception:
    logger.exception("Failed to convert data type of postal code to str.")
    raise


# Rename Orders
try:
    logger.info("Renaming Orders columns.")
    Orders = Orders.rename(
        columns={
            "Row ID": "row_id",
            "Order ID": "order_id",
            "Order Date": "order_date",
            "Ship Date": "ship_date",
            "Ship Mode": "ship_mode",
            "Customer ID": "customer_id",
            "Segment": "segment",
            "Product ID": "product_id",
            "Sales": "sales",
            "Quantity": "quantity",
            "Discount": "discount",
            "Profit": "profit",
        }
    )
    logger.info("Successfully renamed Orders columns.")
except Exception:
    logger.exception("Failed to rename Orders columns.")
    raise


try:
    logger.info("Converting date types of orders and ship dates in Orders.")
    Orders["order_date"] = convert_datetype(Orders["order_date"])
    Orders["ship_date"] = convert_datetype(Orders["ship_date"])
    logger.info("Successfully converted date types of orders and ship dates in Orders.")
except Exception:
    logger.exception("Failed to convert date types of orders and ship dates in Orders.")
    raise


# print((Orders['ship_date']<Orders['order_date']).sum())


# validating whether datasets have missing values in fields that do not allow nulls
try:

    logger.info("Validating missing values in required fields.")

    missing_customers = Customers[["customer_id", "customer_name"]].isna().sum()
    missing_location = Location[["city", "state", "region", "country"]].isna().sum()
    missing_products = (
        Products[["product_id", "category", "sub_category", "product_name"]]
        .isna()
        .sum()
    )
    missing_orders = (
        Orders[
            [
                "row_id",
                "order_id",
                "order_date",
                "ship_date",
                "ship_mode",
                "customer_id",
                "segment",
                "product_id",
                "sales",
                "quantity",
                "discount",
                "profit",
            ]
        ]
        .isna()
        .sum()
    )

    missing_fields = {
        "missing_customers": missing_customers,
        "missing_orders": missing_orders,
        "missing_location": missing_location,
        "missing_products": missing_products,
    }

    fields_with_missing_values = {}

    for dataset, counts in missing_fields.items():
        missing_columns = counts[counts > 0]

        if not missing_columns.empty:
            fields_with_missing_values[dataset] = missing_columns.to_dict()

    if fields_with_missing_values:
        raise ValueError(
            f"Missing values found in required fields: " f"{fields_with_missing_values}"
        )

    logger.info("Missing-value validation passed.")

except Exception:
    logger.exception("Missing-value validation failed.")
    raise


date_columns = ["order_date", "ship_date"]

# validating datetime type for date columns
try:
    logger.info("Validating datetime type for date columns.")
    for column in date_columns:
        if not pd.api.types.is_datetime64_any_dtype(Orders[column]):
            raise TypeError(f"{column} must be a datetime column")
        else:
            logger.info(f"{column} datatype validation passed.")
except Exception:
    logger.exception(
        "Failed to validate datetime type for date columns in Orders dataset."
    )
    raise


# validating all order dates to be before ship dates

try:
    logger.info("Date relationship validation ")
    invalid_dates = (Orders["ship_date"] < Orders["order_date"]).sum()
    if invalid_dates > 0:
        raise ValueError(f" There are ship dates that come before order dates.")
    else:
        logger.info("Date relationship validation passed.")
except Exception:
    logger.exception("Failed to validate all order dates to be before ship dates.")
    raise


# validation: customer_id must be unique
try:
    logger.info("Validating customer_id uniqueness.")
    if Customers["customer_id"].nunique() != len(Customers):
        raise ValueError("Customer ID contains duplicate values.")
    logger.info("Customer_id was unique.")
except Exception:
    logger.exception("Failed to validate customer_id uniqueness.")
    raise


# Orders: row_id must be unique
try:
    logger.info("Validating row_ids uniqueness.")
    if Orders["row_id"].nunique() != len(Orders):
        raise ValueError("Row ID contains duplicate values.")
    logger.info("Row_ids are unique.")
except Exception:
    logger.exception("Failed to validate row_ids uniqueness.")
    raise


# validation: referential integrity for customers
try:
    logger.info("Referential integrity validation for customers.")
    missingCustomers = set(Orders["customer_id"]) - set(Customers["customer_id"])

    if missingCustomers:
        raise ValueError(
            f"Orders contain customer IDs not found in Customers: {missingCustomers}"
        )
    logger.info("All customer IDs in Orders exist in Customers.")
except Exception:
    logger.exception("Referential integrity has been violated in Customers.")
    raise


# numeric/data-type validation
numeric_columns = ["sales", "quantity", "discount", "profit"]

try:
    logger.info("Numeric/data-type validation.")
    for column in numeric_columns:
        if not pd.api.types.is_numeric_dtype(Orders[column]):
            raise TypeError(f"{column} must be numeric")
    logger.info("Numeric/data-type validation passed.")
except Exception:
    logger.exception("Numeric/data-type validation failed.")
    raise

try:
    logger.info("Validating if quantity column in Orders is an integer.")
    if not pd.api.types.is_integer_dtype(Orders["quantity"]):
        raise TypeError("Quantity must be an integer")
    logger.info("Quantity datatype validation passed.")
except Exception:
    logger.exception("Quantity datatype validation failed.")
    raise

# text type validation

text_columns = ["customer_id", "order_id", "product_id"]


try:
    logger.info("Validating identifier columns contain strings.")

    for column in text_columns:
        for value in Orders[column]:
            if pd.notna(value) and not isinstance(value, str):
                raise TypeError(f"{column} contains a non-string value: {value}")

    logger.info("Text column validation passed.")

except Exception:
    logger.exception("Text column validation failed.")
    raise


# pre-load constraint validation

required_orders = [
    "row_id",
    "order_id",
    "order_date",
    "ship_date",
    "ship_mode",
    "customer_id",
    "segment",
    "product_id",
    "sales",
    "quantity",
    "discount",
    "profit",
]


try:
    logger.info("Pre-load constraint validation.")
    null_constraints = Orders[required_orders].isna().sum()

    if null_constraints.any():
        raise ValueError(
            f"Orders contain NULL values in required fields: "
            f"{null_constraints[null_constraints > 0].to_dict()}"
        )
    logger.info("Pre-load constraint validation passed.")
except Exception:
    logger.exception("Pre-load constraint validation failed.")
    raise


try:
    logger.info("Starting full database refresh.")

    with engine.begin() as conn:

        # Clear existing records, starting with orders
        logger.info("Clearing existing table records.")

        conn.execute(
            text(
                "TRUNCATE TABLE orders, products, locations, customers "
                "RESTART IDENTITY CASCADE"
            )
        )

        # Load customers
        logger.info(f"Loading {len(Customers)} customers.")

        Customers.to_sql(name="customers", con=conn, if_exists="append", index=False)

        logger.info("Customers loaded successfully.")

        # Load locations
        logger.info(f"Loading {len(Location)} locations.")

        Location.to_sql(name="locations", con=conn, if_exists="append", index=False)

        logger.info("Locations loaded successfully.")

        # Load products
        logger.info(f"Loading {len(Products)} products.")

        Products.to_sql(name="products", con=conn, if_exists="append", index=False)

        logger.info("Products loaded successfully.")

    logger.info("Database refresh completed successfully.")

except Exception:
    logger.exception("Database refresh failed.")
    raise


# Create location mapping
try:
    logger.info("Mapping locations.")
    query = "SELECT location_id, postal_code FROM locations"

    location_mapping = pd.read_sql(query, con=engine)
    logger.info("Successfully retrieved location mapping from database.")
except Exception:
    logger.exception("Failed to map locations.")
    raise


# Normalize postal codes
try:
    logger.info(
        "Converting the data type of postal codes to strings in location_mapping."
    )
    location_mapping["postal_code"] = (
        location_mapping["postal_code"].astype(str).str.replace(".0", "", regex=False)
    )
    logger.info("Successfully converted data type of postal codes in location_mapping.")
except Exception:
    logger.exception(
        "Failed to converted data type of postal code in location_mapping."
    )
    raise


# One location_id per postal code
try:
    # Record the number of location mapping rows before deduplication
    logger.info(
        f"Location mapping contains {len(location_mapping)} rows before deduplication."
    )
    # Remove duplicate postal codes, retaining the first occurrence
    location_mapping = location_mapping.drop_duplicates(
        subset="postal_code", keep="first"
    )
    logger.info(
        f"Location mapping contains {len(location_mapping)} rows after deduplication."
    )
    logger.info("Successfully removed duplicate postal codes from location mapping.")

except Exception:
    logger.exception("Failed to drop duplicated postal codes in location_mapping.")
    raise


Orders["Postal Code"] = (
    Orders["Postal Code"].astype(str).str.replace(".0", "", regex=False)
)

try:
    logger.info("Merging Order with location_mapping.")
    Orders = Orders.merge(
        location_mapping, left_on="Postal Code", right_on="postal_code", how="left"
    )
    logger.info("Successfully merged Orders with location_mapping.")
except Exception:
    logger.exception("Failed to merge Orders with location_mapping.")
    raise

if Orders["location_id"].isna().any():
    raise ValueError("Orders contains missing location IDs.")


logger.info(f"Orders shape after merging with location mapping: {Orders.shape}")
logger.info(f"Missing location IDs:{Orders['location_id'].isna().sum()}")


try:
    logger.info("Dropping postal code columns from Orders after merge.")
    Orders = Orders.drop(columns=["Postal Code", "postal_code"])
    logger.info("Successfully dropped postal code columns from Orders after merge.")
except Exception:
    logger.exception("Failed to drop postal code columns from Orders after merge.")
    raise


# validation: referential integrity for location

try:
    logger.info("Referential integrity check for location.")

    if Orders["location_id"].isna().any():
        raise ValueError("Orders contains missing location IDs.")

    missingLocation = set(Orders["location_id"]) - set(location_mapping["location_id"])

    if missingLocation:
        raise ValueError(
            f"Orders contains location IDs not found in Location: " f"{missingLocation}"
        )

    logger.info("Location passed the referential integrity check.")

except Exception:
    logger.exception("Referential integrity check failed for Location.")
    raise


# Load orders
try:
    logger.info("Loading Orders into database.")
    with engine.begin() as conn:
        logger.info(f"Loading {len(Orders)} orders.")
        Orders.to_sql(name="orders", con=conn, if_exists="append", index=False)
    logger.info("Orders loaded successfully.")
except Exception:
    logger.exception("Failed to load orders.")
    raise

logger.info("ETL pipeline completed successfully.")

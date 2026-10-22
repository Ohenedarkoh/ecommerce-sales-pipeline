# Database Design and ETL Pipeline

## 1. Purpose

This phase focused on designing the PostgreSQL database and implementing the ETL process to load the e-commerce datasets into relational tables.

The objective was to move from raw CSV files to structured, queryable data while maintaining the relationships between customers, locations, products, and orders.

## 2. Database Technology

PostgreSQL was selected as the primary database for the project. It provides relational data storage, primary and foreign key constraints, and SQL querying capabilities for downstream analysis.

The Python pipeline uses pandas to read and prepare the datasets, SQLAlchemy for database connectivity, and the PostgreSQL driver to communicate with the database.

## 3. Relational Schema

The database contains four main tables:

| Table | Primary key | Purpose |
|---|---|---|
| `customers` | `customer_id` | Stores customer identifiers and names |
| `locations` | `location_id` | Stores geographic information |
| `products` | `product_key` | Stores product identifiers, categories, sub-categories, and names |
| `orders` | `row_id` | Stores transaction-line data and references to customers and locations |

### Customers

The Customers table uses `customer_id` as its primary key. This identifies each customer and allows order records to reference the corresponding customer.

### Locations

The Locations table uses a generated integer `location_id` as its primary key. The postal code is allowed to be missing because one source record had no postal code.

Using an internal key avoids relying on a postal code as the database's primary identifier.

### Products

The Products table uses a generated integer `product_key` as its primary key. The original `product_id` is retained as an attribute because profiling found repeated Product IDs associated with different product names.

This design preserves the source records without incorrectly assuming that Product ID uniquely identifies every row.

### Orders

The Orders table stores order dates, shipping dates, shipping mode, customer and location references, product ID, sales, quantity, discount, and profit.

The `row_id` field is the primary key for each transaction-line record. The table also contains foreign keys referencing Customers and Locations.

Order ID is not the primary key because multiple rows can belong to the same order.

## 4. Table Relationships

The schema establishes the following relationships:

- Customers to Orders: `customers.customer_id` → `orders.customer_id`
- Locations to Orders: `locations.location_id` → `orders.location_id`

These relationships allow transaction data to be analysed by customer and geographic attributes.

The Orders table retains `product_id`, but the Products table uses `product_key` as its primary key. Since Product ID is not unique in the source product records, joining Orders to Products on Product ID can produce multiple matches. Product-level aggregations must therefore be validated before being treated as accurate.

## 5. ETL Workflow

The pipeline follows three main stages.

### Extract

The pipeline reads the source CSV datasets from the local data directory. The source files remain outside version control.

### Transform

The data is prepared for loading using the cleaning and transformation logic developed during exploration. This includes handling the source formatting issues and ensuring that the columns are suitable for the target database schema.

### Load

The pipeline connects to PostgreSQL and loads the datasets into the corresponding relational tables.

The database schema is maintained in `sql/schema.sql`, separating database structure from the Python ETL implementation.

## 6. Database Configuration

The pipeline reads its database connection settings from environment variables rather than hard-coding credentials.

The configuration includes:

- Host
- Username
- Password
- Port
- Database name

The local `.env` file supplies these settings during development. In Docker Compose, the ETL and database services use their configured environment variables to connect to one another.

The `.env` file is excluded from version control to protect credentials.

## 7. Data Validation

After loading, database row counts were compared with the expected source dataset counts.

| Table | Expected row count | Verified row count |
|---|---:|---:|
| `customers` | 793 | 793 |
| `locations` | 632 | 632 |
| `products` | 1,894 | 1,894 |
| `orders` | 9,994 | 9,994 |

The matching counts confirmed that the expected number of records was loaded into each table during the verified run.

Row-count validation is useful for detecting missing or unexpectedly duplicated records during ingestion. It does not, by itself, prove that every value or relationship is correct; those require additional checks.

## 8. PostgreSQL and ETL Outcome

The database schema was created and the pipeline successfully loaded all four datasets into PostgreSQL. The verified table counts matched the expected source counts.

The resulting database provides the foundation for SQL analysis and Metabase dashboards.

The implementation also established a clear separation between source data, Python processing, database schema definitions, and the PostgreSQL destination.

## 9. Known Limitation

The repeated Product IDs discovered during profiling remain an important analytical limitation. A join from Orders to Products using Product ID alone can duplicate transaction rows when a Product ID matches multiple product records.

This should be resolved or explicitly accounted for before publishing product-level sales or profit figures as definitive. Matching table row counts does not eliminate this issue because the duplication can occur later during analytical joins.
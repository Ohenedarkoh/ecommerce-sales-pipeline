# Data Exploration and Cleaning

## 1. Purpose

The purpose of this phase was to understand the structure and quality of the raw e-commerce datasets before loading them into PostgreSQL.

The exploration focused on identifying missing values, duplicate records, inconsistent formatting, malformed rows, data types, and potential issues with identifiers. The findings informed the cleaning decisions and subsequent database design.

## 2. Source Datasets

Four CSV datasets were examined:

- Customers
- Location
- Products
- Orders

The files were inspected using Python and pandas. Initial exploration included checking dataset dimensions, column names, data types, missing values, duplicate records, unique identifiers, and the consistency of date fields.

The raw data was kept separate from the cleaned and processed data to preserve the original source files.

## 3. Customers Dataset

The Customers dataset contains customer identifiers and customer names.

### Findings

- The dataset contained 793 customer records.
- No missing values were identified in the relevant columns.
- No duplicate customer identifiers or duplicate rows were found.

### Cleaning decision

No substantial cleaning was required for this dataset. The customer identifiers were retained for use as the customer key and for linking orders to customers in PostgreSQL.

## 4. Location Dataset

The Location dataset contains postal codes and geographic attributes, including city, state, region, and country.

### Findings

- The dataset contained 632 records.
- One record had a missing postal code, corresponding to Burlington, Vermont, in the East region of the United States.
- A recheck found no duplicate postal codes among the non-missing values.

### Cleaning decision

The missing postal code was retained as missing rather than inventing a replacement. Postal codes were treated as identifiers rather than numeric measurements, so they were not intended for arithmetic calculations.

The dataset was subsequently represented in PostgreSQL using a generated `location_id` as the primary key. This provides a stable internal identifier for referencing location records from the Orders table.

## 5. Products Dataset

The Products dataset contains product identifiers, categories, sub-categories, and product names.

### Findings

The initial inspection identified formatting problems in the source file:

- Some rows had product information incorrectly combined into the Product ID field.
- Several product names contained trailing commas.
- The malformed rows resulted in unexpected or unnamed columns during the initial CSV import.
- After parsing and cleaning, the dataset contained 1,894 rows.
- The cleaned dataset contained 1,862 distinct Product ID values, meaning Product ID was not unique across all product records.
- Some Product IDs were associated with different product names.

### Cleaning decisions

The malformed product records were repaired by splitting the combined text into the intended fields and removing unwanted trailing commas from product names.

A further investigation showed that Product ID could not safely serve as the primary key for the Products table because the same identifier could occur across different product names.

Rather than forcing Product ID to be unique or arbitrarily deleting records, the database design introduced a generated `product_key` as the primary key. The original Product ID was retained as a separate attribute.

This preserves the cleaned source records while providing a unique internal key for each row in the Products table.

**Important limitation:** Repeated Product IDs also affect how product attributes can be joined to order records. Joins using Product ID may produce multiple matches and inflate sales or profit totals. Product-level analysis should therefore be validated before the resulting figures are treated as authoritative.

## 6. Orders Dataset

The Orders dataset contains transaction-level information, including order identifiers, dates, shipping details, customer and product references, sales, quantity, discount, and profit.

### Findings

- The dataset contained 9,994 rows.
- It contained 5,009 distinct Order ID values.
- Repeated combinations of Order ID and Product ID were present.
- No exact duplicate rows were identified.
- No records were found where Ship Date occurred before Order Date.

### Cleaning decisions

Repeated Order IDs were not automatically treated as duplicates because an order can contain multiple product lines. Similarly, repeated Order ID and Product ID combinations were not automatically removed without evidence that the rows were erroneous.

The absence of exact duplicate rows and the date-order check were recorded as data-quality findings.

The distinction between order records and individual order lines was important for subsequent analysis. For example, the total number of orders must be calculated using a distinct count of Order ID rather than counting every row in the Orders table.

## 7. Data Quality Summary

| Dataset | Main finding | Decision |
|---|---|---|
| Customers | 793 records; no identified missing values or duplicate IDs | Retain records |
| Location | 632 records; one missing postal code | Preserve the missing value |
| Products | Malformed rows, trailing commas, repeated Product IDs | Repair formatting and use a generated primary key |
| Orders | 9,994 rows; 5,009 distinct orders; repeated order-line combinations | Preserve legitimate transaction lines and use distinct order counts for order-level metrics |

## 8. Implications for Database Design and Analysis

The profiling phase influenced several downstream decisions:

1. **Customer relationships:** Customer IDs were retained for linking Orders to Customers.
2. **Location relationships:** A generated location key was introduced to reference location records.
3. **Product relationships:** A generated product key was introduced because Product ID was not unique in the cleaned Products dataset.
4. **Order metrics:** Distinct Order ID counts were required to calculate the number of orders correctly.
5. **Missing values:** The missing postal code was preserved rather than filled with an assumed value.
6. **Analytical validation:** Product joins required additional care because repeated Product IDs could create multiple matches.

These decisions were made to preserve source information, avoid unjustified data removal, and make the limitations discovered during exploration visible to downstream users.

## 9. Outcome

The exploration and cleaning phase established a clearer understanding of the source data and the issues that needed to be addressed before database loading and reporting.

The findings provided the basis for the PostgreSQL schema, ETL implementation, data validation, and the interpretation of the project's sales, profitability, product, and customer dashboards.
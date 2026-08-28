### Data Exploration and Profiling
## Overview
 This phase focuses on understanding the four datasets before making any changes to the data. The datasets are Customers, Location, Products and Orders.

 The profiling was done to understand the structure of each dataset, identify missing values and duplicates, check data types, and examine relationships between the datasets.

### Customers

The Customers dataset contains 793 rows and 2 columns:
- Customer ID
- Customer Name

There are no missing values and no duplicate Customer IDs. All 793 customer ids are unique.

- Finding: Customer ID can be used as the identifier for customers.

### Location

The Location dataset contains 632 rows and 5 columns:

- Postal Code
- City
- State
- Region
- Country/Region

There is 1 missing Postal Code. No duplicate Postal Codes were found.

All Postal Codes found in the Orders dataset also exist in the Location dataset.

- Finding: Location data is mostly complete, with one missing Postal Code that will need to be considered during cleaning.

### Products

The Products dataset contains 1,894 rows. The main fields are:

- Product ID
- Category
- Sub-Category
- Product Name

The dataset has some formatting and parsing issues. Some records have the entire semicolon-separated row stored in the Product ID column, which causes Category, Sub-Category, and Product Name to appear missing.

There are also repeated Product IDs. In some cases, the same Product ID is associated with different product names.

The Product file also contains unexpected trailing commas in the header and some product name values.

- Finding: The Products dataset requires further cleaning and investigation before it can be reliably used in the pipeline.

### Orders

The Orders dataset contains 9,994 rows and 13 columns.

The main fields include:

- Row ID
- Order ID
- Order Date
- Ship Date
- Ship Mode
- Customer ID
- Segment
- Postal Code
- Product ID
- Sales
- Quantity
- Discount
- Profit

There are no exact duplicate rows, and Row ID is unique across the dataset.

Order ID and Product ID are not unique. The combination of Order ID and Product ID is also not unique, as the same product can appear more than once within an order.

The Order Date and Ship Date are initially stored as text and will need to be converted to appropriate date types during cleaning.

After checking the dates, no records were found where the Ship Date was earlier than the Order Date.

### Relationships

The following relationships were checked:

Orders → Customers

All Customer IDs in Orders exist in Customers.

Orders → Location

All Postal Codes in Orders exist in Location.

Orders → Products

The initial check showed 771 Product IDs in Orders that could not be matched to Products. However, the Products dataset has known parsing issues, so this result cannot yet be treated as a confirmed referential integrity problem.

### Main Findings

The main issues identified during profiling are:

- One missing Postal Code in Location.
- Formatting and parsing problems in Products.
- Repeated Product IDs in Products.
- Some Product IDs are associated with different product information.
- Orders contains repeated Order IDs and Product IDs.
- Order ID + Product ID is not unique.
- Order and Ship dates require proper data types.
- Customer and Location relationships with Orders are valid.
- The Products relationship with Orders needs to be reassessed after the Products data is cleaned.

## Conclusion

The profiling phase gave a clear understanding of the structure and main issues in the raw datasets.

The Customers and Location datasets are relatively clean, while Products has the most significant structural issues. Orders is generally consistent, but its grain and relationships need to be considered carefully when designing the database.

These findings will guide the cleaning and transformation decisions in Phase 3.
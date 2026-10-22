# SQL Analysis and Project Release

## 1. Overview

This phase focuses on using the ecommerce data for business analysis and preparing the project for publication.

PostgreSQL serves as the analytical database, while Metabase provides dashboards for exploring key business metrics. The release process includes checking the project structure, protecting sensitive files, confirming that the pipeline runs, and integrating the completed work into the main Git branch.

## 2. Analytical Data Model

The database contains four main tables:

- `customers` — customer identifiers and names.
- `locations` — city, state, region, country, and postal code information.
- `products` — product identifiers, categories, sub-categories, and product names.
- `orders` — order dates, customer and product identifiers, sales, quantity, discount, and profit.

The Orders table connects to Customers through `customer_id` and to Locations through `location_id`.

Product-level analysis requires additional care because Product IDs are not consistently unique to individual product names in the source data.

## 3. Business Questions

The project is designed to support questions such as:

### Sales performance

- What are total sales over the reporting period?
- How do sales change over time?
- How do sales differ by customer segment and region?
- Which product sub-categories contribute the most sales?

### Profitability

- What is the total profit?
- How does profit change over time?
- Which regions and customer segments contribute to profitability?
- How does profit margin vary across the business?

### Product demand

- Which product sub-categories have the highest quantities sold?
- How does sales volume change over time?
- How does demand differ by segment and region?

### Customer activity

- How many distinct customers are represented in the data?
- Which customers have the highest order counts?
- How much sales revenue and profit are associated with customers?
- How does customer activity change over time?

These questions guide the SQL-based exploration and the four Metabase dashboards.

## 4. Metric Definitions

Consistent metric definitions help prevent misleading comparisons.

| Metric | Definition |
|---|---|
| Total Sales | Sum of the `sales` field. |
| Total Profit | Sum of the `profit` field. |
| Total Quantity | Sum of the `quantity` field. |
| Total Orders | Count of distinct `order_id` values. |
| Total Customers | Count of distinct `customer_id` values. |
| Profit Margin | Total profit divided by total sales. |
| Sales per Customer | Total sales divided by distinct customers. |
| Orders per Customer | Distinct orders divided by distinct customers. |

Profit margin should be calculated from aggregate profit and sales rather than by simply averaging individual row-level margins.

Metrics based on product joins require additional validation because duplicate Product ID matches may inflate aggregated values.

## 5. Data Quality Considerations

The analysis must account for limitations identified during data exploration.

- The Orders dataset contains 9,994 rows but 5,009 distinct order IDs. An order can contain multiple product rows, so row counts should not be treated as order counts.
- Product IDs repeat across different product names. Joining Orders to Products on Product ID alone can multiply rows and distort product-level aggregations.
- One location record has a missing postal code. The missing value is preserved rather than replaced with an invented code.
- Postal codes are identifiers, not numeric measures for calculations.

These considerations should be included when interpreting results and documenting future improvements.

## 6. Final Project Review

Before releasing the project, review the following areas.

### Pipeline and database

- Confirm that the ETL pipeline completes successfully.
- Confirm that the expected database tables exist.
- Compare the loaded row counts with the expected counts.
- Check that the documented database configuration matches the actual Compose setup.

### Code and configuration

- Confirm that required dependencies are documented.
- Ensure `.env`, raw data, virtual environments, and generated logs are excluded from Git.
- Review error handling, logging, and tests against the actual implementation.
- Remove temporary files that do not belong in the repository.

### Dashboards

- Confirm that all four dashboards are saved in Metabase.
- Review the displayed metrics and chart labels.
- Check whether joins can inflate product-level results.
- Avoid presenting unvalidated product-level figures as definitive business findings.

### Documentation

- Ensure the README explains the project, technology stack, setup, pipeline execution, and dashboards.
- Ensure phase documentation reflects what was actually implemented.
- Clearly state known limitations and potential future improvements.

## 7. Git Release Workflow

The project uses three levels of branches:

- `main` — the final, stable version of the project.
- `develop` — integration branch for completed features.
- Feature branches — isolated work for specific tasks.

The intended release sequence is:

1. Finish and review the documentation.
2. Commit the documentation and any remaining changes on the active feature branch.
3. Merge the feature branch into `develop`.
4. Run the relevant checks on `develop` and fix any issues.
5. Merge the tested `develop` branch into `main`.
6. Push the updated branches to the remote repository.

The feature branches are retained after merging to preserve the project's development history.

### Commit message convention

Commit messages should use a clear conventional prefix, such as:

- `docs:` for documentation.
- `feat:` for new functionality.
- `fix:` for bug fixes.
- `test:` for testing changes.
- `refactor:` for code restructuring.

For example:

`docs: document Docker setup and Metabase dashboards`

## 8. Future Improvements

Potential improvements include:

- Resolving product identifier ambiguity before relying on product-level aggregations.
- Expanding automated tests for transformations and pipeline failure scenarios.
- Adding more robust data quality checks and reporting.
- Introducing automated pipeline scheduling.
- Evaluating a cloud warehouse such as BigQuery as a future extension.

These are potential future enhancements, not claims about the current implementation.

## 9. Conclusion

The project brings together Python-based data processing, PostgreSQL storage, Docker-based service management, and Metabase dashboards.

The release review ensures that the repository is understandable, reproducible, and transparent about its limitations. This is important for both maintaining the project and presenting it as a portfolio example of practical data engineering.
# Docker and Metabase

## 1. Overview

Docker was introduced to make the ecommerce sales pipeline and its supporting services easier to run in a consistent environment.

The project uses Docker Compose to manage PostgreSQL, the ETL application, and Metabase. Metabase connects to PostgreSQL to explore the loaded data and present business insights through dashboards.

## 2. Docker Architecture

The Docker setup contains three services.

| Service | Purpose |
|---|---|
| `postgres` | Stores the ecommerce data in PostgreSQL. |
| `etl` | Runs the Python ETL pipeline when explicitly requested. |
| `metabase` | Provides a web interface for data exploration and dashboards. |

The PostgreSQL service uses a persistent Docker volume so the database can retain its data when containers are stopped or recreated.

### Ports

- PostgreSQL: host port `5433` mapped to container port `5432`.
- Metabase: available at `http://localhost:3000`.

The host PostgreSQL service was already using port `5432`, so the containerized database was exposed on port `5433` to avoid a port conflict.

## 3. Docker Configuration Files

### `Dockerfile`

The Dockerfile defines the environment used to run the Python ETL application. It uses Python 3.11, installs the dependencies listed in `requirements.txt`, copies the application and SQL files into the image, and defines the pipeline command.

### `compose.yaml`

The Compose file defines the services, their configuration, port mappings, volumes, and service dependencies.

The ETL service uses the `run-etl` profile, so it can be run when needed rather than starting automatically with the main services.

### `docker/init.sql`

This initialization script creates a separate `metabase` database for Metabase's own application data.

The ecommerce data remains in the `ecommerce` database. Keeping these databases separate prevents Metabase's internal application tables from being mixed with the project data.

### `sql/schema.sql`

This script defines the tables used by the ecommerce pipeline. PostgreSQL initialization scripts are mounted into the container so the schema and the Metabase application database can be initialized when the database volume is first created.

**Important:** PostgreSQL initialization scripts run automatically when the database data directory is initialized for the first time. Editing an initialization script does not automatically rerun it against an existing persistent volume.

## 4. Important Docker Commands

Run these commands from the project root, where `compose.yaml` is located.

### Check the Compose configuration

```bash
docker compose config --quiet
```

Checks whether the Compose configuration can be parsed successfully.

### Build and start PostgreSQL and Metabase

```bash
docker compose up -d --build postgres metabase
```

Builds the relevant images where needed and starts the selected services in the background.

### Check running containers

```bash
docker compose ps
```

Shows the status of the services managed by Docker Compose.

### View service logs

```bash
docker compose logs postgres
```

Displays PostgreSQL logs.

```bash
docker compose logs metabase
```

Displays Metabase logs.

### Run the ETL pipeline

```bash
docker compose --profile run-etl run --rm etl
```

Runs the ETL service using the `run-etl` profile and removes the temporary ETL container after it exits. The PostgreSQL service must be available for the load to succeed.

### Stop the services

```bash
docker compose down
```

Stops and removes the Compose containers and network. The named PostgreSQL data volume is retained.

**Data safety:** Avoid `docker compose down -v` unless intentionally deleting the persistent database volume. Removing that volume can permanently delete the data stored in the containerized database.

## 5. Data Loading Verification

After running the ETL pipeline, the loaded PostgreSQL tables contained the following row counts:

| Table | Rows |
|---|---:|
| Customers | 793 |
| Locations | 632 |
| Products | 1,894 |
| Orders | 9,994 |

These counts matched the expected source dataset counts.

## 6. Metabase Setup

Metabase was started as a container and accessed through:

`http://localhost:3000`

The ecommerce PostgreSQL database was added as a data source using the Docker network connection details.

When connecting from the Metabase container, the PostgreSQL host should be the Compose service name, `postgres`, and the database port should be `5432`. The host machine uses port `5433` to connect to the same containerized PostgreSQL instance.

Metabase was configured to use the separate `metabase` application database to store its own settings, saved questions, and dashboards.

After connecting, the ecommerce tables were available in Metabase for exploration and visualization.

## 7. Dashboards

Four dashboards were created to explore sales performance, profitability, product demand, and customer activity.

### Sales Performance

Focuses on overall sales and how sales change across time and business dimensions.

Key metrics include:

- Total Sales
- Total Profit
- Total Quantity
- Total Orders

The supporting charts examine sales trends, sales by segment, sales by region, and sales by sub-category.

### Profitability Analysis

Focuses on business profitability rather than revenue alone.

Key metrics include total profit, total sales, total orders, and profit margin.

Supporting charts examine profit trends and differences across segments, regions, and product sub-categories.

### Product & Demand

Focuses on product demand and sales volume.

Key metrics include total quantity, total orders, total sales, and distinct product IDs sold.

Supporting charts examine quantity trends and differences across segments, regions, and product sub-categories.

### Customer Insights

Focuses on customer activity and purchasing behavior.

Key metrics include total customers, sales per customer, orders per customer, and total sales.

Supporting charts examine customers with the highest order counts, customers by profit, monthly active customers, and customer distribution by region.

## 8. Visualization Limitation

The Products dataset contains repeated Product IDs associated with different product names. Consequently, joining Orders to Products using Product ID alone may create duplicated matches and inflate sales, profit, or quantity in product-level charts.

Product-level results should therefore be treated cautiously until the product identifiers and join logic have been validated. The overall row-count checks do not resolve this issue.

## 9. Outcome

Docker provides a repeatable way to run the database, ETL pipeline, and visualization service. Metabase provides a visual layer for exploring the data and communicating business insights.

Together, these components make the project more representative of an end-to-end data pipeline, from source files and transformation through database storage and business-facing dashboards.
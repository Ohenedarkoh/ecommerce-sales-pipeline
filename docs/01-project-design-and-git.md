# Project Design and Git Workflow

## 1. Project Overview

The `ecommerce-sales-pipeline` project is an end-to-end data engineering project built to demonstrate how raw e-commerce data can be processed, stored in a relational database, and made available for business analysis.

The project uses Python for data processing, PostgreSQL for data storage, Docker for containerisation, and Metabase for interactive dashboards.

The main objective is to build a reproducible data pipeline that takes raw CSV files, prepares them for analysis, loads them into a structured database, and supports business reporting.

## 2. Project Objectives

The project was designed to achieve the following objectives:

- Explore and assess the quality of raw e-commerce datasets.
- Clean and prepare data for reliable downstream use.
- Design a relational PostgreSQL database with appropriate keys and relationships.
- Build a Python ETL pipeline to load the datasets into PostgreSQL.
- Apply data validation, error handling, logging, and environment-based configuration.
- Use Docker to containerise the application environment and supporting services.
- Develop business dashboards in Metabase to analyse sales, profitability, product demand, and customer activity.
- Maintain a version-controlled repository with a clear development and release workflow.

## 3. Source Data

The project uses four CSV datasets:

| Dataset | Purpose |
|---|---|
| Customers | Customer identifiers and customer names |
| Location | Postal codes, cities, states, regions, and countries |
| Products | Product identifiers, categories, sub-categories, and product names |
| Orders | Order dates, shipping information, customer and product references, sales, quantity, discount, and profit |

The raw files are kept in the local project data directory and excluded from version control to avoid committing the source data to the repository.

## 4. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data processing and ETL |
| pandas | Reading, profiling, and transforming tabular data |
| PostgreSQL | Relational database and pipeline destination |
| SQLAlchemy | Database connectivity |
| psycopg2 | PostgreSQL driver |
| python-dotenv | Loading environment variables from `.env` |
| pytest | Automated testing |
| Docker | Containerising the application and services |
| Docker Compose | Configuring and running the multi-container environment |
| Metabase | Business intelligence and dashboard visualisation |
| Git and GitHub | Version control and repository management |

## 5. High-Level Architecture

The pipeline follows this general flow:

1. Raw CSV files are stored locally.
2. Python reads and prepares the datasets.
3. The ETL process loads the prepared data into PostgreSQL.
4. PostgreSQL stores the data in relational tables.
5. Metabase connects to PostgreSQL to support business analysis and dashboard reporting.
6. Docker Compose manages the PostgreSQL and Metabase services and provides a containerised environment for running the ETL pipeline.

The architecture separates data processing, storage, and visualisation so that each component has a clear responsibility.

## 6. Repository Structure

The repository is organised into the following main directories and files:

| Path | Purpose |
|---|---|
| `src/` | Python source code |
| `src/etl/` | ETL pipeline implementation |
| `sql/` | SQL scripts, including the database schema |
| `data/` | Local source data, excluded from Git |
| `docs/` | Project documentation |
| `logs/` | Local pipeline logs, excluded from Git |
| `notebooks/` | Exploratory analysis and investigation |
| `.env` | Local environment configuration and credentials |
| `.gitignore` | Excludes local and sensitive files from version control |
| `.dockerignore` | Excludes unnecessary files from Docker build context |
| `Dockerfile` | Defines the ETL container image |
| `compose.yaml` | Configures PostgreSQL, ETL, and Metabase services |
| `requirements.txt` | Lists Python dependencies |
| `README.md` | Main project overview and setup guide |

The virtual environment and generated Python cache files are also excluded from version control.

## 7. Git Workflow

The project uses separate branches to distinguish ongoing development from the final release.

### Main branches

- `main`: Contains the final, stable version of the project.
- `develop`: Integrates completed work before the final release.
- Feature branches: Isolate specific tasks, allowing changes to be developed and reviewed before integration.

### Development process

The workflow follows these steps:

1. Create a descriptive feature branch from `develop`.
2. Implement the changes on that feature branch.
3. Commit the work using a clear, conventional commit message.
4. Merge the completed feature branch into `develop`.
5. Test the integrated project and fix any issues.
6. Merge the verified `develop` branch into `main` when the project is ready for release.

Feature branches are retained after merging to preserve the development history.

### Commit messages

Commit messages use a conventional prefix followed by a concise description of the change.

Common prefixes include:

- `feat:` for new functionality.
- `fix:` for corrections.
- `docs:` for documentation.
- `test:` for tests.
- `refactor:` for code restructuring.
- `chore:` for maintenance tasks.

For example:

`docs: document project design and git workflow`

## 8. Data and Credential Protection

The repository excludes the following local resources:

- Raw project data under `data/`.
- Environment credentials in `.env`.
- The local Python virtual environment.
- Pipeline logs.
- Python cache files and test cache files.

The `.dockerignore` file also prevents unnecessary or sensitive local files from being included in the Docker build context.

Credentials are supplied through environment variables rather than hard-coded into the pipeline configuration.

## 9. Design Principles

The project prioritises:

- **Reproducibility:** The pipeline and supporting services should be straightforward to configure and run again.
- **Modularity:** Processing responsibilities should be separated into understandable components.
- **Data quality:** Cleaning and validation decisions should be documented and justified.
- **Maintainability:** Code and configuration should remain readable and easy to update.
- **Security:** Credentials and private source data should remain outside version control.
- **Version control:** Changes should be integrated and tested through a defined Git workflow.

These principles guide the implementation, testing, documentation, and final release of the project.
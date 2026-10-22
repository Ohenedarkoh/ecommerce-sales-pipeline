# Code Quality and Configuration

## 1. Overview

This phase focuses on making the ecommerce sales pipeline easier to configure, maintain, troubleshoot, and run in different environments.

The project uses Python for data processing and PostgreSQL for storage. Configuration is separated from the pipeline code where possible, and environment-specific values are managed through environment variables.

## 2. Code Organization

The project separates pipeline code from SQL scripts, documentation, and data files.

Key components include:

- `src/etl/pipeline.py` — the main entry point for running the ETL pipeline.
- `sql/schema.sql` — defines the PostgreSQL tables and relationships.
- `requirements.txt` — lists the Python dependencies.
- `.env` — stores local configuration and database credentials.
- `logs/` — stores pipeline log output.
- `tests/` — intended for automated tests, where implemented.

This structure makes it easier to locate individual responsibilities and maintain the project as it grows.

## 3. Environment Configuration

Database connection details and other environment-specific settings should not be hard-coded into the pipeline.

The project uses `python-dotenv` to load values from the local `.env` file. The pipeline uses:

`load_dotenv(override=False)`

This loads environment variables from `.env` without replacing variables that are already set in the environment.

The pipeline also supports a configurable data directory through `DATA_PATH`, with `data/raw` as the default.

### Configuration and security

- `.env` is excluded from Git.
- Raw data files are excluded from Git.
- `.venv/` and generated logs are excluded from Git.
- Database credentials should not be written directly into source files or committed to the repository.

These controls help prevent sensitive information and local development files from being published accidentally.

## 4. Logging and Troubleshooting

Logging provides a record of pipeline activity and helps identify problems during execution.

The project uses a log file at `logs/pipeline.log`. This makes it possible to review pipeline activity without relying entirely on terminal output.

When troubleshooting, useful information includes:

- Which stage of the pipeline was running.
- Whether data extraction and loading completed.
- Whether an error occurred.
- Whether the loaded row counts match the expected source counts.

Logs should provide enough information to diagnose failures without exposing database passwords or other sensitive configuration.

## 5. Validation and Error Handling

Data validation is important because a pipeline can finish running without guaranteeing that the resulting data is correct.

The project’s validation considerations include:

- Confirming that the expected source files are available.
- Checking that source data can be read and processed.
- Confirming that the database schema supports the expected relationships.
- Comparing source and database row counts after loading.
- Checking data quality issues identified during profiling and cleaning.

The row-count checks confirmed the following loaded totals:

| Table | Rows loaded |
|---|---:|
| Customers | 793 |
| Locations | 632 |
| Products | 1,894 |
| Orders | 9,994 |

These checks confirm that the loaded row counts matched the expected dataset counts. They do not, by themselves, prove that every business rule or relationship is correct.

## 6. Testing

The project includes `pytest` among its Python dependencies for automated testing.

Tests should focus on the behavior of individual transformation functions and important pipeline assumptions. Examples include checking how missing values are handled, verifying expected output structures, and confirming that invalid input is handled appropriately.

The presence of `pytest` alone does not establish that the pipeline has comprehensive test coverage. Test completion and results should be confirmed during the final project review.

## 7. Code Quality Principles

The implementation aims to follow these principles:

- **Readability:** use straightforward code that is easy to explain and maintain.
- **Modularity:** separate responsibilities where this improves clarity and reuse.
- **Configuration:** keep environment-specific settings outside the main processing logic.
- **Validation:** check important assumptions and compare expected results with actual results.
- **Maintainability:** keep SQL, pipeline code, configuration, and documentation organized.
- **Security:** keep credentials and raw data out of version control.

## 8. Outcome

This phase establishes the configuration and code-quality practices needed to maintain the pipeline beyond a one-time local execution.

The final review should confirm that logging, error handling, reusable functions, and automated tests reflect the actual implementation before the repository is released.
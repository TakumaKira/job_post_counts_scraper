# Job Post Counts Scraper

## Table of Contents

- [Job Post Counts Scraper](#job-post-counts-scraper)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Setup your database](#setup-your-database)
    - [Database for development](#database-for-development)
    - [Migration](#migration)
    - [Prepare database user account for the app which does not have grants to administrative edits](#prepare-database-user-account-for-the-app-which-does-not-have-grants-to-administrative-edits)
  - [Get ScrapeOps API key](#get-scrapeops-api-key)
  - [Run](#run)
  - [Run tests](#run-tests)
  - [Deploying to AWS Lambda](#deploying-to-aws-lambda)
    - [The limitation I noticed](#the-limitation-i-noticed)
    - [Required environment variables](#required-environment-variables)
    - [Package this manually to zip for uploading to AWS Lambda](#package-this-manually-to-zip-for-uploading-to-aws-lambda)

## Prerequisites

You can quickly run this app using [Poetry](https://python-poetry.org/).

```bash
pip install poetry
```

Then install packages:

```bash
poetry install --sync
```

## Setup your database

### Database for development

You can create local database for development with the name `dev.db` using sqlite3 with the following command:

```bash
sqlite3
```

Then:

```bash
sqlite> .save dev.db
```

Then, you can directly work with the existing `dev.db` with the following command:

```bash
sqlite3 dev.db
sqlite>
```

*You need to [migrate](#migration) before running this app.*

### Migration

To set up tables on your database:

1. Generate a migration script with Alembic:

```bash
poetry run alembic revision --autogenerate -m "Migration description"
```

2. Apply the migration to the database:

```bash
ENV=production \
DB_USER=your_db_administrative_user_name \
DB_PASS=your_db_administrative_user_pass \
DB_HOST=your_db_host_name \
DB_PORT=your_db_port \
DB_NAME=your_db_name \
poetry run alembic upgrade head
```

(Omit lines from `ENV=production` to `DB_NAME=...` when migrating `/dev.db` because the script shares the database URL getter script with the app itself.)

### Prepare database user account for the app which does not have grants to administrative edits

The database user account needs to be granted the permission like below(assuming the user name is `job_post_count_scraper`):

```sql
GRANT ALL ON SEQUENCE public.results_id_seq TO job_post_count_scraper;
GRANT ALL ON SEQUENCE public.targets_id_seq TO job_post_count_scraper;
GRANT ALL ON TABLE public.results TO job_post_count_scraper;
GRANT ALL ON TABLE public.targets TO job_post_count_scraper;
```

## Get ScrapeOps API key

You need your own [ScrapeOps](https://scrapeops.io/) API key to run this app.

## Run

To run this app in production, you need to provide some environment variables like the following:

```bash
ENV=production \
DB_USER=your_db_app_user_name \
DB_PASS=your_db_app_user_pass \
DB_HOST=your_db_host_name \
DB_PORT=your_db_port \
DB_NAME=your_db_name \
SCRAPE_OPS_ENDPOINT=https://proxy.scrapeops.io/v1/ \
SCRAPE_OPS_API_KEY=your-scrape-ops-api-key \
poetry run python src/app.main.py
```

For test run on your local terminal, you can omit `ENV` to `DB_NAME` to run this app with `dev.db`.

If you provide `no_request` arg at the last of the command, it prevents this function from sending a request to ScrapeOps.

If you provide `store_results` instead, this will store scraped raw HTML content in a file `content.txt` and date in a file `header_date.txt`, and you can avoid sending requests by loading content from the file. To do it, just do not provide arguments AFTER you have executed to store the file.

## Run tests

To run the tests, run:

```bash
poetry run python -m pytest -s
```

*You can omit `-s` if you don't need prints.*

## Deploying to AWS Lambda

### The limitation I noticed

I chose ScrapeOps for proxy scraping requests to Glassdoor and to run the scraper as an AWS Lambda function. It took around a minute to get one result from Glassdoor through ScrapeOps and AWS Lambda's timeout is up to 15 minutes. It means it will fail if I put over 15 targets on the database.

### Required environment variables

`FUNCTION_ENVIRONMENT` needs to be `aws_lambda`.
`AWS_DB_SECRETS_NAME`	has to tell your AWS Secrets Manager secrets name which contains `username` / `password` / `port` / `dbname` of your target database.
`AWS_API_KEY_SECRETS_NAME` has to tell your AWS Secrets Manager secrets name which contains your API key for scrape proxy service.
`AWS_RDS_ENDPOINT` has to tell your RDS database endpoint.
`SCRAPE_OPS_ENDPOINT` needs to be `https://proxy.scrapeops.io/v1/`.

### Package this manually to zip for uploading to AWS Lambda

I set up GitHub actions workflow to package and deploy this to AWS lambda, but you can also do it manually with the following commands **if your environment is Linux**;

*Packaging needs to be executed on Linux to make psycopg2 work on the Lambda environment. See <https://stackoverflow.com/a/46366104>*

```bash
rm -rf dist && mkdir -p dist/lambda-package
rm -rf .venv && poetry install --only main --sync
cp -r .venv/lib/python*/site-packages/* dist/lambda-package/
cp -r src/app/pkg/* dist/lambda-package/
rm -rf dist/lambda-package/**/__pycache__
cd dist/lambda-package
zip -r ../lambda.zip .
cd ../..
```

The above makes your packages only for production (which means excluding packages for development purposes such as testing).
So you'd better revert it to the development environment ASAP with the below:

```bash
rm -rf .venv && poetry install --sync
```

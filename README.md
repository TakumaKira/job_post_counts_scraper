To run this app, you need to provide some environment variables like following:

```bash
ENV=production \
SCRAPE_OPS_ENDPOINT=https://proxy.scrapeops.io/v1/ \
SCRAPE_OPS_API_KEY=your-scrape-ops-api-key \
poetry run python src/app should_request
```

Notice `should_request` arg. This makes this function send a request to [ScrapeOps](https://scrapeops.io/).

If you provide `should_request_with_store` instead, this will store scraped raw HTML content in a file `content.txt` and date in a file `date.txt`, and you can avoid sending requests by loading content from the file. To do it, just do not provide arguments AFTER you have executed to store the file.

To migrate your database:

1. Generate a migration script with Alembic:

```bash
poetry run alembic revision --autogenerate -m "Migration description"
```

2. Apply the migration to the database:

```bash
ENV=production \
DB_USER=your_db_user_name \
DB_PASS=your_db_user_pass \
DB_HOST=your_db_host_name \
DB_PORT=your_db_port \
DB_NAME=your_db_name \
poetry run alembic upgrade head
```

(Omit lines from `ENV=production` to `DB_NAME=...` when migrating `/dev.db`)

You can create `dev.db` with the following command:

```bash
sqlite3
sqlite> .save dev.db
```

Then, you can directly work with the existing `dev.db` with the following command:

```bash
sqlite3 dev.db
sqlite>
```

To run test, run:

```bash
poetry run pytest
```

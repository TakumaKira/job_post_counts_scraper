To run this app, you need to provide some environment variables like following:

```bash
SCRAPE_OPS_ENDPOINT=https://proxy.scrapeops.io/v1/ \
SCRAPE_OPS_API_KEY=your-scrape-ops-api-key \
poetry run python main.py should_request
```

Notice `should_request` arg. This makes this function send a request to [ScrapeOps](https://scrapeops.io/).

If you provide `should_request_with_store` instead, this will store scraped raw HTML content in a file `content.txt`, and you can avoid sending requests by loading content from the file. To do it, just do not provide arguments AFTER you have executed to store the file.

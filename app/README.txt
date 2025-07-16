
Scripts for scraping the American Presidency Project (more comprehensive source for SOTUs)

One script is provided for each type of document (e.g., scrape_letters.py)

Scripts should be invoked from the root of the repository in the following way. 
`-h` can be added to any script for help/usage.
By default all data will be stored in `data/app` in the root of the repository.

```
python -m app.scrape_farewell_addresses
python -m app.scrape_inaugurals
python -m app.scrape_letters
python -m app.scrape_misc_remarks
python -m app.scrape_news_conferences
python -m app.scrape_press_briefings
python -m app.scrape_sotu_addresses
python -m app.scrape_sotu_messages
python -m app.scrape_spoken_addresses
python -m app.scrape_statements
python -m app.scrape_written_messages
python -m app.scrape_written_statements
```

After scraping all data, use combine_categories.py to combine all data into a single jsonlist file

```
python -m app.combine_categories . data/combined.jsonlist
```

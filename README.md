# Craigslist Scraper

Who needs a UI anyways

## What's here

The code here can help you parse craigslist searches and place the results in a sqlite3 database.
If you look at the main method, you'll see that I'm looking for an ikea chair and used car.

There are 2 tables in the database, *query* and *result*. *query* describes a search.
*result* are the collected results of executing queries.

The `category.csv` file shows you the url path parameter mapping which you'll need if you want to
search specific categories.
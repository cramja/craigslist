# Craigslist Watcher

## Usage

```
mkdir venv
virtualenv venv
source venv/bin/activate

pip install -r requirements.txt

python main.py create-watch moto https://sfbay.craigslist.org/search/mca?query=honda+rebel+500

python main.py update-watch-results

python main.py list-watch-results moto 24h
```

## What's here

There are 2 tables in the database, *watches* and *watch_results*.

*watches* describes a search.
*watch_results* are the collected results of executing queries.
import time
import sqlite3
from cl.result_parser import get_and_parse
from datetime import datetime
import os

db_file = os.path.dirname(os.path.realpath(".")) + "/instance/flaskr.sqlite"
print(db_file)
conn = sqlite3.connect(db_file, detect_types=sqlite3.PARSE_DECLTYPES)
conn.row_factory = sqlite3.Row

while True:
    watches = conn.execute("SELECT * FROM watches WHERE last_search_time IS NULL OR " +
                           " (julianday(CURRENT_TIMESTAMP) - julianday(last_search_time)) * 1440.0 " +
                           " > update_interval_minutes ").fetchall()
    for watch in watches:
        print("updating watch {}".format(watch['name']))
        try:
            results = get_and_parse(watch['url'])
            for result in results:
                conn.execute(
                    "INSERT OR IGNORE INTO watch_results (watch_id, post_time, query_time, cl_id, title, place, price, url) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (watch['id'], result['create_time'], datetime.now(), str(result['id']), result['title'], result['place'],
                     result['price'], result['url']))
            conn.execute("UPDATE watches SET last_search_time = datetime('now') WHERE id = ?", (str(watch['id'])))
            conn.commit()
        except Exception as e:
            print("failed to get url {}: {}".format(watch['url'], e))
    print("{} results updated".format(len(watches)))

    time.sleep(10)

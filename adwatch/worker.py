import time
import sqlite3
import sys
from adwatch.db import Database
from adwatch.result_parser import get_and_parse


def run_forever(db, sleep_interval_seconds=10):
    while True:
        watches = db.get_pending_watches()

        for watch in watches:
            print("attempting to update watch {}".format(watch['name']))
            try:
                update_watch_results(db, watch['id'])
                db.update_watch_last_search_time(watch['id'])
                db.commit_pending()
                print("updated {} successfully".format(watch["name"]))
            except Exception as e:
                print("failed to get url {}: {}".format(watch['url'], e))

        print("{} results updated, sleeping...\n".format(len(watches)))

        time.sleep(sleep_interval_seconds)


def update_watch_results(db, watch_id):
    watch = db.get_watch(watch_id)
    results = get_and_parse(watch['url'])
    for result in results:
        db.create_watch_result(watch_id,
                               result['create_time'],
                               result['id'],
                               result['title'],
                               result['place'],
                               result['price'],
                               result['url'])
    db.update_watch_last_search_time(watch['id'])
    db.commit_pending()


def main(args):
    db_file = args[0]
    sleep_interval = 10 if len(args) < 2 else int(args[1])

    print("opening db {}".format(db_file))

    run_forever(Database(sqlite3.connect(db_file, detect_types=sqlite3.PARSE_DECLTYPES)),
                sleep_interval)


if __name__ == '__main__':
    main(sys.argv[1:])

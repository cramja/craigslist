#!/usr/bin/env python

import fire
from cl.watch_db import WatchDb
from cl.result_parser import get_and_parse

class AdWatcher:

    def __init__(self):
        self.db = WatchDb()

    def create_watch(self, name, url):
        self.db.create_watch(name, url)

    def delete_watch(self, name):
        self.db.delete_watch(name)

    def list_watches(self):
        for watch in self.db.get_watches():
            print(watch[1] + " " + watch[2])

    def update_watch_results(self):
        watches = self.db.get_watches()
        for watch in watches:
            watch_name = watch[1]
            for result in get_and_parse(watch[2]):
                if self.db.get_watch_result(watch_name, result['id']) is not None:
                    continue
                self.db.create_watch_result(watch[1],
                                            result['create_time'],
                                            result['id'],
                                            result['title'],
                                            result['place'],
                                            result['price'],
                                            result['url'],
                                            "")

    def list_watch_results(self, watch_name, since="1d"):
        hours_since = 24
        if since.endswith("d"):
            hours_since = int(since[:-1]) * 24
        elif since.endswith("h"):
            hours_since = int(since[:-1])
        else:
            print("using default since time, " + hours_since)

        for result in self.db.get_watch_results(watch_name, hours_since):
            print(result)


if __name__ == '__main__':
    fire.Fire(AdWatcher)

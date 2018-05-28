drop table if exists watches;
drop table if exists watch_results;

DROP TABLE IF EXISTS user;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

create table if not exists watches (
    id integer primary key autoincrement,
    create_time timestamp DEFAULT CURRENT_TIMESTAMP,
    last_search_time timestamp DEFAULT NULL,
    update_interval_minutes integer,
    name text unique,
    url text,
    user_id integer,
    foreign key(user_id) references user(id)
);

create table if not exists watch_results (
    id integer primary key autoincrement,
    watch_id integer,
    post_time timestamp,
    query_time timestamp,
    cl_id int unique,
    title text,
    place text,
    price int,
    url text,
    raw text,
    foreign key(watch_id) references watches(id) on delete cascade
);

--select watch_name, post_time, query_time, cl_id, title, place, price, url from watch_results order by
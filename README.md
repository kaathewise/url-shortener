# Url shortener
A comparison of several implementations of a simple url shortener app.

## Overall design decisions
* Output urls are unique, would not output the same short url for the same input. Reason: efficiency.
* Generated ids are Base64-encoded sequential numbers. Reason: simplicity for prototype. Better randomized ids may be added later.

## App variants

### Flask

Flask implementation is available for 4 storage types (SQLite, sharded SQLite, in-memory, and sharded in-memory), though it would only make sense to use it with SQLite, of which the sharded version has the best performance.

Steps to run the flask app (with flask dev server):
1. Init the storage:
```
mkdir sqlite
python -c "from shortener.storage import ShardedSQLiteStorage; ShardedSQLiteStorage('sqlite/db').init_db()"
```
2. Run with an appropriate configuration:
`export SHRT_CONFIG=../script/flask_sqlite_sharded.cfg; python shortener/app.py`

### Tornado + in-memory storage

A single-threaded and single-worker implementation with a simple in-memory storage.
Exists solely for its simplicity and good performance. Obvious limitations of an
in-memory storage.

To run the tornado app with in-memory storage, run:
`python shortener/tornado_app.py`

### Tornado + Redis

A multi-worker implementation using redis as a shared data storage. Utilizes client-side sharding by `task_id`.

Steps to run the tornado app with redis storage:
1. Run redis: `redis-server redis.conf`
2. Run app: `python shortener/tornado_redis.py`

This app is configured to run with 16 workers, and doesn't yet support external configuration.

## Comparison and conclusions

1. Single file SQLite is extremely slow because of the lock-based access to a single file.
2. Sharded SQLite is slightly better, and doesn't have the locking problem, but
it still has to write to disk, and the threaded implementation doesn't really help
with parallelisation.
3. In-memory storage is rather a proof of concept, and has an obvious disadvantage
of being temporary and bound to a single process. Multiple threads don't help in
this implementation because the handlers are completely blocking, and don't have
any IO. That's why tornado is a better choice for this approach.
4. Tornado with multiple workers + redis is the best single-machine solution,
and is arguably the closest to being production-like (though in this implementation
key generation is given to workers for efficiency, that certainly should be pushed
to the database in the real world). It doesn't write to disk, and can utilise the cores
to the max, yay! The obvious downside of redis is it being in-memory as well,
so some several million of records may consume 8Gb of RAM pretty fast.
A (sharded) redis cluster or a similar distributed key-value storage may be used
to productionise this solution.


## Load test measurements

### Flask + SQLite

```
16 threads and 16 connections
Thread Stats   Avg      Stdev     Max   +/- Stdev
  Latency    55.08ms    7.16ms  80.51ms   76.32%
  Req/Sec    17.84      4.50    30.00     76.96%
2897 requests in 10.10s, 554.59KB read
Requests/sec:    286.89
```

### Flask (threaded) + ShardedSQLite

```
16 threads and 256 connections
Thread Stats   Avg      Stdev     Max   +/- Stdev
  Latency   355.40ms   54.06ms 463.35ms   77.99%
  Req/Sec    27.84     27.29   161.00     86.36%
3607 requests in 10.10s, 690.40KB read
Socket errors: connect 0, read 505, write 7, timeout 0
Requests/sec:    357.02
```

### Tornado + InMemory

```
16 threads and 256 connections
Thread Stats   Avg      Stdev     Max   +/- Stdev
  Latency   129.99ms   21.23ms 175.52ms   79.73%
  Req/Sec   121.69     58.85   323.00     79.06%
18720 requests in 10.07s, 3.50MB read
Socket errors: connect 0, read 121, write 15, timeout 0
Requests/sec:   1859.24
```

### Tornado (16 workers) + Redis

```
16 threads and 256 connections
Thread Stats   Avg      Stdev     Max   +/- Stdev
  Latency   100.42ms   51.05ms 493.38ms   75.51%
  Req/Sec   164.67     34.11   272.00     69.39%
26181 requests in 10.10s, 4.89MB read
Socket errors: connect 0, read 4, write 4, timeout 0
Requests/sec:   2592.89
```

## TODO

Add tests and external configuration for tornado apps.

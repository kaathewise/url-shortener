# Url shortener test
An url shortener app prototype

# Design assumptions
* Output urls are unique, would not output the same short url for the same input. Reason: efficiency.
* Generated ids are Base64-encoded sequential numbers. Reason: simplicity for prototype. Better randomized ids may be added later.
* In-memory database implemented via a dictionary with a single lock. Reason: simplicity. In-memory db may be improved by sharding, but ultimately it should be separate.
* Synchronous server. Reason: simplicity, should be enough for a 1k prototype, doesn't make sense to make an async prototype anyway, as there is no IO.

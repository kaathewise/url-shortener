# Url shortener test
An url shortener app prototype

# Design decisions
* Output urls are unique, would not output the same short url for the same input. Reason: efficiency.
* Generated ids are Base64-encoded sequential numbers. Reason: simplicity for prototype. Better randomized ids may be added later.
* SQlite is used as storage, which will quickly become a bottle-neck in real world.

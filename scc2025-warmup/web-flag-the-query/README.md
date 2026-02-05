# Flag The Query

**Author** : legasi  
**Difficulty**: Easy  
**Description**: Our library's digital catalog has been compromised, leading to unauthorized access and mysterious disappearances of rare book records. Investigate the breach, uncover the exploit used by the perpetrators, and help us secure our treasured collection.

**Flag**: `SCC{n0_sql_1njection}`

# Writeup

The query is being executed without proper sanitization, allowing for NoSQL Injection.

Payload: `{ "$ne": null }`

[Checker script](https://github.com/CyberHeroRS/scc2025-warmup/blob/master/web_flag_the_query/checker/checker.py)


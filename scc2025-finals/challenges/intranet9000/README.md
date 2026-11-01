# Intranet 9000

**Name:** `intranet9000`   
**Category:** `web`   
**FLAG:** `SCC{no_sql_means_no_sql_injection}`   
**Provided:** full application source code.

Welcome to **Intranet 9000**! We tasked our best engineers to rewrite our previous SQL-injection-vulnerable app using NoSQL technology, meaning we'll never have an SQL injection problem again! 

Not only is our company directory app now GDPR-compliant, allowing employees to mark their contact information non-public, we have also added a brand new feature for storing important company secrets: Secure Notes!

## Solution

The goal, visible from the init script, is to log in as the company CEO and find the flag, which is stored in their personal notes.

The first vuln is the ability to filter on invisible fields, which includes the password field, in the public company directory. This allows you to leak the password hash one character at a time. You can query `/api/directory` with `?department=CEO&password=^a.*` to check if the first character of the hash is `a` - if you get a result, it is, if you get no results, it isn't. Repeat this until you know the password hash.

The passwords are generated...badly, so `hashcat` can make quick work of the hash. The list of first names, last names and years can be extracted from the `Faker` Python library and `combinator3` can be used to generate the final wordlist. 

The second vuln is a NoSQL injection on the login page, letting you bypass the need to know the employee ID (you can't leak it like the hash because $regex doesn't work on integers). POST something like `{"password": "[from hashcat]", "employee_number": { "$gt": 0 }}`.

With the session token you've received, you can now use authenticated endpoints such as `/api/notes`, where you'll find the flag.

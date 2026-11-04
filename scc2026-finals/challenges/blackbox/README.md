# web-pit

**Category:** web  
**Author:** MartinCo

## Description

Another blackbox pentest on a production server...REALLY?!

## Writeup

### Vulnerability

There are 2 vulnerabilities present, that need to be chained:
    - The first is a simple stored XSS in the contact form
    - The second is an XXE that needs to be exploited via the XSS on the admin bot 

### Intended solution

The attacker needs to exploit the XSS on the contact form which is visited and used on the admin bot. The cookies on the website have the HTTPOnly flag, which means that the attacker needs to enumerate the website through the admin bot:
    1. The admin user has 1 extra endpoint present in the header of the web app
    2. On that endpoint there is a JS file, which shows that the data sent on that enpoint is XML
    3. Construct an XXE payload to get the flag at /app/flag.txt
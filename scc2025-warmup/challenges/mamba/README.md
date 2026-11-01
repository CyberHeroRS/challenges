# Mamba

**Author** : tampon  
**Difficulty**: Easy  
**Description**: I hear mambas are a group of highly venomous snakes belonging to the genus Dendroaspis, found primarily in sub-Saharan Africa. They are known for their speed, agility, and potent neurotoxic venom.

**Flag**: `SCC{526a887e-8aff-41c5-9781-ec62375f69c4}`

## Writeup

```python
>>> code=marshal.load(f)
>>> code.co_consts
('1f7ae-4c6}--{a918c9e6-8278347f2565cf8C5SC', (19, 15, 10, 14, 28, 17, 39, 38, 36, 40, 27, 22, 3, 7, 23, 26, 9, 29, 37, 11, 30, 12, 13, 31, 24, 8, 32, 18, 33, 16, 5, 34, 6, 21, 20, 35, 25, 2, 4, 0, 1), '', 'The flag is:', 'Nope', None)
>>> enc = '1f7ae-4c6}--{a918c9e6-8278347f2565cf8C5SC'
>>> x = [19, 15, 10, 14, 28, 17, 39, 38, 36, 40, 27, 22, 3, 7, 23, 26, 9, 29, 37, 11, 30, 12, 13, 31, 24, 8, 32, 18, 33, 16, 5, 34, 6, 21, 20, 35, 25, 2, 4, 0, 1]
>>> ''.join([enc[x.index(i)] for i in range(len(enc))])
'SCC{526a887e-8aff-41c5-9781-ec62375f69c4}'
```

```bash
>> python mamba.pyc
SCC{526a887e-8aff-41c5-9781-ec62375f69c4}
The flag is: SCC{526a887e-8aff-41c5-9781-ec62375f69c4}
```

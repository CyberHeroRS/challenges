# CRY - Let's Create Generators Again

**Author** : Lofer
**Difficulty**: <font color='lightgreen'>Easy</font>  
**Description**: Last time I gave a bit too much info. Let's try again!

**External resources**:
- `generator.py` - [Download](public/generator.py)
- `out.txt` - [Download](public/out.txt)

**Flag**: ``SCC{maybe_i_should_give_up...}``

# Writeup
Subtract two outputs, use third output to solve linear equation, recover multiplier.

Construct a modular linear equation and solve for the flag and increment using first two outputs.
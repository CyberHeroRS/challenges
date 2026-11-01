# CRY - Exponents

**Author** : Lofer
**Difficulty**: <font color='lightgreen'>Easy</font>  
**Description**: Privacy this, privacy that. Why keep things private if we can encrypt them instead?

**External resources**:
- `exponents.py` - [Download](public/exponents.py)
- `out.txt` - [Download](public/out.txt)

**Flag**: ``SCC{pr1vat3_3xpoN3nts_n33d_t0_st4y_pr1v4t3}``

# Writeup

$enc = m^e$
$enc^hint = (m^e) ^ (d^e) = m^(e * d^e) = m^(3 * d^3)$
$enc^hint = m^(d^2)$
$(enc^hint)^9 = m^(d^2 * 3^2) = m$

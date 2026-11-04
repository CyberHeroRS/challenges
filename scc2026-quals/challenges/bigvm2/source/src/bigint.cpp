#include "bigint.hpp"


BigInt::BigInt() : vals(1, 0) {}

BigInt::BigInt(uint64_t n)
{
    vals.push_back((uint32_t)n);
    if (n >> 32) vals.push_back((uint32_t)(n >> 32));
}

BigInt::BigInt(const BigInt& other) : vals(other.vals) {}

BigInt& BigInt::operator=(const BigInt& other)
{
    vals = other.vals;
    return *this;
}

void BigInt::remove_leading_zeros()
{
    while (vals.size() > 1 && vals.back() == 0)
        vals.pop_back();
}

void BigInt::normalize()
{
    if (vals.empty()) vals.push_back(0);
    remove_leading_zeros();
}

int BigInt::cmp(const BigInt& a, const BigInt& b)
{
    if (a.vals.size() != b.vals.size())
        return a.vals.size() < b.vals.size() ? -1 : 1;

    for (size_t i = a.vals.size(); i-- > 0;)
        if (a.vals[i] != b.vals[i])
            return a.vals[i] < b.vals[i] ? -1 : 1;

    return 0;
}

bool BigInt::operator==(const BigInt& o) const { return vals == o.vals; }
bool BigInt::operator!=(const BigInt& o) const { return !(*this == o); }
bool BigInt::operator<(const BigInt& o) const { return cmp(*this, o) < 0; }
bool BigInt::operator<=(const BigInt& o) const { return cmp(*this, o) <= 0; }
bool BigInt::operator>(const BigInt& o) const { return cmp(*this, o) > 0; }
bool BigInt::operator>=(const BigInt& o) const { return cmp(*this, o) >= 0; }

BigInt BigInt::add(const BigInt& a, const BigInt& b)
{
    BigInt r;
    r.vals.assign(std::max(a.vals.size(), b.vals.size()) + 1, 0);

    uint64_t carry = 0;

    for (size_t i = 0; i < r.vals.size(); ++i)
    {
        uint64_t sum = carry;
        if (i < a.vals.size()) sum += a.vals[i];
        if (i < b.vals.size()) sum += b.vals[i];

        r.vals[i] = (uint32_t)sum;
        carry = sum >> 32;
    }

    r.normalize();
    return r;
}

BigInt BigInt::operator+(const BigInt& o) const { return add(*this, o); }
BigInt& BigInt::operator+=(const BigInt& o) { return *this = *this + o; }

BigInt BigInt::sub(const BigInt& a, const BigInt& b)
{
    BigInt r;
    r.vals.assign(a.vals.size(), 0);

    int64_t borrow = 0;

    for (size_t i = 0; i < a.vals.size(); ++i)
    {
        int64_t diff = (int64_t)a.vals[i]
                     - (i < b.vals.size() ? b.vals[i] : 0)
                     - borrow;

        if (diff < 0)
        {
            diff += (1LL << 32);
            borrow = 1;
        }
        else borrow = 0;

        r.vals[i] = (uint32_t)diff;
    }

    r.normalize();
    return r;
}

BigInt BigInt::operator-(const BigInt& o) const
{
    if (*this < o)
        throw std::runtime_error("BigInt cannot be negative");

    return sub(*this, o);
}

BigInt& BigInt::operator-=(const BigInt& o) { return *this = *this - o; }

BigInt BigInt::mul(const BigInt& a, const BigInt& b)
{
    BigInt r;
    r.vals.assign(a.vals.size() + b.vals.size(), 0);

    for (size_t i = 0; i < a.vals.size(); ++i)
    {
        uint64_t carry = 0;

        for (size_t j = 0; j < b.vals.size(); ++j)
        {
            uint64_t cur =
                r.vals[i + j] +
                (uint64_t)a.vals[i] * b.vals[j] +
                carry;

            r.vals[i + j] = (uint32_t)cur;
            carry = cur >> 32;
        }

        r.vals[i + b.vals.size()] += carry;
    }

    r.normalize();
    return r;
}

BigInt BigInt::operator*(const BigInt& o) const { return mul(*this, o); }
BigInt& BigInt::operator*=(const BigInt& o) { return *this = *this * o; }

uint32_t BigInt::get_bit(size_t i) const
{
    size_t w = i / 32;
    if (w >= vals.size()) return 0;
    return (vals[w] >> (i % 32)) & 1;
}

void BigInt::set_bit(size_t i)
{
    size_t w = i / 32;
    if (w >= vals.size()) vals.resize(w + 1, 0);
    vals[w] |= (1u << (i % 32));
}

void BigInt::divmod(const BigInt& a,
                    const BigInt& b,
                    BigInt& q,
                    BigInt& r)
{
    if (b.is_zero())
        throw std::runtime_error("Division by zero");

    q = BigInt(0);
    r = BigInt(0);

    size_t bits = a.vals.size() * 32;

    for (size_t i = bits; i-- > 0;)
    {
        r = r << 1;
        if (a.get_bit(i)) r.set_bit(0);

        if (r >= b)
        {
            r -= b;
            q.set_bit(i);
        }
    }

    q.normalize();
    r.normalize();
}

BigInt BigInt::operator/(const BigInt& o) const
{
    BigInt q, r;
    divmod(*this, o, q, r);
    return q;
}

BigInt BigInt::operator%(const BigInt& o) const
{
    BigInt q, r;
    divmod(*this, o, q, r);
    return r;
}

BigInt& BigInt::operator/=(const BigInt& o) { return *this = *this / o; }
BigInt& BigInt::operator%=(const BigInt& o) { return *this = *this % o; }

BigInt BigInt::operator&(const BigInt& o) const
{
    BigInt r;
    r.vals.resize(std::min(vals.size(), o.vals.size()));

    for (size_t i = 0; i < r.vals.size(); ++i)
        r.vals[i] = vals[i] & o.vals[i];

    r.normalize();
    return r;
}

BigInt BigInt::operator|(const BigInt& o) const
{
    BigInt r;
    r.vals.resize(std::max(vals.size(), o.vals.size()), 0);

    for (size_t i = 0; i < r.vals.size(); ++i)
    {
        uint32_t a = i < vals.size() ? vals[i] : 0;
        uint32_t b = i < o.vals.size() ? o.vals[i] : 0;
        r.vals[i] = a | b;
    }

    r.normalize();
    return r;
}

BigInt BigInt::operator^(const BigInt& o) const
{
    BigInt r = *this | o;
    BigInt a = *this & o;

    for (size_t i = 0; i < r.vals.size(); ++i)
        r.vals[i] ^= (i < a.vals.size() ? a.vals[i] : 0);

    r.normalize();
    return r;
}

BigInt BigInt::operator~() const
{
    BigInt r = *this;
    for (auto& v : r.vals) v = ~v;
    r.normalize();
    return r;
}

BigInt BigInt::operator<<(uint32_t s) const
{
    BigInt r;

    uint32_t w = s / 32;
    uint32_t b = s % 32;

    r.vals.assign(w, 0);

    uint64_t carry = 0;

    for (auto v : vals)
    {
        uint64_t cur = ((uint64_t)v << b) | carry;
        r.vals.push_back((uint32_t)cur);
        carry = cur >> 32;
    }

    if (carry) r.vals.push_back((uint32_t)carry);

    return r;
}

BigInt BigInt::operator>>(uint32_t s) const
{
    BigInt r;

    uint32_t w = s / 32;
    uint32_t b = s % 32;

    if (w >= vals.size()) return BigInt(0);

    r.vals.assign(vals.begin() + w, vals.end());

    uint64_t carry = 0;

    for (size_t i = r.vals.size(); i-- > 0;)
    {
        uint64_t cur = r.vals[i];
        r.vals[i] = (cur >> b) | (carry << (32 - b));
        carry = cur & ((1ULL << b) - 1);
    }

    r.normalize();
    return r;
}

BigInt BigInt::rol(uint32_t s) const { return (*this << s) | (*this >> s); }
BigInt BigInt::ror(uint32_t s) const { return (*this >> s) | (*this << s); }

BigInt BigInt::modpow(const BigInt& base, const BigInt& exp, const BigInt& mod)
{
    BigInt result(1);
    BigInt b = base % mod;
    BigInt e = exp;

    while (!e.is_zero())
    {
        if (e.get_bit(0))
            result = (result * b) % mod;

        e = e >> 1;
        b = (b * b) % mod;
    }

    return result;
}

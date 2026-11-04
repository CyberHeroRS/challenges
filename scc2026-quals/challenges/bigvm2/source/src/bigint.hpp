#ifndef BIGINT_HPP
#define BIGINT_HPP

#include <vector>
#include <fstream>
#include <cstdint>
#include <string>
#include <stdexcept>

class BigInt
{
public:
    BigInt();
    BigInt(uint64_t num);
    BigInt(const BigInt& other);
    
    BigInt& operator=(const BigInt& other);
    
    BigInt operator+(const BigInt& other) const;
    BigInt operator-(const BigInt& other) const;
    BigInt operator*(const BigInt& other) const;
    BigInt operator/(const BigInt& other) const;
    BigInt operator%(const BigInt& other) const;
    
    BigInt& operator+=(const BigInt& other);
    BigInt& operator-=(const BigInt& other);
    BigInt& operator*=(const BigInt& other);
    BigInt& operator/=(const BigInt& other);
    BigInt& operator%=(const BigInt& other);

    BigInt operator&(const BigInt& other) const;
    BigInt operator|(const BigInt& other) const;
    BigInt operator^(const BigInt& other) const;
    BigInt operator~() const;
    BigInt operator<<(uint32_t shift) const;
    BigInt operator>>(uint32_t shift) const;

    BigInt rol(uint32_t shift) const;
    BigInt ror(uint32_t shift) const;
    
    bool operator==(const BigInt& other) const;
    bool operator!=(const BigInt& other) const;
    bool operator<(const BigInt& other) const;
    bool operator<=(const BigInt& other) const;
    bool operator>(const BigInt& other) const;
    bool operator>=(const BigInt& other) const;
    
    static BigInt modpow(const BigInt& base, const BigInt& exp, const BigInt& mod);
    
    bool is_zero() const { return vals.size() == 1 && vals[0] == 0; }
    size_t size() const { return vals.size(); }
    
    const std::vector<uint32_t>& get_vals() const { return vals; }
    void set_vals(const std::vector<uint32_t>& new_vals) { vals = new_vals; }
    void push_back(uint32_t val) { vals.push_back(val); }
    uint32_t get_digit(size_t index) const { return vals[index]; }
    void set_digit(size_t index, uint32_t val) { vals[index] = val; }

private:
    std::vector<uint32_t> vals;
    
    void remove_leading_zeros();
    void normalize();

    static int cmp(const BigInt& a, const BigInt& b);
    static BigInt add(const BigInt& a, const BigInt& b);
    static BigInt sub(const BigInt& a, const BigInt& b);
    static BigInt mul(const BigInt& a, const BigInt& b);
    static void divmod(const BigInt& a, const BigInt& b, BigInt& q, BigInt& r);

    uint32_t get_bit(size_t i) const;
    void set_bit(size_t i);
};

#endif // BIGINT_HPP

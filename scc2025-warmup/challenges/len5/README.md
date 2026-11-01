# len5

**Author** : legasi  
**Difficulty**: Easy  
**Description**: Can you give us the number we need to be worthy of a flag?
**Flag**: `SCC{4rray5_are_p4r53d_7oo}`

# Writeup

The goal of this challenge was to pass the array as a value of `num`

```json
{
    "num":[767879,0,0,0,0] 
}
```
Length of this array equals to 5.

When you pass an array to parseInt, JavaScript converts the array to a string and then processes the first valid number it finds.


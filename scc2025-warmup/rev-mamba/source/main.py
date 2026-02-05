s = input()
f = '1f7ae-4c6}--{a918c9e6-8278347f2565cf8C5SC'
indices = [19, 15, 10, 14, 28, 17, 39, 38, 36, 40, 27, 22, 3, 7, 23, 26, 9, 29, 37, 11, 30, 12, 13, 31, 24, 8, 32, 18, 33, 16, 5, 34, 6, 21, 20, 35, 25, 2, 4, 0, 1]
if ''.join([f[indices.index(i)] for i in range(len(f))]) == s:
    print('The flag is:', s)
else:
    print('Nope')

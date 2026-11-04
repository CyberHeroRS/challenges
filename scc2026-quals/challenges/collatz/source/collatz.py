from os import getenv

flag = getenv("FLAG") or "SCC{test}"
s = set()

def step(n):
	if n % 2 == 0:
		return n // 2
	else:
		return 3*n + 1

print("I think mathematics has caught up to this problem!")
n = int(input())
if n == 0:
	exit()

for _ in range(2**10):
	if n == 1:
		exit()
	if n in s:
		print("Exception found! Well done!")
		print(flag)
		exit()
	s.add(n)
	n = step(n)
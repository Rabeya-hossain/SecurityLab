from random import randint

def powmod ( a,  b,  p) :
    res = 1
    while b != 0:
        if (b & 1) == 1:
            res =  res  * a % p
            b -= 1
        else:
            a = a  * a % p
            b >>= 1
    return res


def check_composite(n, a, d, s):
    x = powmod(a, d, n)
    if x == 1 or x == n - 1:
        return False
    for _ in range(1, s):
        x = (x * x) % n
        if x == n - 1:
            return False
    return True

def MillerRabin(n, iter=5):
    if n < 4:
        return n == 2 or n == 3

    s = 0
    d = n - 1
    while d & 1 == 0:
        d >>= 1
        s += 1

    for _ in range(iter):
        a = randint(2, n - 3)
        if check_composite(n, a, d, s):
            return False
    return True

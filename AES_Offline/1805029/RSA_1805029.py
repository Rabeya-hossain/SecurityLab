import random as rn
import math
import millar_rabin_1805029 as MR

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

def encryption(msg,e,n):
    arr = []
    for i in msg:
        asci = ord(i)
        arr.append(powmod(asci,e,n))
    return arr

def decryption(msg,d,n):
    dMsg = ""
    for i in msg:
        asci = powmod(i,d,n)
        ch = chr(asci)
        dMsg += ch
    return dMsg

def prime(k):
    kmin=k-2
    kmax=k+5
    num =rn.randint(2**kmin,2**kmax)
    ok =False
    while ok != True:
        num =rn.randint(2**kmin,2**kmax)
        if MR.MillerRabin(num,20) == True and MR.MillerRabin(num*2+1,20) == True:
            ok =True
    return num*2+1

def totient(n,p,q):
    result = n
    # p= 2*p'
    # q=2*q'

    result -= result // 2
    result -= result // (p//2)
    result -= result // (q//2)

    return result


def getNumbers(k):
    p = prime(k)
    q = prime(k)
    while p == q:
        q = prime(k)
    
    n = p * q
    lamda = (p - 1) * (q - 1)
   
    ok = False
    e = 1
    while ok == False:
        e += 1
        if math.gcd(e,lamda) == 1:
            ok = True
    
    phi = int(totient(lamda,p-1,q-1))
    d = powmod(e,phi - 1, lamda)
    
    publicKey = [e,n]
    privateKey = [d,n]
    # print(publicKey)
    # print(privateKey)
    return [publicKey,privateKey]

if __name__ == "__main__":
    [publicKey,privateKey] = getNumbers(128)
    # print(publicKey[0],publicKey[1])
    # print(privateKey[0],privateKey[1])
    ec=encryption("this is for encryption",publicKey[0],publicKey[1])
    dc= decryption(ec,privateKey[0],privateKey[1])
    print(dc)



    
    
    

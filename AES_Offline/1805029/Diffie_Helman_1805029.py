import random as rn
import time as tm
from tabulate import tabulate
import millar_rabin_1805029 as MR


ptime =0
gtime =0
atime =0
Atime =0
sharedkeytime =0


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

def generator (p):
    fact = []
    
    phi = p-1
    n = p-1
    fact.append(2)
    fact.append(int((p-1)/2))


    ok = False
    while ok == False:
        res = rn.randint(2,p)
        ok = True
        for i in range(0,len(fact)):
            ok &= (powmod (res,int( phi / fact[i]), p) != 1)
            if ok == True:
                break
        if ok == True:
            return res
    return -1

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

def getNumbers(k):

    global ptime
    ptime -= tm.time()
    p = prime(k)
    ptime += tm.time()

    global gtime
    gtime -= tm.time()
    g = generator(p)
    gtime += tm.time()

    global atime 
    atime -= tm.time()
    a = prime(int(k/2))
    atime += tm.time()

    global Atime
    Atime -= tm.time()
    A = powmod(g,a,p)
    Atime += tm.time()


    b = prime(int(k/2))
    B = powmod(g,b,p)

    global sharedkeytime
    sharedkeytime -= tm.time()
    finalA = powmod(A,b,p)
    sharedkeytime += tm.time()

    # finalB = powmod(B,a,p)
    return [p,g,A,a]


def printComparison():

    print("          computation time ")

    table = []
    table.append(["K","p","g","a or b","A or B","sharedKey"])

    # Printing the table

    for k in [128,192,256]:
        global ptime
        ptime =0
        global gtime
        gtime =0
        global atime
        atime =0
        global Atime
        Atime =0
        global sharedkeytime
        sharedkeytime =0

        for i in range(10):
            getNumbers(k)
        
        ptime /= 10
        gtime /=10
        atime /=10
        Atime /=10
        sharedkeytime /=10
        table.append([k,ptime,gtime,atime,Atime,sharedkeytime])
    print(tabulate(table, headers="firstrow"))


if __name__ == "__main__":
    printComparison()
    # k = int(input())
    # print( getNumbers(k))





import socket		
import Diffie_Helman_1805029 as DH
import inverseAES_1805029

s = socket.socket()		

port = 12345			

s.connect(('127.0.0.1', port))


keyMsg =s.recv(1024).decode()
[p,g,A] = keyMsg.split(',')
p = int (p)
g = int (g)
A = int (A)
b = DH.prime(int(64))
B = DH.powmod(g,b,p)

s.send(str(B).encode())
sharedKey = str(DH.powmod(A,b,p))
print("in client :",sharedKey)

s.send("Ready".encode())
     
readyMsg = s.recv(1024).decode()

if readyMsg == "Ready":
    cipherText = s.recv(1024).decode()
    print("decrypting ciphertext")
    plainText = inverseAES_1805029.inverseAES(cipherText,sharedKey,128)


# close the connection
s.close()	
	

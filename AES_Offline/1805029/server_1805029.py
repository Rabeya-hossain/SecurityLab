import socket	
import Diffie_Helman_1805029 as DH	
import AES_1805029	

s = socket.socket()		
print ("Socket successfully created")

port = 12345			

s.bind(('', port))		
print ("socket binded to %s" %(port))

s.listen(5)	
print ("socket is listening")		

while True:

    # Establish connection with client.
    c, addr = s.accept()	
    print ('Got connection from', addr )
    [p,g,A,a] = DH.getNumbers(128)
    keyMsg = str(p) + ',' +str(g) + ','+str(A)
    c.send(keyMsg.encode())

    B = int(c.recv(1024).decode())

    p = int (p)
    g = int (g)
    A = int (A)
    a = int(a)

    sharedKey = str(DH.powmod(B,a,p))
    print("in server :",sharedKey)

    c.send("Ready".encode())
     
    readyMsg = c.recv(1024).decode()

    if readyMsg == "Ready":
        file = open('painText.txt','r')
        text = file.read()
        print("plaintext : ", text)
        cipherText = AES_1805029.AES(text,sharedKey,128)
        print("sending ciphertext")
        c.send(cipherText.encode())


    # Close the connection with the client
    c.close()

    # Breaking once connection closed
    break

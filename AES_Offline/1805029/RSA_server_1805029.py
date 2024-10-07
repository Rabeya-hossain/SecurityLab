import socket	
import RSA_1805029 as RSA
import pickle

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

    tmp = c.recv(1024)
    cPublicKey = pickle.loads(tmp)
    print(cPublicKey)

    received_data =c.recv(4096)
    deserialized_data = pickle.loads(received_data)

    [plainText,encryptedMsg] = deserialized_data
   
    decryptedMsg = RSA.decryption(encryptedMsg,cPublicKey[0],cPublicKey[1])

    print(decryptedMsg)
    
    if plainText == decryptedMsg:
        print("client authenticated")
    else:
        print("Not authentic user")

    c.close()
    break

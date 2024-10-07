import socket		
import RSA_1805029 as RSA
import pickle


s = socket.socket()		

port = 12345			

s.connect(('127.0.0.1', port))

[publicKey,privateKey] = RSA.getNumbers(128)
keyMsg = str(publicKey[0])+','+str(publicKey[1])
print("client sending its public key")
s.send(pickle.dumps(publicKey))

plainText = "this is for authentication"
encryptedMsg = RSA.encryption(plainText,privateKey[0],privateKey[1])
decrytedMsg = RSA.decryption(encryptedMsg,publicKey[0],publicKey[1])
print(decrytedMsg)

data = [plainText,encryptedMsg]
serializedData = pickle.dumps(data)
print("client sending msg for authentication")
s.sendall(serializedData)

s.close()


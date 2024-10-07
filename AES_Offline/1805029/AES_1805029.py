import numpy as np
import bitvector_1805029 as bv
import inverseAES_1805029 as invAES
import time as tm

roundNum = 10
keySize = int(128/8)
textSize = int(128/8)
keyScheduleTime = 0
encryptionTime = 0

roundConstant = np.full((roundNum +1, 4 ), "hello")


def file_to_string(file_path):
    with open(file_path, 'rb') as file:
        binary_data = file.read()
    # return str(binary_data)
    return str(binary_data)[2:-1]
    return ascii_string

def setRound(keyLength):
    global roundNum
    global keySize
    global roundConstant
    if keyLength == 128:
        roundNum = 10
        keySize = int(128/8)
    elif keyLength == 192:
        roundNum = 12
        keySize = int(192/8)
    else :
        roundNum = 14
        keySize = int(256/8)
    roundConstant.resize((roundNum+1,4))


def adjustKey(key):
    if len(key) > keySize :
        key = key[-keySize:]
    else:
        i = 1
        while len(key) != keySize:
            if i == 1:
                 key = key[- i :] + key
            else:
                 key = key[- i : - i + 1] + key
            i += 1
    return key

def adjustText(text): 
    i = 1
    # while len(text) != textSize:
    #     if i == 1:
    #             text = text[- i :] + text
    #     else:
    #             text = text[- i : - i + 1] + text
    #     i += 1
    while len(text) != textSize:
        text += '\0'
    return text

def XOR(str1,str2):
    integer1 = int(str1, 16)
    integer2 = int(str2, 16)
    result_integer = integer1 ^ integer2
    #print(integer1," ",integer2," ",result_integer)

    result_hex = hex(result_integer)
    return result_hex[2:]

def roundConstantCalculation():
    x = "1"
    mxLimit = str("11b")
    roundConstant[1] = [x,"00","00","00"]
    for i in range(2,roundNum+1):
        x_int = int(x,16)
        x_int = x_int * 2
        x_hex = hex(x_int)
        x_hex = x_hex[2:]
        if int(x,16) >= int("80",16):
            x_hex = XOR(x_hex,mxLimit)
        x = x_hex
        roundConstant[i] = [x_hex,"00","00","00"]

def gKey(word,roundNum):
    wordLength =len(word)
    word = np.roll(word, -1) #left shift
    #substitution
    for i in range(wordLength):
        b = bv.BitVector(hexstring=word[i])
        int_val = b.intValue()
        s = bv.Sbox[int_val]
        s = bv.BitVector(intVal=s, size=8)
        word[i] = s.get_bitvector_in_hex()
    #adding round constant
    roundConstantTmp = roundConstant[roundNum]
    #print(roundConstantTmp)
    for i in range(len(word)):
        word[i] = XOR(word[i],roundConstantTmp[i])
    return word

def keyExapnsion(key):
    roundConstantCalculation()
    length = len(key)
    keys = np.full((roundNum + 1 , length ), "hello")
    for i in range(len(key)):
        mystr = hex(ord(key[i]))
        keys[0][i] = mystr[2:]
    # w = np.full((roundNum + 1) * 4,"hello")
    # subarrays = np.array_split(keys[0], 4)
    # w = np.array(subarrays)
    for i in range(1,roundNum + 1):
        for j in range(0, length, 4):
            if j == 0:
                #print(keys[i-1][length-4: length])
                word = gKey(keys[i-1][length-4: length],i)
                for k in range(j, j+4):
                    keys[i][k] = XOR(keys[i-1][k],word[k-j])
            else:
                for k in range(j, j+4):
                    keys[i][k] = XOR(keys[i-1][k],keys[i][k-4])
    return keys


def substitutionBytes(stateMatrix):
    row_dimension = stateMatrix.shape[0]
    clm_dimension = stateMatrix.shape[1]
    for i in range(row_dimension):
        for j in range(clm_dimension):
            b = bv.BitVector(hexstring=stateMatrix[i][j])
            int_val = b.intValue()
            s = bv.Sbox[int_val]
            s = bv.BitVector(intVal=s, size=8)
            stateMatrix[i][j] = s.get_bitvector_in_hex()
    return stateMatrix

def shiftRows(stateMatrix):
    row_dimension = stateMatrix.shape[0]
    for i in range(row_dimension):
        stateMatrix[i] = np.roll(stateMatrix[i],-i)
    return stateMatrix

def mixColoums(stateMatrix):
    row_dimension = stateMatrix.shape[0]
    newStateMatrix = np.full((row_dimension,row_dimension),"00000000")
    for i in range(row_dimension):
        for j in range(row_dimension):
            for k in range(row_dimension):
                bv1 = bv.Mixer[i][k]
                bv2 = bv.BitVector(hexstring=stateMatrix[k][j])
                bv3 = bv1.gf_multiply_modular(bv2, bv.AES_modulus, 8)
                integer_value = int(str(bv3),2)
                hex_value = hex(integer_value)[2:]
                newStateMatrix[i][j] = XOR(newStateMatrix[i][j],hex_value)
    return newStateMatrix

    

def addRoundKey(stateMatrix,roundKey):
    row_dimension = stateMatrix.shape[0]
    clm_dimension = stateMatrix.shape[1]

    clmRound = np.full((row_dimension,clm_dimension),"hello")
    for i in range(row_dimension):
        for  j in range(clm_dimension):
            clmRound[j][i] = roundKey[i*row_dimension+j]

    for i in range(row_dimension):
        for j in range(clm_dimension):
            stateMatrix[i][j] = XOR(stateMatrix[i][j],clmRound[i][j])
    return stateMatrix

def AES(lrgPlainText,key,keyLength):
    setRound(keyLength)
    start = tm.time()
    key = adjustKey(key)
    keys = keyExapnsion(key)
    end = tm.time()

    global keyScheduleTime
    keyScheduleTime = end - start

    start = tm.time()

    dimension = 4
    cipherTextHex = ""
    cipherTextAscii = ""

    for i in range(0, len(lrgPlainText), textSize):
        if i+textSize <= len(lrgPlainText):
            plainText = lrgPlainText[i:i+textSize]
        else:
             plainText = lrgPlainText[i:]
             plainText = adjustText(plainText)
    
        stateMatrix = np.full((dimension,dimension),"hello")
        for i in range(dimension):
            for j in range(dimension):
                stateMatrix[j][i] = hex(ord(plainText[i*dimension+j]))[2:]
        #round 0
        #print(keys[0])
        stateMatrix = addRoundKey(stateMatrix,keys[0])
        for i in range(1,roundNum):
            stateMatrix = substitutionBytes(stateMatrix)
            stateMatrix = shiftRows(stateMatrix)
            stateMatrix = mixColoums(stateMatrix)
            stateMatrix = addRoundKey(stateMatrix,keys[i])

        #round 10 , without mix coloums
        stateMatrix = substitutionBytes(stateMatrix)
        stateMatrix = shiftRows(stateMatrix)
        stateMatrix = addRoundKey(stateMatrix,keys[roundNum])

        
        for i in range(dimension):
            for j in range(dimension):
                cipherTextHex += stateMatrix[j][i]
                #print(stateMatrix[i][j], end = '')
        
        for i in range(dimension):
            for j in range(dimension):
                cipherTextAscii += chr(int(stateMatrix[i][j],16))
                #print(chr(int(stateMatrix[i][j],16)), end = '')
        
    
    end = tm.time()
    global encryptionTime
    encryptionTime = end - start

    print("Cipher Text:")
    print("In HEX: ",cipherTextHex)
    print()
    print("In ASCII: ",cipherTextAscii)
    return cipherTextAscii

def printText(text,key):

    hexText = ""
    for i in range(0, len(text)):
        hexText += hex(ord(text[i]))[2:]
    hexKey = ""
    for i in range(0, len(key)):
        hexKey += hex(ord(key[i]))[2:]

    # hexText = ""
    # for i in range(0, min([len(text),128])):
    #     hexText += hex(ord(text[i]))[2:]
    # hexKey = ""
    # for i in range(0, len(key)):
    #     hexKey += hex(ord(key[i]))[2:]

    # text2 =""
    # for i in range(0, min([len(text),128])):
    #     text2 += text[i]

    print("plain Text:")
    print("In ASCII: ",text)
    print("In Hex : ",hexText)
    print()
    print("Key:")
    print("In ASCII: ",key)
    print("In Hex : ",hexKey)
    print()


if __name__ == "__main__":
    fileName = input()
    key = input()
    keyLength = int(input())
    
   
    text = file_to_string(fileName)

    printText(text, key)

    cipherText = AES(text,key,keyLength)
    print()
    plainText = invAES.inverseAES(cipherText,key,keyLength)

    print()
    print("Execution Details:")
    print("Key Scheduling :",keyScheduleTime)
    print("Encryption Time :",encryptionTime)
    print("Decryption Time :",invAES.decryptionTime)



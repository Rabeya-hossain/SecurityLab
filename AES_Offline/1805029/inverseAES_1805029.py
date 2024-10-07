import numpy as np
import bitvector_1805029 as bv
import time as tm



roundNum = 10
keySize = int(128/8)
textSize = int(128/8)
decryptionTime =0


roundConstant = np.full((roundNum +1, 4 ), "hello")

def setRound(keyLength):
    global roundNum
    global keySize
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
    # i = 1
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


def inverseSubstitutionBytes(stateMatrix):
    row_dimension = stateMatrix.shape[0]
    clm_dimension = stateMatrix.shape[1]
    for i in range(row_dimension):
        for j in range(clm_dimension):
            b = bv.BitVector(hexstring=stateMatrix[i][j])
            int_val = b.intValue()
            s = bv.InvSbox[int_val]
            s = bv.BitVector(intVal=s, size=8)
            stateMatrix[i][j] = s.get_bitvector_in_hex()
    return stateMatrix

def inverseShiftRows(stateMatrix):
    row_dimension = stateMatrix.shape[0]
    for i in range(row_dimension):
        stateMatrix[i] = np.roll(stateMatrix[i],i)
    return stateMatrix

def inverseMixColoums(stateMatrix):
    row_dimension = stateMatrix.shape[0]
    newStateMatrix = np.full((row_dimension,row_dimension),"00000000")
    for i in range(row_dimension):
        for j in range(row_dimension):
            for k in range(row_dimension):
                bv1 = bv.InvMixer[i][k]
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
    
def inverseAES(lrgCipherText,key,keyLength):
    setRound(keyLength)
    key = adjustKey(key)
    keys = keyExapnsion(key)
    dimension = 4
    plainTextHex = ""
    plainTextAscii = ""

    start = tm.time()

    for i in range(0, len(lrgCipherText), textSize):
        if i+textSize <= len(lrgCipherText):
            cipherText = lrgCipherText[i:i+textSize]
        else:
            cipherText = lrgCipherText[i:]
            cipherText = adjustText(plainText)

        stateMatrix = np.full((dimension,dimension),"hello")
        for i in range(dimension):
            for j in range(dimension):
                stateMatrix[i][j] = hex(ord(cipherText[i*dimension+j]))[2:]
        #round 0
        #print(keys[0])
        stateMatrix = addRoundKey(stateMatrix,keys[roundNum])
        for i in range(roundNum - 1,0,-1):
            stateMatrix = inverseShiftRows(stateMatrix)
            stateMatrix = inverseSubstitutionBytes(stateMatrix)
            stateMatrix = addRoundKey(stateMatrix,keys[i])
            stateMatrix = inverseMixColoums(stateMatrix)
            

        #round 10 , without mix coloums
        stateMatrix = inverseShiftRows(stateMatrix)
        stateMatrix = inverseSubstitutionBytes(stateMatrix)
        stateMatrix = addRoundKey(stateMatrix,keys[0])

        for i in range(dimension):
            for j in range(dimension):
                plainTextHex += stateMatrix[j][i]
    
        plainText = ""
        for i in range(dimension):
            for j in range(dimension):
                plainTextAscii += chr(int(stateMatrix[j][i],16))
    end = tm.time()
    global decryptionTime
    decryptionTime =  end - start
    print("Deciphered Text:")
    print("In HEX: ",plainTextHex)
    print()
    print("In ASCII: ",plainTextAscii)

    return plainTextAscii


if __name__ == "__main__":
    inverseAES("dksnds","infsu",128)


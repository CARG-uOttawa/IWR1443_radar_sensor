import pandas as pd
import numpy as np
import math

class UartParser:

    def searchMagicWord(data):
        MAGIC_WORD = np.array([2, 1, 4, 3, 6, 5, 8, 7])
        orderedMagicWord = np.arange(MAGIC_WORD.size)
        M = (data[np.arange(data.size - MAGIC_WORD.size + 1)[:, None] + orderedMagicWord] == MAGIC_WORD).all(1)
        return np.where(M == True)[0]
    
    def convertHex():
        return np.frombuffer(b"\x02\x01\x04\x03\x06\x05\x08\x07\x04\x00\x01\x02\xa0\x02\x00\x00C\x14\n\x00*\x00\x00\x00f\xdb\xbb\x1c\x05\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00@\x00\x00\x00\x05\x00\t\x00\x02\x00\x00\x00\x04\x03\x1f\x00\x1c\x00\x00\x000\x00\x00\x00\xae\n\x1f\x00\xed\x03\x00\x006\x00\x00\x00\x1b\x06#\x00j\x04\x00\x00]\x00\x00\x00\x8d\x00\xc3\xff\x9b\x07\x00\x00\x02\x00\x00\x00\xc3\x02\xf3\xff(\x00\x00\x00\x02\x00\x00\x00\x00\x02\x00\x00\x88#\x90%\xd8%H$\xa8\x1f@\x1e\xa0\x1fH\x1eH\x1f\xd8 \x08 h\x1f\x18 \x10!\xc0 \xe0\x1f \x1fh\x1e \x1e\xa0\x1e\xe8\x1dX\x1dP\x1b\xd8\x1b\xc8\x1c\x18\x1d\xc8\x1d\xc8\x1d\xd0\x1c\xa0\x1b\xf0\x1aH\x1c\x10\x1b\xc0\x1a(\x1c\xe0\x1b@\x1b0\x1cX\x1b0\x1b\x88\x1a\x90\x1b\x18\x1b\xa8\x19\x98\x1a0  &\xb8(\xc8(\xb0&@$\xf0! $\xc0&\x10'\x18%\x00#\x90!P \xc0\x1f\xb8 x\x1e\xd8\x1d\x18\x1e\xf8\x1cH\x1c\xe8\x1d\x88\x1d\x18\x1c\x18\x1b`\x1b\xd0\x1c(\x1d\xa0\x1b\x08\x1b\xf0\x1a@\x1a\xd8\x1a`\x19\xd0\x19\x90\x19\xf0\x18\x10\x1b\xc0\x1a\xa8\x19\xf8\x19P\x19\xe0\x18h\x19x\x1a\xb8\x1a\xa0\x1bx\x1e@ \x00 \x10\x1e(\x1d\xb8\x1d@\x1e\xf8\x1e`\x1f\xb0\x1e`\x1c\xc8\x1a\x00\x1c \x1dX\x1d\xf0\x1b\xc0\x1a\xf8\x19\xb8\x18\xa0\x19\x88\x19\x88\x18\xa0\x18(\x1b \x1c\xe0\x1b\xb0\x1bx\x1a\xe8\x19x\x1a(\x1a\x00\x1a\x90\x1aP\x1a8\x1a\xd0\x18\xb8\x17\x10\x17\x10\x18(\x17\xf0\x17P\x17\xa8\x16\x18\x18\xd0\x17\xd0\x17\x88\x18\xc8\x18(\x17\x80\x16x\x18\x08\x19\xd0\x18(\x18\xa8\x188\x17\x88\x17\xf8\x160\x16\xe8\x15x\x16\x80\x16@\x16\xb8\x15\xa0\x15\xd8\x15\x10\x16\x88\x15\x08\x16\xe8\x14\xe8\x14P\x16\xc0\x16\xb0\x15\x00\x16\xe8\x15\xe8\x16`\x18", dtype='uint8')
    
    def convertData(encodedData):
        '''This method assumes that the magic word was found and is the begining of the string
        '''
        # print(encodedData)
        BYTE_TO_INT_ARRAY = [1, math.pow(2, 8), math.pow(2, 16), math.pow(2, 24)]

        #Start By Veryfing if the Magic Word is received
        magicWord = encodedData[0:8]
        version = bytearray(encodedData[8:12]).hex() #Not to sure about how to convert these from their hexadecimal values to actually something
        packetLength = np.matmul(encodedData[12:16], BYTE_TO_INT_ARRAY)
        platform = bytearray(encodedData[16:20]).hex()
        frameNumber = np.matmul(encodedData[20:24], BYTE_TO_INT_ARRAY)
        time = np.matmul(encodedData[24:28], BYTE_TO_INT_ARRAY)
        numberObjects = np.matmul(encodedData[28:32], BYTE_TO_INT_ARRAY)
        numberStructures = np.matmul(encodedData[32:36], BYTE_TO_INT_ARRAY)

        structures = []
        offset = 0

        for indexStructure in range(int(numberStructures-1)): #figure out for multiple packages what is going on
            structure = UartParser.Structure()
            structure.parseStructure(encodedData[36+offset:])
            structures.append(structure)
            offset += structure.getLength()+8 # We add the 8 bytes for the Tag and Length that aren't counted in the Length calculations
        
        return structures
    

        
        
    class Structure:

        BYTE_TO_INT_ARRAY = [1, math.pow(2, 8)]
    
        def __init__(self):
            self.__structureTag = None
            self.__lengthOfStructure = None
            self.__descriptor = None
            self.__points = []
        
        def parseStructure(self, structureEncodedData):
            self.__structureTag = "POINTS_DETECTED" if np.matmul(structureEncodedData[0:4], [1, math.pow(2, 8), math.pow(2, 16), math.pow(2, 24)]) == 1 else None 
            self.__lengthOfStructure = np.matmul(structureEncodedData[4:8], [1, math.pow(2, 8), math.pow(2, 16), math.pow(2, 24)])

            if self.__structureTag == "POINTS_DETECTED":
                numPoints = np.matmul(structureEncodedData[8:10], UartParser.Structure.BYTE_TO_INT_ARRAY)
                xyzFormat = math.pow(2, np.matmul(structureEncodedData[10:12], UartParser.Structure.BYTE_TO_INT_ARRAY))
            
                for i in range(int(numPoints)):
                    point = UartParser.Structure.Point()
                    point.parsePoint(structureEncodedData[i*12:(1+i)*12], xyzFormat)
                    self.__points.append(point)
        
            else:
                pass


        def getLength(self):
            return int(self.__lengthOfStructure)

        def getType(self):
            return self.__structureTag
        def getPoints(self):
            return self.__points

        class Point:

            def __init__(self):
                self.__rangeIndex = None
                self.__dopplerIndex = None
                self.__peakValue = None
                self.__position = [None, None, None]
            
            def parsePoint(self, objectEncodedData, structureXYZFromat):
                self.__rangeIndex = np.matmul(objectEncodedData[0:2], UartParser.Structure.BYTE_TO_INT_ARRAY)
                self.__dopplerIndex = np.matmul(objectEncodedData[2:4], UartParser.Structure.BYTE_TO_INT_ARRAY)
                self.__peakValue = np.matmul(objectEncodedData[4:6], UartParser.Structure.BYTE_TO_INT_ARRAY)
                x = np.matmul(objectEncodedData[6:8], UartParser.Structure.BYTE_TO_INT_ARRAY)/structureXYZFromat
                y = np.matmul(objectEncodedData[8:10], UartParser.Structure.BYTE_TO_INT_ARRAY)/structureXYZFromat
                z = np.matmul(objectEncodedData[10:12], UartParser.Structure.BYTE_TO_INT_ARRAY)/structureXYZFromat
                self.__position = [x, y, z]
            
            def getPosition(self):
                return self.__position
        
if __name__ == "__main__":
    UartParser.convertData(UartParser.convertHex())
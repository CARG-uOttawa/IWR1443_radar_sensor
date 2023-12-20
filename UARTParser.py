import pandas as pd
import numpy as np
import math

class UartParser:

    def convertHex():
        return np.frombuffer(b'\x02\x01\x04\x03\x06\x05\x08\x07\x04\x00\x01\x02\xa0\x02\x00\x00C\x14\n\x00\x12\x00\x00\x00\x9b.\x84[\x04\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x004\x00\x00\x00\x04\x00\t\x00\x02\x00\x00\x00\xe7\x02\x1f\x00\x1c\x00\x00\x00/\x00\x00\x00\x9f\x05\x00\x00\xd8\x03\x00\x006\x00\x00\x00E\t#\x00j\x04\x00\x00\x02\x00\x00\x00\xaa\x02\xf3\xff(\x00\x00\x00\x02\x00\x00\x00\x00\x02\x00\x00H#X%\xc0%8$\xe0\x1fX\x1fH\x1fH\x1e\xc0\x1f\x18 \x18!\xb0!\xb8 \xe0\x1fP\x1f8\x1f`\x1e\xf8\x1dH\x1d\x98\x1d \x1dh\x1d\xf8\x1c\x18\x1cx\x1c \x1dX\x1d\x18\x1d\xf0\x1b\xd0\x1c\xa0\x1b\xf8\x18\x18\x1b\x10\x1b(\x19X\x19\xe0\x1bH\x1d\xc8\x1cX\x1a\x18\x19\x00\x19\xb8\x19\x08\x19h\x18\xe8\x1ep$\xf0&\xa0&\xd0%\x80#H"\x18%@(p(\xe0%\x90"\xc0 \xd8\x1fh   \xf8\x1fx\x1f\xe0\x1e\xd0\x1d0\x1d\x08\x1d\x88\x1c\xd0\x1bh\x1bp\x1a\x98\x1a\xb0\x1a\xc0\x1a\x98\x1a\x10\x1bP\x1a\xf8\x19\x18\x1a\xd0\x19\x10\x198\x19\xf8\x18P\x1a\x80\x1b\xa8\x19 \x19\xd0\x18@\x19p\x19\xd8\x18\x98\x19\x10\x1c\xa8\x1d\xb0\x1dP\x1c\xe0\x1b@\x1d\xa0\x1d\xa8\x1f\xa8\x1f0\x1b\x88\x1bh\x1b\xd0\x1a\xc0\x1c8\x1d\xe8\x1bH\x1b\xd0\x1aP\x19\xb0\x19\x88\x190\x17 \x19\xe0\x19\xc0\x19h\x19\xa0\x19\xb8\x1a\xa0\x1bH\x1bP\x19\x80\x18p\x19H\x19H\x19\xd0\x18\xd8\x19\x90\x19\x18\x1a\xe0\x1ax\x1a\xf8\x17\xf0\x16\xe0\x16x\x16@\x17\xf8\x17\xf8\x17', dtype='uint8')
    
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

        for indexStructure in range(int(numberStructures)):
            structure = UartParser.Structure()
            structure.parseStructure(encodedData[36+offset:])
            structures.append(structure)
            offset += structure.getLength()+8 # We add the 8 bytes for the Tag and Length that aren't counted in the Length calculations
        
        pass

        
        
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
        
        def getLength(self):
            return int(self.__lengthOfStructure)

        def getType(self):
            return self.__structureTag

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
        

UartParser.convertData(UartParser.convertHex())
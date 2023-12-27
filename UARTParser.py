import pandas as pd
import numpy as np
import math

class UartParser:

    def searchMagicWord(data):
        MAGIC_WORD = np.array([2, 1, 4, 3, 6, 5, 8, 7])
        orderedMagicWord = np.arange(MAGIC_WORD.size)
        M = (data[np.arange(data.size - MAGIC_WORD.size + 1)[:, None] + orderedMagicWord] == MAGIC_WORD).all(1)
        return np.where(M == True)[0]
    
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
            structure = UartParser.Structure(time)
            structure.parseStructure(encodedData[36+offset:])
            structures.append(structure)
            offset += structure.getLength()+8 # We add the 8 bytes for the Tag and Length that aren't counted in the Length calculations
        
        return structures
    

        
        
    class Structure:

        BYTE_TO_INT_ARRAY = [1, math.pow(2, 8)]
    
        def __init__(self, time):
            self.__structureTag = None
            self.__lengthOfStructure = None
            self.__descriptor = None
            self.__points = []
            self.__time = time
        
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
        
            else: # We ignore the statistics structure and fourier transform details
                pass


        def getLength(self):
            return int(self.__lengthOfStructure)

        def getType(self):
            return self.__structureTag
        
        def getPoints(self):
            return self.__points
        
        def getTime(self):
            return self.__time

        def getDataFrame(self):
            if self.getType() == "POINTS_DETECTED":
                objectData = pd.DataFrame(columns = ["Time", "X", "Y", "Z"])
                for point in self.getPoints():
                    x, y, z = point.getPosition()
                    objectData = pd.concat([objectData, pd.DataFrame(data= [{"Time":self.getTime(), "X":x, "Y":y, "Z":z}])])
                return objectData

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
            def getTime(self):
                return self.__time
        
if __name__ == "__main__":
    UartParser.convertData(UartParser.convertHex())
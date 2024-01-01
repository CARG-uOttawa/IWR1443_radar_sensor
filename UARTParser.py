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
                objectData = None
                for point in self.getPoints():
                    x, y, z = point.getPosition()
                    if objectData is None:
                        objectData = pd.DataFrame(data= [{"Time":self.getTime(), "X":x, "Y":y, "Z":z}])
                    else:
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

                #Do not forget the data is in signed data representation in 2's complement
                x = np.matmul(objectEncodedData[6:8], UartParser.Structure.BYTE_TO_INT_ARRAY)/structureXYZFromat if np.matmul(objectEncodedData[6:8], UartParser.Structure.BYTE_TO_INT_ARRAY) < (math.pow(2, 15)-1) else (np.matmul(objectEncodedData[6:8], UartParser.Structure.BYTE_TO_INT_ARRAY) -math.pow(2, 16))/structureXYZFromat
                y = np.matmul(objectEncodedData[8:10], UartParser.Structure.BYTE_TO_INT_ARRAY)/structureXYZFromat if np.matmul(objectEncodedData[8:10], UartParser.Structure.BYTE_TO_INT_ARRAY) < (math.pow(2, 15)-1) else (np.matmul(objectEncodedData[8:10], UartParser.Structure.BYTE_TO_INT_ARRAY) -math.pow(2, 16))/structureXYZFromat
                z =  np.matmul(objectEncodedData[10:12], UartParser.Structure.BYTE_TO_INT_ARRAY)/structureXYZFromat if np.matmul(objectEncodedData[10:12], UartParser.Structure.BYTE_TO_INT_ARRAY) < (math.pow(2, 15)-1) else (np.matmul(objectEncodedData[10:12], UartParser.Structure.BYTE_TO_INT_ARRAY) -math.pow(2, 16))/structureXYZFromat
                self.__position = [x, y, z]
            
            def getPosition(self):
                return self.__position
            def getTime(self):
                return self.__time
        
if __name__ == "__main__":
    UartParser.convertData(b"02 01 04 03 06 05 08 20 04 20 01 02 A0 02 20 20 43 14 0A 20 4E 20 20 20 FF 2E E2 2020 05 20 20 20 03 20 20 20 01 20 20 20 40 20 20 20 05 20 09 20 02 20 20 20 AB 02 1E 20 1D 20 20 20 31 20 20 20 7E 06 40 20 20 04 20 20 38 20 20 20 20 26 02 49 20 201C 04 20 20 02 20 20 20 78 02 E6 FF 21 20 20 20 38 20 20 20 FA 01 24 FE 30 04 20 20 02 20 20 20 20 02 20 20 60 23 50 25 2DC 25 E8 23 F0 1F A8 1D 08 1C 20 1B 20AC 1B B0 1B 50 19 10 18 F0 1A 2C6 1D C8 1D D0 1B 90 19 C8 19 10 18 F0 19 58 1B 08 1A 20 18 2DC 18 20 1A 58 1A 10 1A 68 1A 30 1C C0 1D 40 1D E8 1B 50 1C 38 1D 08 1D 20 1D 20 1C C0 1D 28 21 20AC 21 E0 1F D8 1F B8 1E C8 1D C0 1D 48 1D 50 1D 78 1F 48 25 58 27 38 26 20 23 50 22 70 20 38 21 C0 23 E0 24 70 24 A0 22 E0 21 E8 20 20AC 20 B8 1F D8 1E E0 1E 20 1F 50 1F A8 1E 10 1E 38 1E 18 1D A0 1C 48 1C 68 1C B8 1B 20AC 1A B8 1A F8 1A E0 1A 08 1B E0 1A 2C6 1A D0 1B 2DC 1C 60 1B 30 19 70 1A D0 1B 70 1B A8 1A 20 1A B0 18 B8 17 10 19 2DC 19 2C6 19 E8 19 50 1A E8 19 D8 19 A0 1A A8 1B F0 1A B0 19 78 1B C8 1B E8 1A C8 1A 10 1B 20 1B E8 1A 90 1A E8 18 D0 18 18 19 A0 18 78 1A 20AC 1A 20 1A 20AC 1C 40 1D D8 1C 28 1C 30 1B C0 1A A0 1A 48 1B F8 1A C8 19 10 1A 70 19 60 18 78 19 40 18 90 17 A0 16 28 19 D8 19 08 19 2C6 18 08 18 50 17 2C6 17 70 17 F8 17 58 17 B0 16 60 17 C8 17 2C6 16 F8 16 78 16 A8 16 18 17 78 17 E8 16 10 16 2C6 16 38 16 18 16 70 15 38 15 68 15 50 16 20 16 90 17 B0 17 28 17 20 17 18 16 2C6 16 20AC 16 40 17 60 15 F0 14 58 15 20 15 50 16 B0 16 B8 15 F0 15 28 16 A0 15 20 15 50 16 D8 15 B8 14 18 15 20AC 16 30 17 40 17 08 17 60 15 90 14 28 15 C8 14 30 14 38 15 70 14 B8 14 A8 15 A8 15 F8 15 F0 14 C8 14 E0 14 D8 15 F8 14 20 14 38 15 20AC 14 78 13 90 14 70 14 20AC 13 C8 13 2C6 13 58 14 D8 13 78 12 A8 13 48 13 30 14 A8 13 A0 14 A8 13 20 14 2C6 13 E8 13 60 14 38 14 D8 13 E0 12 E8 12 E8 13 70 14 2C6 12 F8 12 50 12 28 12 50 11 2DC 11 58 12 A0 12 C8 11 68 10 F8 10 58 11 D8 12 48 14 20 16 40 16 40 18 D8 1A 68 1B E8 1E 06 20 20 20 18 20 20 20 3D 08 20 20 54 1D 20 20 2B 24 01 20 20 20 20 20 20 20 20 20 0A 20 20 20 08 20 20 20 C0 4C 20 51 26 20 20 20")

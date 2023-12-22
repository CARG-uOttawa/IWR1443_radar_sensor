import serial
import time
import numpy as np
from UARTParser import UartParser as up


if __name__ == "__main__":
    PROFILE_PATH = 'profile.cfg'

    userPort = serial.Serial('/dev/ttyACM0', 115200)  # User Port
    dataPort = serial.Serial('/dev/ttyACM1', 921600)

    try:
        print("Opening configuration file")
        with open(PROFILE_PATH, 'r') as file:
            lines = file.readlines()
        print("Configuration was opened successfully")

    except Exception as e:
        print("The Configuration File '" + PROFILE_PATH + "' was not found")

    else:
        print("Loading Configuration to board")
        for line in lines:
            time.sleep(0.001)
            userPort.write(line.encode('utf-8'))
            byteCount = userPort.inWaiting()
            s = userPort.read(byteCount)

        userPort.write(b'\n')  # We add this \n since the startSensor instruction in the .cfg file doesn't have one
        byteCount = userPort.inWaiting()
        s = userPort.read(byteCount)

        print("Configuration was loaded successfully")

        data = np.array([])
        try:
            print("Reading Data from board. Press Ctrl+C to exit and save data.")
            while True:
                byteCount = dataPort.inWaiting()
                s = np.frombuffer(dataPort.read(byteCount), dtype='uint8')
                if s.any():
                    data = np.concatenate((data, s), axis=0)

        except KeyboardInterrupt:
            print("\nData read successfully")

        except Exception:
            print("An error occurred while reading the Data")
        try:
            print("Processing Data")
            indices = up.searchMagicWord(data)
            objectData = []
            for index in range(indices.size-2):
                objectData.append(up.convertData(data[indices[index]:indices[index+1]]))
            print("Data was processed")

        except Exception:
            print("An error occurred while processing the Data")
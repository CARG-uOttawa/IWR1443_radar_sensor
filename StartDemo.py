#To get the list of com ports: python -m serial.tools.miniterm

import serial

PROFILE_PATH = 'profile.cfg'

userPort = serial.Serial('/dev/ttyACM0', 115200) # User Port
dataPort = serial.Serial('/dev/ttyACM1', 921600)


# userPort.write(b'%\n')
# msg = userPort.read(11) #This methods reads up to 11 characters which are the characters for "\nmmwDemo:/>"
# print(msg)

try:
    with open(PROFILE_PATH, 'r') as file:
        lines = file.readlines()

except Exception as e:
    print("The Configuration File '" + PROFILE_PATH + "' was not found")

else:
    for line in lines:
        userPort.write(line.encode('utf-8'))
        byteCount = userPort.inWaiting()
        s = userPort.read(byteCount)
        print(s)
    
    userPort.write(b'\n') # We add this \n since the startSensor instruction in the .cfg file doesn't have one 
    byteCount = userPort.inWaiting()
    s = userPort.read(byteCount)
    print(s)

    while True:
        byteCount = dataPort.inWaiting()
        s = dataPort.read(byteCount)
        print(s)


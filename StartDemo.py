import serial

userPort = serial.Serial('/dev/ttyACM0', 115200) # User Port

userPort.write(b'\n')
msg = userPort.read(11) #This methods reads up to 11 characters which are the characters for "\nmmwDemo:/>"
userPort.close()
print(msg)

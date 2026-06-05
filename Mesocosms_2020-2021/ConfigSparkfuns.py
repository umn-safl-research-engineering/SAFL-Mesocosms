import serial
import time

timeout = 1 #seconds
baudrate = 9600
LC = []
LC.append(serial.Serial('/dev/ttyUSB2',baudrate,timeout=timeout))
LC.append(serial.Serial('/dev/ttyUSB1',baudrate,timeout=timeout))
LC.append(serial.Serial('/dev/ttyUSB0',baudrate,timeout=timeout))
LC.append(serial.Serial('/dev/ttyUSB5',baudrate,timeout=timeout))
LC.append(serial.Serial('/dev/ttyUSB4',baudrate,timeout=timeout))
LC.append(serial.Serial('/dev/ttyUSB3',baudrate,timeout=timeout))
LC.append(serial.Serial('/dev/ttyUSB8',baudrate,timeout=timeout))
LC.append(serial.Serial('/dev/ttyUSB7',baudrate,timeout=timeout))
LC.append(serial.Serial('/dev/ttyUSB6',baudrate,timeout=timeout))
LC.append(serial.Serial('/dev/ttyUSB9',baudrate,timeout=timeout))

# Pause while the OpenScale board intializes the serial communications
time.sleep(5)

#Clear the serial buffer to clear out the initialization info that the OpenScale board spits out when it establishes comms. 
for i in LC: 
	i.reset_input_buffer()
	
	#Write commands to Devices:
	i.write(b'x') # Open Up the configuration interface
	time.sleep(1)
	i.write(b'c') # Select option to set the Serial Trigger Character
	i.write(b'?\r\n') # Set Trigger Character (must include a carriage return in this command)
	i.write(b't') # toggle the Serial Trigger setting

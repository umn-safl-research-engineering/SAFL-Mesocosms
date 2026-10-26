#!/usr/bin/python3

import serial
import time
import datetime
import os

#---------------------------------------------------
# Set up and open Serial Ports
LC = []
LC.append(serial.Serial('/dev/ttyUSB2',9600,timeout=0.5))
LC.append(serial.Serial('/dev/ttyUSB1',9600,timeout=0.5))
LC.append(serial.Serial('/dev/ttyUSB0',9600,timeout=0.5))
LC.append(serial.Serial('/dev/ttyUSB5',9600,timeout=0.5))
LC.append(serial.Serial('/dev/ttyUSB4',9600,timeout=0.5))
LC.append(serial.Serial('/dev/ttyUSB3',9600,timeout=0.5))
LC.append(serial.Serial('/dev/ttyUSB8',9600,timeout=0.5))
LC.append(serial.Serial('/dev/ttyUSB7',9600,timeout=0.5))
LC.append(serial.Serial('/dev/ttyUSB6',9600,timeout=0.5))
LC.append(serial.Serial('/dev/ttyUSB9',9600,timeout=0.5))

# Pause while the OpenScale board intializes the serial communications
time.sleep(5)

#Clear the serial buffer to clear out the initialization info that the OpenScale board spits out when it establishes comms. 
for i in LC: 
	i.reset_input_buffer()


time.sleep(1)


# Read the records from the serial string and write to an array. 
data_bytes = []
for i in LC:
	data_bytes.append(i.read_until(b'\r\n'))
print(data_bytes)
	
# Get the current Timestamp: 
ts = datetime.datetime.now()
timestamp = ts.strftime('%Y-%m-%d %H:%M:%S')
	
#Convert bytes to text string:
data_string = []
for i in data_bytes: 
	data_string.append(i.decode('utf-8'))
	
#Create Record to write to file
values = []
for i in data_string:
	values.append(i.split(','))

record = timestamp
for i in values:
	record=record+','+i[1]+','+i[3]+','+i[4]

record = record+'\r\n'
	
#print(record)

Header_Array = []
Header_Array.append(',Meso 1 Top Load,Meso 1 Top PCB Temp,Meso 1 Top Remote Temp')
Header_Array.append(',Meso 1 Bot Load,Meso 1 Bot PCB Temp,Meso 1 Bot Remote Temp')
Header_Array.append(',Meso 2 Top Load,Meso 2 Top PCB Temp,Meso 2 Top Remote Temp')
Header_Array.append(',Meso 2 Bot Load,Meso 2 Bot PCB Temp,Meso 2 Bot Remote Temp')
Header_Array.append(',Meso 3 Top Load,Meso 3 Top PCB Temp,Meso 3 Top Remote Temp')
Header_Array.append(',Meso 3 Bot Load,Meso 3 Bot PCB Temp,Meso 3 Bot Remote Temp')
Header_Array.append(',Meso 4 Top Load,Meso 4 Top PCB Temp,Meso 4 Top Remote Temp')
Header_Array.append(',Meso 4 Bot Load,Meso 4 Bot PCB Temp,Meso 4 Bot Remote Temp')
Header_Array.append(',Meso 5 Top Load,Meso 5 Top PCB Temp,Meso 5 Top Remote Temp')
Header_Array.append(',Meso 5 Bot Load,Meso 5 Bot PCB Temp,Meso 5 Bot Remote Temp')

filename = '/home/pi/Data/Mesocosms_LC_1-10_'+ts.strftime('%Y-%m-%d')+'.csv'

exists= os.path.isfile(filename)
if exists:
	fid = fid = open(filename,'a')
	fid.write(record)
	fid.close()
else:
	header = 'Timestamp'
	header_units = ''
	for i in range(len(values)):
		header=header+Header_Array[i]
		header_units = header_units+',kg,deg C,deg C'
	
	header = header+'\r\n'
	header_units = header_units+'\r\n'

	fid = open(filename,'w')
	fid.write(header)
	fid.write(header_units)
	fid.write(record)
	fid.close()

print('Successfully Completed')

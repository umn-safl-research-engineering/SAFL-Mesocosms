#!/usr/bin/python3
import serial
import time
import datetime
import os

def Setup_SerialPorts(): 
	#---------------------------------------------------
	# Set up and open Serial Ports
	timeout = 1 #seconds
	baudrate = 9600
	ports = ['/dev/ttyUSB2','/dev/ttyUSB1','/dev/ttyUSB0','/dev/ttyUSB5','/dev/ttyUSB4','/dev/ttyUSB3','/dev/ttyUSB8','/dev/ttyUSB7','/dev/ttyUSB6','/dev/ttyUSB9']
	LC = [0,0,0,0,0,0,0,0,0,0]
	
	for p in range(len(ports)): 
		try:
			LC[p]=(serial.Serial(ports[p],baudrate,timeout=timeout))
		except: 
			print('Unable to connect to port: '+ports[p])


	# Pause while the OpenScale board intializes the serial communications
	time.sleep(5)

	#Clear the serial buffer to clear out the initialization info that the OpenScale board spits out when it establishes comms. 
	for i in LC:
		try: 
			i.reset_input_buffer()
		except:
			pass
	return LC


	#time.sleep(1)
	
def Read_One_Sparkfun(LC,data_bytes,data_string,i):
	#print(i)
	LC[i].write(b'?')
	data_bytes.append(LC[i].read_until(b'\r\n'))
	data_string.append(data_bytes[i].decode('utf-8'))
	data = data_string[i].split(',')
	return data_bytes,data_string,data

def Read_Data(LC):
	# Get the current Timestamp: 
	ts = datetime.datetime.now()
	timestamp = ts.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
	
	# Read the records from the serial string and write to an array. 
	data_bytes = []
	data_string = []
	values = []
	for i in range(len(LC)):
		
		#print('Reading data from Device #: '+str(i))
		try:
			data_bytes,data_string,data = Read_One_Sparkfun(LC,data_bytes,data_string,i)
		except:
			print('Unable to retrieve data from one Sparkfun board')
			data = [0]
		
		if len(data) == 6: 
			values.append(data)			
		else:
			#values.append(['NAN','NAN','NAN','NAN','NAN','NAN'])
			print('Retrying '+str(i))
			try:
				data_bytes,data_string,data = Read_One_Sparkfun(LC,data_bytes,data_string,i)
			except:
				print('Unable to connect to Sparkfun board')
			print('After Retry, Number of fields returned: '+str(len(data)))
			print(data)
			if len(data) == 6:
				values.append(data)
			else:
				values.append(['NAN','NAN','NAN','NAN','NAN','NAN'])
	#print(data_bytes)
			
		
#	#Convert bytes to text string:
#	data_string = []
#	for i in data_bytes: 
#		data_string.append(i.decode('utf-8'))

	
#	values = []
#	ind = -1 # index for where we are in the data array in case there's an issue
	
#	for i in data_string:
#		ind = ind+1
#		data = i.split(',')
		#print(len(data))
		
#		retries = 0
#		if len(data) == 6: # Check for a complete response from each sparkfun board.  There should be 6 comma separated values returned.  If not, append an array of 'NAN' to the string.
#			values.append(data)
#		elif retries == 0:
#			print('retrying communication to '+str(ind))
#			retries = retries+1
#			data_string[ind] = LC[ind].read_until(b'\r\n').decode('utf-8')
#			
#		else: 
#			values.append(['NAN','NAN','NAN','NAN','NAN'])

	return values,timestamp,ts

def Write_Data(values,timestamp,ts,rec_num):		
	#Create Record to write to file
	

	record = timestamp+','+str(rec_num)
	for i in values:
		record=record+','+i[0]+','+i[1]+','+i[3]+','+i[4]

	record = record+'\r\n'
		
	#print(record)

	Header_Array = []
	Header_Array.append(',DeviceName,Meso 11 Top Load,Meso 11 Top PCB Temp,Meso 11 Top Remote Temp')
	Header_Array.append(',DeviceName,Meso 11 Bot Load,Meso 11 Bot PCB Temp,Meso 11 Bot Remote Temp')
	Header_Array.append(',DeviceName,Meso 12 Top Load,Meso 12 Top PCB Temp,Meso 12 Top Remote Temp')
	Header_Array.append(',DeviceName,Meso 12 Bot Load,Meso 12 Bot PCB Temp,Meso 12 Bot Remote Temp')
	Header_Array.append(',DeviceName,Meso 13 Top Load,Meso 13 Top PCB Temp,Meso 13 Top Remote Temp')
	Header_Array.append(',DeviceName,Meso 13 Bot Load,Meso 13 Bot PCB Temp,Meso 13 Bot Remote Temp')
	Header_Array.append(',DeviceName,Meso 14 Top Load,Meso 14 Top PCB Temp,Meso 14 Top Remote Temp')
	Header_Array.append(',DeviceName,Meso 14 Bot Load,Meso 14 Bot PCB Temp,Meso 14 Bot Remote Temp')
	Header_Array.append(',DeviceName,Meso 15 Top Load,Meso 15 Top PCB Temp,Meso 15 Top Remote Temp')
	Header_Array.append(',DeviceName,Meso 15 Bot Load,Meso 15 Bot PCB Temp,Meso 15 Bot Remote Temp')

	filename = '/home/pi/Data/Mesocosms_11-15_'+ts.strftime('%Y-%m-%d')+'.csv'
	#filename = '/home/cmilliren/GitHub/Mesocosms/Data/Mesocosms_LC_1-10_'+ts.strftime('%Y-%m-%d')+'.csv'

	exists= os.path.isfile(filename)
	if exists:
		fid = fid = open(filename,'a')
		fid.write(record)
		fid.close()
	else:
		header = 'Timestamp,RecordNumber'
		header_units = ','
		for i in range(len(values)):
			header=header+Header_Array[i]
			header_units = header_units+',,kg,deg C,deg C'
		
		header = header+'\r\n'
		header_units = header_units+'\r\n'

		fid = open(filename,'w')
		fid.write(header)
		fid.write(header_units)
		fid.write(record)
		fid.close()

	#print('Successfully Completed')

import Mesocosms_Toolbox
import datetime as dt


Data_Interval = 15 #seconds
last_run_time = dt.datetime.strptime('1999-01-01 00:00:00','%Y-%m-%d %H:%M:%S') # a start date to make sure it writes on the first time through 
start_time  = dt.datetime.now()
time_now    = dt.datetime.now()
rec_num = 0
#print(start_time.day)
LC = Mesocosms_Toolbox.Setup_SerialPorts()

while start_time.day == time_now.day: #Run for 1 day.  Crontab will restart it on the next day at Midnight 
	time_now  = dt.datetime.now()

	delta_t = time_now - last_run_time 

	#print(delta_t.total_seconds())

	if delta_t.total_seconds() >=Data_Interval:
		last_run_time = time_now
		rec_num = rec_num+1
		#print(delta_t.total_seconds())
		#print('Read Data and Write to File:')
		values,timestamp,ts = Mesocosms_Toolbox.Read_Data(LC)
		#print(data_string)
		Mesocosms_Toolbox.Write_Data(values,timestamp,ts,rec_num)
		

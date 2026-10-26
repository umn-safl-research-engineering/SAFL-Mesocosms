from influxdb import InfluxDBClient
import datetime
import pytz
from os import path
from os import listdir

conf_id = open('ingest.conf','r')
conf_id.readline() # SKip the headerline
conf_values = []
while True:
    txt_confs = conf_id.readline()
    # end of file is reached
    if not txt_confs:
        break
    txt_confs = txt_confs.replace('\n','')
    conf_values.append(txt_confs.split(','))

for c in range(len(conf_values)):
    filelocation = conf_values[c][1]#'C:/Users/milli079/Documents/GitHub/InfluxDB-Scripts/'
    filename = conf_values[c][0]#'Buoy_CedarBogLake_ProfileData.dat'
    column_name_line = int(conf_values[c][2])#2
    total_header_lines = int(conf_values[c][3])#4
    database = conf_values[c][4]#'CedarBogLake'
    table = conf_values[c][5]#'Profiles'
    timezone = conf_values[c][6]#'US/Central'

    ## List all files in filelocation directory that match the filename base
    directory_list = listdir(filelocation)
    file_list= []
    for f in directory_list:
        if f.find(filename[:-4])>=0 and (f.find('.dat')>=0 or f.find('.csv')>=0):
             file_list.append(f)
    #print(file_list)

    localtz = pytz.timezone(timezone)
    utctz = pytz.timezone('UTC')

    #client = InfluxDBClient(host='localhost', port=8086)
    client = InfluxDBClient(host='192.168.1.120', port=8086)
    client.create_database(database)


    for current_file in file_list:
        print('Reading File: '+current_file)
        fid = open(filelocation+current_file,'r')
        #fid = open('Test File','r')
        data_array = []
        try:
            ## First Time through the File, find the header names:\
            for i in range(column_name_line):
                header = fid.readline()
                #print(header)

            #remove any characters that aren't allowed from the string.
            header = header.replace('\n','')
            header = header.replace('\r\n','')
            header = header.replace('"','')
            header = header.replace(' ','_')

            #Split the string into a list of column names
            column_names = header.split(',')
            #print(column_names)

            # Skip the rest of the header lines:
            for i in range(total_header_lines-column_name_line):
                fid.readline()
            #Get all the data and put it into an array
            values = []
            timestamp = []

            # Skip to where we left off in the file before:
            query = "select Last_Read_Location from "+table+" where Ingested_Files= '"+current_file+"';"
            #print(query)
            result = client.query(query,database=database)
            #print(list(result.get_points()))
            if list(result.get_points()) == []:
                pass
            else:
                points = list(result.get_points())
                cursor = int(points[-1]['Last_Read_Location'])
                fid.seek(int(cursor),0)

            while True:
                txt = fid.readline()
                # end of file is reached
                if not txt:
                    break
                txt = txt.replace('\n','')
                values.append(txt.split(','))

            for j in range(len(values)):
                data = table+' '

                if len(values[j])==len(column_names): # Check that there are the same number of values in this row as in the header.  If not this line of data is corrupted and we should skip it.
                    for i in range(len(column_names)):

                        if column_names[i].lower().find('time') == 0:
                            ts_string = values[j][i].replace('"','')
                            ts = datetime.datetime.strptime(ts_string,'%Y-%m-%d %H:%M:%S')
                            ts = localtz.localize(ts)
                            ts_utc = ts.astimezone(utctz)
                            #print(ts)
                            timestamp.append(str(round(ts_utc.timestamp()*1000)))
                            row_ind = len(timestamp)-1
                            #print(ts)
                        else:
                            #print(values[j][i].find('NAN')>=0)
                            if values[j][i].find('NAN')>=0 or values[j][i].find('NULL')>=0 or  values[j][i].find('nan')>=0 or values[j][i].find('NaN')>=0 or values[j][i]=='' or values[j][i].isalpha():
                                pass#print('Value is NAN!')
                            else:
                                if i<len(column_names)-1:
                                    data = data+column_names[i]+'='+values[j][i]+','
                                else:
                                    data = data+column_names[i]+'='+values[j][i]+' '

                            # If there was a trailng comma due to a NAN value at the end of the data string, remove it and add the timestamp to the end of the string
                    if data[-1] == ',':
                        data = data[:-1]+' '+timestamp[row_ind]
                    else:
                        data = data+' '+timestamp[row_ind]

                    data_array.append(data)

        except:
            fid.close()
            raise

        client.write_points(data_array, database=database,time_precision='ms', batch_size=10000, protocol='line')
        print('\nWrite to InfluxDB complete!\n')

        ## Write the lastfile location to the InfluxDB database as well
        log_data = [table+' '+'Ingested_Files="'+current_file+'",'+'Last_Read_Location='+str(fid.tell())]
        client.write_points(log_data,database=database,time_precision='ms',batch_size=10000, protocol='line')

        fid.close()

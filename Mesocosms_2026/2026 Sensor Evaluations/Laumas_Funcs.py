import minimalmodbus
import json
import datetime
import pandas as pd 

timeout = 0.05 #seconds

class laumas():
    def __init__(self,comm_port,dev_id,perc_or_mV):
        try:
            self.comm = minimalmodbus.Instrument(comm_port,dev_id)
            self.comm.serial.baudrate = 9600  # Baud
            self.comm.serial.bytesize = 8
            self.comm.serial.parity = 'N'
            self.comm.serial.stopbits = 1
            self.comm.serial.timeout = timeout   # seconds
            self.comm.mode = minimalmodbus.MODE_RTU   # rtu or ascii mode
            self.status  = 'Com Port Found: '+comm_port

            self.sign_dict = {'0':1,'1':-1,0:1,1:-1}

            self.perc_or_mv = perc_or_mV

            if perc_or_mV == 0:
                # Send Command to enable mV reading per channel
                self.comm.write_register(registeraddress=5,value=6902)
            else:
                self.comm.write_registers(registeraddress=50,values=[0,0]) # 0=% of load related to the gross weight 1=% of load related to the total weight (gross weight+zeroing component)
                time.sleep(0.2)
                self.comm.write_register(registeraddress=5,value=6808)

        except Exception as e:
            print(e)

    def poll_SN(self):
        try: 
            self.SN = self.comm.read_registers(109,number_of_registers=8,functioncode=3)
            print(f"Registers: {self.SN}")
        except Exception as e:
            print('Error polling Device Serial Number')
            print(e)

    def scan_registers(self):
        valid_registers= {}

        for i in range(254):
            try:
                print(f"Attempting to read from Register: {i}")
                response = self.comm.read_register(registeraddress=i,number_of_decimals=0,functioncode=3)
                valid_registers[i]= response
                time.sleep(0.2)

            except minimalmodbus.IllegalRequestError:
                print(f'Illegal Request Error reading data from register: {i}')

        with open('Laumas_Valid_Registers.csv','w') as fid: 
            fid.write('Register Offset,Value\n')
            for row in valid_registers:
                fid.write(f"{row},{valid_registers[row]}\n")


        


    def send_99(self):
        try:
            self.comm.write_register(registeraddress=5,value=99)
        except Exception as e:
            print(e)

    def read_status_register(self):
        status_raw = self.comm.read_register(registeraddress=6,number_of_decimals=0,functioncode=3)
        self.status = f"{status_raw:016b}"
        self.load_cell_error = bool(int(self.status[0]))
        self.AD_converter_malfunction = bool(int(self.status[1]))
        self.maximum_weight_exceeded = bool(int(self.status[2]))
        self.gross_weight_sign = self.sign_dict[self.status[-8]]

    def read_gross_weight(self):
        self.read_status_register()
        time.sleep(0.01)
        try: 
            self.gross_weight = self.comm.read_register(registeraddress=8,number_of_decimals=3,functioncode=3,signed=False)*self.gross_weight_sign

        except Exception as e:
            print(f"Error reading Gross Weight: {e}")

    def read_load_percentages(self):
        self.load_percentages = self.comm.read_registers(registeraddress=52,number_of_registers=4,functioncode=3)
        for i,load in enumerate(self.load_percentages):
            self.load_percentages[i] = load/10

    def read_mVs(self):
        self.mVs = [0,0,0,0]
        for ind,reg in enumerate(range(52,56)):
            self.mVs[ind] = self.comm.read_register(registeraddress=reg,functioncode=3,signed=True)

        for i,ch in enumerate(self.mVs):
            self.mVs[i] = ch/100

    def read_mV_Test(self):
        self.ch1_mV = self.comm.read_registers(registeraddress=52,number_of_registers=2,functioncode=3)
        print(self.ch1_mV)

    def read_channels(self):
        if self.perc_or_mv == 0: # output mV
            self.read_mVs()

            # for i,mV in enumerate(self.mVs):
            #     Fs_ouput_mV = 2.9990*4.974 # calibrated mV/V multipied by the excitation voltage
            #     slope = 50/Fs_ouput_mV     # max output in lbs divded by the full scale mV
                
            #     self.loads[i] = mV*slope
            # # print(f"Minimum Resolution: {0.01*slope} lbs")


        else:
            self.read_load_percentages()

        # print('-------------')
        # print(f'Timestamp: {datetime.datetime.now()}')
        # for i in range(4):            
        #     if self.perc_or_mv == 0:
        #         print(f"Cell {i+1}: {self.mVs[i]} mV   =   {self.loads[i]:.2f}lbs ")
        #     else:
        #         print(f"% on Cell {i+1}: {self.load_percentages[i]}%")

        




if __name__ == "__main__":
    import time

    lc = laumas('COM3',1,0)

    # try:
    #     while True: 

    #         lc.read_mVs()
    #         print(lc.mVs)
    #         time.sleep(0.2)
    #         # print(lc.mVs)


    # except KeyboardInterrupt:
    #     print('Stopping')

    print('Remove all Buckets from Load Cells!.  Press Enter when ready')
    input('')

    filename = f'LoadCalibration_{datetime.datetime.now().strftime("%Y-%d-%m_%H%M%S")}.csv'
    

    with open(filename,'w') as fid:
        fid.write(f"Timestamp,Bucket1,Bucket2,Bucket3,Ch1,Ch2,Ch3,Ch4,Vx,Ch1,Ch2,Ch3,Ch4,Gross Weight\n")
        fid.write(f",lbs,lbs,lbs,mV,mV,mV,mV,V,%,%,%,%,lbs\n")

    try:
        while True:
            bucket_1 = input('Enter Weight of Bucket 1: ')
            bucket_2 = input('Enter Weight of Bucket 2: ')
            bucket_3 = input('Enter Weight of Bucket 3: ')

            data_string = f"{datetime.datetime.now().strftime('%Y-%d-%m %H:%M:%S')},{bucket_1},{bucket_2},{bucket_3}"

            input('Press Enter when Buckets are hung and stable.')

            lc.read_mVs()

            for i in lc.mVs:
                data_string = data_string+f",{i}"

            Vx = input('Enter the Excitation Voltage: ')

            data_string = data_string+f",{Vx}"

            # Switch to displaying each channel in Percent
            lc.comm.write_registers(registeraddress=50,values=[0,0]) # 0=% of load related to the gross weight 1=% of load related to the total weight (gross weight+zeroing component)
            time.sleep(0.2)
            lc.comm.write_register(registeraddress=5,value=6808)

            lc.read_load_percentages()

            for i in lc.load_percentages:
                data_string=data_string+f",{i}"

            # Switch back to reading each channel in mV
            lc.comm.write_register(registeraddress=5,value=6902)

            lc.read_gross_weight()

            data_string = data_string+f",{lc.gross_weight}\n"

            with open(filename,'a') as fid:
                fid.write(data_string)

            print('\n\nAdd Weight to the Buckets\n')

    except KeyboardInterrupt:
        print('Ending')



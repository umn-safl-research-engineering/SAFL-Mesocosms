import minimalmodbus
import json
import datetime

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
            self.SN = self.comm.read_register(1,number_of_decimals=0,functioncode=3)
        except Exception as e:
            print('Error polling Device Serial Number')
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
        self.mVs = self.comm.read_registers(registeraddress=52,number_of_registers=4,functioncode=3)

    def read_channels(self):
        if self.perc_or_mv == 0: # output mV
            self.read_mVs()

            for i,mV in enumerate(self.mVs):
                Fs_ouput_mV = 2.9990*4.974 # calibrated mV/V multipied by the excitation voltage
                slope = 50/Fs_ouput_mV     # max output in lbs divded by the full scale mV
                
                self.loads[i] = mV*slope
            # print(f"Minimum Resolution: {0.01*slope} lbs")

        else:
            self.read_load_percentages()

        print('-------------')
        print(f'Timestamp: {datetime.datetime.now()}')
        for i in range(4):            
            if self.perc_or_mv == 0:
                print(f"Cell {i+1}: {self.mVs[i]} mV   =   {self.loads[i]:.2f}lbs ")
            else:
                print(f"% on Cell {i+1}: {self.load_percentages[i]}%")


if __name__ == "__main__":
    import time

    lc = laumas('COM3',1,1)

    try:
        while True:
            lc.read_channels()

            # if lc.perc_or_mv == 0:
            #     print(lc.loads)


            # lc.read_gross_weight()
            # print(f'Gross Weight: {lc.gross_weight}')


            time.sleep(0.2)


    except KeyboardInterrupt:
        print('Stopping')
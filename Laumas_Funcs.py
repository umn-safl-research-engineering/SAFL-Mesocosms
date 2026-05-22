import minimalmodbus
import json

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

            self.sign_dict = {'0':-1,'1':1}

            self.perc_or_mv = perc_or_mV

            if perc_or_mV == 0:
                # Send Command to enable mV reading per channel
                self.comm.write_register(registeraddress=5,value=6902)
            else:
                self.comm.write_register(registeraddress=51,value=0) # 0=% of load related to the gross weight 1=% of load related to the total weight (gross weight+zeroing component)
                self.comm.write_register(registeraddress=5,value=6908)

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
        self.gross_weight_sign = self.sign_dict[self.status[6]]

    def read_gross_weight(self):
        self.read_status_register()
        try: 
            bytes = self.comm.read_registers(registeraddress=7,number_of_registers=2,functioncode=3)
            byte1 = self.comm.read_register(registeraddress=7,number_of_decimals=0,functioncode=3,signed=True)
            byte2 = self.comm.read_register(registeraddress=8,number_of_decimals=0,functioncode=3,signed=True)
            print([byte1,byte2])
            # print(int(bytes[1])/1000)
            gross_weight_string = f"{bytes[0]}.{bytes[1]}"
            self.gross_weight = self.gross_weight_sign*float(gross_weight_string)
        except Exception as e:
            print(f"Error reading Gross Weight: {e}")

    def read_load_percentages(self):
        self.load_percentages = [0,0,0,0]
        self.load_percentages[0] = self.comm.read_register(registeraddress=52,number_of_decimals=1,functioncode=3)
        self.load_percentages[1] = self.comm.read_register(registeraddress=53,number_of_decimals=1,functioncode=3)
        self.load_percentages[2] = self.comm.read_register(registeraddress=54,number_of_decimals=1,functioncode=3)
        self.load_percentages[3] = self.comm.read_register(registeraddress=55,number_of_decimals=1,functioncode=3)

    def read_mVs(self):
        self.mVs = [0,0,0,0]
        self.mVs[0] = self.comm.read_register(registeraddress=52,number_of_decimals=2,functioncode=3,signed=True)
        self.mVs[1] = self.comm.read_register(registeraddress=53,number_of_decimals=2,functioncode=3,signed=True)
        self.mVs[2] = self.comm.read_register(registeraddress=54,number_of_decimals=2,functioncode=3,signed=True)
        self.mVs[3] = self.comm.read_register(registeraddress=55,number_of_decimals=2,functioncode=3,signed=True)

        for i in range(4):
            print(f"mVs on Cell {i+1}: {self.mVs[i]}")

    def read_channels(self):
        self.channels = [0,0,0,0]
        if self.perc_or_mv == 0:
            self.channels[0] = self.comm.read_register(registeraddress=52,number_of_decimals=2,functioncode=3,signed=True)
            self.channels[1] = self.comm.read_register(registeraddress=53,number_of_decimals=2,functioncode=3,signed=True)
            self.channels[2] = self.comm.read_register(registeraddress=54,number_of_decimals=2,functioncode=3,signed=True)
            self.channels[3] = self.comm.read_register(registeraddress=55,number_of_decimals=2,functioncode=3,signed=True)

        else:
            self.channels[0] = self.comm.read_register(registeraddress=52,number_of_decimals=1,functioncode=3,signed=True)
            self.channels[1] = self.comm.read_register(registeraddress=53,number_of_decimals=1,functioncode=3,signed=True)
            self.channels[2] = self.comm.read_register(registeraddress=54,number_of_decimals=1,functioncode=3,signed=True)
            self.channels[3] = self.comm.read_register(registeraddress=55,number_of_decimals=1,functioncode=3,signed=True)
        
        print('-------------')
        for i in range(4):            
            if self.perc_or_mv == 0:
                print(f"mVs on Cell {i+1}: {self.channels[i]} mV")
            else:
                print(f"% on Cell {i+1}: {self.channels[i]}%")


if __name__ == "__main__":
    import time

    lc = laumas('COM3',1,1)

    try:
        while True:
            lc.read_channels()
            time.sleep(1)

    except KeyboardInterrupt:
        print('Stopping')
# Mesocosms
Python Code for Reading loadcells and temperature probes on Mesocosms.

Reads 60 load cells and 60 temperature probes over a serial connection to SparkFun Openscale boards.

## Username and Passwords
All 6 raspberry pi computers are set up with the same username and password: 

Username: `pi`\
Password: `biofilt`

## Networks

### Local Wifi ("Biofilt Mesocosms Local")
Prior to summer 2022 the Raspberry Pi's were connected with a Local only WiFi network.  This allowed them to share a common clock and users could connect to each device with a laptop in the vicinity by connecting to the same local Wifi Network.  The following table shows the IP addresses for the local network. 
|  RPi #        |  IP Address  |
|---------------|--------------|
| 1             |192.168.1.101 |
| 2             |192.168.1.102 |
| 3             |192.168.1.103 |
| 4             |192.168.1.104 |
| 5             |192.168.1.105 |
| 6             |192.168.1.106 |

### SAFL Research Network (wired ethernet)
In the summer of 2022 ethernet was brought over to the mesocosms from the ethernet drops that were placed in the OSL for the WAP that was installed in 2021.  This allowed the Raspberry Pis to be directly connected into SAFL's research network and therefore accessed by anyone connected over the SAFL-002 VPN.  The table below shows the Raspberry pi numbers, MAC IDs (needed to register the devices on the network) and their IP addresses on the SAFL research network.

|  RPi #    |  MAC ID           |  IP Address   |
|-----------|-------------------|---------------|
| 1         | b8:27:eb:0e:0e:15 | 192.168.4.191 |
| 2         | b8:27:eb:6e:86:97 | 192.168.4.136 |
| 3         | b8:27:eb:f1:09:91 | 192.168.4.138 |
| 4         | b8:27:eb:78:1f:17 | 192.168.4.193 |
| 5         | b8:27:eb:5c:2c:29 | 192.168.4.192 |
| 6         | b8:27:eb:a5:26:c2 | 192.168.4.135 |


## Note on Arduino Serial Connections
January 4, 2021 - Every time you connect to an Arduino (the SparkFun OpenScale board uses an Arduino Microcontroller as its 'Brain') over serial, it does a soft reset to the arduino.  This is why I got the header every time I connected and had to wait 5 seconds in my python program before I could read the actual data.  This can be avoided by disabling the DTR in pySerial BEFORE you open the serial connection.  The DTR is what tells the Arduino to reset or not when the connection is established.  By default, DTR is enable in a serial connection so you have to manually disable this before you open the comm port in python.  

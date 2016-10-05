'''
Created on Sep 20, 2016

@author: Alphacore Engineer 1
'''
from ok.ok import PLL22150
import sys
import time
import timeit

"""
NOTE (for later, or others):
To install the 'ok' package for you python environment to use, you must download
the FrontPanel.exe package provided by Lav/Kush/Max (I can't find on the website
where the download button is, I think it comes with a purchased device). 

Then, find the API folder, find the python folder, and find you python version.
Within that folder, there will be 4 files which you will copy into the site-pacakges
folder within your python.exe folder. Ex: C:\Anaconda3\Lib\site-packages
(Anaconda is a my version of a python package). 

Then make a folder called "ok" within the site-packages folder and paste the 4 
files from the FrontPanel folder. Then run the __init__.py file using your 
python.exe program and it should be available for you to use now.
"""

import ok
"""
http://assets00.opalkelly.com/library/FrontPanel-UM.pdf
page 34
(Max's computer)
API reference 
C:\Program Files\Opal Kelly\FrontPanelUSB\Documentation
FrontPanelAPI.chm
"""

"""
Look into:
address = 0xA0
read_size = 1024
dev.ReadFromPipeOut(address, read_size, buf)
"""

"""
Endpoint Type | Address Range | Sync/Async   | Data Type
-------------------------------------------------------------------
Wire In       | 0x00 - 0x1F   | Asynchronous | Signal state
Wire Out      | 0x20 - 0x3F   | Asynchronous | Signal state
Pipe In       | 0x80 - 0x9F   | Synchronous  | Multi-byte transfer
Pipe Out      | 0xA0 - 0xBF   | Synchronous  | Multi-byte transfer

ENDPOINT DATAWIDTH
Endpoint Type | USB 2.0
Pipe          | 16bit
"""

from MessageTexts import *
from tkinter import Tk
from tkinter import filedialog as FD
from Utils import MBox, Conversions
import sys
import math

ADC_DATA_ADDR = 0xA0
FIFO_DATA_COUNT_ADDR = 0xA1
FIFO_EMPTY_ADDR = 0x20 # bit [0]
DEBUG_ADDR = 0x20 # bit [1]
RESET_ADDR = 0x00 # bit [0]

class FPGA_Communication(ok.okCFrontPanel, ok.okCPLL22393):
    """
    Class: FPGA_Communication
    Inherit: ok.okCFrontPanel and ok.okCPLL22393
    Inheritance was chosen over composition for two reasons.
    1) You can reference the super classes from this class directly
    2) Learning experience (if comp is necessary, I will change this class)
    """
    
    def __init__(self):
        super().__init__()
        self.MB = MBox()
        self.hasBeenConfigured = False
        self.CV = Conversions()
        
        if (self.NoError != self.OpenBySerial("")):
            self.MB.showerror('Connection error', connect_to_device_error_text)
            del self
            return None
    
    def testConnection(self):
        if (self.NoError != self.OpenBySerial("")):
            self.MB.showerror('Connection error', connect_to_device_error_text)
            return False
        else:
            self.MB.showerror('Connection Success', connect_to_device_success_text)
            return True
    
    def readPipe(self, epAddr=0xA0, bufSize=1):
        # bytearray assumes 8 bit byte
        # pipeout byte is 16 bits
        bufSize = 2*bufSize
        buf = bytearray(bufSize)
        self.ReadFromPipeOut(epAddr, buf)
        return buf
    
    def readWire(self, epAddr=0x20, binary=False, bits=None):
        self.UpdateWireOuts()
        wireVal = self.GetWireOutValue(epAddr)
        if binary == False:
            return wireVal
        else:
            wireVal = format(wireVal, 'b')
            if bits == None:
                return wireVal
            else:
                l = len(wireVal)-1
                bitVal = [wireVal[l-x] for x in bits]
                bitVal = ''.join(bitVal)
                return bitVal
                
    
    def writeWire(self, epAddr=0x00, val=0x00, mask=None):
        if mask == None:
            self.SetWireInValue(epAddr, val)
        else:
            self.SetWireInValue(epAddr, val, mask)
        self.UpdateWireIns()
    
    def manualReset(self, epAddr=RESET_ADDR, mask=0x01):
        self.SetWireInValue(epAddr, 0xff, mask)
        self.UpdateWireIns()
        self.SetWireInValue(epAddr, 0x00, mask)
        self.UpdateWireIns()
    
    def configureFPGA(self, fileName=None, fromFlash=False):
        if not fromFlash:
            
            if fileName == None:
                try:
                    file_opt = options = {}
                    options['defaultextension'] = '.bit'
                    options['filetypes'] = [('Bit file', '.bit'), ('all files', '.*')]
                    options['initialdir'] = 'C:\\'
                    options['initialfile'] = 'ADC_Testing.bit'
                    options['title'] = 'Open FPGA .bit file.'
                    fileName = FD.askopenfilename(mode='r', **file_opt)
                except:
                    self.MB.showerror('File Error', data_file_error_text)
                    
                self.ConfigureFPGA(fileName)
                self.hasBeenConfigured = True
            else:
                self.ConfigureFPGA(fileName)
                self.hasBeenConfigured = True
                
        else:
            # configure FPGA from flash here
            pass

    def openDataFileNameWrite(self, extension='.txt'):
        file_opt = options = {}
        options['defaultextension'] = '{}'.format(extension)
        options['filetypes'] = [('{} File'.format(extension), '{}'.format(extension)), ('all files', '.*')]
        options['initialdir'] = 'C:\\'
        options['initialfile'] = 'ADC_results{}'.format(extension)
        options['title'] = 'Open FPGA {} file.'.format(extension)
        root = Tk()
        root.withdraw()
        return FD.askopenfilename(**file_opt)
    
    def testADC(self, fileName=None, samples=2048, bufSize=1, timeout=1, slowStart=True):
        
        """
        samples=number values read from FPGA fifo
        timeout(ms)=time to wait for fifo to be not empty (in milliseconds)
        slowStart=boolean whether or not timeout should be applied immediate. Keep
                  True if external source is not on before this code is ran. 
        """
        if not self.hasBeenConfigured:
            self.configureFPGA(fileName)
        
        try:
            data_file = open(self.openDataFileNameWrite(), 'w')
        except FileNotFoundError:
            self.MB.showerror('File Error', data_file_error_text)
            sys.exit()
            
        for i in range(math.ceil(samples/bufSize)):
            # Take 'samples' samples
            
            
            if bufSize <= 1:
                timeout_senti = '1' == self.readWire(FIFO_EMPTY_ADDR, binary=True, bits=[1])
                """
                0x20<0> == fifo_empty signal
                Wait until the fifo is no longer empty
                """
            else:
                fifo_data_count = self.CV.ba2ia(self.readPipe(epAddr=FIFO_DATA_COUNT_ADDR))[0]
                timeout_senti = fifo_data_count < bufSize
                """
                0xA1 == fifo_data_count signal
                Wait until the fifo has enough data in it
                """
                
            timestart = time.time()
            while (timeout_senti):
                
                if slowStart == False:
                    if ((time.time() - timestart)*1000 >= timeout):
                        self.MB.showerror('Timeout', test_adc_timeout_error_text)
                        data_file.write(test_adc_timeout_error_text)
                        data_file.close()
                        sys.exit()
                
                if bufSize <= 1:
                    timeout_senti = '1' == self.readWire(FIFO_EMPTY_ADDR, binary=True, bits=[1])
                else:
                    fifo_data_count = self.CV.ba2ia(self.readPipe(epAddr=FIFO_DATA_COUNT_ADDR, bufSize=bufSize))[0]
                    print("fifo_data_count: {}".format(str(fifo_data_count)))
                    timeout_senti = fifo_data_count < bufSize
                    
            slowStart = False            
            
            data = self.CV.ba2ia(self.readPipe(epAddr = ADC_DATA_ADDR, bufSize=bufSize))
            print("data: {}".format(data))
            for d in data:
                data_file.write(str(d) +'\n')
            
        data_file.close()
        self.MB.showinfo('Write complete', results_written_complete_text)
            
            
    def __repr__(self):
        self.devInfo = ok.okTDeviceInfo()
        if (self.NoError != self.GetDeviceInfo(self.devInfo)):
            self.MB.showerror('No Device Info', retrieve_device_info_error_text)
            return 'No Device Info'
        else:
            return FPGA_Communication_repr_text.format(self.GetDeviceMajorVersion(), 
                       self.GetDeviceMinorVersion(),
                       self.GetSerialNumber(),
                       self.GetDeviceID(),
                       self.GetBoardModel(), 
                       self.IsFrontPanelEnabled())

def initFPGA():
    fileName = "adc_testing_top.bit"
    xem = FPGA_Communication()
    if xem == None:
        print("no connect")
        return None
    else:
        xem.configureFPGA(fileName)
        print(xem)
        return xem



xem = initFPGA()
xem.manualReset()

xem.testADC(samples=512, bufSize=2, timeout=1000)

#while(1):
#    print("debugOut: {}".format(xem.readWire(DEBUG_ADDR, True, [1])))


#ADC_CLOCK_COUNT_ADDR = 0xA2
#while(1):
#    print("adc_clock_count: {}".format(xem.readPipe(ADC_CLOCK_COUNT_ADDR)))

    



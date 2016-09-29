'''
Created on Sep 20, 2016

@author: Alphacore Engineer 1
'''
from ok.ok import PLL22150
import sys
import time

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
from Utils import MBox

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
    
    def readPipe(self, epAddr=0xA0, bufSize=128):
        buf = bytearray(bufSize)
        self.ReadFromPipeOut(epAddr, buf)
        return buf
    
    def readWire(self, epAddr=0x20):
        self.UpdateWireOuts()
        return self.GetWireOutValue(epAddr)
    
    def writeWire(self, epAddr=0x00, val=0x00, mask=None):
        if mask == None:
            self.SetWireInValue(epAddr, val)
        else:
            self.SetWireInValue(epAddr, val, mask)
        self.UpdateWireIns()
    
    def manualReset(self, epAddr=0x00, mask=0x01):
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
            else:
                self.ConfigureFPGA(fileName)
                
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
    
    def testADC(self, fileName, samples=2048, timeout=1, slowStart=True):
        """
        samples=number values read from FPGA fifo
        timeout(ms)=time to wait for fifo to be not empty (in milliseconds)
        slowStart=boolean whether or not timeout should be applied immediate. Keep
                  True if external source is not on before this code is ran. 
        """
        self.configureFPGA(fileName)
        timestart = 0
        data_file = open(self.openDataFileNameWrite())
        for i in range(samples):
            # Take 'samples' samples
            while (self.readWire(0x20)):
                """
                0x20<0> == fifo_empty signal
                Wait until the fifo is no longer empty
                """
                if slowStart == False:
                    if ((time.time() - timestart)*1000 >= timeout):
                        self.MB.showerror('Timeout', test_adc_timeout_error_text)
                        break
                    else:
                        timestart = time.time()
                else:
                    continue
                
            slowStart = False
            
            data_file.write(self.readPipe(bufSize=10))
            
            
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


xem = FPGA_Communication()
if xem == None:
    print("no connect")
    sys.exit()
else:
    """
    fileName = "adc_testing_top.bit"
    xem.testADC(fileName)
    """
    print(xem.readWire())



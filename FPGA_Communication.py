'''
Created on Sep 20, 2016

@author: Alphacore Engineer 1
'''
from ok.ok import PLL22150


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

dev = ok.okCFrontPanel()
pll = ok.okCPLL22393() # On Opal Kelly board

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





class FPGA_Communication(object):
    def __init__(self, dev, pll):
        self.dev = dev
        self.pll = pll
        
    def readADC(self, epAddr=0xA0, length=1):
        data = -1
        self.dev.ReadFromPipeOut(epAddr, length, data)
        return data

        











'''
Created on Sep 20, 2016

@author: Max Ruiz
'''


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

import ok
import time
from MessageTexts import *
from Utils import MBox, FDialog, Conversions
import sys
import math
from ep_address import *


class FPGA_Communication(ok.okCFrontPanel, ok.okCPLL22393):
    """
    Class: FPGA_Communication
    Inherit: ok.okCFrontPanel,ok.okCPLL22393
    Composition: Conversions
    Inheritance was chosen over composition for two reasons.
    1) You can reference the super classes from this class directly
    2) Learning experience (if comp is necessary, I will change this class)
    Description:
        Use this class to communicate with the Opal Kelly (OK) board as if you were using
        the inherited classes. There are macro methods in this class, such as
        writeWire, readWire, and readPipe that perform extra tasks before they
        communication to the OK board; with this in mind, use this classes version
        of those methods. For methods such as controlling the PLL on the OK board,
        you can use this class to invoke the methods from the OK API for the PLL.
    """

    def __init__(self):
        super().__init__() # inherit and initialize the parent classes using the method super()
        self.MB = MBox() # Message box for popup warnings or information
        self.FD = FDialog()
        self.hasBeenConfigured = False

        # Using composition, create an instance of Conversions() for the later
        # purpose of converting bytearrays (the return data type of readPipe)
        # into a list of integers.
        self.CV = Conversions()

        # Check for a connection to the OK board. If there is a connection: continue,
        # if there is NO connection, delete the reference to this class and return
        # 'None' type as the instance of this class.
        if (self.NoError != self.OpenBySerial("")):
            self.MB.showerror('Connection error', connect_to_device_error_text)
            del self
            return None

    def testConnection(self):
        """
        Method: testConnection
        Params:
        Returns: boolean
        Description: Option for re-testing the connection to the OK board.
        """
        if (self.NoError != self.OpenBySerial("")):
            self.MB.showerror('Connection error', connect_to_device_error_text)
            return False
        else:
            self.MB.showerror('Connection Success', connect_to_device_success_text)
            return True

    def readPipe(self, epAddr=0xA0, bufSize=1):
        """
        Method: readPipe
        Params: int epAddr=0xA0: pipe address
            int bufSize=1: consecutive reads from pipe link
        Returns: (bytearray)buf
        Descriptions: Sets up a bytearray and corrects the bufSize to accomodate
            the difference in the 8-bit python bufSize, and the 16-bit pipe bufSize.
        """
        # bytearray assumes 8 bit byte
        # pipeout byte is 16 bits
        bufSize = 2*bufSize
        buf = bytearray(bufSize)
        self.ReadFromPipeOut(epAddr, buf)
        return buf

    def readWire(self, epAddr=0x20, binary=False, bits=None):
        """
        Method: readWire
        Params: int epAddr=0x20: address of wire
            bool binary=False: determine return representation of wire
            list bits=None: list of bits in wire to return eg. [b] or [m:n]
        Returns: if(binary==False): int
                 elif (binary==True and bits==None): str
                 elif (binary==True and bits==[b]): str
                 elif (binary==True and bits==[m:n]): str
        Description: Depending on the return method/type you are looking for
            this method will return:
            +full 16-bit wire if called generally or binary=False;
            +full 16-bit wire in binary format (as a str) if binary=True;
            +a single bit str if you specify only one bit of the 16-bit wire;
            +a str of bits specified by a list of bit indices in the 16-bit wire;
        """
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
        """
        Method: writeWire
        Params: int epAddr=0x00: address of wire
            int val=0x00: value to write to wire
            int mask=None: position in wire to write val to
        Returns:
        Description: Write a value, val, to the addr, epAddr, on the OK board.
            The position of that value can be set by using a mask.
            Example: change the values of bit-0 and bit-2 (of the wire/reg on the OK board)
            to 1's. val=1, mask=0x05
        """
        if mask == None:
            self.SetWireInValue(epAddr, val)
        else:
            self.SetWireInValue(epAddr, val, mask)
        self.UpdateWireIns()

    def manualReset(self, epAddr=RESET_ADDR, mask=0x01):
        """
        Method: manualReset
        Params: int epAddr=RESET_ADDR: address of wire with the reset bit in it
            int mask=0x01: position of the reset bit in the wire
        Returns:
        Description: Manually toggle on-off the bit placed as reset on the OK board.
        """
        self.SetWireInValue(epAddr, 0xff, mask)
        self.UpdateWireIns()
        self.SetWireInValue(epAddr, 0x00, mask)
        self.UpdateWireIns()

    def configureFPGA(self, fileName=None, fromFlash=False):
        """
        Method: configureFPGA
        Params: str fileName=None: file name of .bit file to configure FPGA with
            bool fromFlash=False: determine if configuring from file or onboard
                flash
        Returns:
        Description: configure the FPGA based on the .bit file, with name fileName,
        of from flash (does not work for flash programming right now). If no fileName
        is provided, the user will be prompted for the file path.
        """
        if not fromFlash:

            if fileName == None:
                try:
                    file_opt = options = {}
                    options['defaultextension'] = '.bit'
                    options['filetypes'] = [('Bit file', '.bit'), ('all files', '.*')]
                    options['initialdir'] = 'C:\\'
                    options['initialfile'] = 'ADC_Testing.bit'
                    options['title'] = 'Open FPGA .bit file.'
                    fileName = self.FD.openDataFileNameWrite(file_opt=file_opt)
                except:
                    self.MB.showerror('File Error', data_file_error_text)
                    self.hasBeenConfigured = False

                self.ConfigureFPGA(fileName)
                self.hasBeenConfigured = True
            else:
                self.ConfigureFPGA(fileName)
                self.hasBeenConfigured = True

        else:
            # configure FPGA from flash here
            pass

    def getConfigStatus(self):
        return self.hasBeenConfigured

    def getDeviceInfo(self, infoPopUp=False):
        """
        Method: getDeviceInfo
        Params: bool infoPopUp=False: display pop version of device info
            as opposed to returning it.
        Returns: if (infoPopUp==False): str
        Description: returns OK board device info or creates a popup
        """
        self.devInfo = ok.okTDeviceInfo()
        if (self.NoError != self.GetDeviceInfo(self.devInfo)):
            self.MB.showerror('No Device Info', retrieve_device_info_error_text)
            return 'No Device Info'
        else:
            deviceInfo = FPGA_Communication_repr_text.format(self.GetDeviceMajorVersion(),
                           self.GetDeviceMinorVersion(),
                           self.GetSerialNumber(),
                           self.GetDeviceID(),
                           self.GetBoardModel(),
                           self.IsFrontPanelEnabled())
            if not infoPopUp:
                return deviceInfo
            else:
                self.MB.showinfo('Device Info', deviceInfo)


    def __repr__(self):
        """
        Method: __repr__
        Params:
        Returns:
        Description: returns OK board device info and class info
        """
        print(self.getDeviceInfo())
        return """
        Class: FPGA_Communication
        Inherit: ok.okCFrontPanel,ok.okCPLL22393
        Composition: Conversions
        Inheritance was chosen over composition for two reasons.
        1) You can reference the super classes from this class directly
        2) Learning experience (if comp is necessary, I will change this class)
        Description:
            Use this class to communicate with the Opal Kelly (OK) board as if you were using
            the inherited classes. There are macro methods in this class, such as
            writeWire, readWire, and readPipe that perform extra tasks before they
            communication to the OK board; with this in mind, use this classes version
            of those methods. For methods such as controlling the PLL on the OK board,
            you can use this class to invoke the methods from the OK API for the PLL.
        """



def initFPGA(fileName=None, autoConfig=True):
    """
    Function: initFPGA
    Params: str fileName=None: file name used for configuring the FGPA if not already done
        bool autoConfig=True: should initFPGA configure the FPGA, or leave the programmer
            to do that later?
    Returns: FPGA_Communication() instance
    Description: create instance of FPGA_Communication() and check
        if it was created successfully or not.
    """
    fileName = "adc_testing_top.bit"
    xem = FPGA_Communication()
    MB = MBox()
    if xem == None:
        MB.showerror('No Connect', connect_to_device_error_text)
        sys.exit()
    else:
        if autoConfig:
            xem.configureFPGA(fileName)
        print(xem)
        return xem


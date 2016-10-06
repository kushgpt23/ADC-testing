'''
Created on Oct 6, 2016

@author: Max Ruiz
'''

from FPGA_Communication import FPGA_Communication
from MessageTexts import *
from Utils import MBox, FDialog, Conversions
import sys
import time
import math
from ep_address import *

def initFPGA(fileName=None):
    """
    Function: initFPGA
    Params: str fileName=None: file name used for configuring the FGPA if not already done
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
        xem.configureFPGA(fileName)
        print(xem)
        return xem

def testADC(fileName=None, samples=2048, bufSize=1, timeout=1, slowStart=True):
    """
    Function: testADC
    Params:
        str fileName=None: file name used for configuring the FGPA if not already done
        int samples=2048: number values read from FPGA fifo
        int bufSize=1: How many consecutive reads from the FIFO occur
        int timeout=1: time(ms) to wait for fifo to be not empty (in milliseconds)
        bool slowStart=True: boolean whether or not timeout should be applied immediate.
            Keep True if external source is not on before this code is ran.
    Returns:
    Description: Read data back from OK boards FIFO. Write that data to a file.
    """
    xem = initFPGA(fileName)
    MB = MBox()
    FD = FDialog()
    CV = Conversions()

    if not xem.hasBeenConfigured:
        sys.exit()

    try:
        results_file = open(FD.openDataFileName(), 'w')
    except FileNotFoundError:
        MB.showerror('File Error', data_file_error_text)
        sys.exit()

    for i in range(math.ceil(samples/bufSize)):

        if bufSize <= 1:
            timeout_senti = '1' == xem.readWire(FIFO_EMPTY_ADDR, binary=True, bits=[1])
            """
            0x20<0> == fifo_empty signal
            Wait until the fifo is no longer empty
            """
        else:
            fifo_data_count = CV.ba2ia(xem.readPipe(epAddr=FIFO_DATA_COUNT_ADDR))[0]
            timeout_senti = fifo_data_count < bufSize
            """
            0xA1 == fifo_data_count signal
            Wait until the fifo has enough data in it
            """

        timestart = time.time()
        while (timeout_senti):

            if slowStart == False:
                if ((time.time() - timestart)*1000 >= timeout):
                    MB.showerror('Timeout', test_adc_timeout_error_text)
                    results_file.write(test_adc_timeout_error_text)
                    results_file.close()
                    sys.exit()

            if bufSize <= 1:
                timeout_senti = '1' == xem.readWire(FIFO_EMPTY_ADDR, binary=True, bits=[1])
            else:
                fifo_data_count = CV.ba2ia(xem.readPipe(epAddr=FIFO_DATA_COUNT_ADDR, bufSize=bufSize))[0]
                print("fifo_data_count: {}".format(str(fifo_data_count)))
                timeout_senti = fifo_data_count < bufSize

        slowStart = False

        data = CV.ba2ia(xem.readPipe(epAddr = ADC_DATA_ADDR, bufSize=bufSize))
        print("data: {}".format(data))
        for d in data:
            results_file.write(str(d) +'\n')

    results_file.close()
    MB.showinfo('Write complete', results_written_complete_text)










'''
Created on Sep 16, 2016

@author: Alphacore Engineer 1
'''
from math import log10, pi
from tkinter import filedialog as FD
from tkinter import messagebox as MB
from tkinter import Tk
from MessageTexts import *

class MBox:

    @staticmethod
    def showerror(title, message):
        root = Tk()
        root.withdraw()
        MB.showerror(title, message)

    @staticmethod
    def showinfo(title, message):
        root = Tk()
        root.withdraw()
        MB.showinfo(title, message)

class FDialog:

    @staticmethod
    def openDataFileName(extension='.txt', file_opt=None):
        """
        Method: openDataFileName
        Params: str extension='.txt': default file extension
            dict file_opt=None: file options to be used in prompting the file name
        Returns: str
        Description: Prompt and retrieve file path from user.
        """
        if file_opt == None:
            file_opt = options = {}
            options['defaultextension'] = '{}'.format(extension)
            options['filetypes'] = [('{} File'.format(extension), '{}'.format(extension)), ('all files', '.*')]
            options['initialdir'] = 'C:\\'
            options['initialfile'] = 'ADC_results{}'.format(extension)
            options['title'] = 'Open FPGA {} file.'.format(extension)
        root = Tk()
        root.withdraw()
        return FD.askopenfilename(**file_opt)

class Conversions:

    def __init__(self):
        """
        Class: Conversions
        Inherit:
        Composition:
        Description: This class will be a coagulation of data type conversions,
            or file type conversions, or other conversions.
        """
        self.setBytesInWord()


    def setBytesInWord(self, bytesInWord=2):
        """
        Method: setBytesInWord
        Params: int bytesInWord=2: how many 8-bit bytes are in an arbitrary, case
            specific word. (initial word size is 16-bits)
        Returns:
        Description: create integer offset for every 8 bits in the word
        """
        self.bytesInWord = bytesInWord
        self.byteChunks = []
        for b in range(self.bytesInWord):
            self.byteChunks.append(255**b)


    def ba2ia(self, byteArray):
        """
        Method: ba2ia
        Params: bytearray byteArray:  bytearray to convert
        Returns: list
        Description: convert bytearray to list of ints. Bytes are grouped in
            pairs to form the int ({8-bit, 8-bit} -> int). If you have more or less
            bytes per word that you wish to convert into an int, change the
            amount by using the method setBytesInWord.
        """
        iarr = []
        word = 0
        i = 0
        ix = 0
        for b in byteArray:
            if i == self.bytesInWord-1:
                word += b*self.byteChunks[ix]
                iarr.append(word)
                i = 0
                word = 0
                ix = 0
            else:
                word += b*self.byteChunks[ix]
                ix += 1
                i += 1

        return iarr

def extractData(dataFileName=None, oneLine=False, samplesPerCode=1):

    fd = FDialog()
    mb = MBox()
    if dataFileName is None:
        file_opt = options = {}
        options['defaultextension'] = '.csv'
        options['filetypes'] = [('Comma Seperated Values', '.csv'),
                                ('Text file', '.txt'), ('all files', '.*')]
        options['initialdir'] = 'C:\\'
        options['initialfile'] = 'adc_data.csv'
        options['title'] = 'Open ADC data file'
        dataFileName = fd.openDataFileName()(**file_opt)

        if '.csv' in dataFileName:
            extension = '.csv'
        elif '.txt' in dataFileName:
            extension = '.txt'
        else:
            extension = None

    else:
        if '.csv' in dataFileName:
            extension = '.csv'
        elif '.txt' in dataFileName:
            extension = '.txt'
        else:
            extension = None


    if extension is None:
        mb.showerror("Bad file", data_file_error_text)
        return -1
    elif extension == '.csv':
        dataFile = open(dataFileName, 'r')

        sampledCodes = []
        sampleCount = 0
        avgSample = 0

        if oneLine:
            tempSamples = dataFile.readline().split(',')
            sampledCodes = []
            for samples in tempSamples:

                val = samples.strip()
                if '\n' in val:
                    val = float(val.strip('\n'))
                else:
                    val = float(val)

                if samplesPerCode > 1:
                    if sampleCount == samplesPerCode - 1:
                        sampleCount = 0
                        avgSample /= samplesPerCode
                        sampledCodes.append(avgSample)
                    else:
                        sampleCount += 1
                        avgSample += float(val)
                else:
                    sampledCodes.append(val)


        else:
            for line in dataFile:
                if samplesPerCode > 1:
                    if sampleCount == samplesPerCode - 1:
                        sampleCount = 0
                        avgSample /= samplesPerCode
                        sampledCodes.append(avgSample)
                    else:
                        sampleCount += 1
                        if ',' in line:
                            line = line.replace(',')
                        if '\n' in line:
                            line = line.strip('\n')
                        avgSample += float(line)
                else:
                    if ',' in line:
                        line = line.replace(',','')
                    if '\n' in line:
                        line = line.strip('\n')
                    sampledCodes.append(float(line))

        dataFile.close()

    elif extension == '.txt':
        dataFile = open(dataFileName, 'r')
        sampledCodes = []

        if oneLine:
            data = dataFile.read()
            samples = data.split() # assumed splitting based on ' ' (space)
            if samplesPerCode > 1:
                sum = 0
                for i, s in enumerate(samples):
                    if i % samplesPerCode-1 == 0:
                        sampledCodes.append(sum/samplesPerCode)
                        sum = 0
                    else:
                        sum += float(s)
            else:
                for s in samples:
                    sampledCodes.append(float(s))

        else:
            for line in dataFile:
                sampledCodes.append(float(line))

        dataFile.close()

    return sampledCodes


def findInputFreq(fsample, M=None, N=1, k=10):
    """
    fsample = sampling frequency
    M = sample size (2^k)
    N = number of periods of input sine wave
    k = bit width of sample size
    """
    if M is None:
        M = 2 ** k
        return fsample*(N/M)
    else:
        return fsample*(N/M)

def findSamplingFreq(fin, M=None, N=1, k=10):
    """
    fin = input frequency
    M = sample size (2^k)
    N = number of periods of input sine wave
    k = bit width of sample size
    """
    if M is None:
        M = 2 ** k
        return fin*(M/N)
    else:
        return fin*(M/N)

def findClockJitter(fin, tj):
    """
    fin = input frequency (fundamental)
    tj = jitter of the sampling clock and the ADC internal aperture jitter,
        combined on a root-sum-square basis, since they are not correlated
    """
    return 20*log10(1 / (2*pi*fin*tj))

def noisePower(samples):
    N = len(samples)
    Pn = 1 / N
    squareSum = 0
    # May need to split samples into bins and made the calculations
    # on sections at a time
    for k in range(N):
        squareSum += samples(k) ** 2

    Pn *= squareSum

    return Pn








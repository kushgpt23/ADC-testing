'''
Created on Sep 16, 2016

@author: Alphacore Engineer 1
'''
from math import log10, pi
from tkinter import filedialog
from tkinter import messagebox
from MessageTexts import *

def extractData(dataFileName=None, oneLine=False, samplesPerCode=1):
    if dataFileName is None:
        file_opt = options = {}
        options['defaultextension'] = '.csv'
        options['filetypes'] = [('Comma Seperated Values', '.csv'), 
                                ('Text file', '.txt'), ('all files', '.*')]
        options['initialdir'] = 'C:\\'
        options['initialfile'] = 'adc_data.csv'
        options['title'] = 'Open ADC data file'
        dataFileName = filedialog.askopenfilename(mode='r', **file_opt)
        
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
        messagebox.showerror("Bad file", data_file_error_text)
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








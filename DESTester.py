




"""
FOR REFERENCE USE
"""




import ok
import sys
import string

class DESTester:
	def __init__(self):
		return
		
	def InitializeDevice(self):
		# Open the first device we find.
		self.xem = ok.okCFrontPanel()
		if (self.xem.NoError != self.xem.OpenBySerial("")):
			print ("A device could not be opened.  Is one connected?")
			return(False)

		# Get some general information about the device.
		self.devInfo = ok.okTDeviceInfo()
		if (self.xem.NoError != self.xem.GetDeviceInfo(self.devInfo)):
			print ("Unable to retrieve device information.")
			return(False)
		print("         Product: " + self.devInfo.productName)
		print("Firmware version: %d.%d" % (self.devInfo.deviceMajorVersion, self.devInfo.deviceMinorVersion))
		print("   Serial Number: %s" % self.devInfo.serialNumber)
		print("       Device ID: %s" % self.devInfo.deviceID)
		
		self.xem.LoadDefaultPLLConfiguration()

		# Download the configuration file.
		if (self.xem.NoError != self.xem.ConfigureFPGA("des.bit")):
			print ("FPGA configuration failed.")
			return(False)

		# Check for FrontPanel support in the FPGA configuration.
		if (False == self.xem.IsFrontPanelEnabled()):
			print ("FrontPanel support is not available.")
			return(False)
		
		print ("FrontPanel support is available.")
		return(True)


	def SetKey(self, key):
		for i in range(4):
			self.xem.SetWireInValue((0x0b-i), key[i], 0xffff)
		self.xem.UpdateWireIns()


	def ResetDES(self):
		self.xem.SetWireInValue(0x10, 0xff, 0x01)
		self.xem.UpdateWireIns()
		self.xem.SetWireInValue(0x10, 0x00, 0x01)
		self.xem.UpdateWireIns()


	def EncryptDecrypt(self, infile, outfile):
		fileIn = open(infile, "rb")
		fileOut = open(outfile, "wb")

		# Reset the RAM address pointer.
		self.xem.ActivateTriggerIn(0x41, 0)
		
		while fileIn:
			buf = bytearray(fileIn.read(2048))
			
			got = len(buf)
			if (got == 0):
				break

			if (got < 2048):
				buf += b"\x00"*(2048-got)

			# Write a block of data.
			self.xem.ActivateTriggerIn(0x41, 0)
			self.xem.WriteToPipeIn(0x80, buf)

			# Perform DES on the block.
			self.xem.ActivateTriggerIn(0x40, 0)

			# Wait for the TriggerOut indicating DONE.
			for i in range(100):
				self.xem.UpdateTriggerOuts()
				if (self.xem.IsTriggered(0x60, 1)):
					break

			self.xem.ReadFromPipeOut(0xa0, buf)
			fileOut.write(buf)
		
		fileIn.close()
		fileOut.close()


	def Encrypt(self, infile, outfile):
		print ("Encrypting %s ----> %s" % (infile, outfile))
		# Set the encrypt Wire In.
		self.xem.SetWireInValue(0x0010, 0x0000, 0x0010)
		self.xem.UpdateWireIns()
		self.EncryptDecrypt(infile, outfile)


	def Decrypt(self, infile, outfile):
		print ("Decrypting %s ---> %s" % (infile, outfile))
		# Set the decrypt Wire In.
		self.xem.SetWireInValue(0x0010, 0x00ff, 0x0010)
		self.xem.UpdateWireIns()
		self.EncryptDecrypt(infile, outfile)


# Main code
print ("------ DES Encrypt/Decrypt Tester in Python ------")
des = DESTester()
if (False == des.InitializeDevice()):
	exit

des.ResetDES()

if (len(sys.argv) != 5):
	print ("Usage: DESTester [d|e] key infile outfile")
	print ("   [d|e]   - d to decrypt the input file.  e to encrypt it.")
	print ("   key     - 64-bit hexadecimal string used for the key.")
	print ("   infile  - an input file to encrypt/decrypt.")
	print ("   outfile - destination output file.")

# Get the hex digits entered as the key
key = []
strkey = sys.argv[2]
for i in range(4):
	key.append(int(strkey[i*4 : i*4+4], 16))
des.SetKey(key)

# Encrypt or decrypt
if (sys.argv[1] == 'd'):
	des.Decrypt(sys.argv[3], sys.argv[4])
else:
	des.Encrypt(sys.argv[3], sys.argv[4])

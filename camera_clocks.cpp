#include <iostream>
#include <fstream>
#include <stdio.h>
#include <string.h>
#include <Windows.h>

#include "okFrontPanelDLL.h"
#include "time.h"


#define XILINX_CONFIGURATION_FILE   "camera_clocks_v1.bit"
#define ALTERA_CONFIGURATION_FILE   "des.rbf"
#if defined(_WIN32)
#define strncpy strncpy_s
#define sscanf  sscanf_s
#endif

bool
clock_generation(okCFrontPanel *xem, char *outfilename)
{
	int i,len=2;
	std::ofstream f_out;
	unsigned long a,b;
	//time_t current_time;
	__int64 initial_time,current_time,frequency;
	double time;
	// Assert then deassert RESET.
	xem->SetWireInValue(0x00, 0xff, 0x01);
	xem->UpdateWireIns();
	xem->SetWireInValue(0x00, 0x00, 0x01);
	xem->SetWireInValue(0x01, 0x0e, 0x1f);
	xem->SetWireInValue(0x02, 0x07, 0x07);
	xem->UpdateWireIns();


	// Open the output file.
	f_out.open(outfilename, std::ios::binary | std::ofstream::app);
	if (false == f_out.is_open()) {
		printf("Error: Output file could not be opened.\n");
		return(false);
	}
	QueryPerformanceFrequency((LARGE_INTEGER *)&frequency);
	QueryPerformanceCounter((LARGE_INTEGER *)&initial_time);
	unsigned long start_time, new_time, time2;
	start_time = timeGetTime();
	for (i = 0; i < 1000; i++) {
		xem->UpdateWireOuts();
		QueryPerformanceCounter((LARGE_INTEGER *) &current_time);
		new_time = timeGetTime();
		//current_time = time(NULL);
		a = xem->GetWireOutValue(0x20);
		b = xem->GetWireOutValue(0x21);
//		xem->ReadFromPipeOut(0xA0, len, buf);
		//f_out << a[0] << "\t" << a[4]<<a[3]<<a[2]<<a[1]<<"\n";
		time = ((current_time-initial_time)*1.0 / frequency)*1000000.0;
		time2 = new_time - start_time;
		f_out << a<<"\t"<<b<<"\t"<< time<<"\t"<<time2<<"\r\n";
		}
	f_out.close();

	return(true);
}


okCFrontPanel *
initializeFPGA()
{
	okCFrontPanel *dev;
	okCPLL22393 pll22393;
	okCFrontPanel::ErrorCode error;
	std::string   config_filename;

	// Open the first XEM - try all board types.
	dev = new okCFrontPanel;
	if (okCFrontPanel::NoError != dev->OpenBySerial()) {
		delete dev;
		printf("Device could not be opened.  Is one connected?\n");
		return(NULL);
	}

	printf("Found a device: %s\n", dev->GetBoardModelString(dev->GetBoardModel()).c_str());
	
	error = dev->GetPLL22393Configuration(pll22393);
	pll22393.SetReference(48.0f);//48  //1.0  //48
	pll22393.SetPLLParameters(0, 100, 48);//0,10,48 //0,6,192  //0,100,48
	pll22393.SetOutputSource(0, okCPLL22393::ClkSrc_PLL0_0);
	pll22393.SetOutputDivider(0, 1); //100
	pll22393.SetOutputEnable(0, true);
	//pll22393.SetPLLLF(0, 100);
	dev->SetPLL22393Configuration(pll22393);
	double freq = pll22393.GetPLLFrequency(0);
	double freq2 = pll22393.GetOutputFrequency(0);
	std::cout<< "clock frequency is "<<freq<<"\n";
	std::cout << "Output frequency is " << freq2 << "\n";
	//dev->LoadDefaultPLLConfiguration();

	// Get some general information about the XEM.
	std::string str;
	printf("Device firmware version: %d.%d\n", dev->GetDeviceMajorVersion(), dev->GetDeviceMinorVersion());
	str = dev->GetSerialNumber();
	printf("Device serial number: %s\n", str.c_str());
	str = dev->GetDeviceID();
	printf("Device device ID: %s\n", str.c_str());

	// Download the configuration file.
	switch (dev->GetBoardModel()) {
	case okCFrontPanel::brdZEM4310:
	case okCFrontPanel::brdZEM5305A2:
		config_filename = ALTERA_CONFIGURATION_FILE;
		break;
	default:
		config_filename = XILINX_CONFIGURATION_FILE;
		break;
	}

	if (okCFrontPanel::NoError != dev->ConfigureFPGA(config_filename)) {
		printf("FPGA configuration failed.\n");
		delete dev;
		return(NULL);
	}

	// Check for FrontPanel support in the FPGA configuration.
	if (dev->IsFrontPanelEnabled())
		printf("FrontPanel support is enabled.\n");
	else
		printf("FrontPanel support is not enabled.\n");

	return(dev);
}


static void
printUsage(char *progname)
{
	printf("Usage: %s outfile\n", progname);
	printf("   outfile - destination output file.\n");
}


int
main(int argc, char *argv[])
{
	char outfilename[128];
	char dll_date[32], dll_time[32];
	
	printf("---- Opal Kelly ---- FPGA-DES Application v1.0 ----\n");
	if (FALSE == okFrontPanelDLL_LoadLib(NULL)) {
		printf("FrontPanel DLL could not be loaded.\n");
		return(-1);
	}
	okFrontPanelDLL_GetVersion(dll_date, dll_time);
	printf("FrontPanel DLL loaded.  Built: %s  %s\n", dll_date, dll_time);


	if (argc != 2) {
		printUsage(argv[0]);
		return(-1);
	}

	strncpy(outfilename, argv[1], 128);
	
	// Initialize the FPGA with our configuration bitfile.
	okCFrontPanel *xem;
	xem = initializeFPGA();
	if (NULL == xem) {
		printf("FPGA could not be initialized.\n");
		return(-1);
	}

	// Now perform the encryption/decryption process.
	if (clock_generation(xem, outfilename) == false) {
		printf("Clock generation process failed.\n");
		return(-1);
	}
	else {
		printf("Clock generation process succeeded!\n");
	}

	return(0);
}

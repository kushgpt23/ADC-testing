`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: Alphacore Inc.
// Engineer: Max Ruiz
// 
// Create Date:    12:24:52 09/19/2016 
// Design Name: 
// Module Name:    ADC_Testing_Top 
// Project Name: 
// Target Devices: 
// Tool versions: 
// Description: 
//
// Dependencies: 
//
// Revision: 
// Revision 0.01 - File Created
// Additional Comments: 
//
//////////////////////////////////////////////////////////////////////////////////
module ADC_Testing_Top(
	input clk, 
	input adc_clk,
	input [PRECISION-1:0] adc_code_in,
	input ext_reset,
	
	// Opal Kelly
	input  wire [7:0]  hi_in,
	output wire [1:0]  hi_out,
	inout  wire [15:0] hi_inout,
	inout wire hi_aa,    
	
	output wire i2c_sda,
	output wire i2c_scl,
	output wire hi_muxsel 
);

parameter PRECISION = 10;
parameter FIFO_COUNT_WIDTH = 12;
parameter UNDERFLOW_THRESHOLD = 0; // lowest # available databytes in FIFO
//parameter OVERFLOW_THRESHOLD = {FIFO_COUNT_WIDTH {1'b1}}; // 


/*************************************************/
//------------ Handle reset signals -------------//
/*************************************************/
wire reset; // internal reset, FrontPanel
wire ext_rst;
wire rst;
assign rst = reset | ext_rst;
Debounce debounce_0(
	.clk(clk),
	.signalIn(ext_reset),
	.signalOut(ext_rst)
);


/*************************************************/
//------------------- FIFO ----------------------//
/*************************************************/
reg rd_en;
wire [PRECISION-1:0] adc_code_out;
wire fifo_full;
wire fifo_empty;
wire [FIFO_COUNT_WIDTH-1:0] rd_data_count;
wire [FIFO_COUNT_WIDTH-1:0] wr_data_count;
wire fifo_clk;
fifo_adc fifo_adc_0(
  .rst(rst),
  .wr_clk(~adc_clk), // data will be avaible for reading from ADC on negedge of adc_clock
  .rd_clk(fifo_clk),
  .din(adc_code_in), // 10 bit;
  .wr_en(1'b1),
  //.rd_en(rd_en),
  .rd_en(1'b1),
  .dout(adc_code_out), // 10 bit;
  .full(fifo_full),
  .empty(fifo_empty),
  .rd_data_count(rd_data_count), // 12 bit;
  .wr_data_count(wr_data_count) // 12 bit;
);

wire underflowflag;
assign underflowflag = rd_data_count <= UNDERFLOW_THRESHOLD ? 1'b1 : 1'b0;

//wire overflowflag;
//assign overflowflag = wr_data_count >= OVERFLOW_THRESHOLD ? 1'b1 : 1'b0;

/*************************************************/
//------------- Opal Kelly Comm. ----------------//
/*************************************************/
/*
file:///C:/Users/Alphacore%20Engineer%201/Desktop/FrontPanel-UM.pdf
page 41

Endpoint Type | Address Range | Sync/Async   | Data Type
-------------------------------------------------------------------
Wire In 	     | 0x00 - 0x1F 	| Asynchronous | Signal state
Wire Out 	  | 0x20 - 0x3F 	| Asynchronous | Signal state
Pipe In       | 0x80 - 0x9F   | Synchronous  | Multi-byte transfer
Pipe Out      | 0xA0 - 0xBF   | Synchronous  | Multi-byte transfer

ENDPOINT DATAWIDTH
Endpoint Type | USB 2.0
-----------------------
Wire			  | 16bit
Pipe          | 16bit
*/

// Target interface bus
wire ti_clk;
wire [30:0] ok1;
wire [16:0] ok2;

// Endpoint connections:
wire [15:0] ep00wire; // wire in
wire [15:0] ep20wire; // wire out
wire [15:0] epA0pipe; // pipe out
wire epA0read; // pipe out read signal from host

assign i2c_sda = 1'bz;
assign i2c_scl = 1'bz;
assign hi_muxsel = 1'b0;

assign reset = ep00wire[0];
assign ep20wire[0] = fifo_empty;

wire [17*2-1:0] ok2x;

okHost hostIF (
	.hi_in(hi_in),
	.hi_out(hi_out),
	.hi_inout(hi_inout),
	.hi_aa(hi_aa),
	.ti_clk(ti_clk),
	.ok1(ok1),
	.ok2(ok2)
);

okWireIn wire00 (
	.ok1(ok1),
	.ep_addr(8'h00),
	.ep_dataout(ep00wire)
);

okPipeOut pipeA0 (
	.ok1(ok1),
	.ok2(ok2x[0*17 +: 17]),
	.ep_addr(8'hA0),
	.ep_datain(epA0pipe), // data from FIFO
	.ep_read(epA0read) // enable rd_en at FIFO
);

// DEBUG
wire debugOut;
assign debugOut = adc_code_in[0] & adc_code_in[1];
assign ep20wire[1] = debugOut;
// DEBUG

okWireOut wire20 (
	.ok1(ok1),
	.ok2(ok2x[1*17 +: 17]),
	.ep_addr(8'h20),
	.ep_datain(ep20wire)
);

okWireOR #(.N(2)) wireOR(
	.ok2(ok2),
	.ok2s(ok2x)
);

/*************************************************/
//------------- Readback ADC data ---------------//
/*************************************************/

assign epA0pipe = ~underflowflag ? 
						{{16-PRECISION {1'b0}}, adc_code_out} :
						{16 {1'b0}};

assign fifo_clk = ~ti_clk; // page 50 of FrontPanel-UM.pdf

always @(posedge ti_clk) begin
	if (epA0read) begin
		rd_en <= ~underflowflag;
	end
end

/*************************************************/
//------------- Write in ADC data ---------------//
/*************************************************/

// Writing data is all taken care of via the ADC signals

endmodule

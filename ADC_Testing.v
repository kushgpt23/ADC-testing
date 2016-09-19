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
	input ext_reset
);

parameter PRECISION = 10;
parameter FIFO_COUNT_WIDTH = 12;

wire reset; // internal reset
wire ext_rst;
wire rst;
assign rst = reset | ext_rst;
reg wr_en = 1'b0;
reg rd_en = 1'b0;
wire [PRECISION-1:0] adc_code_out;
wire fifo_full;
wire fifo_empty;
wire [FIFO_COUNT_WIDTH-1:0] rd_data_count;
wire [FIFO_COUNT_WIDTH-1:0] wr_data_count;


Debounce debounce_0(
	.clk(clk),
	.signalIn(ext_reset),
	.signalOut(ext_rst)
);


fifo_adc fifo_adc_0(
  .rst(rst),
  .wr_clk(adc_clk),
  .rd_clk(clk),
  .din(adc_code_in), // 10 bit;
  .wr_en(wr_en),
  .rd_en(rd_en),
  .dout(adc_code_out), // 10 bit;
  .full(fifo_full),
  .empty(fifo_empty),
  .rd_data_count(rd_data_count), // 12 bit;
  .wr_data_count(wr_data_count) // 12 bit;
);


endmodule

`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: Alphacore Inc.
// Engineer: Max Ruiz
// 
// Create Date:    13:44:07 09/19/2016 
// Design Name: 
// Module Name:    Debounce 
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
module Debounce(
	input clk,
	input signalIn,
	output wire signalOut
);

parameter SAMPLE_WIDTH = 4;
parameter SAMPLE_THRESHOLD = 10;

reg [SAMPLE_WIDTH-1:0] signal_sample = {SAMPLE_WIDTH {1'b0}};
reg signalIn_ff = 1'b0;

assign signalOut = signalIn_ff;

/*
Why not simply put FF in toplevel?

This module allows for a neat implementation of 
debouncing a signal for more than 1 clock cycle.
Right now, this only debounces a signal for 1 clock
cycle, like a FF does, but you can change that internally
to this block (using a counter).
*/

/* 
Method

The debounce uses an type of delay known as inertial delay.
Inertial delay requires a signal be in a certain state at the 
input of the block for a specific amount of time inorder to appear
at the output. If the signal does not hold it's state for that 
specific amount of time, it does not appear at the output.

So, if the signal is not held at 1'b1 for SAMPLE_THRESHOLD amount
of clock cycles, then signalOut will stay at 1'b0, otherwise it will
reflect signalIn (which is 1'b1).
*/

always @(posedge clk) begin
	if (signalIn) begin
		if (signal_sample == SAMPLE_THRESHOLD) begin
			signalIn_ff <= signalIn;
		end else begin
			signal_sample <= signal_sample + 1'b1;
		end
	end else begin
		signal_sample <= {SAMPLE_WIDTH {1'b0}};
		signalIn_ff <= signalIn;
	end
end


endmodule

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

reg signalIn_ff = 1'b0;

assign signalOut = signalIn_ff;


// Why not simply put FF in toplevel?

// This module allows for a neat implementation of 
// debouncing a signal for more than 1 clock cycle.
// Right now, this only debounces a signal for 1 clock
// cycle, like a FF does, but you can change that internally
// to this block (using a counter).

always @(posedge clk) begin
	if (signalIn) begin
		signalIn_ff <= 1'b1;
	end else begin
		signalIn_ff <= 1'b0;
	end
end


endmodule

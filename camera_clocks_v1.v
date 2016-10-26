module camera_clocks_v1(input clk,
	input  wire [7:0]  hi_in,
	output wire [1:0]  hi_out,
	inout  wire [15:0] hi_inout,
	inout  wire        hi_aa,
	input  wire        ADC_clk,	
	input  wire [9:0]  ADC0_data,
	input  wire [9:0]  ADC1_data,
	input  wire [9:0]  ADC2_data,
	input  wire [9:0]  ADC3_data,	
	output wire        i2c_sda,
	output wire        i2c_scl,
	output wire        hi_muxsel,
	output wire			 RST_SEL_0,
	output wire			 RST_SEL_1,
	output wire        RST_IN,
	output wire			 SAM_IN,
	output wire			 PRE_IN,
	output wire			 MEM_SEL,
	output wire			 VPULSE_IN,
	output wire [3:0]	 R_SEL,	
	output wire        R_shift_clk,
	output wire			 R_RSTDECC,
	output wire			 R_RSTSHIFT,
	input  wire        input_shiftclk,
	output wire			 PIX_OUT_CONTROL,
	input  wire			 R_output,
	output wire			 R_update,
	output wire 		 C_shift_clk,
	input  wire			 C_output,
	output wire 		 C_RSTSHIFT,
	output wire			 C_UPDATE,
	output wire			 C_SET,
	output wire			 C_RSTDEC,
	output wire			 CLK_OUTPUT,
	output wire        G33,
	output wire			 G32,
	output wire			 G23,
	output wire			 G12,
	output wire        G13,
	output wire			 G22,
	input  wire			 CLK_ADC_PGA_IN,
	output wire			 IQWRT1,
	output wire			 IQCLK1,
	output wire			 IQRESET1,
	output wire			 IQSEL1,
	output wire			 IQSEL2,
	output wire			 IQRESET2,
	output wire			 IQCLK2,
	output wire			 IQWRT2,
	output wire			 IQSEL3,
	output wire			 IQRESET3,
	output wire			 IQCLK3,
	output wire			 IQWRT3,
	output wire			 DB31,
	output wire 		 DB33,
	output wire			 DB52,
	output wire			 DB42,
	output wire			 DB01,
	output wire			 DB11,
	output wire			 DB21,
	output wire			 DB02,
	output wire			 DB12,
	output wire			 DB22,
	output wire			 DB32,
	output wire			 DB23,
	output wire			 DB13,
	output wire			 DB03,
	output wire			 RS,
	output wire			 SCL,
	output wire			 SDA,
	output wire			 CS
	);
	
//initialization
reg [13:0] counter1,counter;
wire reset;
wire rst_sample;

//Target interface bus:
wire        ti_clk;
wire [30:0] ok1;
wire [16:0] ok2;

// Endpoint connections:
wire [15:0]  ep00wire;
wire [15:0]  ep01wire;
wire [15:0]  ep02wire;
wire [15:0]  ep20wire;
wire [15:0]  ep21wire;
wire [15:0] TrigIn40;

assign i2c_sda = 1'bz;
assign i2c_scl = 1'bz;
assign hi_muxsel = 1'b0;

// Instantiate the okHost and connect endpoints.
wire [17*7-1:0]  ok2x;
okHost okHI(
	.hi_in(hi_in), .hi_out(hi_out), .hi_inout(hi_inout), .hi_aa(hi_aa), .ti_clk(ti_clk),
	.ok1(ok1), .ok2(ok2));

okWireOR # (.N(2)) wireOR (.ok2(ok2), .ok2s(ok2x));

okWireIn     ep00 (.ok1(ok1),                          .ep_addr(8'h00), .ep_dataout(ep00wire));
//okWireIn     ep01 (.ok1(ok1),                          .ep_addr(8'h01), .ep_dataout(ep01wire));
//okWireIn     ep02 (.ok1(ok1),                          .ep_addr(8'h02), .ep_dataout(ep02wire));
//okTriggerIn  ep40 (.ok1(ok1),                           .ep_addr(8'h40), .ep_clk(clk), .ep_trigger(TrigIn40));

okWireOut    ep20 (.ok1(ok1), .ok2(ok2x[ 0*17 +: 17 ]), .ep_addr(8'h20), .ep_datain(ep20wire));
okWireOut    ep21 (.ok1(ok1), .ok2(ok2x[ 1*17 +: 17 ]), .ep_addr(8'h21), .ep_datain(ep21wire));



okWireIn    ep01 (.ok1(ok1), .ep_addr(8'h01), .ep_dataout(ep01wire));
assign R_SEL = ep01wire [3:0];

okWireIn    ep02 (.ok1(ok1), .ep_addr(8'h02), .ep_dataout(ep02wire));
assign R_shift_clk_en= ep02wire[0];
assign R_shift_clk = R_shift_clk_en & input_shiftclk;
assign PIX_OUT_CONTROL= ep02wire[2];
assign RST_SEL_1= 1'b0;
wire [15:0] ep22wire;
okWireOut    ep22 (.ok1(ok1), .ok2(ok2x[ 2*17 +: 17 ]), .ep_addr(8'h22), .ep_datain(ep22wire));
assign ep22wire[0] = R_output;

wire counter2_en;
assign C_shift_clk_en= ep02wire[1] & counter2_en;
assign C_shift_clk = C_shift_clk_en & CLK_ADC_PGA_IN;
assign ep22wire[1]= C_output;
assign C_SET = ep01wire[4];
assign {G12, G13, G22, G23, G32, G33} = 6'b0;

assign IQWRT1 = ~input_shiftclk;
assign IQCLK1 = (~input_shiftclk)& (1<=counter3 && counter3<=10);
assign IQRESET1 = reset;
assign IQSEL1 = input_shiftclk;
assign IQSEL2 = input_shiftclk;
assign IQRESET2 = reset;
assign IQCLK2 = (~input_shiftclk)& (1<=counter3 && counter3<=10);
assign IQWRT2 = ~input_shiftclk;
assign IQSEL3 = input_shiftclk;
assign IQRESET3 = reset;
assign IQCLK3 = (~input_shiftclk)& (1<=counter3 && counter3<=10);
assign IQWRT3 = ~input_shiftclk;
assign DB31 = 1'b0;
assign DB33 = 1'b0;
assign DB52 = 1'b0;
assign DB42 = 1'b0;
assign DB01 = 1'b0;
assign DB11 = 1'b0;
assign DB21 = 1'b0;
assign DB02 = 1'b0;
assign DB12 = 1'b0;
assign DB22 = 1'b0;
assign DB32 = 1'b0;
assign DB23 = 1'b0;
assign DB13 = 1'b0;
assign DB03 = 1'b0;
assign RS = reset;
assign SCL = ~input_shiftclk;
assign SDA = SDA_reg;


reg [6:0] counter3;
always @(posedge input_shiftclk)
begin
	if (reset)
		counter3<=0;
	else
	begin
		if (counter3 <= 70)
			counter3<=counter3+1;
		else counter3<=counter3;	
	end
end

assign CS = 
			((1<=counter3 && counter3<=10)||(21<=counter3 && counter3<=30) || (41<=counter3 && counter3<=50) || (61<=counter3 && counter3<=70))? 1'b0 : 1'b1;

wire [7:0] IBIAS_GS1_ADC;
wire [7:0] IBIAS_ADC;
wire [7:0] IBIAS_BUFFER_ADC;
wire [7:0] IBIAS_VGA;

assign IBIAS_GS1_ADC = 128;
assign IBIAS_ADC = 128;
assign IBIAS_BUFFER_ADC = 128;
assign IBIAS_VGA = 128;

reg SDA_reg;

always @(*)
case(counter3)
1:  SDA_reg = 1'b0;
2:  SDA_reg = 1'b0;
3:  SDA_reg = IBIAS_GS1_ADC[7];
4:  SDA_reg = IBIAS_GS1_ADC[6];
5:  SDA_reg = IBIAS_GS1_ADC[5];
6:  SDA_reg = IBIAS_GS1_ADC[4];
7:  SDA_reg = IBIAS_GS1_ADC[3];
8:  SDA_reg = IBIAS_GS1_ADC[2];
9:  SDA_reg = IBIAS_GS1_ADC[1];
10: SDA_reg = IBIAS_GS1_ADC[0];
21: SDA_reg = 1'b0;
22: SDA_reg = 1'b1;
23: SDA_reg = IBIAS_ADC[7];
24: SDA_reg = IBIAS_ADC[6];
25: SDA_reg = IBIAS_ADC[5];
26: SDA_reg = IBIAS_ADC[4];
27: SDA_reg = IBIAS_ADC[3];
28: SDA_reg = IBIAS_ADC[2];
29: SDA_reg = IBIAS_ADC[1];
30: SDA_reg = IBIAS_ADC[0];
41: SDA_reg = 1'b1;
42: SDA_reg = 1'b0;
43: SDA_reg = IBIAS_BUFFER_ADC[7];
44: SDA_reg = IBIAS_BUFFER_ADC[6];
45: SDA_reg = IBIAS_BUFFER_ADC[5];
46: SDA_reg = IBIAS_BUFFER_ADC[4];
47: SDA_reg = IBIAS_BUFFER_ADC[3];
48: SDA_reg = IBIAS_BUFFER_ADC[2];
49: SDA_reg = IBIAS_BUFFER_ADC[1];
50: SDA_reg = IBIAS_BUFFER_ADC[0];
61: SDA_reg = 1'b1;
62: SDA_reg = 1'b1;
63: SDA_reg = IBIAS_VGA[7];
64: SDA_reg = IBIAS_VGA[6];
65: SDA_reg = IBIAS_VGA[5];
66: SDA_reg = IBIAS_VGA[4];
67: SDA_reg = IBIAS_VGA[3];
68: SDA_reg = IBIAS_VGA[2];
69: SDA_reg = IBIAS_VGA[1];
70: SDA_reg = IBIAS_VGA[0];
default: SDA_reg = 1'b0;
endcase

//Signals to and fro host
assign reset = ep00wire[0];
assign ep20wire = {15'b0,SAM_IN};
assign ep21wire = {15'b0, RST_IN};

assign fifo_clk = ~ti_clk; // page 50 of FrontPanel-UM.pdf

wire [9:0] fifo0_data;
wire full0,empty0;
reg rd_en0;
fifo_generator_v9_3  f0(
  .rst(reset),
  .wr_clk(ADC_clk),
  .rd_clk(fifo_clk),
  .din(ADC0_data),
  .wr_en(~full0),
  .rd_en(rd_en0),
  .dout(fifo0_data),
  .full(full0),
  .empty(empty0)
);

wire [15:0] epA0pipe; // pipe out; adc data from fifo
wire epA0read; // pipe out read signal from host
okPipeOut pipeA0 (
	.ok1(ok1),
	.ok2(ok2x[3*17 +: 17]),
	.ep_addr(8'hA0),
	.ep_datain(epA0pipe), // data from FIFO
	.ep_read(epA0read) // enable rd_en at FIFO
);
assign epA0pipe = {{6 {1'b0}}, fifo0_data};

always @(posedge ti_clk) begin
	if (epA0read) begin
		rd_en0 <= ~empty0;
	end
end

wire [9:0] fifo1_data;
wire full1,empty1;
reg  rd_en1;
fifo_generator_v9_3  f1(
  .rst(reset),
  .wr_clk(ADC_clk),
  .rd_clk(fifo_clk),
  .din(ADC1_data),
  .wr_en(~full1),
  .rd_en(rd_en1),
  .dout(fifo1_data),
  .full(full1),
  .empty(empty1)
);

wire [15:0] epA1pipe; // pipe out; adc data from fifo
wire epA1read; // pipe out read signal from host
okPipeOut pipeA1 (
	.ok1(ok1),
	.ok2(ok2x[4*17 +: 17]),
	.ep_addr(8'hA1),
	.ep_datain(epA1pipe), // data from FIFO
	.ep_read(epA1read) // enable rd_en at FIFO
);
assign epA1pipe = {{6 {1'b0}}, fifo1_data};

always @(posedge ti_clk) begin
	if (epA1read) begin
		rd_en1 <= ~empty1;
	end
end

wire [9:0] fifo2_data;
wire full2,empty2;
reg rd_en2;
fifo_generator_v9_3  f2(
  .rst(reset),
  .wr_clk(ADC_clk),
  .rd_clk(fifo_clk),
  .din(ADC2_data),
  .wr_en(~full2),
  .rd_en(rd_en2),
  .dout(fifo2_data),
  .full(full2),
  .empty(empty2)
);

wire [15:0] epA2pipe; // pipe out; adc data from fifo
wire epA2read; // pipe out read signal from host
okPipeOut pipeA2 (
	.ok1(ok1),
	.ok2(ok2x[5*17 +: 17]),
	.ep_addr(8'hA2),
	.ep_datain(epA2pipe), // data from FIFO
	.ep_read(epA2read) // enable rd_en at FIFO
);
assign epA2pipe = {{6 {1'b0}}, fifo2_data};

always @(posedge ti_clk) begin
	if (epA2read) begin
		rd_en2 <= ~empty2;
	end
end

wire [9:0] fifo3_data;
wire full3,empty3;
reg rd_en3;
fifo_generator_v9_3  f3(
  .rst(reset),
  .wr_clk(ADC_clk),
  .rd_clk(fifo_clk),
  .din(ADC3_data),
  .wr_en(~full3),
  .rd_en(rd_en3),
  .dout(fifo3_data),
  .full(full3),
  .empty(empty3)
);

wire [15:0] epA3pipe; // pipe out; adc data from fifo
wire epA3read; // pipe out read signal from host
okPipeOut pipeA3 (
	.ok1(ok1),
	.ok2(ok2x[6*17 +: 17]),
	.ep_addr(8'hA3),
	.ep_datain(epA3pipe), // data from FIFO
	.ep_read(epA3read) // enable rd_en at FIFO
);
assign epA3pipe = {{6 {1'b0}}, fifo3_data};

always @(posedge ti_clk) begin
	if (epA3read) begin
		rd_en3 <= ~empty3;
	end
end

//Output pin assignment using counter values

wire [9:0] delay1 = 11;				// multiples of 10ns
wire [9:0] delay = 10;				// multiples of 10ns
wire [9:0] exposure_time = 100;	// multiples of 10ns


assign RST_SEL_0 =
		(1<=counter1 && counter1<=delay1) ? 1'b0 : 1'b1;

assign RST_SEL_1 = 1'b0;
		
assign RST_IN = 
		(2<=counter1 && counter1<=(delay1-1)) ? 1'b1 : 1'b0;


negedge_detecter i1 (.A(RST_IN), .rst(reset), .clk(clk), .delay(delay), .Y(rst_sample));
negedge_detecter i2 (.A(rst_sample), .rst(reset), .clk(clk), .delay(exposure_time-delay), .Y(PRE_IN));
negedge_detecter i3 (.A(rst_sample), .rst(reset), .clk(clk), .delay(exposure_time+10'b1010-delay), .Y(SAM_IN));

assign MEM_SEL =
		(14'b1<=counter1 && counter1<=(delay1+exposure_time+15)) ? 1'b1: 1'b0;

assign VPULSE_IN =		
		(14'b1<=counter1 && counter1<=(delay1+exposure_time+16)) ? 1'b0: 1'b1;

assign R_update = 
		(0<=counter1 && counter1<=(delay1+exposure_time+17)) ? 1'b1: 1'b0;		

assign R_RSTDECC = 
		(0<=counter1 && counter1<=(delay1+exposure_time+17)) ? 1'b1: 1'b0;

assign R_RSTSHIFT = 
		(0<=counter1 && counter1<=(delay1+exposure_time+17)) ? 1'b0: 1'b1;

assign counter2_en = 
		(0<=counter1 && counter1<=(delay1+exposure_time+17)) ? 1'b0: 1'b1;
		
assign C_UPDATE = 
		(1<=counter2 && counter1<=4) ? 1'b1: 1'b0;		

assign C_RSTDEC = 
		(1<=counter2 && counter2<=4) ? 1'b1: 1'b0;

assign C_RSTSHIFT = 
		(1<=counter2 && counter2<=4) ? 1'b0: 1'b1;		
	
assign row_select =
		((delay1+exposure_time+18)<=counter1 && counter1<=(delay1+exposure_time+401)) ? 1'b1: 1'b0;		


//Main Counter		
always @(posedge clk)
begin
	if (reset)
		counter<=14'b0;
	else
	begin
		if (counter == 19999)
			counter<=14'b0;
		else counter<=counter+14'b1;
	end
end

reg [6:0] counter2;
always @(posedge clk)
begin
	if (reset)
		counter2<= 0;
	else if (counter2_en == 1)
		begin
		if (counter2 == 99)
		counter2 <= 0;
		else counter2<= counter2+1;
		end
end

//Latch to prevent counter ripple effect 
always @(clk or counter)
begin
	if (reset)
	counter1<=14'b0;
	else if (~clk)
	counter1<=counter;
end

endmodule

module camera_clocks_v1(input clk,
	input  wire [7:0]  hi_in,
	output wire [1:0]  hi_out,
	inout  wire [15:0] hi_inout,
	inout  wire        hi_aa,

	output wire        i2c_sda,
	output wire        i2c_scl,
	output wire        hi_muxsel,
	output wire			 Vrst_sel0,
	output wire        rst,
	output wire			 sample,
	output wire			 precharge,
	output wire			 mem_sel,
	output wire			 pulse,
	output wire			 row_select
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
wire [17*2-1:0]  ok2x;
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

//Signals to and fro host
assign reset = ep00wire[0];
assign ep20wire = {15'b0,sample};
assign ep21wire = {15'b0, rst};


//Output pin assignment using counter values

wire [9:0] delay1 = 11;				// multiples of 10ns
wire [9:0] delay = 10;				// multiples of 10ns
wire [9:0] exposure_time = 100;	// multiples of 10ns


assign Vrst_sel0 =
		(1<=counter1 && counter1<=delay1) ? 1'b0 : 1'b1;		
assign rst = 
		(2<=counter1 && counter1<=(delay1-1)) ? 1'b1 : 1'b0;


negedge_detecter i1 (.A(rst), .rst(reset), .clk(clk), .delay(delay), .Y(rst_sample));
negedge_detecter i2 (.A(rst_sample), .rst(reset), .clk(clk), .delay(exposure_time-delay), .Y(precharge));
negedge_detecter i3 (.A(rst_sample), .rst(reset), .clk(clk), .delay(exposure_time+10'b1010-delay), .Y(sample));

assign mem_sel =
		(14'b1<=counter1 && counter1<=(delay1+exposure_time+15)) ? 1'b1: 1'b0;

assign pulse =		
		(14'b1<=counter1 && counter1<=(delay1+exposure_time+16)) ? 1'b0: 1'b1;

assign row_select =
		((delay1+exposure_time+18)<=counter1 && counter1<=(delay1+exposure_time+401)) ? 1'b1: 1'b0;		

//Main Counter		
always @(posedge clk)
begin
	if (reset)
		counter<=14'b0;
	else
	begin
		if (counter == 14'b10011100001111)
			counter<=14'b0;
		else counter<=counter+14'b1;
	end
end

//Flip flop to latch out 
always @(clk or counter)
begin
	if (reset)
	counter1<=14'b0;
	else if (~clk)
	counter1<=counter;
end

endmodule

module alignment (
    input  logic       clk_i,
    input  logic [7:0] data_i,
    output logic       valid_o
);
    localparam int AddrWidth = 4;
    localparam int Count = 2;
    logic        valid;
    logic [7:0]  data;
    logic [15:0] wide;
    assign valid_o    = valid;
    assign data = data_i;
    sub u_sub (
        .clk_i    (clk_i),
        .data_in_i(data),
        .rst_ni   (1'b1)
    );
    always_comb begin
        case (data)
            8'd0:    valid = 1'b0;
            8'd1: valid = 1'b0;
            default: valid = 1'b1;
        endcase
    end
endmodule

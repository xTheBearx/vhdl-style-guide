// Problems slang finds when it elaborates the file; everything the file uses is defined in it
module lint (
    input  logic       clk_i,
    input  logic [7:0] a_i,
    input  logic       b_i,
    input  logic [3:0] s_i,
    output logic [3:0] y_o,
    output logic       l_o,
    output logic       m_o,
    output logic       z_o,
    output logic       u_o
);
    logic spare;
    assign y_o = a_i;
    always_comb begin
        if (b_i) l_o = a_i[0];
    end
    assign m_o = 1'b0;
    always_ff @(posedge clk_i) m_o <= 1'b1;
    assign implicit_net = a_i[1];
    always @(a_i) z_o = a_i[2] & b_i;
    always_comb begin
        case (s_i)
            4'd1: spare = 1'b0;
            4'd1: spare = 1'b1;
            default: spare = 1'b0;
        endcase
    end
    always_ff @(posedge clk_i) begin
        if (s_i == -1) u_o <= 1'b1;
        else u_o <= 1'b0;
    end
endmodule

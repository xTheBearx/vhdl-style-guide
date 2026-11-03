module sub (
    input  logic       clk_i,
    input  logic [3:0] d_i,
    output logic [7:0] q_o,
    output logic       unused_o
);
    always_ff @(posedge clk_i) begin
        q_o <= {4'b0000, d_i};
    end
endmodule

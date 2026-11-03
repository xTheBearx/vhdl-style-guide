// Uses a package of a file listed after it, and a module no file of the run defines
module vl_top
    import vl_pkg::*;
(
    input  logic       clk_i,
    input  logic [1:0] sel_i,
    input  logic       d_i,
    output logic       q_o,
    output logic       r_o,
    output logic       s_o
);

    logic t;

    always_ff @(posedge clk_i) begin
        t = d_i;
        q_o <= t;
    end

    always_comb begin
        r_o <= d_i;
    end

    always_comb begin
        case (sel_i)
            2'b00: s_o = 1'b0;
            2'b01: s_o = 1'b1;
        endcase
    end

    vendor_cell #(.INIT(WIDTH)) u_cell (.a(d_i), .y());

endmodule

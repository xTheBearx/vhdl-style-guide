// Module: do254
// Function: violations of the DO-254 checks for SystemVerilog
// Author: mhsg tests
// Date: 2026-11-08
module do254 (
    input  logic       clk_i,
    input  logic       rst_ni,
    input  logic       a_i,
    input  logic [3:0] d_i,
    output logic       q_o = 1'b0,
    output logic       b_o,
    output logic [3:0] c_o
);

    logic busy = 1'b0;
    logic a_n;
    logic a_d;
    logic [3:0] mem [4];
    logic [1:0] addr;

    // Inverters in a chain
    assign a_n = ~a_i;
    assign a_d = ~a_n;

    // A register without reset, and a memory, which needs none
    always_ff @(posedge clk_i) begin
        busy <= a_d;
        mem[addr] <= d_i;
    end

    // rst_ni active low and asynchronous here
    always_ff @(posedge clk_i or negedge rst_ni) begin : p_count
        if (!rst_ni) c_o <= '0;
        else c_o <= c_o + 4'd5;
    end

    // and active high and synchronous here
    always_ff @(posedge clk_i) begin : p_b
        if (rst_ni) b_o <= 1'b0;
        else b_o <= busy;
    end

    // if (busy) q_o <= a_i;
    always_ff @(posedge clk_i or negedge rst_ni) begin : p_q
        if (!rst_ni) q_o <= 1'b0;
        else q_o <= a_i;
    end

endmodule

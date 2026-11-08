// Module: do254_more
// Function: violations of the DO-254 checks for SystemVerilog, second batch
// Author: mhsg tests
// Date: 2026-11-08

typedef enum logic [1:0] {Idle, Run, Done, Fault} state_e;

module leaf #(
    parameter int Width = 8
) (
    input  logic             clk_i,
    input  logic [Width-1:0] data_i,
    output logic [Width-1:0] data_o,
    output logic             valid_o
);
    assign data_o  = data_i;
    assign valid_o = 1'b1;
endmodule

module do254_more (
    input  logic       clk_i,
    input  logic       start_i,
    input  logic       last_i,
    input  logic [7:0] payload,
    inout  wire        pad_io,
    output logic [7:0] data_o,
    output logic       hold
);
    state_e state_q, state_d;
    logic [7:0] sum;
    logic [7:0] count;
    logic enable;
    logic [7:0] data_o2;
    logic valid;

    leaf u_leaf (
        .clk_i  (clk_i),
        .data_i (payload),
        .data_o (data_o),
        .valid_o()
    );

    leaf u_leaf_open (
        .clk_i  (clk_i),
        .data_o (data_o2),
        .valid_o(valid)
    );

    assign hold   = hold | start_i;
    assign enable = start_i;

    // synopsys translate_off
    initial $display("do254_more");
    // synopsys translate_on

    always_comb begin : p_next
        case (state_q)
            Idle:    if (start_i) state_d = Run;
            Run:     if (last_i) state_d = Done;
            Done:    ;
            default: state_d = Idle;
        endcase
    end

    always_comb begin : p_sum
        int count;
        count = 0;
        if (enable) sum = payload;
        data_o_unused = sum;
    end

    logic [7:0] data_o_unused;
    logic [7:0] acc;
    logic [7:0] total;

    always_ff @(posedge clk_i) begin : p_state
        state_q <= state_d;
        acc = acc + payload;
        total <= acc;
    end
endmodule

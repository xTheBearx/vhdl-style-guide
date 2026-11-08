// Module: do254_more_clean
// Function: code that passes the DO-254 checks for SystemVerilog of the second batch
// Author: mhsg tests
// Date: 2026-11-08

typedef enum logic [1:0] {Idle, Run, Done} state_e;

// REQ: HWR-101
module leaf_clean #(
    parameter int Width = 8
) (
    input  logic [Width-1:0] data_i,
    output logic [Width-1:0] data_o
);
    if (Width < 1) begin : g_width_check
        $error("Width must be positive");
    end

    assign data_o = data_i;
endmodule

// REQ: HWR-102
module do254_more_clean (
    input  logic       clk_i,
    input  logic       start_i,
    input  logic       last_i,
    input  logic [7:0] data_i,
    output logic [7:0] data_o,
    output logic [7:0] sum_o
);
    state_e state_q, state_d;
    logic [7:0] sum;

    leaf_clean u_leaf (
        .data_i (data_i),
        .data_o (data_o)
    );

    // REQ: HWR-103
    always_comb begin : p_next
        state_d = state_q;
        case (state_q)
            Idle:    if (start_i) state_d = Run;
            Run:     if (last_i) state_d = Done;
            Done:    state_d = Idle;
            default: state_d = Idle;
        endcase
    end

    // REQ: HWR-104
    always_comb begin : p_sum
        sum = '0;
        if (start_i) sum = data_i;
    end

    assign sum_o = sum;

    // REQ: HWR-105
    always_ff @(posedge clk_i) begin : p_state
        state_q <= state_d;
    end
endmodule

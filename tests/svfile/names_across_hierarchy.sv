// Module: names_across_hierarchy
// Function: signals connected to ports named by direction, sv_module_018 (DR9)
// Author: mhsg tests
// Date: 2026-11-08

module leaf (
    input  logic clk_i,
    input  logic rst_n_i,
    input  logic rst_ni,
    input  logic data_i,
    output logic tick_o
);
endmodule

module sync (
    input  logic clk_i,
    input  logic d_i,
    output logic q_o
);
endmodule

module lane (
    input logic d_i
);
endmodule

module names_across_hierarchy (
    input  logic clk_i,
    input  logic rst_n,
    input  logic foo,
    input  logic bar,
    output logic tick
);
    localparam int Lanes = 2;

    logic foo_s;
    logic bar_s;

    // The names without their direction suffixes are those of the ports, apart from data_i
    leaf u_leaf (
        .clk_i  (clk_i),
        .rst_n_i(rst_n),
        .rst_ni (rst_n),
        .data_i (foo),
        .tick_o (tick)
    );

    // A module instantiated more than once cannot have the names of its ports in every instance
    sync u_sync_foo (
        .clk_i(clk_i),
        .d_i  (foo),
        .q_o  (foo_s)
    );

    sync u_sync_bar (
        .clk_i(clk_i),
        .d_i  (bar),
        .q_o  (bar_s)
    );

    // Neither can an instance in a loop generate
    for (genvar i = 0; i < Lanes; i++) begin : g_lane
        lane u_lane (
            .d_i(foo)
        );
    end
endmodule

// A SystemVerilog design that read_verilog -sv cannot read: a packed struct and its assignment pattern
module sv_only (input logic clk_i, output logic q_o);
    typedef struct packed { logic a; logic b; } pair_t;
    pair_t p;
    always_ff @(posedge clk_i) p <= pair_t'{a: 1, b: 0};
    assign q_o = p.a;
endmodule

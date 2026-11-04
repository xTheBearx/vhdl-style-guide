// sv_lint_008: reads through functions and tasks, hierarchical names, members, package items and variables the
// block computes
module sens (
    input  logic a_i,
    input  logic b_i,
    input  logic c_i,
    output logic y_o,
    output logic z_o,
    output logic w_o
);
    typedef struct packed {logic f;} cfg_t;
    cfg_t cfg;
    logic q;

    function automatic logic gate(input logic x);
        gate = x & c_i;
    endfunction

    function automatic logic twice(input logic x);
        twice = gate(x) | b_i;
    endfunction

    task automatic copy(input logic i, output logic o);
        o = i;
    endtask

    assign cfg = '{f: a_i};

    always @(a_i) begin
        y_o = twice(a_i);
    end

    always @(a_i or cfg) begin
        copy(a_i, q);
        z_o = q | cfg.f | pkg::ON;
    end

    always @(a_i) begin
        w_o = a_i | u_sub.valid;
    end
endmodule

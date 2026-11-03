`define data_width 8
`define DATA_OK 1
`include "/abs/defines.svh"
package types;
    typedef enum logic {Idle, Busy} State;
    typedef struct packed {logic a;} Beat;
    typedef enum logic {A, B} mode_e;
endpackage
module declarations #(
    parameter data_width = 8,
    parameter int DisableParity = 0,
    parameter int Depth = 'd4
) (
    input logic [0:7] in_i,
    output logic Valid_o
);
    localparam int MAX_COUNT = 10;
    localparam int MaxCount = 64'h1_0000_0000;
    logic [7:0] mem [15:0];
    logic [7:0] mem2 [16];
    logic signal;
    logic vdd_ok;
    logic data, Data;
    logic v;
    logic _x;
    enum logic {X, Y} anon;
    struct packed {logic a;} anon_s;
    assign v = 4'b1;
    assign v = 4'hFF;
    assign v = 4'b0;
    assign v = 'h1_0000_0000;
    function logic parity(input data);
        parity <= ^data;
    endfunction
    task wait_cycles(input int n);
    endtask
    function automatic logic ok(input logic [7:0] d);
        return ^d;
    endfunction
    initial v = 0;
    always_comb begin
        if (v == 1'bx) v = 0;
        if (v) v = 1;
        case (1'b1)
            v: ;
            default: v = 0;
        endcase
    end
    always @(posedge clk) begin
        @(posedge clk) v <= 1;
    end
    always_comb case (v) // synopsys full_case
        default: v = 0;
    endcase
endmodule
module second;
endmodule
interface Bus;
endinterface
class pkt;
    rand int x;
    constraint Length { x < 2; }
endclass

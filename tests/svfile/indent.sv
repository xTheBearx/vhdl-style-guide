// Indentation of SystemVerilog: the constructs the indent model knows
`default_nettype none

package indent_pkg;
    typedef enum logic [1:0] {
        Idle,
        Busy
    } state_e;

    typedef struct packed {
        logic       valid;
        logic [7:0] data;
    } beat_t;

    function automatic logic parity(input logic [7:0] data);
        return ^data;
    endfunction
endpackage

module indent #(
    parameter int Width = 8,
    parameter int Depth = 4  // trailing comment
) (
    input  logic             clk_i,
    input  logic             rst_ni,
    input  logic [Width-1:0] data_i,
    output logic [Width-1:0] data_o
);
    import indent_pkg::*;

    state_e state_q, state_d;
    logic [Width-1:0] data_q;
    // A comment above a declaration
    logic valid;

    always_ff @(posedge clk_i or negedge rst_ni) begin : proc_state
        if (!rst_ni) begin
            state_q <= Idle;
        end else if (valid)
            state_q <= state_d;
        else begin
            state_q <= state_q;
            // A comment above end
        end
    end

    always_comb begin
        state_d = state_q;
        unique case (state_q)
            Idle: state_d = Busy;
            Busy: begin
                state_d = Idle;
            end
            default:
                state_d = Idle;
        endcase
    end

    // Continuation lines and aligned lists are not checked
    assign valid = data_i[0] &&
                     data_i[1];
    assign data_o = combine(data_q,
                            data_i);

    sub #(
        .Width(Width)
    ) u_sub (
        .clk_i (clk_i),
        .data_i(data_i),
        .data_o()
    );

    for (genvar i = 0; i < Depth; i++) begin : gen_stage
        assign stage[i] = data_i;
    end

    if (Width > 8) begin : gen_wide
        assign wide = 1'b1;
    end else begin : gen_narrow
        assign wide = 1'b0;
    end

`ifdef SIMULATION
    initial begin
        $display("Width: %0d — Depth: %0d", Width, Depth);
    end
`endif

    task automatic wait_cycles(input int n);
        repeat (n) begin
            @(posedge clk_i);
        end
    endtask
endmodule

interface bus_if;
    logic req;
    logic gnt;
    modport host (
        output req,
        input  gnt
    );
endinterface

class packet;
    rand bit [7:0] length;
    constraint c_length {
        length inside {[1:64]};
    }

    function new();
        length = 1;
    endfunction
endclass

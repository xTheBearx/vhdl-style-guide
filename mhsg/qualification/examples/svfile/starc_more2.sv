// Violations of the STARC checks of sv_function_006 to 008, sv_always_010 to 014, sv_statement_010 to 013,
// sv_case_005 to 007 and sv_declaration_003
module starc_more2 (
    input  logic       clk_i,
    input  logic       clk2_i,
    input  logic       rst_i,
    input  logic       set_ni,
    input  logic [1:0] sel_i,
    input  logic [7:0] a_i,
    input  logic [7:0] b_i,
    output logic [7:0] y_o
);
    logic valid, ready;
    logic [7:0] q;
    logic [7:0] r;
    logic [7:0] s;
    logic [7:0] t;

    function automatic logic [7:0] add(input logic [7:0] x);
        valid = 1'b1;
        add = x + b_i;
    endfunction

    task automatic wait_clock;
        @(posedge clk_i);
    endtask

    always @(a_i or 1'b1 or r) begin
        r = a_i;
    end

    always_ff @(posedge clk_i or posedge rst_i or negedge set_ni) begin
        if (rst_i || !set_ni) begin
            q <= 8'd0;
        end else begin
            q <= a_i;
        end
    end

    always_ff @(posedge clk_i or posedge clk2_i) begin
        s <= a_i;
    end

    always_comb begin
        if (sel_i[0] && sel_i[1] || valid) begin
            t = a_i;
        end else if (a_i + 1 == b_i) begin
            t = b_i;
        end
        y_o = (a_i + b_i) / b_i;
        casez (sel_i & 2'b11)
            ready: y_o = add(a_i);
            default: y_o = 8'd0;
        endcase
    end
endmodule

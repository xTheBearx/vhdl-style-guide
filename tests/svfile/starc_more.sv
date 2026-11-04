// Violations of the STARC checks of sv_naming_014 to 015, sv_always_007 to 009, sv_statement_007 to 009,
// sv_case_004, sv_dimension_003, sv_literal_006, sv_module_003, sv_declaration_002 and sv_comment_002
module starc_more #(
    parameter int Depth
) (
    input  logic       clk__i,
    input  logic       rst_ni,
    input  logic [8:1] data_i,
    output logic [7:0] data_o,
    output logic       flag_
);
    /* A block comment */
    logic [7:0] value;
    logic       a;
    logic       b;
    logic       c;

    always_ff @(negedge clk__i or negedge rst_ni) begin
        if (!rst_ni) begin
            value <= 8'b0;
        end else begin
            value <= data_i;
        end
    end

    assign data_o = a ? value : b ? 8'bxxxx_0000 : 8'd0;

    always_comb begin
        for (int i = 0; i < 4; i++) begin
            i = i + 1;
        end
    end

    sub buffer (clk__i, a);
    sub sub (.clk(clk__i), .q(b));
    sub sub_2 (.clk(clk__i), .q(c));

    always_comb begin
        case (a)
            1'b0: c = 1'b1;
            default: c = 1'bx;
        endcase
    end

    assign flag_ = a;
endmodule

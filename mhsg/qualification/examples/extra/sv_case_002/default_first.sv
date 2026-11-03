// Qualification example of sv_case_002: the default item comes first in the first case statement, last in the second
module default_first (
    input  logic [1:0] sel,
    input  logic       a,
    output logic       y,
    output logic       z
);

    always_comb begin
        case (sel)
            default: y = 1'b0;
            2'b01:   y = a;
        endcase
    end

    always_comb begin
        case (sel)
            2'b01:   z = a;
            default: z = 1'b0;
        endcase
    end

endmodule

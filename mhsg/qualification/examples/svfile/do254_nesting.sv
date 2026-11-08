// Module: do254_nesting
// Function: if statements nested deeper than the limit of DO-254 check SS20
// Author: mhsg tests
// Date: 2026-11-08
module do254_nesting (
    input  logic [4:0] a_i,  // conditions
    output logic       y_o   // result
);

    // Five if statements, each in the branch of the one before; the limit is four
    always_comb begin : p_nested
        y_o = 1'b0;
        if (a_i[0]) begin
            if (a_i[1]) begin
                if (a_i[2]) begin
                    if (a_i[3]) begin
                        if (a_i[4]) begin
                            y_o = 1'b1;
                        end
                    end
                end
            end
        end
    end

endmodule

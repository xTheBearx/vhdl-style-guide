module continuation (
    input  logic a_i,
    input  logic b_i,
    output logic y_o,
    output logic z_o,
    output logic w_o
);
    assign y_o = a_i &
    b_i;
    assign z_o = select(a_i,
                        b_i);
    (* keep = "true" *)
    logic flag;
    always_comb begin
        w_o = combine(
            a_i,
        b_i
        );
        case (a_i)
            1'b0,
            1'b1: flag = b_i;
            default: flag = 1'b0;
        endcase
    end
endmodule

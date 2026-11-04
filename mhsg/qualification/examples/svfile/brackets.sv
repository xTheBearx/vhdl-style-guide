module brackets #(
    parameter int W = 4
)(
    input  logic [W-1:0] a_i,
    output logic [W-1:0] y_o
);
    typedef struct packed { logic x; } s_t;
    s_t s;
    assign y_o = ( a_i & { 2'b0, a_i[1:0] } ) | '{ default: 1'b0 };
    sub u_sub ( .a_i(a_i), .y_o() );
    always_comb begin
        foo(  // the arguments
            a_i
        );
        if ( a_i[0] ) begin
            $display( "x" );
        end
    end
endmodule

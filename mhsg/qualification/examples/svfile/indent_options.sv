module indent_options #(
        parameter int W = 8
) (
        input  logic         clk_i,
        // the data
        input  logic [W-1:0] d_i,
        output logic         q_o
);

    sub u_sub (
            .a(d_i),
            .y()
    );

    always_ff @(posedge clk_i)
        begin
            if (d_i[0])
                begin
                    q_o <= 1'b1;
                end
            else
                q_o <= 1'b0;
        end

endmodule

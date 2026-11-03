module structure;
    genvar g;
    defparam u_sub.Width = 2;
    always @* y = a;
    always @(*) begin
        y = a;
    end
    always @(posedge clk) q = d;
    always_comb begin
        y <= a; ;;
    end
    initial x = 1;
    begin : blk
    end
    generate
        if (Width > 1) begin
            assign z = 1;
        end
    endgenerate
    for (genvar i = 0; i < 2; i++) begin : loop
    end : other
    for (genvar i = 0; i < 2; i++) begin : gen_ok
    end
    always_ff @(posedge clk) begin : proc_q
        int k;
        for (int j = 0; j < 2; j++) begin
            q <= d;
        end
        k = 1;
        unique case (s)
            1: q <= 1;
        endcase
        case (s)
            1: q <= 1;
        endcase
        if (x) begin
            q <= 0;
        end else if (y) begin
            q <= 1;
        end
    end : proc_q
    always_comb begin
        a = 1; b = 2;
    end
    always_ff @(posedge clk) begin
    end : unnamed
endmodule

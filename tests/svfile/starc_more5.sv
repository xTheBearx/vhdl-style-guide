// Zähler
module starc_more5 (
    input  logic       clk_i,  // described
    input  logic       rst_i,  // described
    input  logic [1:0] state,  // described
    input  logic [3:0] addr,  // described
    output logic [7:0] y_o  // described
);
    logic [7:0] mem [16];
    logic q, r, ready, oe, bus, s, t;  // described
    assign #1 bus = (oe & q) ? r : 1'bz;
    always_ff @(posedge clk_i or negedge rst_i) begin
        if (!rst_i) q <= 1'b0;
        else begin
            q <= 1'b0;
            if (r) q <= 1'b1;
        end
    end
    always_ff @(posedge clk_i or negedge rst_i)
        if (!rst_i) ready <= 1'b1;
        else ready <= 1'b1;
    always_ff @(posedge clk_i or negedge rst_i)
        for (int i = 0; i < 8; i++)
            if (!rst_i) y_o[i] <= 1'b0;
            else y_o[i] <= mem[addr + 1][i];
    always_comb
        if (bus) s = 1'b1;
        else if (r) s = 1'b1;
        else if (bus) s = 1'b0;
        else s = 1'b0;
    always_comb t = q ? r + s : s - r + q;
    always_comb begin
        case (state)
            2'b00: r = 1'b1;
            default: r = 1'b0;
        endcase
    end
    task automatic send(input logic d, output logic done);
        #(1.5) done = d;
    endtask
    initial begin
        r <= 1'b0;
        $fdisplay(1, "%h", r);
    end
endmodule

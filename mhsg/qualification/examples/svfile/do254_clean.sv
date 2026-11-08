// Module: do254_clean
// Function: the code of do254.sv, written to pass the new DO-254 checks
// Author: mhsg tests
// Date: 2026-11-08
module do254_clean (
    input  logic       clk_i,   // clock
    input  logic       rst_ni,  // reset, active low
    input  logic       a_i,     // data
    input  logic [3:0] d_i,     // memory data
    output logic       q_o,     // registered data
    output logic       b_o,     // registered state
    output logic [3:0] c_o      // counter
);

    // Memory of four words, written each cycle
    logic [3:0] mem [4];
    logic [1:0] addr;
    // Busy flag, reset asynchronously
    logic busy;

    // The address counts with the memory writes
    always_ff @(posedge clk_i or negedge rst_ni) begin : p_addr
        if (!rst_ni) addr <= '0;
        else addr <= addr + 2'd1;
    end

    // A memory needs no reset
    always_ff @(posedge clk_i) begin : p_mem
        mem[addr] <= d_i;
    end

    // The registers of the module, reset as on every use of rst_ni
    always_ff @(posedge clk_i or negedge rst_ni) begin : p_regs
        if (!rst_ni) begin
            busy <= 1'b0;
            b_o  <= 1'b0;
            c_o  <= '0;
            q_o  <= 1'b0;
        end else begin
            busy <= a_i;
            b_o  <= busy;
            c_o  <= mem[addr];
            q_o  <= a_i;
        end
    end

endmodule

module fsm_user
    import fsm_pkg::*;
(
    input  logic clk_i,
    input  logic start_i,
    input  logic last_i,
    output logic busy_o
);
    // The type of the package by its bare name, imported
    state_e state_q, state_d;

    always_comb begin
        state_d = state_q;
        case (state_q)
            Idle:    if (start_i) state_d = Run;
            Run:     if (last_i) state_d = Done;
            Done:    state_d = Done;
            default: state_d = Idle;
        endcase
    end

    always_ff @(posedge clk_i) begin
        state_q <= state_d;
    end

    assign busy_o = state_q == Run;
endmodule

module fsm_qualified (
    input  logic clk_i,
    input  logic start_i,
    output logic busy_o
);
    // The type and the states written with their package
    fsm_pkg::state_e state_q, state_d;

    always_comb begin
        case (state_q)
            fsm_pkg::Idle:  state_d = start_i ? fsm_pkg::Run : fsm_pkg::Idle;
            fsm_pkg::Run:   state_d = fsm_pkg::Fault;
            fsm_pkg::Fault: state_d = fsm_pkg::Idle;
            default:        state_d = fsm_pkg::Idle;
        endcase
    end

    always_ff @(posedge clk_i) begin
        state_q <= state_d;
    end

    assign busy_o = state_q == fsm_pkg::Run;
endmodule

module fsm_sv (
    input  logic clk,
    input  logic rst,
    input  logic req,
    input  logic stop,
    output logic busy
);

    typedef enum logic [1:0] {S_IDLE, S_WORK, S_STUCK, S_NEVER} state_t;

    state_t state;
    logic [1:0] count;

    always_ff @(posedge clk) begin
        if (rst) begin
            state <= S_IDLE;
            count <= '0;
        end else begin
            case (state)
                S_IDLE: if (req) state <= S_WORK;
                S_WORK: begin
                    count <= count + 1;
                    if (stop) state <= S_STUCK;
                    else if (count == 2'd3) state <= S_IDLE;
                end
                S_STUCK: state <= S_STUCK;
                default: state <= S_IDLE;
            endcase
            if (count == 2'd3 && state == S_IDLE) state <= S_NEVER;
        end
    end

    assign busy = state != S_IDLE;

endmodule

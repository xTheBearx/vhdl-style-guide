// Assignment patterns over several lines; the last one is written on the line of its '{ and left alone
module patterns;
    localparam logic [7:0] Table [4] = '{
      8'h01,
          8'h02,
      8'h03,
      8'h04
      };
    always_comb begin
        cfg = '{
          mode: 2'b01,
          inner: '{
              x: 1,
            y: 2
          }
        };
    end
    assign q = '{
        a: 1,
        b: 2
    };
    assign r = '{a: 1,
                 b: 2};
endmodule

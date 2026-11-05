// Calls and randomize with over several lines; the call with arguments after its ( is left alone
class c;
    rand int a, b;
    function void f();
        if (!this.randomize() with {
            a < some_long_limit_value_a;
                b > some_long_limit_value_b;
        })
            $error("x");
        void'(this.randomize() with {
                a < some_long_limit_value_a;
          b > some_long_limit_value_b;
            });
        if (some_function_name(
            first_long_argument_name, second_long_argument_name
        )) begin
            a = 1;
        end
        result = some_function_name(first_long_argument_name, second_long_argument_name,
                                    third_long_argument_name);
    endfunction
endclass
module m;
    assign x = some_function_name(
            first_long_argument_name, second_long_argument_name
      );
endmodule

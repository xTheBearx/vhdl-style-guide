module inout_pad (
    inout  wire io,
    input  wire oe,
    input  wire d,
    output wire r
);
    assign io = oe ? d : 1'bz;
    // The input of the pad is read from the inout port directly
    assign r = io;
endmodule

module inout_wire_top (
    inout  wire pin,
    inout  wire pin_pad,
    input  wire a,
    input  wire oe,
    output wire pin_copy,
    output wire q
);
    assign pin_copy = pin;
    inout_pad u_pad (
        .io(pin_pad),
        .oe(oe),
        .d (a),
        .r (q)
    );
endmodule

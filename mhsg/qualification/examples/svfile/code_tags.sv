module code_tags (
    input  logic a,
    output logic b
);

/* mhsg_off */
      assign b = a;
/* mhsg_on */

/* mhsg_disable_next_line sv_indent_001 */
      logic c;
      logic d;

/* mhsg_off sv_indent_001 : legacy block */
      logic e;
/* mhsg_on sv_indent_001 */
      logic f;

endmodule

* ``global`` (clock_buffer): ``a_in``: clock; ``a_out``: clock, the same as a_in.
  Reference: Designing with low-level primitives, GLOBAL.
* ``altpll`` (clock_generator): ``inclk``: clock; ``clk``: clock, derived from inclk; ``areset``: asynchronous reset; ``locked``: async.
  Reference: ALTPLL user guide.
* ``altsyncram`` (dual_clock): ``aclr0``: asynchronous reset; ``aclr1``: asynchronous reset; ``clock0``: clock; ``address_a``: timed by clock0; ``data_a``: timed by clock0; ``wren_a``: timed by clock0; ``rden_a``: timed by clock0; ``byteena_a``: timed by clock0; ``addressstall_a``: timed by clock0; ``q_a``: timed by clock0; ``clocken0``: timed by clock0; ``clock1``: clock; ``address_b``: timed by clock1; ``data_b``: timed by clock1; ``wren_b``: timed by clock1; ``rden_b``: timed by clock1; ``byteena_b``: timed by clock1; ``addressstall_b``: timed by clock1; ``q_b``: timed by clock1; ``clocken1``: timed by clock1.
  When outdata_reg_b = CLOCK0: ``q_b``: timed by clock0.
  When outdata_reg_b = CLOCK1: ``q_b``: timed by clock1.
  When address_reg_b = CLOCK0: ``address_b``: timed by clock0; ``data_b``: timed by clock0; ``wren_b``: timed by clock0; ``rden_b``: timed by clock0; ``byteena_b``: timed by clock0; ``addressstall_b``: timed by clock0; ``q_b``: timed by clock0.
  Reference: Embedded memory user guide, altsyncram.
* ``dcfifo`` (dual_clock_fifo): ``aclr``: asynchronous reset; ``wrclk``: clock; ``data``: timed by wrclk; ``wrreq``: timed by wrclk; ``wrfull``: timed by wrclk; ``wrempty``: timed by wrclk; ``wrusedw``: timed by wrclk; ``rdclk``: clock; ``q``: timed by rdclk; ``rdreq``: timed by rdclk; ``rdempty``: timed by rdclk; ``rdfull``: timed by rdclk; ``rdusedw``: timed by rdclk.
  Reference: SCFIFO and DCFIFO IP cores user guide, DCFIFO.
* ``scfifo`` (single_clock): ``clock``: clock; ``aclr``: asynchronous reset; ``*``: timed by clock.
  Reference: SCFIFO and DCFIFO IP cores user guide, SCFIFO.
* ``altddio_in`` (single_clock): ``inclock``: clock; ``aclr``: asynchronous reset; ``*``: timed by inclock.
  Reference: ALTDDIO user guide, ALTDDIO_IN.
* ``altddio_out`` (single_clock): ``outclock``: clock; ``aclr``: asynchronous reset; ``*``: timed by outclock.
  Reference: ALTDDIO user guide, ALTDDIO_OUT.

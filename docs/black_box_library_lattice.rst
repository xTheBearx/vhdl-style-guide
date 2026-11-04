* ``DCCA`` (clock_buffer): ``CLKI``: clock; ``CLKO``: clock, the same as CLKI; ``CE``: enable of CLKO.
  Reference: FPGA libraries reference guide, DCCA.
* ``DCSC``: ``CLK0``: clock; ``CLK1``: clock; ``DCSOUT``: an independent clock; ``SEL0``: async; ``SEL1``: async; ``MODESEL``: async.
  Reference: FPGA libraries reference guide, DCSC.
* ``EHXPLLL`` (clock_generator): ``CLKFB``: clock; ``REFCLK``: clock, the same as CLKI; ``CLKINTFB``: clock, derived from CLKI; ``ENCLKOP``: enable of CLKOP; ``ENCLKOS``: enable of CLKOS; ``ENCLKOS2``: enable of CLKOS2; ``ENCLKOS3``: enable of CLKOS3; ``INTLOCK``: async; ``STDBY``: async; ``PLLWAKESYNC``: async; ``PHASE*``: async; ``CLKI``: clock; ``CLKOP``: clock, derived from CLKI; ``CLKOS``: clock, derived from CLKI; ``CLKOS2``: clock, derived from CLKI; ``CLKOS3``: clock, derived from CLKI; ``RST``: asynchronous reset; ``LOCK``: async.
  Reference: TN1263, EHXPLLL.
* ``OSCG``: ``OSC``: an independent clock.
  Reference: FPGA libraries reference guide, OSCG.
* ``IB`` (buffer): ``O``: follows I.
  Reference: FPGA libraries reference guide, IB.
* ``OB`` (buffer): ``O``: follows I.
  Reference: FPGA libraries reference guide, OB.
* ``OBZ`` (buffer): ``O``: follows I, T.
  Reference: FPGA libraries reference guide, OBZ.
* ``BB``: ``B``: follows I, T; ``O``: follows B.
  Reference: FPGA libraries reference guide, BB.
* ``IDDRX1F`` (single_clock): ``SCLK``: clock; ``RST``: asynchronous reset; ``*``: timed by SCLK.
  Reference: FPGA libraries reference guide, IDDRX1F.
* ``ODDRX1F`` (single_clock): ``SCLK``: clock; ``RST``: asynchronous reset; ``*``: timed by SCLK.
  Reference: FPGA libraries reference guide, ODDRX1F.
* ``FD1S3AX`` (single_clock): ``CK``: clock; ``*``: timed by CK.
  Reference: FPGA libraries reference guide, FD1S3AX.
* ``FD1P3AX`` (single_clock): ``CK``: clock; ``*``: timed by CK.
  Reference: FPGA libraries reference guide, FD1P3AX.
* ``FD1P3DX`` (single_clock): ``CK``: clock; ``CD``: asynchronous reset; ``*``: timed by CK.
  Reference: FPGA libraries reference guide, FD1P3DX.
* ``FD1P3BX`` (single_clock): ``CK``: clock; ``PD``: asynchronous reset; ``*``: timed by CK.
  Reference: FPGA libraries reference guide, FD1P3BX.
* ``FD1P3IX`` (single_clock): ``CK``: clock; ``*``: timed by CK.
  Reference: FPGA libraries reference guide, FD1P3IX.
* ``FD1P3JX`` (single_clock): ``CK``: clock; ``*``: timed by CK.
  Reference: FPGA libraries reference guide, FD1P3JX.
* ``DP16KD`` (dual_clock): ``CLKA``: clock; ``DIA*``: timed by CLKA; ``ADA*``: timed by CLKA; ``DOA*``: timed by CLKA; ``CEA``: timed by CLKA; ``OCEA``: timed by CLKA; ``WEA``: timed by CLKA; ``CSA*``: timed by CLKA; ``RSTA``: timed by CLKA; ``CLKB``: clock; ``DIB*``: timed by CLKB; ``ADB*``: timed by CLKB; ``DOB*``: timed by CLKB; ``CEB``: timed by CLKB; ``OCEB``: timed by CLKB; ``WEB``: timed by CLKB; ``CSB*``: timed by CLKB; ``RSTB``: timed by CLKB.
  When resetmode = ASYNC: ``RSTA``: asynchronous reset; ``RSTB``: asynchronous reset.
  Reference: TN1264, DP16KD.
* ``PDPW16KD`` (dual_clock): ``CLKW``: clock; ``DI*``: timed by CLKW; ``ADW*``: timed by CLKW; ``BE*``: timed by CLKW; ``CEW``: timed by CLKW; ``CSW*``: timed by CLKW; ``CLKR``: clock; ``DO*``: timed by CLKR; ``ADR*``: timed by CLKR; ``CER``: timed by CLKR; ``OCER``: timed by CLKR; ``CSR*``: timed by CLKR; ``RST``: timed by CLKR.
  When resetmode = ASYNC: ``RST``: asynchronous reset.
  Reference: TN1264, PDPW16KD.
* ``GSR``: ``GSR``: asynchronous reset.
  Reference: FPGA libraries reference guide, GSR.
* ``SB_GB`` (clock_buffer): ``USER_SIGNAL_TO_GLOBAL_BUFFER``: clock; ``GLOBAL_BUFFER_OUTPUT``: clock, the same as USER_SIGNAL_TO_GLOBAL_BUFFER.
  Reference: iCE40 technology library, SB_GB.
* ``SB_GB_IO``: ``PACKAGE_PIN``: clock; ``GLOBAL_BUFFER_OUTPUT``: clock, the same as PACKAGE_PIN; ``INPUT_CLK``: clock; ``OUTPUT_CLK``: clock.
  Reference: iCE40 technology library, SB_GB_IO.
* ``SB_PLL40_CORE`` (clock_generator): ``EXTFEEDBACK``: clock; ``BYPASS``: async; ``DYNAMICDELAY``: async; ``LATCHINPUTVALUE``: async; ``SCLK``: clock; ``SDI``: timed by SCLK; ``SDO``: timed by SCLK; ``REFERENCECLK``: clock; ``PLLOUTCORE``: clock, derived from REFERENCECLK; ``PLLOUTGLOBAL``: clock, derived from REFERENCECLK; ``RESETB``: asynchronous reset; ``LOCK``: async.
  Reference: iCE40 technology library, SB_PLL40_CORE.
* ``SB_PLL40_PAD`` (clock_generator): ``EXTFEEDBACK``: clock; ``BYPASS``: async; ``DYNAMICDELAY``: async; ``LATCHINPUTVALUE``: async; ``SCLK``: clock; ``SDI``: timed by SCLK; ``SDO``: timed by SCLK; ``PACKAGEPIN``: clock; ``PLLOUTCORE``: clock, derived from PACKAGEPIN; ``PLLOUTGLOBAL``: clock, derived from PACKAGEPIN; ``RESETB``: asynchronous reset; ``LOCK``: async.
  Reference: iCE40 technology library, SB_PLL40_PAD.
* ``SB_HFOSC``: ``CLKHF``: an independent clock; ``CLKHFEN``: async; ``CLKHFPU``: async; ``TRIM*``: async.
  Reference: iCE40 technology library, SB_HFOSC.
* ``SB_LFOSC``: ``CLKLF``: an independent clock; ``CLKLFEN``: async; ``CLKLFPU``: async.
  Reference: iCE40 technology library, SB_LFOSC.
* ``SB_RAM40_4K`` (dual_clock): ``WCLK``: clock; ``WADDR``: timed by WCLK; ``WDATA``: timed by WCLK; ``WE``: timed by WCLK; ``WCLKE``: timed by WCLK; ``MASK``: timed by WCLK; ``RCLK``: clock; ``RADDR``: timed by RCLK; ``RDATA``: timed by RCLK; ``RE``: timed by RCLK; ``RCLKE``: timed by RCLK.
  Reference: iCE40 technology library, SB_RAM40_4K.
* ``SB_DFF`` (single_clock): ``C``: clock; ``*``: timed by C.
  Reference: iCE40 technology library, SB_DFF.
* ``SB_DFFE`` (single_clock): ``C``: clock; ``*``: timed by C.
  Reference: iCE40 technology library, SB_DFFE.
* ``SB_DFFSR`` (single_clock): ``C``: clock; ``*``: timed by C.
  Reference: iCE40 technology library, SB_DFFSR.
* ``SB_DFFSS`` (single_clock): ``C``: clock; ``*``: timed by C.
  Reference: iCE40 technology library, SB_DFFSS.
* ``SB_DFFESR`` (single_clock): ``C``: clock; ``*``: timed by C.
  Reference: iCE40 technology library, SB_DFFESR.
* ``SB_DFFESS`` (single_clock): ``C``: clock; ``*``: timed by C.
  Reference: iCE40 technology library, SB_DFFESS.
* ``SB_DFFR`` (single_clock): ``C``: clock; ``R``: asynchronous reset; ``*``: timed by C.
  Reference: iCE40 technology library, SB_DFFR.
* ``SB_DFFS`` (single_clock): ``C``: clock; ``S``: asynchronous reset; ``*``: timed by C.
  Reference: iCE40 technology library, SB_DFFS.
* ``SB_DFFER`` (single_clock): ``C``: clock; ``R``: asynchronous reset; ``*``: timed by C.
  Reference: iCE40 technology library, SB_DFFER.
* ``SB_DFFES`` (single_clock): ``C``: clock; ``S``: asynchronous reset; ``*``: timed by C.
  Reference: iCE40 technology library, SB_DFFES.

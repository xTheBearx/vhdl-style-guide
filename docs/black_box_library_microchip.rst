* ``CLKINT`` (clock_buffer): ``A``: clock; ``Y``: clock, the same as A.
  Reference: Macro library guide, CLKINT.
* ``CLKINT_PRESERVE`` (clock_buffer): ``A``: clock; ``Y``: clock, the same as A.
  Reference: Macro library guide, CLKINT_PRESERVE.
* ``RCLKINT`` (clock_buffer): ``A``: clock; ``Y``: clock, the same as A.
  Reference: Macro library guide, RCLKINT.
* ``RCLKINT_PRESERVE`` (clock_buffer): ``A``: clock; ``Y``: clock, the same as A.
  Reference: Macro library guide, RCLKINT_PRESERVE.
* ``GCLKINT`` (clock_buffer): ``A``: clock; ``Y``: clock, the same as A; ``EN``: enable of Y.
  Reference: Macro library guide, GCLKINT.
* ``RGCLKINT`` (clock_buffer): ``A``: clock; ``Y``: clock, the same as A; ``EN``: enable of Y.
  Reference: Macro library guide, RGCLKINT.
* ``CLKBUF`` (clock_buffer): ``PAD``: clock; ``Y``: clock, the same as PAD.
  Reference: Macro library guide, CLKBUF.
* ``CLKBUF_DIFF``: ``PADP``: clock; ``PADN``: unused; ``Y``: clock, the same as PADP.
  Reference: Macro library guide, CLKBUF_DIFF.
* ``INBUF`` (buffer): ``Y``: follows PAD.
  Reference: Macro library guide, INBUF.
* ``INBUF_DIFF``: ``Y``: follows PADP, PADN.
  Reference: Macro library guide, INBUF_DIFF.
* ``OUTBUF`` (buffer): ``PAD``: follows D.
  Reference: Macro library guide, OUTBUF.
* ``OUTBUF_DIFF``: ``PADP``: follows D; ``PADN``: follows D.
  Reference: Macro library guide, OUTBUF_DIFF.
* ``TRIBUFF``: ``PAD``: follows D, E.
  Reference: Macro library guide, TRIBUFF.
* ``BIBUF``: ``PAD``: follows D, E; ``Y``: follows PAD.
  Reference: Macro library guide, BIBUF.
* ``BIBUF_DIFF``: ``PADP``: follows D, E; ``PADN``: follows D, E; ``Y``: follows PADP, PADN.
  Reference: Macro library guide, BIBUF_DIFF.
* ``SLE``: ``CLK``: clock; ``D``: timed by CLK; ``EN``: timed by CLK; ``SLn``: timed by CLK; ``SD``: timed by CLK; ``Q``: timed by CLK; ``ALn``: asynchronous reset; ``ADn``: async.
  Reference: Macro library guide, SLE.
* ``RAM1K18`` (dual_clock): ``A_ARST_N``: asynchronous reset; ``B_ARST_N``: asynchronous reset; ``A_DOUT_ARST_N``: asynchronous reset; ``B_DOUT_ARST_N``: asynchronous reset; ``A_CLK``: clock; ``A_*``: timed by A_CLK; ``B_CLK``: clock; ``B_*``: timed by B_CLK.
  Reference: SmartFusion2 and IGLOO2 macro library guide, RAM1K18.
* ``RAM1K20`` (dual_clock): ``A_ARST_N``: asynchronous reset; ``B_ARST_N``: asynchronous reset; ``A_DOUT_ARST_N``: asynchronous reset; ``B_DOUT_ARST_N``: asynchronous reset; ``A_CLK``: clock; ``A_*``: timed by A_CLK; ``B_CLK``: clock; ``B_*``: timed by B_CLK.
  Reference: PolarFire macro library guide, RAM1K20.
* ``PF_CCC_*``: ``REF_CLK_*``: clock; ``OUT*_FABCLK_*``: clock, derived from REF_CLK_0; ``PLL_LOCK_*``: async; ``PLL_POWERDOWN_N_*``: async.
  Reference: PolarFire clocking resources user guide, PF_CCC.
* ``PF_OSC_*``: ``RCOSC_*``: an independent clock.
  Reference: PolarFire clocking resources user guide, PF_OSC.
* ``PF_INIT_MONITOR_*`` (async_input): ``*``: async.
  Reference: PolarFire FPGA power-up and resets user guide, PF_INIT_MONITOR.
* ``CORERESET_PF_*``: ``CLK``: clock; ``FABRIC_RESET_N``: reset released synchronously to CLK; ``*``: async.
  Reference: CoreReset_PF handbook.
* ``RAM64x12`` (dual_clock): ``R_ADDR_AL_N``: asynchronous reset; ``R_DATA_AL_N``: asynchronous reset; ``W_CLK``: clock; ``W_EN``: timed by W_CLK; ``W_ADDR``: timed by W_CLK; ``W_DATA``: timed by W_CLK; ``BLK_EN``: timed by W_CLK; ``R_CLK``: clock; ``R_ADDR``: timed by R_CLK; ``R_ADDR_EN``: timed by R_CLK; ``R_ADDR_SL_N``: timed by R_CLK; ``R_ADDR_SD``: timed by R_CLK; ``R_DATA``: timed by R_CLK; ``R_DATA_EN``: timed by R_CLK; ``R_DATA_SL_N``: timed by R_CLK; ``R_DATA_SD``: timed by R_CLK.
  Reference: PolarFire family FPGA macro library guide, RAM64x12.
* ``MACC_PA`` (single_clock): ``CLK``: clock; ``AL_N``: asynchronous reset; ``*``: timed by CLK.
  Reference: PolarFire family FPGA macro library guide, MACC_PA.
* ``SYSRESET``: ``DEVRST_N``: async; ``POWER_ON_RESET_N``: async.
  Reference: SmartFusion2 and IGLOO2 macro library guide, SYSRESET.

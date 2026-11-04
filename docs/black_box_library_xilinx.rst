* ``BUFG`` (clock_buffer): ``I``: clock; ``O``: clock, the same as I.
  Reference: UG953/UG974, BUFG.
* ``BUFGCE`` (clock_buffer): ``I``: clock; ``O``: clock, the same as I; ``CE``: enable of O.
  Reference: UG953/UG974, BUFGCE.
* ``BUFGCE_1`` (clock_buffer): ``I``: clock; ``O``: clock, the same as I; ``CE``: enable of O.
  Reference: UG953, BUFGCE_1.
* ``BUFH`` (clock_buffer): ``I``: clock; ``O``: clock, the same as I.
  Reference: UG953, BUFH.
* ``BUFHCE`` (clock_buffer): ``I``: clock; ``O``: clock, the same as I; ``CE``: enable of O.
  Reference: UG953, BUFHCE.
* ``BUFIO`` (clock_buffer): ``I``: clock; ``O``: clock, the same as I.
  Reference: UG953, BUFIO.
* ``BUFMR`` (clock_buffer): ``I``: clock; ``O``: clock, the same as I.
  Reference: UG953, BUFMR.
* ``BUFMRCE`` (clock_buffer): ``I``: clock; ``O``: clock, the same as I; ``CE``: enable of O.
  Reference: UG953, BUFMRCE.
* ``BUFR``: ``I``: clock; ``O``: clock, derived from I; ``CE``: async; ``CLR``: asynchronous reset.
  Reference: UG953, BUFR.
* ``BUFGCE_DIV``: ``I``: clock; ``O``: clock, derived from I; ``CE``: enable of O; ``CLR``: asynchronous reset.
  Reference: UG974, BUFGCE_DIV.
* ``BUFG_GT``: ``I``: clock; ``O``: clock, derived from I; ``CE``: async; ``CEMASK``: async; ``CLR``: asynchronous reset; ``CLRMASK``: async; ``DIV``: async.
  Reference: UG974, BUFG_GT.
* ``BUFG_GT_SYNC``: ``CLK``: clock; ``CE``: async; ``CLR``: asynchronous reset; ``CESYNC``: timed by CLK; ``CLRSYNC``: timed by CLK.
  Reference: UG974, BUFG_GT_SYNC.
* ``BUFGMUX``: ``I0``: clock; ``I1``: clock; ``O``: an independent clock; ``S``: async.
  Reference: UG953/UG974, BUFGMUX.
* ``BUFGMUX_CTRL``: ``I0``: clock; ``I1``: clock; ``O``: an independent clock; ``S``: async.
  Reference: UG953/UG974, BUFGMUX_CTRL.
* ``BUFGCTRL``: ``I0``: clock; ``I1``: clock; ``O``: an independent clock; ``CE0``: async; ``CE1``: async; ``S0``: async; ``S1``: async; ``IGNORE0``: async; ``IGNORE1``: async.
  Reference: UG953/UG974, BUFGCTRL.
* ``IBUF`` (buffer): ``O``: follows I.
  Reference: UG953/UG974, IBUF.
* ``IBUFG`` (buffer): ``O``: follows I.
  Reference: UG953, IBUFG.
* ``IBUF_IBUFDISABLE``: ``O``: follows I, IBUFDISABLE.
  Reference: UG953, IBUF_IBUFDISABLE.
* ``IBUFDS``: ``O``: follows I, IB.
  Reference: UG953/UG974, IBUFDS.
* ``IBUFGDS``: ``O``: follows I, IB.
  Reference: UG953, IBUFGDS.
* ``IBUFDS_DIFF_OUT``: ``O``: follows I, IB; ``OB``: follows I, IB.
  Reference: UG953/UG974, IBUFDS_DIFF_OUT.
* ``IBUFDS_GTE2``: ``I``: clock; ``IB``: unused; ``O``: clock, the same as I; ``ODIV2``: clock, derived from I; ``CEB``: async.
  Reference: UG953, IBUFDS_GTE2.
* ``IBUFDS_GTE3``: ``I``: clock; ``IB``: unused; ``O``: clock, the same as I; ``ODIV2``: clock, derived from I; ``CEB``: async.
  Reference: UG974, IBUFDS_GTE3.
* ``IBUFDS_GTE4``: ``I``: clock; ``IB``: unused; ``O``: clock, the same as I; ``ODIV2``: clock, derived from I; ``CEB``: async.
  Reference: UG974, IBUFDS_GTE4.
* ``OBUF`` (buffer): ``O``: follows I.
  Reference: UG953/UG974, OBUF.
* ``OBUFT``: ``O``: follows I, T.
  Reference: UG953/UG974, OBUFT.
* ``OBUFDS``: ``O``: follows I; ``OB``: follows I.
  Reference: UG953/UG974, OBUFDS.
* ``OBUFTDS``: ``O``: follows I, T; ``OB``: follows I, T.
  Reference: UG953/UG974, OBUFTDS.
* ``IOBUF``: ``IO``: follows I, T; ``O``: follows IO.
  Reference: UG953/UG974, IOBUF.
* ``IOBUFDS``: ``IO``: follows I, T; ``IOB``: follows I, T; ``O``: follows IO, IOB.
  Reference: UG953/UG974, IOBUFDS.
* ``MMCME2_*``: ``CLKIN1``: clock; ``CLKIN2``: clock; ``CLKFBIN``: clock; ``CLKOUT*``: clock, derived from CLKIN1; ``CLKFBOUT*``: clock, derived from CLKIN1; ``LOCKED``: async; ``CLKINSTOPPED``: async; ``CLKFBSTOPPED``: async; ``RST``: asynchronous reset; ``PWRDWN``: async; ``CLKINSEL``: async; ``DCLK``: clock; ``DADDR``: timed by DCLK; ``DI``: timed by DCLK; ``DEN``: timed by DCLK; ``DWE``: timed by DCLK; ``DO``: timed by DCLK; ``DRDY``: timed by DCLK; ``PSCLK``: clock; ``PSEN``: timed by PSCLK; ``PSINCDEC``: timed by PSCLK; ``PSDONE``: timed by PSCLK.
  Reference: UG953, MMCME2_BASE and MMCME2_ADV.
* ``MMCME3_*``: ``CLKIN1``: clock; ``CLKIN2``: clock; ``CLKFBIN``: clock; ``CLKOUT*``: clock, derived from CLKIN1; ``CLKFBOUT*``: clock, derived from CLKIN1; ``LOCKED``: async; ``CLKINSTOPPED``: async; ``CLKFBSTOPPED``: async; ``RST``: asynchronous reset; ``PWRDWN``: async; ``CLKINSEL``: async; ``DCLK``: clock; ``DADDR``: timed by DCLK; ``DI``: timed by DCLK; ``DEN``: timed by DCLK; ``DWE``: timed by DCLK; ``DO``: timed by DCLK; ``DRDY``: timed by DCLK; ``PSCLK``: clock; ``PSEN``: timed by PSCLK; ``PSINCDEC``: timed by PSCLK; ``PSDONE``: timed by PSCLK; ``CDDCREQ``: async; ``CDDCDONE``: async.
  Reference: UG974, MMCME3_BASE and MMCME3_ADV.
* ``MMCME4_*``: ``CLKIN1``: clock; ``CLKIN2``: clock; ``CLKFBIN``: clock; ``CLKOUT*``: clock, derived from CLKIN1; ``CLKFBOUT*``: clock, derived from CLKIN1; ``LOCKED``: async; ``CLKINSTOPPED``: async; ``CLKFBSTOPPED``: async; ``RST``: asynchronous reset; ``PWRDWN``: async; ``CLKINSEL``: async; ``DCLK``: clock; ``DADDR``: timed by DCLK; ``DI``: timed by DCLK; ``DEN``: timed by DCLK; ``DWE``: timed by DCLK; ``DO``: timed by DCLK; ``DRDY``: timed by DCLK; ``PSCLK``: clock; ``PSEN``: timed by PSCLK; ``PSINCDEC``: timed by PSCLK; ``PSDONE``: timed by PSCLK; ``CDDCREQ``: async; ``CDDCDONE``: async.
  Reference: UG974, MMCME4_BASE and MMCME4_ADV.
* ``PLLE2_*``: ``CLKIN1``: clock; ``CLKIN2``: clock; ``CLKFBIN``: clock; ``CLKOUT*``: clock, derived from CLKIN1; ``CLKFBOUT*``: clock, derived from CLKIN1; ``LOCKED``: async; ``CLKINSTOPPED``: async; ``CLKFBSTOPPED``: async; ``RST``: asynchronous reset; ``PWRDWN``: async; ``CLKINSEL``: async; ``DCLK``: clock; ``DADDR``: timed by DCLK; ``DI``: timed by DCLK; ``DEN``: timed by DCLK; ``DWE``: timed by DCLK; ``DO``: timed by DCLK; ``DRDY``: timed by DCLK; ``PSCLK``: clock; ``PSEN``: timed by PSCLK; ``PSINCDEC``: timed by PSCLK; ``PSDONE``: timed by PSCLK.
  Reference: UG953, PLLE2_BASE and PLLE2_ADV.
* ``PLLE3_*``: ``CLKIN``: clock; ``CLKFBIN``: clock; ``CLKOUT*``: clock, derived from CLKIN; ``CLKFBOUT``: clock, derived from CLKIN; ``LOCKED``: async; ``RST``: asynchronous reset; ``PWRDWN``: async; ``CLKOUTPHYEN``: async; ``DCLK``: clock; ``DADDR``: timed by DCLK; ``DI``: timed by DCLK; ``DEN``: timed by DCLK; ``DWE``: timed by DCLK; ``DO``: timed by DCLK; ``DRDY``: timed by DCLK.
  Reference: UG974, PLLE3_BASE and PLLE3_ADV.
* ``PLLE4_*``: ``CLKIN``: clock; ``CLKFBIN``: clock; ``CLKOUT*``: clock, derived from CLKIN; ``CLKFBOUT``: clock, derived from CLKIN; ``LOCKED``: async; ``RST``: asynchronous reset; ``PWRDWN``: async; ``CLKOUTPHYEN``: async; ``DCLK``: clock; ``DADDR``: timed by DCLK; ``DI``: timed by DCLK; ``DEN``: timed by DCLK; ``DWE``: timed by DCLK; ``DO``: timed by DCLK; ``DRDY``: timed by DCLK.
  Reference: UG974, PLLE4_BASE and PLLE4_ADV.
* ``FDRE`` (single_clock): ``C``: clock; ``*``: timed by C.
  Reference: UG953/UG974, FDRE.
* ``FDSE`` (single_clock): ``C``: clock; ``*``: timed by C.
  Reference: UG953/UG974, FDSE.
* ``FDCE`` (single_clock): ``C``: clock; ``CLR``: asynchronous reset; ``*``: timed by C.
  Reference: UG953/UG974, FDCE.
* ``FDPE`` (single_clock): ``C``: clock; ``PRE``: asynchronous reset; ``*``: timed by C.
  Reference: UG953/UG974, FDPE.
* ``SRL16E`` (single_clock): ``CLK``: clock; ``*``: timed by CLK.
  Reference: UG953/UG974, SRL16E.
* ``SRLC16E`` (single_clock): ``CLK``: clock; ``*``: timed by CLK.
  Reference: UG953, SRLC16E.
* ``SRLC32E`` (single_clock): ``CLK``: clock; ``*``: timed by CLK.
  Reference: UG953/UG974, SRLC32E.
* ``DSP48E1`` (single_clock): ``CLK``: clock; ``*``: timed by CLK.
  Reference: UG953, DSP48E1.
* ``DSP48E2`` (single_clock): ``CLK``: clock; ``*``: timed by CLK.
  Reference: UG974, DSP48E2.
* ``IDDR``: ``C``: clock; ``D``: timed by C; ``CE``: timed by C; ``Q1``: timed by C; ``Q2``: timed by C; ``R``: timed by C; ``S``: timed by C.
  When srtype = ASYNC: ``R``: asynchronous reset; ``S``: asynchronous reset.
  Reference: UG953, IDDR.
* ``ODDR``: ``C``: clock; ``D1``: timed by C; ``D2``: timed by C; ``CE``: timed by C; ``Q``: timed by C; ``R``: timed by C; ``S``: timed by C.
  When srtype = ASYNC: ``R``: asynchronous reset; ``S``: asynchronous reset.
  Reference: UG953, ODDR.
* ``IDDRE1``: ``C``: clock; ``CB``: clock; ``D``: timed by C; ``Q1``: timed by C; ``Q2``: timed by C; ``R``: asynchronous reset.
  Reference: UG974, IDDRE1.
* ``ODDRE1``: ``C``: clock; ``D1``: timed by C; ``D2``: timed by C; ``Q``: timed by C; ``SR``: asynchronous reset.
  Reference: UG974, ODDRE1.
* ``IDELAYE2``: ``C``: clock; ``DATAOUT``: follows IDATAIN, DATAIN; ``CE``: timed by C; ``INC``: timed by C; ``LD``: timed by C; ``LDPIPEEN``: timed by C; ``CNTVALUEIN``: timed by C; ``CNTVALUEOUT``: timed by C; ``REGRST``: timed by C; ``CINVCTRL``: timed by C.
  Reference: UG953, IDELAYE2.
* ``ODELAYE2``: ``C``: clock; ``DATAOUT``: follows ODATAIN, CLKIN; ``CE``: timed by C; ``INC``: timed by C; ``LD``: timed by C; ``LDPIPEEN``: timed by C; ``CNTVALUEIN``: timed by C; ``CNTVALUEOUT``: timed by C; ``REGRST``: timed by C; ``CINVCTRL``: timed by C.
  Reference: UG953, ODELAYE2.
* ``IDELAYE3``: ``CLK``: clock; ``DATAOUT``: follows IDATAIN, DATAIN; ``CE``: timed by CLK; ``INC``: timed by CLK; ``LOAD``: timed by CLK; ``CNTVALUEIN``: timed by CLK; ``CNTVALUEOUT``: timed by CLK; ``EN_VTC``: timed by CLK; ``RST``: asynchronous reset.
  Reference: UG974, IDELAYE3.
* ``ODELAYE3``: ``CLK``: clock; ``DATAOUT``: follows ODATAIN; ``CE``: timed by CLK; ``INC``: timed by CLK; ``LOAD``: timed by CLK; ``CNTVALUEIN``: timed by CLK; ``CNTVALUEOUT``: timed by CLK; ``EN_VTC``: timed by CLK; ``RST``: asynchronous reset.
  Reference: UG974, ODELAYE3.
* ``IDELAYCTRL``: ``REFCLK``: clock; ``RST``: asynchronous reset; ``RDY``: async.
  Reference: UG953/UG974, IDELAYCTRL.
* ``ISERDESE2``: ``CLK``: clock; ``CLKB``: clock; ``CLKDIV``: clock; ``CLKDIVP``: clock; ``OCLK``: clock; ``OCLKB``: clock; ``D``: timed by CLK; ``DDLY``: timed by CLK; ``Q*``: timed by CLKDIV; ``BITSLIP``: timed by CLKDIV; ``CE1``: timed by CLKDIV; ``CE2``: timed by CLKDIV; ``RST``: asynchronous reset; ``O``: follows D.
  Reference: UG953, ISERDESE2.
* ``OSERDESE2``: ``CLK``: clock; ``CLKDIV``: clock; ``D*``: timed by CLKDIV; ``T[1-4]``: timed by CLKDIV; ``OCE``: timed by CLK; ``TCE``: timed by CLK; ``OQ``: timed by CLK; ``TQ``: timed by CLK; ``OFB``: timed by CLK; ``TFB``: timed by CLK; ``RST``: asynchronous reset.
  Reference: UG953, OSERDESE2.
* ``ISERDESE3``: ``CLK``: clock; ``CLK_B``: clock; ``CLKDIV``: clock; ``FIFO_RD_CLK``: clock; ``D``: timed by CLK; ``Q``: timed by CLKDIV; ``FIFO_RD_EN``: timed by FIFO_RD_CLK; ``FIFO_EMPTY``: timed by FIFO_RD_CLK; ``INTERNAL_DIVCLK``: clock, derived from CLK; ``RST``: asynchronous reset.
  When fifo_enable = TRUE: ``Q``: timed by FIFO_RD_CLK.
  Reference: UG974, ISERDESE3.
* ``OSERDESE3``: ``CLK``: clock; ``CLKDIV``: clock; ``D``: timed by CLKDIV; ``T``: timed by CLKDIV; ``OQ``: timed by CLK; ``T_OUT``: follows T; ``RST``: asynchronous reset.
  Reference: UG974, OSERDESE3.
* ``RAMB18E1`` (dual_clock): ``CLKARDCLK``: clock; ``ADDRARDADDR``: timed by CLKARDCLK; ``DIADI``: timed by CLKARDCLK; ``DIPADIP``: timed by CLKARDCLK; ``DOADO``: timed by CLKARDCLK; ``DOPADOP``: timed by CLKARDCLK; ``ENARDEN``: timed by CLKARDCLK; ``REGCEAREGCE``: timed by CLKARDCLK; ``RSTRAMARSTRAM``: timed by CLKARDCLK; ``RSTREGARSTREG``: timed by CLKARDCLK; ``WEA``: timed by CLKARDCLK; ``CLKBWRCLK``: clock; ``ADDRBWRADDR``: timed by CLKBWRCLK; ``DIBDI``: timed by CLKBWRCLK; ``DIPBDIP``: timed by CLKBWRCLK; ``DOBDO``: timed by CLKBWRCLK; ``DOPBDOP``: timed by CLKBWRCLK; ``ENBWREN``: timed by CLKBWRCLK; ``REGCEB``: timed by CLKBWRCLK; ``RSTRAMB``: timed by CLKBWRCLK; ``RSTREGB``: timed by CLKBWRCLK; ``WEBWE``: timed by CLKBWRCLK.
  Reference: UG953, RAMB18E1.
* ``RAMB36E1`` (dual_clock): ``DBITERR``: timed by CLKARDCLK; ``SBITERR``: timed by CLKARDCLK; ``RDADDRECC``: timed by CLKARDCLK; ``ECCPARITY``: timed by CLKBWRCLK; ``INJECTDBITERR``: timed by CLKBWRCLK; ``INJECTSBITERR``: timed by CLKBWRCLK; ``CASCADEINA``: timed by CLKARDCLK; ``CASCADEOUTA``: timed by CLKARDCLK; ``CASCADEINB``: timed by CLKBWRCLK; ``CASCADEOUTB``: timed by CLKBWRCLK; ``CLKARDCLK``: clock; ``ADDRARDADDR``: timed by CLKARDCLK; ``DIADI``: timed by CLKARDCLK; ``DIPADIP``: timed by CLKARDCLK; ``DOADO``: timed by CLKARDCLK; ``DOPADOP``: timed by CLKARDCLK; ``ENARDEN``: timed by CLKARDCLK; ``REGCEAREGCE``: timed by CLKARDCLK; ``RSTRAMARSTRAM``: timed by CLKARDCLK; ``RSTREGARSTREG``: timed by CLKARDCLK; ``WEA``: timed by CLKARDCLK; ``CLKBWRCLK``: clock; ``ADDRBWRADDR``: timed by CLKBWRCLK; ``DIBDI``: timed by CLKBWRCLK; ``DIPBDIP``: timed by CLKBWRCLK; ``DOBDO``: timed by CLKBWRCLK; ``DOPBDOP``: timed by CLKBWRCLK; ``ENBWREN``: timed by CLKBWRCLK; ``REGCEB``: timed by CLKBWRCLK; ``RSTRAMB``: timed by CLKBWRCLK; ``RSTREGB``: timed by CLKBWRCLK; ``WEBWE``: timed by CLKBWRCLK.
  Reference: UG953, RAMB36E1.
* ``RAMB18E2`` (dual_clock): ``CAS*A``: timed by CLKARDCLK; ``CAS*_A``: timed by CLKARDCLK; ``CAS*B``: timed by CLKBWRCLK; ``CAS*_B``: timed by CLKBWRCLK; ``CLKARDCLK``: clock; ``ADDRARDADDR``: timed by CLKARDCLK; ``ADDRENA``: timed by CLKARDCLK; ``DINADIN``: timed by CLKARDCLK; ``DINPADINP``: timed by CLKARDCLK; ``DOUTADOUT``: timed by CLKARDCLK; ``DOUTPADOUTP``: timed by CLKARDCLK; ``ENARDEN``: timed by CLKARDCLK; ``REGCEAREGCE``: timed by CLKARDCLK; ``RSTRAMARSTRAM``: timed by CLKARDCLK; ``RSTREGARSTREG``: timed by CLKARDCLK; ``WEA``: timed by CLKARDCLK; ``CLKBWRCLK``: clock; ``ADDRBWRADDR``: timed by CLKBWRCLK; ``ADDRENB``: timed by CLKBWRCLK; ``DINBDIN``: timed by CLKBWRCLK; ``DINPBDINP``: timed by CLKBWRCLK; ``DOUTBDOUT``: timed by CLKBWRCLK; ``DOUTPBDOUTP``: timed by CLKBWRCLK; ``ENBWREN``: timed by CLKBWRCLK; ``REGCEB``: timed by CLKBWRCLK; ``RSTRAMB``: timed by CLKBWRCLK; ``RSTREGB``: timed by CLKBWRCLK; ``WEBWE``: timed by CLKBWRCLK.
  Reference: UG974, RAMB18E2.
* ``RAMB36E2`` (dual_clock): ``DBITERR``: timed by CLKARDCLK; ``SBITERR``: timed by CLKARDCLK; ``RDADDRECC``: timed by CLKARDCLK; ``ECCPIPECE``: timed by CLKARDCLK; ``CASINDBITERR``: timed by CLKARDCLK; ``CASINSBITERR``: timed by CLKARDCLK; ``CASOUTDBITERR``: timed by CLKARDCLK; ``CASOUTSBITERR``: timed by CLKARDCLK; ``ECCPARITY``: timed by CLKBWRCLK; ``INJECTDBITERR``: timed by CLKBWRCLK; ``INJECTSBITERR``: timed by CLKBWRCLK; ``CAS*A``: timed by CLKARDCLK; ``CAS*_A``: timed by CLKARDCLK; ``CAS*B``: timed by CLKBWRCLK; ``CAS*_B``: timed by CLKBWRCLK; ``CLKARDCLK``: clock; ``ADDRARDADDR``: timed by CLKARDCLK; ``ADDRENA``: timed by CLKARDCLK; ``DINADIN``: timed by CLKARDCLK; ``DINPADINP``: timed by CLKARDCLK; ``DOUTADOUT``: timed by CLKARDCLK; ``DOUTPADOUTP``: timed by CLKARDCLK; ``ENARDEN``: timed by CLKARDCLK; ``REGCEAREGCE``: timed by CLKARDCLK; ``RSTRAMARSTRAM``: timed by CLKARDCLK; ``RSTREGARSTREG``: timed by CLKARDCLK; ``WEA``: timed by CLKARDCLK; ``CLKBWRCLK``: clock; ``ADDRBWRADDR``: timed by CLKBWRCLK; ``ADDRENB``: timed by CLKBWRCLK; ``DINBDIN``: timed by CLKBWRCLK; ``DINPBDINP``: timed by CLKBWRCLK; ``DOUTBDOUT``: timed by CLKBWRCLK; ``DOUTPBDOUTP``: timed by CLKBWRCLK; ``ENBWREN``: timed by CLKBWRCLK; ``REGCEB``: timed by CLKBWRCLK; ``RSTRAMB``: timed by CLKBWRCLK; ``RSTREGB``: timed by CLKBWRCLK; ``WEBWE``: timed by CLKBWRCLK.
  Reference: UG974, RAMB36E2.
* ``STARTUPE2``: ``CFGCLK``: an independent clock; ``CFGMCLK``: an independent clock; ``CLK``: clock; ``*``: async.
  Reference: UG953, STARTUPE2.
* ``STARTUPE3``: ``CFGCLK``: an independent clock; ``CFGMCLK``: an independent clock; ``*``: async.
  Reference: UG974, STARTUPE3.
* ``ICAPE2`` (single_clock): ``CLK``: clock; ``*``: timed by CLK.
  Reference: UG953, ICAPE2.
* ``ICAPE3`` (single_clock): ``CLK``: clock; ``*``: timed by CLK.
  Reference: UG974, ICAPE3.
* ``xpm_cdc_single`` (synchronizer): ``src_clk``: clock; ``src_in``: timed by src_clk; ``dest_clk``: clock; ``dest_out``: src_in synchronized to dest_clk, DEST_SYNC_FF stages (manual review).
  Reference: UG974, XPM_CDC_SINGLE.
* ``xpm_cdc_array_single`` (synchronizer): ``src_clk``: clock; ``src_in``: timed by src_clk; ``dest_clk``: clock; ``dest_out``: src_in synchronized to dest_clk, DEST_SYNC_FF stages (manual review).
  Reference: UG974, XPM_CDC_ARRAY_SINGLE.
* ``xpm_cdc_gray`` (synchronizer): ``src_clk``: clock; ``src_in_bin``: timed by src_clk; ``dest_clk``: clock; ``dest_out_bin``: src_in_bin synchronized to dest_clk, DEST_SYNC_FF stages (manual review).
  Reference: UG974, XPM_CDC_GRAY.
* ``xpm_cdc_handshake``: ``src_clk``: clock; ``dest_clk``: clock; ``src_in``: timed by src_clk; ``src_send``: timed by src_clk; ``src_rcv``: dest_ack synchronized to src_clk, SRC_SYNC_FF stages (manual review); ``dest_ack``: timed by dest_clk; ``dest_req``: src_send synchronized to dest_clk, DEST_SYNC_FF stages (manual review); ``dest_out``: src_in synchronized to dest_clk, DEST_SYNC_FF stages (manual review).
  Reference: UG974, XPM_CDC_HANDSHAKE.
* ``xpm_cdc_pulse``: ``src_clk``: clock; ``dest_clk``: clock; ``src_pulse``: timed by src_clk; ``src_rst``: timed by src_clk; ``dest_rst``: timed by dest_clk; ``dest_pulse``: src_pulse synchronized to dest_clk, DEST_SYNC_FF stages (manual review).
  Reference: UG974, XPM_CDC_PULSE.
* ``xpm_cdc_sync_rst``: ``dest_clk``: clock; ``src_rst``: async; ``dest_rst``: src_rst synchronized to dest_clk, DEST_SYNC_FF stages (manual review).
  Reference: UG974, XPM_CDC_SYNC_RST.
* ``xpm_cdc_async_rst``: ``dest_clk``: clock; ``src_arst``: asynchronous reset; ``dest_arst``: reset released synchronously to dest_clk.
  Reference: UG974, XPM_CDC_ASYNC_RST.
* ``FIFO36E1`` (dual_clock_fifo): ``RST``: asynchronous reset; ``WRCLK``: clock; ``DI``: timed by WRCLK; ``DIP``: timed by WRCLK; ``WREN``: timed by WRCLK; ``FULL``: timed by WRCLK; ``ALMOSTFULL``: timed by WRCLK; ``WRCOUNT``: timed by WRCLK; ``WRERR``: timed by WRCLK; ``INJECTDBITERR``: timed by WRCLK; ``INJECTSBITERR``: timed by WRCLK; ``ECCPARITY``: timed by WRCLK; ``RDCLK``: clock; ``DO``: timed by RDCLK; ``DOP``: timed by RDCLK; ``RDEN``: timed by RDCLK; ``EMPTY``: timed by RDCLK; ``ALMOSTEMPTY``: timed by RDCLK; ``RDCOUNT``: timed by RDCLK; ``RDERR``: timed by RDCLK; ``REGCE``: timed by RDCLK; ``RSTREG``: timed by RDCLK; ``SBITERR``: timed by RDCLK; ``DBITERR``: timed by RDCLK.
  Reference: UG953, FIFO36E1.
* ``FIFO18E1`` (dual_clock_fifo): ``RST``: asynchronous reset; ``WRCLK``: clock; ``DI``: timed by WRCLK; ``DIP``: timed by WRCLK; ``WREN``: timed by WRCLK; ``FULL``: timed by WRCLK; ``ALMOSTFULL``: timed by WRCLK; ``WRCOUNT``: timed by WRCLK; ``WRERR``: timed by WRCLK; ``INJECTDBITERR``: timed by WRCLK; ``INJECTSBITERR``: timed by WRCLK; ``ECCPARITY``: timed by WRCLK; ``RDCLK``: clock; ``DO``: timed by RDCLK; ``DOP``: timed by RDCLK; ``RDEN``: timed by RDCLK; ``EMPTY``: timed by RDCLK; ``ALMOSTEMPTY``: timed by RDCLK; ``RDCOUNT``: timed by RDCLK; ``RDERR``: timed by RDCLK; ``REGCE``: timed by RDCLK; ``RSTREG``: timed by RDCLK; ``SBITERR``: timed by RDCLK; ``DBITERR``: timed by RDCLK.
  Reference: UG953, FIFO18E1.
* ``FIFO36E2`` (dual_clock_fifo): ``WRCLK``: clock; ``DIN``: timed by WRCLK; ``DINP``: timed by WRCLK; ``WREN``: timed by WRCLK; ``FULL``: timed by WRCLK; ``PROGFULL``: timed by WRCLK; ``WRCOUNT``: timed by WRCLK; ``WRERR``: timed by WRCLK; ``WRRSTBUSY``: timed by WRCLK; ``INJECTDBITERR``: timed by WRCLK; ``INJECTSBITERR``: timed by WRCLK; ``ECCPARITY``: timed by WRCLK; ``RST``: timed by WRCLK; ``RDCLK``: clock; ``DOUT``: timed by RDCLK; ``DOUTP``: timed by RDCLK; ``RDEN``: timed by RDCLK; ``EMPTY``: timed by RDCLK; ``PROGEMPTY``: timed by RDCLK; ``RDCOUNT``: timed by RDCLK; ``RDERR``: timed by RDCLK; ``RDRSTBUSY``: timed by RDCLK; ``REGCE``: timed by RDCLK; ``RSTREG``: timed by RDCLK; ``SBITERR``: timed by RDCLK; ``DBITERR``: timed by RDCLK.
  Reference: UG974, FIFO36E2.
* ``FIFO18E2`` (dual_clock_fifo): ``WRCLK``: clock; ``DIN``: timed by WRCLK; ``DINP``: timed by WRCLK; ``WREN``: timed by WRCLK; ``FULL``: timed by WRCLK; ``PROGFULL``: timed by WRCLK; ``WRCOUNT``: timed by WRCLK; ``WRERR``: timed by WRCLK; ``WRRSTBUSY``: timed by WRCLK; ``INJECTDBITERR``: timed by WRCLK; ``INJECTSBITERR``: timed by WRCLK; ``ECCPARITY``: timed by WRCLK; ``RST``: timed by WRCLK; ``RDCLK``: clock; ``DOUT``: timed by RDCLK; ``DOUTP``: timed by RDCLK; ``RDEN``: timed by RDCLK; ``EMPTY``: timed by RDCLK; ``PROGEMPTY``: timed by RDCLK; ``RDCOUNT``: timed by RDCLK; ``RDERR``: timed by RDCLK; ``RDRSTBUSY``: timed by RDCLK; ``REGCE``: timed by RDCLK; ``RSTREG``: timed by RDCLK; ``SBITERR``: timed by RDCLK; ``DBITERR``: timed by RDCLK.
  Reference: UG974, FIFO18E2.
* ``xpm_fifo_async`` (dual_clock_fifo): ``sleep``: async; ``wr_clk``: clock; ``rst``: timed by wr_clk; ``din``: timed by wr_clk; ``wr_en``: timed by wr_clk; ``full``: timed by wr_clk; ``almost_full``: timed by wr_clk; ``wr_ack``: timed by wr_clk; ``overflow``: timed by wr_clk; ``prog_full``: timed by wr_clk; ``wr_data_count``: timed by wr_clk; ``wr_rst_busy``: timed by wr_clk; ``injectsbiterr``: timed by wr_clk; ``injectdbiterr``: timed by wr_clk; ``rd_clk``: clock; ``dout``: timed by rd_clk; ``rd_en``: timed by rd_clk; ``empty``: timed by rd_clk; ``almost_empty``: timed by rd_clk; ``data_valid``: timed by rd_clk; ``underflow``: timed by rd_clk; ``prog_empty``: timed by rd_clk; ``rd_data_count``: timed by rd_clk; ``rd_rst_busy``: timed by rd_clk; ``sbiterr``: timed by rd_clk; ``dbiterr``: timed by rd_clk.
  Reference: UG974, XPM_FIFO_ASYNC.
* ``xpm_fifo_sync`` (single_clock): ``sleep``: async; ``wr_clk``: clock; ``*``: timed by wr_clk.
  Reference: UG974, XPM_FIFO_SYNC.
* ``xpm_memory_spram`` (single_clock): ``sleep``: async; ``clka``: clock; ``*``: timed by clka.
  Reference: UG974, XPM_MEMORY_SPRAM.
* ``xpm_memory_sdpram`` (memory): ``sleep``: async; ``clka``: clock; ``addra``: timed by clka; ``dina``: timed by clka; ``ena``: timed by clka; ``wea``: timed by clka; ``injectsbiterra``: timed by clka; ``injectdbiterra``: timed by clka; ``clkb``: clock; ``addrb``: timed by clkb; ``doutb``: timed by clkb; ``enb``: timed by clkb; ``regceb``: timed by clkb; ``rstb``: timed by clkb; ``sbiterrb``: timed by clkb; ``dbiterrb``: timed by clkb.
  When clocking_mode = common_clock: ``addrb``: timed by clka; ``doutb``: timed by clka; ``enb``: timed by clka; ``regceb``: timed by clka; ``rstb``: timed by clka; ``sbiterrb``: timed by clka; ``dbiterrb``: timed by clka; ``dinb``: timed by clka; ``web``: timed by clka; ``injectsbiterrb``: timed by clka; ``injectdbiterrb``: timed by clka; ``clkb``: unused.
  Reference: UG974, XPM_MEMORY_SDPRAM.
* ``xpm_memory_tdpram`` (memory): ``sleep``: async; ``clka``: clock; ``addra``: timed by clka; ``dina``: timed by clka; ``douta``: timed by clka; ``ena``: timed by clka; ``regcea``: timed by clka; ``rsta``: timed by clka; ``wea``: timed by clka; ``injectsbiterra``: timed by clka; ``injectdbiterra``: timed by clka; ``sbiterra``: timed by clka; ``dbiterra``: timed by clka; ``clkb``: clock; ``addrb``: timed by clkb; ``dinb``: timed by clkb; ``doutb``: timed by clkb; ``enb``: timed by clkb; ``regceb``: timed by clkb; ``rstb``: timed by clkb; ``web``: timed by clkb; ``injectsbiterrb``: timed by clkb; ``injectdbiterrb``: timed by clkb; ``sbiterrb``: timed by clkb; ``dbiterrb``: timed by clkb.
  When clocking_mode = common_clock: ``addrb``: timed by clka; ``doutb``: timed by clka; ``enb``: timed by clka; ``regceb``: timed by clka; ``rstb``: timed by clka; ``sbiterrb``: timed by clka; ``dbiterrb``: timed by clka; ``dinb``: timed by clka; ``web``: timed by clka; ``injectsbiterrb``: timed by clka; ``injectdbiterrb``: timed by clka; ``clkb``: unused.
  Reference: UG974, XPM_MEMORY_TDPRAM.

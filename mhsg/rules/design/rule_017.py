# -*- coding: utf-8 -*-

from mhsg.design.rule import Finding, Rule


class rule_017(Rule):
    """
    This rule reports black boxes whose effect on clock domains is not declared.

    .. NOTE:: This is a design rule. It runs in design analysis and implements DO-254 check CDC1.

    Design analysis cannot see inside a black box, such as a vendor primitive, a vendor macro or encrypted IP, and
    assumes nothing about one. Each black box type must be declared in the black_boxes part of the design section,
    or in a black box library, with a role for every port: which pins are clocks, which data is timed by which clock,
    which outputs follow inputs, which clocks it makes, and what it synchronizes inside.
    A static port needs a justification and reviewed_by.
    :code:`mhsg --design --black_box_template FILE` writes a template of the declarations a design needs.

    **Violation**

    .. code-block:: vhdl

       -- vendor_dma has no declaration
       u_dma : vendor_dma port map (aclk => clk, irq => irq);
    """

    def __init__(self):
        super().__init__()
        self.solution = "Declare the black box"

    def check_design(self, oContext):
        oAnalysis = oContext.cdc()
        if oAnalysis is None:
            return []
        lReturn = []
        for oCell, sMessage, iCount in oAnalysis.box_problems:
            sFile, iLine = oAnalysis.locate(oCell)
            sCount = f" ({iCount} instances)" if iCount > 1 else ""
            lReturn.append(Finding(sFile, iLine, sMessage + sCount))
        return lReturn

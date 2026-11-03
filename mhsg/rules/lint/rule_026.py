# -*- coding: utf-8 -*-

from mhsg.lint.rule import Rule


class rule_026(Rule):
    """
    This rule checks that entities are instantiated directly, with :code:`entity work.name`, instead of through a component.

    .. NOTE:: This is a lint rule. It runs in lint mode and is part of the do254_plus rule set.

    Direct instantiation needs no component declaration, which could differ from the entity.
    Components whose entity is not in the file or the run, such as vendor primitives, are not reported.

    **Violation**

    .. code-block:: vhdl

       u_fifo : fifo
         port map (

    **Fix**

    .. code-block:: vhdl

       u_fifo : entity work.fifo
         port map (
    """

    def __init__(self):
        super().__init__()
        self.solution = "Instantiate the entity directly"

    def check(self, oModel, oFile):
        dProject = getattr(getattr(oFile, "configuration", None), "project_port_modes", None) or {}
        setEntities = set(oModel.entity_ports) | set((dProject.get("entity") or {}).keys())
        for oArchitecture in oModel.architectures:
            for oInstance in oArchitecture.instances:
                if oInstance.unit_kind == "component" and oInstance.unit in setEntities:
                    self.report(oFile, oInstance.index, f"Instantiate {oInstance.unit} with entity work.{oInstance.unit} instead of a component")

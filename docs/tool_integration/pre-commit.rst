pre-commit Integration
----------------------

MHSG supports integration with pre-commit using the following ``.pre-commit-config.yaml`` file:

.. code-block:: yaml

  repos:
    - repo: https://github.com/xTheBearx/vhdl-style-guide
      rev: <release tag>
      hooks:
        - id: mhsg

The hook fixes the VHDL, Verilog and SystemVerilog files of a commit: those ending in ``.vhd``, ``.vhdl``, ``.sv``,
``.svh``, ``.v`` and ``.vh``. It fails when a file has violations that cannot be fixed.

You may customize MHSG by using the ``args`` node, and choose the files with ``files``, for example to check only
VHDL files:

.. code-block:: yaml

  repos:
    - repo: https://github.com/xTheBearx/vhdl-style-guide
      rev: <release tag>
      hooks:
        - id: mhsg
          files: \.(vhd|vhdl)$
          args:
            - --configuration=.mhsg.yaml
            - --output_format=syntastic

Editor Integration
------------------

If your editor can execute programs on the command line, you can run MHSG without having to leave your editor.
This brings a new level of efficiency to coding in VHDL.

MHSG does not provide its own editor extension or language server.
Instead, general purpose editor extensions can run it using the following command lines.

Formatting
   ``mhsg --stdin --fix --stdout`` reads the code from standard input and writes the fixed code to standard output.
   The input file is not changed, and the violation report goes to standard error.
   This is the interface expected by formatter extensions which format the current buffer.

Diagnostics
   ``mhsg --stdin -of syntastic`` reads the code from standard input and writes one line per violation, which is easy to match with a regular expression.
   ``--json`` writes the violations to a JSON file for tools which prefer structured output.

Configuration
   Add ``-c`` with your configuration file to any of these commands so the editor uses the same rules as your command line and continuous integration checks.

.. NOTE:: Extensions written for VSG run the ``vsg`` command.
   They can be used with MHSG only if they allow the command to be changed to ``mhsg``.

.. toctree::
   :maxdepth: 2

   vim.rst
   vscode.rst

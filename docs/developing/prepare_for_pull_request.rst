Prepare for pull request
------------------------

Before creating a pull request run all checks against the code base:

.. code-block:: bash

   $ uv run pre-commit run --all-files
   $ uv run pytest
   $ uv build

These run the code style checks and the tests, and build the package.
The continuous integration also runs the tests against every supported version of Python, for example locally with:

.. code-block:: bash

   $ uv run --python 3.8 pytest

When this passes create a pull request.

.. NOTE:: `Issue 1157 <https://github.com/jeremiah-c-leary/vhdl-style-guide/issues/1157>`_ is still being resolved and should not gate any PR creation.

If the change touches the parser, or a rule whose fix moves tokens between lines, also run the :ref:`real_world_check`.
If it touches design analysis, also run its design analysis check.

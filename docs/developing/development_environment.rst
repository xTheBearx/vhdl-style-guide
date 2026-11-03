Development Environment
-----------------------

Follow these steps to setup the development environment.

Clone the repo
##############

Clone the repo with the following command:

.. code-block:: bash

   $ git clone https://github.com/jeremiah-c-leary/vhdl-style-guide.git

Setup alias
###########

Set an alias to MHSG as follows:

.. code-block:: bash

   $ set alias mhsg='python3 <path_to_clone_directory>/bin/mhsg'

This allows you to execute MHSG without installing it.

Install prerequisites
#####################

The project is managed with `uv <https://docs.astral.sh/uv/>`_.
Install the locked dependencies, including those for testing and the style checks, into ``.venv``:

.. code-block:: bash

   $ uv sync

Add ``--group docs`` to also install the tools to build the documentation.
Run commands in the environment with ``uv run``:

.. code-block:: bash

   $ uv run pytest
   $ uv run pre-commit run --all-files
   $ uv run --group docs sphinx-build docs build.out/docs/html

Build locally, artifacts will appear in ``dist`` directory.

.. code-block:: bash

   $ uv build

Dependencies are declared in ``pyproject.toml`` and locked in ``uv.lock``.
Add one with ``uv add <package>``, or ``uv add --group tests <package>`` for a development dependency, and commit the updated lock file.

Design analysis also needs GHDL, Yosys and the GHDL plugin for Yosys, which are installed with the system's package manager, see :doc:`../installing`.

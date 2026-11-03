Installation
============

MHSG needs Python 3.12 or newer. There are two methods to install MHSG.

PIP
---

The most recent released version is hosted on PyPI.
It can be installed using **pip**.

.. code-block:: bash

  pip install mhsg --use-pep517

This is the preferred method for installing MHSG.

GitHub
------

The latest development version can be cloned from the GitHub repo.

.. code-block:: bash

  git clone https://github.com/jeremiah-c-leary/vhdl-style-guide.git

The project is managed with `uv <https://docs.astral.sh/uv/>`_.
Install the locked development dependencies, then build; artifacts will appear in the ``dist`` directory.

.. code-block:: bash

  uv sync
  uv build

External tools
--------------

Design analysis, see :doc:`design_analysis`, needs GHDL, Yosys and the GHDL plugin for Yosys.
They are not Python packages, so they are installed with the system's package manager, for example on Ubuntu:

.. code-block:: bash

  sudo apt-get install ghdl yosys yosys-plugin-ghdl

The rest of MHSG works without them.

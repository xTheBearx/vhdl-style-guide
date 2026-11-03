
Release Process
===============

Follow these steps:


1)  Update :code:`release_notes.txt`

2)  Tag with the following command

.. code-block:: bash

   $ git tag <release_number> -F release_notes.txt

3)  Push tag to origin

.. code-block:: bash

   $ git push --tags origin master

4)  Build the Wheel

.. code-block:: bash

   $ uv build --out-dir dist

5)  Submit to PyPI

.. code-block:: bash

   $ uv publish dist/*

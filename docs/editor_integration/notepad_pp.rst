NOTEPAD++
#########

There are two methods to integrate Notepad++ with MHSG:  using the Run command and using PythonScript.

Run Command
-----------

Using the run command requires an update to the %APPDATA%/Notepad++/shortcuts.xml file.

In the <UserDefinedCommands> section, add this line

::

   <Command name="Run MHSG" Ctrl="no" Alt="no" Shift="no" Key="120">mhsg -f &quot;$(FULL_CURRENT_PATH)&quot; --fix</Command>


This macro bound to the <F9> key performs the following steps:

1. Save the current buffer
2. Execute mhsg with the --fix option

After executing MHSG, Notepad++ with prompt to re-read the file if it has changed.

PythonScript
------------

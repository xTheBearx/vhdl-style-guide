Contributing
------------

Any contributions to this project are welcomed.
No matter how small or large.

There are several ways to contribute:

1. Bug reports
2. Code base improvements
3. Feature requests
4. Pull requests

Bug Reports
###########

Code from open cores was utilized to develop MHSG.
It provided many different coding styles to process.
There are bound to be some corner cases or incorrect assumptions in the code due to the small sample size.
If problems are found with the output or in using MHSG, please submit an issue.
When creating the issue, use the **bug** label to highlight it.
Fixing bugs is prioritized over feature enhancements.

Code Base Improvements
######################

MHSG started out to solve a problem and learn how to code in Python.
The learning part is still on going, and the code base could always be improved.
The code base is run through *Codacy* and *Code Climate*, and they are very helpful.
However, any suggestions to improve the code base would be appreciated.

Create an issue and use the **refactor** label for any code which could be improved.

Feature Requests
################

MHSG is still a work in progress and by no means feature complete.
In fact, the following features were not in the original concept of MHSG.

* fix
* fix_phase
* output_format
* backup

Fix is probably the most important feature.
It was added when a user said it would be nice if MHSG just fixed the problems it found.
There may be other important missing features in the current implementation.

Create an issue with the **enhancement** label for any new features.

Pull Requests
#############

Pull requests are always welcome.

MHSG was developed using a Test Driven Development (TDD) process.
There are over 1000 tests which cover individual rules and other features of MHSG.
For each pull request, an accompanying test to validate the pull request would be appreciated.

AI-Assisted Contributions
#########################

Contributions written with the help of AI tools, such as large language models, are accepted on the same terms as any other contribution.
MHSG itself is developed with AI assistance.
Because generated code can look correct while hiding mistakes, the following apply:

* **Disclose it.**
  Say in the pull request which parts were AI-assisted and which tool was used, or add a trailer such as :code:`Co-Authored-By:` to the commits.
* **Own it.**
  You are responsible for every line you submit.
  Read and understand the change before submitting it, and be ready to explain why it is correct.
  Do not submit generated code, tests or documentation you have not reviewed.
* **Prove it.**
  Bug fixes must include a test that fails without the fix and passes with it.
  New features must include tests covering their behavior.
  Run :code:`uv run pre-commit run --all-files` and :code:`uv run pytest` before submitting, so the style checks and the full test suite pass.
* **Expect review.**
  A maintainer reviews every pull request before it is merged, and may ask questions about the change or decline it if it cannot be explained.

The same applies to issues and comments.
Report what you observed, with the actual code, configuration and output, rather than generated text you have not checked.

Quality Control
###############

This project uses the following open source tools to help with code quality:

* *Travis CI* to run all the tests.
* *Codacy* and *Code Climate* to check for code style issues.
* *Codcov* to check the code coverage of the tests.

The results will be available on the pull request GitHub page.

# Contributing to bluepy3

Thank you for your interest in making `bluepy3` better!

## Reporting issues
First, search through the existing [issues](https://github.com/Mausy5043/bluepy3/issues) to see whether your issue is already known. If it is, add your details to the existing issue. Issue-hijacking, however, is not appreciated. If your problem is significantly different you are encouraged to open a new issue. When in doubt, open a new issue.

In order for us to help with an issue, it's useful if you provide as much detail as possible.

1. In the issue title answer this question: What is wrong with what?
2. Fill in the issue body as per the template.
3. Consider assisting us, if you can, by helping us fix the issue:
   1. Investigate the cause.
   2. Suggest changes to the code.
   3. Create and submit a Pull Request.

## Submitting Pull Requests
Normal development happens on the [`devel` branch](https://github.com/Mausy5043/bluepy3/tree/devel).
When you want to make changes, the best way to do that is by creating a [feature branch](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork) off your private fork of this repository's `devel` branch.
 * All pull requests must be made against (the current state of) the `devel` branch. So, make sure, that at the time of the PR-creation *your* version of the branch is up-to-date with the current state of the [`devel` branch](https://github.com/Mausy5043/bluepy3/tree/devel) to prevent merge conflicts.
 * The PR should consist of atomic commits. We prefer many smaller commits as opposed to one large commit that has lots of unrelated changes.
 * Each commit should have a clear message saying what has changed. Use the second line of the commit message to provide context (e.g. why was this changed?)
 * To prevent merge blocking you are required to [sign all commits](https://docs.github.com/en/authentication/managing-commit-signature-verification/about-commit-signature-verification).

### Formatting and Coding Style
 * We use [`black`](https://pypi.org/project/black/).
Code style formatting of all commits must adhere to `black --line-length 98`.
 * Please use `pylint` with this project's `.pylintrc` and `flake8` and `pydocstyle` using the project's `tox.ini` to discover suggestions for code improvement.
 Since the code isn't perfect you are free to ignore any suggestions by the linters that are unrelated to your changes. However, you are also welcome to fix those suggestions if you want ;-)
 * For C, C++ sources we prefer to use [`cpplint`](https://pypi.org/project/cpplint/) for linting and [`clang-format`](https://pypi.org/project/clang-format/) to correct code formatting.
 Here too we use a line length of <= 98.

 To run pre-commit hooks you may need to `pip install pre-commit` or `conda install pre-commit` and `pre-commit run --all-files` on first use.

Note that most, if not all, of us do this in our free time, so sometimes you get a quick response and other times it may take longer.
We assume that you've read GitHub's help page [regarding pull requests](https://help.github.com/articles/using-pull-requests/).

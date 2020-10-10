# Contributing to Kibble #

## Community 

The main development and design discussion happens on our mailing lists.
We have a list specifically for development, and one for future user questions and feedback.

To join in the discussion on the design and roadmap, you can send an email to [dev@kibble.apache.org](mailto:dev@kibble.apache.org).<br/>
You can subscribe to the list by sending an email to [dev-subscribe@kibble.apache.org](mailto:dev-subscribe@kibble.apache.org).<br/>
You can also browse the archives online at [lists.apache.org](https://lists.apache.org/list.html?dev@kibble.apache.org).

We also have:
- IRC channel, #kibble on [Freenode](https://webchat.freenode.net/?channels=#kibble)
- Slack channel, #kibble on [ASF slack](https://s.apache.org/slack-invite)

## Development installation

This project requires Python in higher version than 3.4.
More information will come soon!

## Code Quality

Apache Kibble project is using [pre-commits](https://pre-commit.com) to ensure the quality of the code.
We encourage you to use pre-commits, but it's not a required to contribute. Every change is checked
on CI and if it does not pass the tests it cannot be accepted. If you want to check locally then
you should install Python3.6 or newer together and run:
```bash
pip install pre-commit
# or
brew install pre-commit
```
For more installation options visit the [pre-commits](https://pre-commit.com).

To turn on pre-commit checks for commit operations in git, run:
```bash
pre-commit install
```
To run all checks on your staged files, run:
```bash
pre-commit run
```
To run all checks on all files, run:
```bash
pre-commit run --all-files
```

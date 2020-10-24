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

You should be able to install Apache Kibble by simply doing:
```
pip install -e ."[devel]"
```

The easiest option to spin up a development environment is to use our development docker-compose.
The development image has mounted all Kibble sources so all your local code changes will be automatically
reflected  in the running app.

First you need to configure the Elasticsearch node:
```
docker-compose -f docker-compose-dev.yaml up setup
```
Once you see the
```
setup_1          | All done, Kibble should...work now :)
```
Now you can can launch Apache Kibble ui:
```
docker-compose -f docker-compose-dev.yaml up ui
```
The ui should be available under `http://0.0.0.0:8000` or `http://localhost:8000`. To log in you can use
the dummy admin account `admin@kibble` and password `kibbleAdmin`.

You can also start only the API server:
```
docker-compose -f docker-compose-dev.yaml up kibble
```

## Code Quality

Apache Kibble project is using [pre-commits](https://pre-commit.com) to ensure the quality of the code.
We encourage you to use pre-commits, but it's not required in order to contribute. Every change is checked
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

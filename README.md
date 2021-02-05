<p align="center"><img src="/ui/images/kibble-logo.png" width="300"/></p>

# Apache Kibble
![CI](https://github.com/apache/kibble/workflows/CI/badge.svg)
[![License](http://img.shields.io/:license-Apache%202-blue.svg)](http://www.apache.org/licenses/LICENSE-2.0.txt)

Apache Kibble is a tool to collect, aggregate and visualize data about any software project that uses commonly known tools. It consists of two components:

- **Kibble Server** (this repository) - main database and UI Server. It serves as the hub
 for the scanners to connect to, and provides the overall management of sources as well as the
 visualizations and API end points.
- **Kibble scanners** ([kibble-scanners](https://github.com/apache/kibble-scanners)) - a collection of
 scanning applications each designed to work with a specific type of resource (git repo, mailing list,
 JIRA, etc) and push compiled data objects to the Kibble Server.

## Documentation

For information about the Kibble project and community, visit our
web site at [https://kibble.apache.org/](https://kibble.apache.org/).

## Live demo

If you would love to try Kibble without installing it on your own machine try the online demo of the Kibble
service: [https://demo.kibble.apache.org/](https://demo.kibble.apache.org/).


## Installation

For installation steps see the [documentation](https://apache-kibble.readthedocs.io/en/latest/setup.html#installing-the-server).

## Contributing

We welcome all contributions that improve the state of the Apache Kibble project. For contribution guidelines
check the [CONTRIBUTING.md](/CONTRIBUTING.md).

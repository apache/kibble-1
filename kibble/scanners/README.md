# Kibble Scanner Application
The Kibble Scanners collect information for the Kibble Suite.

## Setup instructions:

 - Edit kibble.ini to match your Kibble service

## How to run:

 - On a daily/weekly/whatever basis, run: `kibble scan`.

### Command line options:

```
Usage: kibble scan [OPTIONS]

Options:
  -t, --type TEXT     Specific type of scanner to run (default is run all
                      scanners)

  -e, --exclude TEXT  Specific type of scanner(s) to exclude
  -o, --org TEXT      The organisation to gather stats for. If left out, all
                      organisations will be scanned.

  -a, --age TEXT      Minimum age in hours before performing a new scan on an
                      already processed source. --age 12 will not process any
                      source that was processed less than 12 hours ago, but
                      will process new sources.

  -s, --source TEXT   Specific source (wildcard) to run scans on.
  -v, --view TEXT     Specific source view to scan (default is scan all
                      sources)

  --help              Show this message and exit.
```

## Currently available scanner plugins:

 - Apache Pony Mail (`scanners/ponymail.py`)
 - Atlassian JIRA (`scanners/jira.py`)
 - BugZilla Issue Tracker (`scanners/bugzilla.py`)
 - BuildBot (`scanners/buildbot.py`)
 - Discourse (`scanners/discourse.py`)
 - Gerrit Code Review (`scanners/gerrit.py`)
 - Git Repository Fetcher (`scanners/git-sync.py`)
 - Git Census Counter (`scanners/git-census.py`)
 - Git Code Evolution Counter (`scanners/git-evolution.py`)
 - Git SLoC Counter (`scanners/git-sloc.py`)
 - GitHub Issues/PRs (`scanners/github.py`)
 - GitHub Traffic Statistics (`scanners/github-stats.py`)
 - GNU Mailman Pipermail (`scanners/pipermail.py`)
 - Jenkins (`scanners/jenkins.py`)
 - Travis CI (`scanners/travis.py`)

## Requirements:

 - [cloc](https://github.com/AlDanial/cloc) version 1.76 or later `(optional)`
 - git binaries
 - python3 (3.3 or later)
 - python3-elasticsearch
 - python3-certifi
 - python3-yaml

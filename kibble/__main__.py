# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from typing import List

import click

from kibble.cli import setup_command
from kibble.cli.make_account_command import make_account_cmd
from kibble.cli.scanner_command import scan_cmd
from kibble.configuration import conf
from kibble.version import version as kibble_version


@click.group()
def cli():
    """A simple command line tool for kibble"""


@cli.command("version", short_help="displays the current kibble version")
def version():
    print(kibble_version)


@cli.command("setup", short_help="starts the setup process for kibble")
@click.option(
    "-u",
    "--uri",
    default=conf.get("elasticsearch", "conn_uri"),
    help="connection uri for ElasticSearch",
)
@click.option(
    "-d",
    "--dbname",
    default=conf.get("elasticsearch", "dbname"),
    help="elasticsearch database prefix",
)
@click.option(
    "-s",
    "--shards",
    default=conf.get("elasticsearch", "shards"),
    help="number of ES shards",
)
@click.option(
    "-r",
    "--replicas",
    default=conf.get("elasticsearch", "replicas"),
    help="number of replicas for ES",
)
@click.option("-a", "--autoadmin", default=False, help="generate generic admin account")
@click.option("-k", "--skiponexist", default=True, help="skip DB creation if DBs exist")
def setup(
    uri: str,
    dbname: str,
    shards: str,
    replicas: str,
    autoadmin: bool,
    skiponexist: bool,
):
    setup_command.do_setup(
        uri=uri,
        dbname=dbname,
        shards=shards,
        replicas=replicas,
        autoadmin=autoadmin,
        skiponexist=skiponexist,
    )


@cli.command("make_account", short_help="creates new kibble user account")
@click.option(
    "-u", "--username", help="username (email) of account to create", required=True
)
@click.option("-p", "--password", help="password to set for account", required=True)
@click.option("-A", "--admin", default=False, help="make account global admin")
@click.option(
    "-a", "--orgadmin", default=False, help="make account owner of orgs invited to"
)
@click.option("-o", "--org", default=None, help="invite to this organisation")
def make_account(
    username: str,
    password: str,
    admin: bool = False,
    orgadmin: bool = False,
    org: str = None,
):
    make_account_cmd(
        username=username, password=password, admin=admin, adminorg=orgadmin, org=org
    )


@cli.command("scan", short_help="starts scanning process")
@click.option(
    "-t",
    "--type",
    "scanners",
    help="Specific type of scanner to run (default is run all scanners). Can be used multiple times.",
    multiple=True,
)
@click.option(
    "-e",
    "--exclude",
    help="Specific type of scanner(s) to exclude. Can be used multiple times.",
    multiple=True,
)
@click.option(
    "-o",
    "--org",
    help="The organisation to gather stats for. If left out, all organisations will be scanned.",
)
@click.option(
    "-a",
    "--age",
    help="Minimum age in hours before performing a new scan on an already processed source. "
    "--age 12 will not process any source that was processed less than 12 hours ago, but "
    "will process new sources.",
)
@click.option("-s", "--source", help="Specific source (wildcard) to run scans on.")
@click.option(
    "-v",
    "--view",
    help="Specific source view to scan (default is scan all sources).",
)
def run_scan(
    scanners: List[str] = None,
    exclude: List[str] = None,
    org: str = None,
    age: int = None,
    source: str = None,
    view: str = None,
):
    scan_cmd(
        scanners=scanners,
        exclude=exclude,
        org=org,
        age=age,
        source=source,
        view=view,
    )


def main():
    cli()


if __name__ == "__main__":
    main()

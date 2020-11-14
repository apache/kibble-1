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

import click

from kibble.cli import setup_command
from kibble.version import version as kibble_version

from kibble.configuration import conf


@click.group()
def cli():
    """A simple command line tool for kibble"""


@cli.command("version", short_help="displays the current kibble version")
def version():
    click.echo(kibble_version)


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
@click.option(
    "-m", "--mailhost", default=conf.get("mail", "mailhost"), help="mail server host"
)
@click.option("-a", "--autoadmin", default=False, help="generate generic admin account")
@click.option("-k", "--skiponexist", default=True, help="skip DB creation if DBs exist")
def setup(
    uri: str,
    dbname: str,
    shards: str,
    replicas: str,
    mailhost: str,
    autoadmin: bool,
    skiponexist: bool,
):
    setup_command.do_setup(
        uri=uri,
        dbname=dbname,
        shards=shards,
        replicas=replicas,
        mailhost=mailhost,
        autoadmin=autoadmin,
        skiponexist=skiponexist,
    )


def main():
    cli()


if __name__ == "__main__":
    main()

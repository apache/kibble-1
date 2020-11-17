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

import json
import logging
import os
import sys
from getpass import getpass

import bcrypt
import click
import tenacity
from elasticsearch import Elasticsearch

from kibble.configuration import conf

KIBBLE_VERSION = conf.get("api", "version")
KIBBLE_DB_VERSION = conf.get("api", "database")


def get_user_input(msg: str, secure: bool = False):
    value = None
    while not value:
        value = getpass(msg) if secure else input(msg)
    return value


def create_es_index(
    conn_uri: str,
    dbname: str,
    shards: int,
    replicas: int,
    admin_name: str,
    admin_pass: str,
    skiponexist: bool,
):
    """Creates Elasticsearch index used by Kibble"""

    # elasticsearch logs lots of warnings on retries/connection failure
    logging.getLogger("elasticsearch").setLevel(logging.ERROR)

    mappings_json = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "../setup/mappings.json"
    )
    with open(mappings_json, "r") as f:
        mappings = json.load(f)

    es = Elasticsearch([conn_uri], max_retries=5, retry_on_timeout=True)
    print(es.info())

    es_version = es.info()["version"]["number"]
    es6 = int(es_version.split(".")[0]) >= 6
    es7 = int(es_version.split(".")[0]) >= 7

    if not es6:
        print(
            f"New Kibble installations require ElasticSearch 6.x or newer! "
            f"You appear to be running {es_version}!"
        )
        sys.exit(-1)

    # If ES >= 7, _doc is invalid and mapping should be rooted
    if es7:
        mappings["mappings"] = mappings["mappings"]["_doc"]

    # Check if index already exists
    if es.indices.exists(dbname + "_api"):
        # Skip this is DB exists and -k added
        if skiponexist:
            print("DB prefix exists, but --skiponexist used, skipping this step.")
            return
        print("Error: ElasticSearch DB prefix '%s' already exists!" % dbname)
        sys.exit(-1)

    types = [
        "api",
        # ci_*: CI service stats
        "ci_build",
        "ci_queue",
        # code_* + evolution + file_history: git repo stats
        "code_commit",
        "code_commit_unique",
        "code_modification",
        "evolution",
        "file_history",
        # forum_*: forum stats (SO, Discourse, Askbot etc)
        "forum_post",
        "forum_topic",
        # GitHub stats
        "ghstats",
        # im_*: Instant messaging stats
        "im_stats",
        "im_ops",
        "im_msg",
        "issue",
        "logstats",
        # email, mail*: Email statitics
        "email",
        "mailstats",
        "mailtop",
        # organisation, view, source, publish: UI Org DB
        "organisation",
        "view",
        "publish",
        "source",
        # stats: Miscellaneous stats
        "stats",
        # social_*: Twitter, Mastodon, Facebook etc
        "social_follow",
        "social_followers",
        "social_follower",
        "social_person",
        # uisession, useraccount, message: UI user DB
        "uisession",
        "useraccount",
        "message",
        # person: contributor DB
        "person",
    ]

    for t in types:
        iname = f"{dbname}_{t}"
        print(f"Creating index {iname}")

        settings = {"number_of_shards": shards, "number_of_replicas": replicas}
        es.indices.create(
            index=iname, body={"mappings": mappings["mappings"], "settings": settings}
        )
    print(f"Indices created!\n")
    print()

    salt = bcrypt.gensalt()
    pwd = bcrypt.hashpw(admin_pass.encode("utf-8"), salt).decode("ascii")
    print("Creating administrator account")
    doc = {
        "email": admin_name,  # Username (email)
        "password": pwd,  # Hashed password
        "displayName": "Administrator",  # Display Name
        "organisations": [],  # Orgs user belongs to (default is none)
        "ownerships": [],  # Orgs user owns (default is none)
        "defaultOrganisation": None,  # Default org for user
        "verified": True,  # Account verified via email?
        "userlevel": "admin",  # User level (user/admin)
    }
    dbdoc = {
        "apiversion": KIBBLE_VERSION,  # Log current API version
        "dbversion": KIBBLE_DB_VERSION,  # Log the database revision we accept (might change!)
    }
    es.index(index=dbname + "_useraccount", doc_type="_doc", id=admin_name, body=doc)
    es.index(index=dbname + "_api", doc_type="_doc", id="current", body=dbdoc)
    print("Account created!")


def do_setup(
    uri: str,
    dbname: str,
    shards: str,
    replicas: str,
    mailhost: str,
    autoadmin: bool,
    skiponexist: bool,
):
    click.echo("Welcome to the Apache Kibble setup script!")

    admin_name = "admin@kibble"
    admin_pass = "kibbleAdmin"
    if not autoadmin:
        admin_name = get_user_input(
            "Enter an email address for the administrator account: "
        )
        admin_pass = get_user_input(
            "Enter a password for the administrator account: ", secure=True
        )

    # Create Elasticsearch index
    # Retry in case ES is not yet up
    click.echo(f"Elasticsearch: {uri}")
    for attempt in tenacity.Retrying(
        retry=tenacity.retry_if_exception_type(exception_types=Exception),
        wait=tenacity.wait_fixed(10),
        stop=tenacity.stop_after_attempt(10),
        reraise=True,
    ):
        with attempt:
            click.echo("Trying to create ES index...")
            create_es_index(
                conn_uri=uri,
                dbname=dbname,
                shards=int(shards),
                replicas=int(replicas),
                admin_name=admin_name,
                admin_pass=admin_pass,
                skiponexist=skiponexist,
            )
    click.echo()
    click.echo("All done, Kibble should...work now :)")

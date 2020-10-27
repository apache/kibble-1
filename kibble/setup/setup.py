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

import sys
import os
import argparse
import logging
from getpass import getpass

import tenacity
import bcrypt
import json
from elasticsearch import Elasticsearch

from kibble.configuration import conf


KIBBLE_VERSION = conf.get("api", "version")
KIBBLE_DB_VERSION = conf.get("api", "database")  # database revision

if sys.version_info <= (3, 3):
    print("This script requires Python 3.4 or higher")
    sys.exit(-1)


# Arguments for non-interactive setups like docker
def get_parser():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "-e",
        "--conn-uri",
        help="Pre-defined connection uri for ElasticSearch.",
        default=conf.get("elasticsearch", "conn_uri"),
    )
    arg_parser.add_argument(
        "-d",
        "--dbname",
        help="Pre-defined Database prefix. Default: kibble",
        default=conf.get("elasticsearch", "dbname"),
    )
    arg_parser.add_argument(
        "-s",
        "--shards",
        help="Predefined number of ES shards, Default: 5",
        default=conf.get("elasticsearch", "shards"),
    )
    arg_parser.add_argument(
        "-r",
        "--replicas",
        help="Predefined number of replicas for ES. Default: 1",
        default=conf.get("elasticsearch", "replicas"),
    )
    arg_parser.add_argument(
        "-m",
        "--mailhost",
        help="Pre-defined mail server host. Default: localhost:25",
        default=conf.get("mail", "mailhost"),
    )
    arg_parser.add_argument(
        "-a",
        "--autoadmin",
        action="store_true",
        help="Generate generic admin account. Default: False",
        default=False,
    )
    arg_parser.add_argument(
        "-k",
        "--skiponexist",
        action="store_true",
        help="Skip DB creation if DBs exist. Defaul: True",
        default=True,
    )
    return arg_parser


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
        os.path.dirname(os.path.realpath(__file__)), "mappings.json"
    )
    with open(mappings_json, "r") as f:
        mappings = json.load(f)

    es = Elasticsearch([conn_uri], max_retries=5, retry_on_timeout=True)

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
    print(f"Indices created!")
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


def get_user_input(msg: str, secure: bool = False):
    value = None
    while not value:
        value = getpass(msg) if secure else input(msg)
    return value


def print_configuration(args):
    print(
        "Configuring Apache Kibble elasticsearch instance with the following arguments:"
    )
    print(f"- conn_uri: {args.conn_uri}")
    print(f"- dbname: {args.dbname}")
    print(f"- shards: {int(args.shards)}")
    print(f"- replicas: {int(args.replicas)}")
    print()


def main():
    """
    The main Kibble setup logic. Using users input we create:
    - Elasticsearch indexes used by Apache Kibble app
    - Configuration yaml file
    """
    parser = get_parser()
    args = parser.parse_args()

    print("Welcome to the Apache Kibble setup script!")
    print_configuration(args)

    admin_name = "admin@kibble"
    admin_pass = "kibbleAdmin"
    if not args.autoadmin:
        admin_name = get_user_input(
            "Enter an email address for the administrator account:"
        )
        admin_pass = get_user_input(
            "Enter a password for the administrator account:", secure=True
        )

    # Create Elasticsearch index
    # Retry in case ES is not yet up
    print(f"Elasticsearch: {args.conn_uri}")
    for attempt in tenacity.Retrying(
        retry=tenacity.retry_if_exception_type(exception_types=Exception),
        wait=tenacity.wait_fixed(10),
        stop=tenacity.stop_after_attempt(10),
        reraise=True,
    ):
        with attempt:
            print("Trying to create ES index...")
            create_es_index(
                conn_uri=args.conn_uri,
                dbname=args.dbname,
                shards=int(args.shards),
                replicas=int(args.replicas),
                admin_name=admin_name,
                admin_pass=admin_pass,
                skiponexist=args.skiponexist,
            )
    print()
    print("All done, Kibble should...work now :)")


if __name__ == "__main__":
    main()

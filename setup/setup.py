#!/usr/bin/env python3
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

KIBBLE_VERSION = '0.1.0' # ABI/API compat demarcation.
KIBBLE_DB_VERSION = 2 # Second database revision

import sys

if sys.version_info <= (3, 3):
    print("This script requires Python 3.4 or higher")
    sys.exit(-1)

import os
import getpass
import subprocess
import argparse
import shutil
import yaml
import bcrypt
import json

mappings = json.load(open("mappings.json"))
myyaml = yaml.load(open("kibble.yaml.sample"))

dopip = False
try:
    from elasticsearch import Elasticsearch
    from elasticsearch import VERSION as ES_VERSION
    ES_MAJOR = ES_VERSION[0]
except:
    dopip = True
    
if dopip and (getpass.getuser() != "root"):
    print("It looks like you need to install some python modules first")
    print("Either run this as root to do so, or run: ")
    print("pip3 install elasticsearch certifi bcrypt")
    sys.exit(-1)

elif dopip:
    print("Before we get started, we need to install some modules")
    print("Hang on!")
    try:
        subprocess.check_call(('pip3','install','elasticsearch', 'certifi', 'bcrypt'))
        from elasticsearch import Elasticsearch
    except:
        print("Oh dear, looks like this failed :(")
        print("Please install elasticsearch and certifi before you try again:")
        print("pip install elasticsearch certifi")
        sys.exit(-1)


# Arguments for non-interactive setups like docker
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("-e", "--hostname", help="Pre-defined hostname for ElasticSearch (docker setups)")
arg_parser.add_argument("-p", "--port", help="Pre-defined port for ES (docker setups)")
arg_parser.add_argument("-d", "--dbname", help="Pre-defined Database prefix (docker setups)")
arg_parser.add_argument("-s", "--shards", help="Predefined number of ES shards (docker setups)")
arg_parser.add_argument("-r", "--replicas", help="Predefined number of replicas for ES (docker setups)")
arg_parser.add_argument("-m", "--mailhost", help="Pre-defined mail server host (docker setups)")
arg_parser.add_argument("-a", "--autoadmin", action='store_true', help="Generate generic admin account (docker setups)")
arg_parser.add_argument("-k", "--skiponexist", action='store_true', help="Skip DB creation if DBs exist (docker setups)")
args = arg_parser.parse_args()

print("Welcome to the Apache Kibble setup script!")
print("Let's start by determining some settings...")
print("")


hostname = args.hostname or ""
port = int(args.port) if args.port else 0
dbname = args.dbname or ""
mlserver = args.mailhost or ""
mldom = ""
wc = ""
genname = ""
wce = False
shards = int(args.shards) if args.shards else 0
replicas = int(args.replicas) if args.replicas else -1

while hostname == "":
    hostname = input("What is the hostname of the ElasticSearch server? [localhost]: ")
    if hostname == "":
        print("Using default; localhost")
        hostname = "localhost"
while port < 1:
    try:
        port = input("What port is ElasticSearch listening on? [9200]: ")
        if port == "":
            print("Using default; 9200")
            port = 9200
        port = int(port)
    except ValueError:
        pass

while dbname == "":
    dbname = input("What would you like to call the DB index [kibble]: ")
    if dbname == "":
        print("Using default; kibble")
        dbname = "kibble"
        
while mlserver == "":
    mlserver = input("What is the hostname of the outgoing mailserver? [localhost:25]: ")
    if mlserver == "":
        print("Using default; localhost:25")
        mlserver = "localhost:25"
    
while shards < 1:
    try:
        shards = input("How many shards for the ElasticSearch index? [5]:")
        if shards == "":
            print("Using default; 5")
            shards = 5
        shards = int(shards)
    except ValueError:
        pass

while replicas < 0:
    try:
        replicas = input("How many replicas for each shard? [1]: ")
        if replicas == "":
            print("Using default; 1")
            replicas = 1
        replicas = int(replicas)
    except ValueError:
        pass

adminName = ""
adminPass = ""
if args.autoadmin:
    adminName = "admin@kibble"
    adminPass = "kibbleAdmin"
while adminName == "":
    adminName = input("Enter an email address for the adminstrator account: ")
while adminPass == "":
    adminPass = input("Enter a password for the adminstrator account: ")
    
print("Okay, I got all I need, setting up Kibble...")

def createIndex():
    global mappings
    es = Elasticsearch([
        {
            'host': hostname,
            'port': port,
            'use_ssl': False,
            'url_prefix': ''
        }],
        max_retries=5,
        retry_on_timeout=True
        )

    es6 = True if int(es.info()['version']['number'].split('.')[0]) >= 6 else False
    es7 = True if int(es.info()['version']['number'].split('.')[0]) >= 7 else False
    if not es6:
        print("New Kibble installations require ElasticSearch 6.x or newer! You appear to be running %s!" % es.info()['version']['number'])
        sys.exit(-1)
    # If ES >= 7, _doc is invalid and mapping should be rooted
    if es7:
        mappings['mappings'] = mappings['mappings']['_doc']
    # Check if index already exists
    if es.indices.exists(dbname+"_api"):
        if args.skiponexist: # Skip this is DB exists and -k added
            print("DB prefix exists, but --skiponexist used, skipping this step.")
            return
        print("Error: ElasticSearch DB prefix '%s' already exists!" % dbname)
        sys.exit(-1)

    types = [
        'api',
        # ci_*: CI service stats
        'ci_build',
        'ci_queue',
        # code_* + evolution + file_history: git repo stats
        'code_commit',
        'code_commit_unique',
        'code_modification',
        'evolution',
        'file_history',
        # forum_*: forum stats (SO, Discourse, Askbot etc)
        'forum_post',
        'forum_topic',
        # GitHub stats
        'ghstats',
        # im_*: Instant messaging stats
        'im_stats',
        'im_ops',
        'im_msg',
        'issue',
        'logstats',
        # email, mail*: Email statitics
        'email',
        'mailstats',
        'mailtop',
        # organisation, view, source, publish: UI Org DB
        'organisation',
        'view',
        'publish',
        'source',
        # stats: Miscellaneous stats
        'stats',
        # social_*: Twitter, Mastodon, Facebook etc
        'social_follow',
        'social_followers',
        'social_follower',
        'social_person',
        # uisession, useraccount, message: UI user DB
        'uisession',
        'useraccount',
        'message',
        # person: contributor DB
        'person',
    ]
    
    for t in types:
        iname = "%s_%s" % (dbname, t)
        print("Creating index " + iname)
    
        settings = {
            "number_of_shards" :   shards,
            "number_of_replicas" : replicas
        }
    
        
        res = es.indices.create(index = iname, body = {
                    "mappings" : mappings['mappings'],
                    "settings": settings
                }
            )
        
    print("Indices created! %s " % res)
    
    salt = bcrypt.gensalt()
    pwd = bcrypt.hashpw(adminPass.encode('utf-8'), salt).decode('ascii')
    print("Creating administrator account")
    doc = {
            'email': adminName,                 # Username (email)
            'password': pwd,              # Hashed password
            'displayName': "Administrator",     # Display Name
            'organisations': [],                # Orgs user belongs to (default is none)
            'ownerships': [],                   # Orgs user owns (default is none)
            'defaultOrganisation': None,        # Default org for user
            'verified': True,                   # Account verified via email?
            'userlevel': "admin"                # User level (user/admin)
        }
    dbdoc = {
        'apiversion': KIBBLE_VERSION,           # Log current API version
        'dbversion': KIBBLE_DB_VERSION          # Log the database revision we accept (might change!)
    }
    es.index(index=dbname+'_useraccount', doc_type = '_doc', id = adminName, body = doc)
    es.index(index=dbname+'_api', doc_type = '_doc', id = 'current', body = dbdoc)
    print("Account created!")

try:
    import logging
    # elasticsearch logs lots of warnings on retries/connection failure
    logging.getLogger("elasticsearch").setLevel(logging.ERROR)
    createIndex()
    
     
except Exception as e:
    print("Index creation failed: %s" % e)
    sys.exit(1)

kibble_yaml = '../api/yaml/kibble.yaml'

if os.path.exists(kibble_yaml):
    print("%s already exists! Writing to %s.tmp instead" % (kibble_yaml, kibble_yaml))
    kibble_yaml = kibble_yaml + ".tmp"
    

print("Writing Kibble config (%s)" % kibble_yaml)

m = mlserver.split(':')
if len(m) == 1:
    m.append(25)
    
myconfig = {
    'api': {
        'version': KIBBLE_VERSION,
        'database': KIBBLE_DB_VERSION
    },
    'elasticsearch': {
        'host': hostname,
        'port': port,
        'ssl': False,
        'dbname': dbname
    },
    'mail': {
        'mailhost': m[0],
        'mailport': m[1],
        'sender': 'Kibble <noreply@kibble.kibble>'
    },
    'accounts': {
        'allowSignup': True,
        'verify': True
    }
}

with open(kibble_yaml, "w") as f:
    f.write(yaml.dump(myconfig, default_flow_style = False))
    f.close()

    
print("All done, Kibble should...work now :)")


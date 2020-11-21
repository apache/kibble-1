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

from urllib.parse import urlparse

import bcrypt
import elasticsearch

from kibble.configuration import conf


class ESDatabase:
    def __init__(self):
        self.dbname = conf.get("elasticsearch", "dbname")
        parsed = urlparse(conf.get("elasticsearch", "conn_uri"))
        es_host = {
            "host": parsed.hostname,
            "port": parsed.port,
            "use_ssl": conf.getboolean("elasticsearch", "ssl"),
            "verify_certs": False,
            "url_prefix": conf.get("elasticsearch", "uri"),
            "http_auth": conf.get("elasticsearch", "auth") or None,
        }
        self.es = elasticsearch.Elasticsearch(
            hosts=[es_host], max_retries=5, retry_on_timeout=True
        )

    def create_index(self, doc_type: str, id_: str, body: dict):
        self.es.index(index=self.dbname, doc_type=doc_type, id=id_, body=body)


def make_account_cmd(
    username: str,
    password: str,
    admin: bool = False,
    adminorg: bool = False,
    org: str = None,
) -> None:
    """
    Create user kibble account.

    :param username: username for login for example email
    :param password: password used for login
    :param admin: set to true if created user should has admin access level
    :param adminorg: organization user owns
    :param org: organisation user belongs to
    """
    orgs = [org] or []
    aorgs = [adminorg] if adminorg else []

    salt = bcrypt.gensalt()
    pwd = bcrypt.hashpw(password.encode("utf-8"), salt).decode("ascii")
    doc = {
        "email": username,
        "password": pwd,
        "displayName": username,
        "organisations": orgs,
        "ownerships": aorgs,
        "defaultOrganisation": None,  # Default org for user
        "verified": True,  # Account verified via email?
        "userlevel": "admin" if admin else "user",
    }
    db = ESDatabase()
    db.create_index(doc_type="useraccount", id_=username, body=doc)
    print("Account created!")

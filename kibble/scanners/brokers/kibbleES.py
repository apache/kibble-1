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
from urllib.parse import urlparse

import elasticsearch
import elasticsearch.helpers

from kibble.configuration import conf

KIBBLE_DB_VERSION = 2  # Current DB struct version
ACCEPTED_DB_VERSIONS = [1, 2]  # Versions we know how to work with.


class KibbleESWrapper:
    """
    Class for rewriting old-style queries to the new ones,
    where doc_type is an integral part of the DB name
    """

    def __init__(self, ES):
        self.ES = ES
        self.indices = self.indicesClass(ES)

    def get(self, index, doc_type, id):
        return self.ES.get(index=index + "_" + doc_type, doc_type="_doc", id=id)

    def exists(self, index, doc_type, id):
        return self.ES.exists(index=index + "_" + doc_type, doc_type="_doc", id=id)

    def delete(self, index, doc_type, id):
        return self.ES.delete(index=index + "_" + doc_type, doc_type="_doc", id=id)

    def index(self, index, doc_type, id, body):
        return self.ES.index(
            index=index + "_" + doc_type, doc_type="_doc", id=id, body=body
        )

    def update(self, index, doc_type, id, body):
        return self.ES.update(
            index=index + "_" + doc_type, doc_type="_doc", id=id, body=body
        )

    def search(self, index, doc_type, size=100, body=None):
        return self.ES.search(
            index=index + "_" + doc_type, doc_type="_doc", size=size, body=body
        )

    def count(self, index, doc_type, body=None):
        return self.ES.count(index=index + "_" + doc_type, doc_type="_doc", body=body)

    class indicesClass:
        """ Indices helper class """

        def __init__(self, ES):
            self.ES = ES

        def exists(self, index):
            return self.ES.indices.exists(index=index)


class KibbleESWrapperSeven:
    """
    Class for rewriting old-style queries to the new ones,
    where doc_type is an integral part of the DB name and NOT USED (>= 7.x)
    """

    def __init__(self, ES):
        self.ES = ES
        self.indices = self.indicesClass(ES)

    def get(self, index, doc_type, id):
        return self.ES.get(index=index + "_" + doc_type, id=id)

    def exists(self, index, doc_type, id):
        return self.ES.exists(index=index + "_" + doc_type, id=id)

    def delete(self, index, doc_type, id):
        return self.ES.delete(index=index + "_" + doc_type, id=id)

    def index(self, index, doc_type, id, body):
        return self.ES.index(index=index + "_" + doc_type, id=id, body=body)

    def update(self, index, doc_type, id, body):
        return self.ES.update(index=index + "_" + doc_type, id=id, body=body)

    def search(self, index, doc_type, size=100, body=None):
        return self.ES.search(index=index + "_" + doc_type, size=size, body=body)

    def count(self, index, doc_type, body=None):
        return self.ES.count(index=index + "_" + doc_type, body=body)

    class indicesClass:
        """ Indices helper class """

        def __init__(self, ES):
            self.ES = ES

        def exists(self, index):
            return self.ES.indices.exists(index=index)


class KibbleBit:
    """ KibbleBit class with direct ElasticSearch access """

    def __init__(self, broker, organisation, tid):
        self.organisation = organisation
        self.broker = broker
        self.json_queue = []
        self.queueMax = 1000  # Entries to keep before bulk pushing
        self.pluginname = ""
        self.tid = tid
        self.dbname = conf.get("elasticsearch", "database")

    def __del__(self):
        """ On unload/delete, push the last chunks of data to ES """
        if self.json_queue:
            print("Pushing stragglers")
            self.bulk()

    def pprint(self, string, err=False):
        line = "[thread#%i:%s]: %s" % (self.tid, self.pluginname, string)
        if err:
            sys.stderr.write(line + "\n")
        else:
            print(line)

    def update_source(self, source):
        """ Updates a source document, usually with a status update """
        self.broker.DB.index(
            index=self.dbname,
            doc_type="source",
            id=source["sourceID"],
            body=source,
        )

    def get(self, doctype, docid):
        """ Fetches a document from the DB """
        doc = self.broker.DB.get(
            index=self.dbname,
            doc_type=doctype,
            id=docid,
        )
        if doc:
            return doc["_source"]
        return None

    def exists(self, doctype, docid):
        """ Checks whether a document already exists or not """
        return self.broker.DB.exists(
            index=self.dbname,
            doc_type=doctype,
            id=docid,
        )

    def index(self, doctype, docid, document):
        """ Adds a new document to the index """
        dbname = self.dbname
        self.broker.DB.index(index=dbname, doc_type=doctype, id=docid, body=document)

    def append(self, t, doc):
        """ Append a document to the bulk push queue """
        if not "id" in doc:
            sys.stderr.write("No doc ID specified!\n")
            return
        doc["doctype"] = t
        self.json_queue.append(doc)
        # If we've crossed the bulk limit, do a push
        if len(self.json_queue) > self.queueMax:
            print("Bulk push forced")
            self.bulk()

    def bulk(self):
        """ Push pending JSON objects in the queue to ES"""
        xjson = self.json_queue
        js_arr = []
        self.json_queue = []
        for entry in xjson:
            js = entry
            doc = js
            js["@version"] = 1
            dbname = self.dbname
            if self.broker.noTypes:
                dbname += "_%s" % js["doctype"]
                js_arr.append(
                    {
                        "_op_type": "update" if js.get("upsert") else "index",
                        "_index": dbname,
                        "_type": "_doc",
                        "_id": js["id"],
                        "doc" if js.get("upsert") else "_source": doc,
                        "doc_as_upsert": True,
                    }
                )
            else:
                js_arr.append(
                    {
                        "_op_type": "update" if js.get("upsert") else "index",
                        "_index": dbname,
                        "_type": js["doctype"],
                        "_id": js["id"],
                        "doc" if js.get("upsert") else "_source": doc,
                        "doc_as_upsert": True,
                    }
                )
        try:
            elasticsearch.helpers.bulk(self.broker.oDB, js_arr)
        except Exception as err:
            print("Warning: Could not bulk insert: %s" % err)


class KibbleOrganisation:
    """ KibbleOrg with direct ElasticSearch access """

    def __init__(self, broker, org):
        """ Init an org, set up ElasticSearch for KibbleBits later on """

        self.broker = broker
        self.id = org
        self.dbname = conf.get("elasticsearch", "database")

    def sources(self, sourceType=None, view=None):
        """ Get all sources or sources of a specific type for an org """
        s = []
        # Search for all sources of this organisation
        mustArray = [{"term": {"organisation": self.id}}]
        if view:
            res = self.broker.DB.get(
                index=self.dbname,
                doc_type="view",
                id=view,
            )
            if res:
                mustArray.append({"terms": {"sourceID": res["_source"]["sourceList"]}})
        # If we want a specific source type, amend the search criteria
        if sourceType:
            mustArray.append({"term": {"type": sourceType}})
        # Run the search, fetch all results, 9999 max. TODO: Scroll???
        res = self.broker.DB.search(
            index=self.dbname,
            doc_type="source",
            size=9999,
            body={"query": {"bool": {"must": mustArray}}, "sort": {"sourceURL": "asc"}},
        )

        for hit in res["hits"]["hits"]:
            if sourceType is None or hit["_source"]["type"] == sourceType:
                s.append(hit["_source"])
        return s


class Broker:
    """Master Kibble Broker Class for direct ElasticSearch access."""

    def __init__(self):
        conn_uri = conf.get("elasticsearch", "conn_uri")
        parsed = urlparse(conf.get("elasticsearch", "conn_uri"))
        self.dbname = conf.get("elasticsearch", "dbname")

        user = conf.get("elasticsearch", "user", fallback=None)
        password = conf.get("elasticsearch", "password", fallback=None)
        auth = (user, password) if user else None

        print(f"Connecting to ElasticSearch database at {conn_uri}")
        es = elasticsearch.Elasticsearch(
            [
                {
                    "host": parsed.hostname,
                    "port": parsed.port,
                    "use_ssl": conf.getboolean("elasticsearch", "ssl"),
                    "verify_certs": False,
                    "url_prefix": conf.get("elasticsearch", "uri"),
                    "http_auth": auth,
                }
            ],
            max_retries=5,
            retry_on_timeout=True,
        )
        es_info = es.info()
        print("Connected!")
        self.DB = es
        self.oDB = es  # Original ES class, always. the .DB may change
        self.bitClass = KibbleBit
        # This bit is required since ES 6.x and above don't like document types
        self.noTypes = (
            True if int(es_info["version"]["number"].split(".")[0]) >= 6 else False
        )
        self.seven = (
            True if int(es_info["version"]["number"].split(".")[0]) >= 7 else False
        )
        if self.noTypes:
            print("This is a type-less DB, expanding database names instead.")
            if self.seven:
                print("We're using ES >= 7.x, NO DOC_TYPE!")
                es = KibbleESWrapperSeven(es)
            else:
                es = KibbleESWrapper(es)
            self.DB = es
            if not es.indices.exists(index=self.dbname + "_api"):
                raise SystemExit(
                    f"Could not find database group {self.dbname}_* in ElasticSearch!"
                )
        else:
            print("This DB supports types, utilizing..")
            if not es.indices.exists(index=self.dbname):
                raise SystemExit(
                    f"Could not find database {self.dbname} in ElasticSearch!"
                )
        apidoc = es.get(index=self.dbname, doc_type="api", id="current")["_source"]
        apidoc_db_version = int(apidoc["dbversion"])

        # We currently accept and know how to use DB versions 1 and 2.
        if apidoc_db_version not in ACCEPTED_DB_VERSIONS:
            if apidoc_db_version > KIBBLE_DB_VERSION:
                raise SystemExit(
                    "The database '%s' uses a newer structure format (version %u) than the scanners "
                    "(version %u). Please upgrade your scanners.\n"
                    % (self.dbname, apidoc_db_version, KIBBLE_DB_VERSION)
                )
            if apidoc_db_version < KIBBLE_DB_VERSION:
                raise SystemExit(
                    "The database '%s' uses an older structure format (version %u) than the scanners "
                    "(version %u). Please upgrade your main Kibble server.\n"
                    % (self.dbname, apidoc_db_version, KIBBLE_DB_VERSION)
                )

    def organisations(self):
        """ Return a list of all organisations """

        # Run the search, fetch all orgs, 9999 max. TODO: Scroll???
        res = self.DB.search(
            index=self.dbname,
            doc_type="organisation",
            size=9999,
            body={"query": {"match_all": {}}},
        )

        for hit in res["hits"]["hits"]:
            org = hit["_source"]["id"]
            orgClass = KibbleOrganisation(self, org)
            yield orgClass

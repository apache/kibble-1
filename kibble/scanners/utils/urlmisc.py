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

"""
This is a Kibble miscellaneous URL functions plugin.
"""
import base64
import gzip
import io
import subprocess
import tempfile
import urllib.request


def unzip(url, creds=None, cookie=None):
    """Attempts to download an unzip an archive. Returns the temporary file path of the unzipped contents"""
    headers = {}
    if creds:
        auth = str(base64.encodestring(bytes(creds)).replace("\n", ""))
        headers = {
            "Content-type": "application/json",
            "Accept": "*/*",
            "Authorization": "Basic %s" % auth,
        }
    if cookie:
        headers = {
            "Content-type": "application/json",
            "Accept": "*/*",
            "Cookie": cookie,
        }
    request = urllib.request.Request(url, headers=headers)
    # Try fetching via python, fall back to wget (redhat == broken!)
    decompressedFile = None
    try:
        result = urllib.request.urlopen(request)
        compressedFile = io.BytesIO()
        compressedFile.write(result.read())
        compressedFile.seek(0)
        decompressedFile = gzip.GzipFile(fileobj=compressedFile, mode="rb")
    except urllib.error.HTTPError as err:
        # We're not interested in 404s, only transport errors
        if err.code != 404 and err.code != 401:
            tmpfile = tempfile.NamedTemporaryFile(mode="w+b", buffering=1, delete=False)
            subprocess.check_call(("/usr/bin/wget", "-O", tmpfile.name, url))

            try:
                compressedFile = open("/tmp/kibbletmp.gz", "rb")
                if compressedFile.read(2) == "\x1f\x8b":
                    compressedFile.seek(0)
                    decompressedFile = gzip.GzipFile(fileobj=compressedFile, mode="rb")
                else:
                    compressedFile.close()
                    return tmpfile.name
            except:
                # Probably not a gzipped file!
                decompressedFile = open(tmpfile.name, "rb")
    if decompressedFile:
        tmpfile = tempfile.NamedTemporaryFile(mode="w+b", buffering=1, delete=False)
        tmpfile.write(decompressedFile.read())
        tmpfile.flush()
        tmpfile.close()
        return tmpfile.name
    return None

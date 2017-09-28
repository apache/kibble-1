#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
Kibble API scripts library:

    oauth:          oauth manager

"""

import importlib
import os
# Define all the submodules we have

rootpath = os.path.dirname(__file__)
print("Reading pages from %s" % rootpath)

# Import each submodule into a hash called 'handlers'
handlers = {}

def loadPage(path):
    for el in os.listdir(path):
        filepath = os.path.join(path, el)
        if el.find("__") == -1:
            if os.path.isdir(filepath):
                loadPage(filepath)
            else:
                p = filepath.replace(rootpath, "")[1:].replace('/', '.')[:-3]
                xp = p.replace('.', '/')
                print("Loading endpoint pages.%s as %s" % (p, xp))
                handlers[xp] = importlib.import_module("pages.%s" % p)
    
loadPage(rootpath)
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

# Define all the submodules we have
__all__ = [
    'account',
    'code-changes',
    'code-evolution',
    'code-trends',
    'commits',
    'committers',
    'issue-trends',
    'issues',
    'session',
    'sloc',
    'sources',
    'top-commits',
    'top-sloc',
    'views',
    'widgets'
    ]

# Import each submodule into a hash called 'handlers'
handlers = {}
for p in __all__:
    handlers[p] = importlib.import_module("pages.%s" % p)
    
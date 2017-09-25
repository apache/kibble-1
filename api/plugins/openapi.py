#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

"""
This is the OpenAPI validator library.
Validates input using the OpenAPI specification version 3 from
https://github.com/OAI/OpenAPI-Specification (a simplified version, ahem)
"""

import yaml
import json
import functools
import operator
import re

class OpenAPIException(Exception):
    def __init__(self, message):
        self.message = message

# Python type names to JSON type names
py2JSON = {
    'int':      'integer',
    'float':    'float',
    'str':      'string',
    'list':     'array',
    'dict':     'object',
    'bool':     'boolean'
}
        
class OpenAPI():
    def __init__(self, APIFile):
        """ Instantiates an OpenAPI validator given a YAML specification"""
        if APIFile.endswith(".json") or APIFile.endswith(".js"):
            self.API = json.load(open(APIFile))
        else:
            self.API = yaml.load(open(APIFile))
        
    def validateType(self, field, value, ftype):
        """ Validate a single field value against an expected type """
        
        # Get type of value, convert to JSON name of type.
        pyType = type(value).__name__
        jsonType = py2JSON[pyType] if pyType in py2JSON else pyType
        
        # Check if type matches
        if ftype != jsonType:
            raise OpenAPIException("OpenAPI mismatch: Field '%s' was expected to be %s, but was really %s!" % (field, ftype, jsonType))
        
    def validateSchema(self, pdef, formdata, schema = None):
        """ Validate (sub)parameters against OpenAPI specs """
        
        # allOf: list of schemas to validate against
        if 'allOf' in pdef:
            for subdef in pdef['allOf']:
                self.validateParams(subdef, formdata)
        
        where = "JSON body"
        # Symbolic link??
        if 'schema' in pdef:
            schema = pdef['schema']['$ref']
        if '$ref' in pdef:
            schema = pdef['$ref']
        if schema:
            # #/foo/bar/baz --> dict['foo']['bar']['baz']
            pdef = functools.reduce(operator.getitem, schema.split('/')[1:], self.API)
            where = "item matching schema %s" % schema
        
        # Check that all required fields are present
        if 'required' in pdef:
            for field in pdef['required']:
                if not field in formdata:
                    raise OpenAPIException("OpenAPI mismatch: Missing input field '%s' in %s!" % (field, where))
        
        # Now check for valid format of input data
        for field in formdata:
            if field not in pdef['properties']:
                raise OpenAPIException("Unknown input field '%s' in %s!" % (field, where))
            if 'type' not in pdef['properties'][field]:
                raise OpenAPIException("OpenAPI mismatch: Field '%s' was found in api.yaml, but no format was specified in specs!" % field)
            ftype = pdef['properties'][field]['type']
            self.validateType(field, formdata[field], ftype)
            
            # Validate sub-arrays
            if ftype == 'array' and 'items' in pdef['properties'][field]:
                for item in formdata[field]:
                    if '$ref' in pdef['properties'][field]['items']:
                        self.validateParams(pdef['properties'][field]['items'], item)
                    else:
                        self.validateType(field, formdata[field], pdef['properties'][field]['items']['type'])
            
            # Validate sub-hashes
            if ftype == 'hash' and 'schema' in pdef['properties'][field]:
                self.validateParams(pdef['properties'][field], formdata[field])
    def validateParameters(self, defs, formdata):
        #
        pass
        
    def validate(self, method = "GET", path = "/foo", formdata = None):
        """ Validate the request method and input data against the OpenAPI specification """
        
        # Make sure we're not dealing with a dynamic URL.
        # If we find /foo/{key}, we fold that into the form data
        # and process as if it's a json input field for now.
        if not self.API['paths'].get(path):
            for xpath in self.API['paths']:
                pathRE = re.sub(r"\{(.+?)\}", r"(?P<\1>[^/]+)", xpath)
                m = re.match(pathRE, path)
                if m:
                    for k,v  in m.groupdict().items():
                        formdata[k] = v
                    path = xpath
                    break
                
        if self.API['paths'].get(path):
            defs = self.API['paths'].get(path)
            method = method.lower()
            if method in defs:
                mdefs = defs[method]
                if formdata and 'parameters' in mdefs:
                    self.validateParameters(mdefs['parameters'], formdata)
                elif formdata and 'requestBody' not in mdefs:
                    raise OpenAPIException("OpenAPI mismatch: JSON data is now allowed for this request type")
                elif formdata and 'requestBody' in mdefs and 'content' in mdefs['requestBody']:
                    
                    # SHORTCUT: We only care about JSON input for Kibble! Disregard other types
                    if not 'application/json' in mdefs['requestBody']['content']:
                        raise OpenAPIException ("OpenAPI mismatch: API endpoint accepts input, but no application/json definitions found in api.yaml!")
                    jdefs = mdefs['requestBody']['content']['application/json']
                    
                    # Check that required params are here
                    self.validateSchema(jdefs, formdata)
                
            else:
                raise OpenAPIException ("OpenAPI mismatch: Method %s is not registered for this API" % method)
        else:
            raise OpenAPIException("OpenAPI mismatch: Unknown API path '%s'!" % path)

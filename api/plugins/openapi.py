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

mcolors = {
    'PUT':      '#fca130',
    'DELETE':   '#f93e3e',
    'GET':      '#61affe',
    'POST':     '#49cc5c',
    'PATCH':    '#d5a37e'
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
                self.validateSchema(subdef, formdata)
        
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
            if 'properties' not in pdef or field not in pdef['properties'] :
                raise OpenAPIException("Unknown input field '%s' in %s!" % (field, where))
            if 'type' not in pdef['properties'][field]:
                raise OpenAPIException("OpenAPI mismatch: Field '%s' was found in api.yaml, but no format was specified in specs!" % field)
            ftype = pdef['properties'][field]['type']
            self.validateType(field, formdata[field], ftype)
            
            # Validate sub-arrays
            if ftype == 'array' and 'items' in pdef['properties'][field]:
                for item in formdata[field]:
                    if '$ref' in pdef['properties'][field]['items']:
                        self.validateSchema(pdef['properties'][field]['items'], item)
                    else:
                        self.validateType(field, formdata[field], pdef['properties'][field]['items']['type'])
            
            # Validate sub-hashes
            if ftype == 'hash' and 'schema' in pdef['properties'][field]:
                self.validateSchema(pdef['properties'][field], formdata[field])
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

    def dumpExamples(self, pdef, array = False):
        schema = None
        if 'schema' in pdef:
            if 'type' in pdef['schema'] and pdef['schema']['type'] == 'array':
                array = True
                schema = pdef['schema']['items']['$ref']
            else:
                schema = pdef['schema']['$ref']
        if '$ref' in pdef:
            schema = pdef['$ref']
        if schema:
            # #/foo/bar/baz --> dict['foo']['bar']['baz']
            pdef = functools.reduce(operator.getitem, schema.split('/')[1:], self.API)
        js = {}
        desc = {}
        if 'properties' in pdef:
            for k, v in pdef['properties'].items():
                if 'description' in v:
                    desc[k] = [v['type'], v['description']]
                if 'example' in v:
                    js[k] = v['example']
                elif 'items' in v:
                    if v['type'] == 'array':
                        js[k], foo = self.dumpExamples(v['items'], True)
                    else:
                        js[k], foo = self.dumpExamples(v['items'])
        return [js if not array else [js], desc]
        
    def toHTML(self):
        """ Blurps out the specs in a pretty HTML blob """
        print("""
<!DOCTYPE html>
<html lang="en">
<head>
</head>
<body>
""")
        li = "<h3>Overview:</h3><ul style='font-size: 12px; font-family: Open Sans, sans-serif;'>"
        for path, spec in sorted(self.API['paths'].items()):
            for method, mspec in sorted(spec.items()):
                method = method.upper()
                summary = mspec.get('summary', 'No summary available')
                linkname = "%s%s" % (method.lower(), path.replace('/', '-'))
                li += "<li><a href='#%s'>%s %s</a>: %s</li>\n" % (linkname, method, path, summary)
        li += "</ul>"
        print(li)
        for path, spec in sorted(self.API['paths'].items()):
            for method, mspec in sorted(spec.items()):
                method = method.upper()
                summary = mspec.get('summary', 'No summary available')
                resp = ""
                inp = ""
                inpvars = ""
                linkname = "%s%s" % (method.lower(), path.replace('/', '-'))
                if 'responses' in mspec:
                    for code, cresp in sorted(mspec['responses'].items()):
                        for ctype, pdef in cresp['content'].items():
                            xjs, desc = self.dumpExamples(pdef)
                            js = json.dumps(xjs, indent = 4)
                            resp += "<div style='float: left; width: 90%%;'><pre style='width: 600px;'><b>%s</b>:\n%s</pre>\n</div>\n" % (code, js)
                
                if 'requestBody' in mspec:
                    for ctype, pdef in mspec['requestBody']['content'].items():
                        xjs, desc = self.dumpExamples(pdef)
                        if desc:
                            for k, v in desc.items():
                                inpvars += "<kbd><b>%s:</b></kbd> (%s) <span style='font-size: 12px; font-family: Open Sans, sans-serif;'>%s</span><br/>\n" % (k, v[0], v[1])
                        js = json.dumps(xjs, indent = 4)
                        inp += "<div style='float: left; width: 90%%;'><h4>Input examples:</h4><blockquote><pre style='width: 600px;'><b>%s</b>:\n%s</pre></blockquote>\n</div>" % (ctype, js)
                    
                if inpvars:
                    inpvars = "<div style='float: left; width: 90%%;'><blockquote><pre style='width: 600px;'>%s</pre>\n</blockquote></div>" % inpvars

                
                print("""
                      <div id="%s" style="margin: 20px; display: flex; box-sizing: border-box; width: 900px; border-radius: 6px; border: 1px solid %s; font-family: sans-serif; background: %s30;">
                        <div style="min-height: 32px;">
                          <!-- method -->
                          
                          <div style="float: left; align-items: center; margin: 4px; border-radius: 5px; text-align: center; padding-top: 4px; height: 20px; width: 100px; color: #FFF; font-weight: bold; background: %s;">%s</div>
                          
                          <!-- path and summary -->
                          <span style="display: flex; padding-top: 6px;"><kbd><strong>%s</strong></kbd></span>
                          <div style="box-sizing: border-box; flex: 1; font-size: 13px; font-family: Open Sans, sans-serif; float: left; padding-top: 6px; margin-left: 20px;">
                          %s</div>
                          <div style="float: left; width: 90%%;display: %s; ">
                            <h4>JSON parameters:</h4>
                            %s
                            <br/>
                            %s
                          </div>
                          <div style="float: left; width: 90%%; ">
                            <h4>Response examples:</h4>
                            <blockquote>%s</blockquote>
                          </div>
                        </div>
                      </div>
                      """ % (linkname, mcolors[method], mcolors[method], mcolors[method], method, path, summary, "block" if inp else "none", inpvars, inp, resp))
                #print("%s %s: %s" % (method.upper(), path, mspec['summary']))
        print("</body></html>")
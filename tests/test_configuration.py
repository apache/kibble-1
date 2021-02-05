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

import pytest

from kibble.configuration import conf


# pylint: disable=no-self-use
class TestDefaultConfig:
    @pytest.mark.parametrize(
        "section, key, value",
        [
            ("accounts", "allowSignup", True),
            ("accounts", "verify", True),
            ("api", "database", 2),
            ("api", "version", "0.1.0"),
            ("elasticsearch", "conn_uri", "http://elasticsearch:9200"),
            ("mail", "mailhost", "localhost:25"),
        ],
    )
    def test_default_values(self, section, key, value):
        if isinstance(value, bool):
            config_value = conf.getboolean(section, key)
        elif isinstance(value, int):
            config_value = conf.getint(section, key)
        else:
            config_value = conf.get(section, key)

        assert config_value == value

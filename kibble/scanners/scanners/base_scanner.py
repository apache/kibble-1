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

from abc import abstractmethod

from loguru import logger

from kibble.scanners.brokers.kibbleES import KibbleBit


class BaseScanner:
    """
    Base scanner class. All scanners should inherit from it.
    """

    version: str
    title: str
    log = logger

    def __init__(self, kibble_bit: KibbleBit, source: dict):
        self.kibble_bit = kibble_bit
        self.source = source

    @property
    @abstractmethod
    def accepts(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def scan(self) -> None:
        raise NotImplementedError

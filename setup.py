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

import os
from importlib import util

from setuptools import find_packages, setup

# Kept manually in sync with kibble.version
spec = util.spec_from_file_location(
    "kibble.version", os.path.join("kibble", "version.py")
)  # noqa
mod = util.module_from_spec(spec)
spec.loader.exec_module(mod)  # type: ignore
version = mod.version  # type: ignore

DEVEL_REQUIREMENTS = ["black==20.8b1", "pre-commit==2.7.1", "pytest==6.1.1"]

INSTALL_REQUIREMENTS = [
    "bcrypt==3.2.0",
    "certifi==2020.6.20",
    "click==7.1.2",
    "elasticsearch==7.9.1",
    "gunicorn==20.0.4",
    "loguru==0.5.3",
    "psutil==5.7.3",
    "python-dateutil==2.8.1",
    "python-twitter==3.5",
    "PyYAML==5.3.1",
    "requests==2.25.0",
    "tenacity==6.2.0",
]

EXTRAS_REQUIREMENTS = {"devel": DEVEL_REQUIREMENTS}


def get_long_description():
    description = ""
    try:
        with open(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "README.md"),
            encoding="utf-8",
        ) as f:
            description = f.read()
    except FileNotFoundError:
        pass
    return description


def do_setup():
    """Perform the Kibble package setup."""
    setup(
        name="apache-kibble",
        description="Apache Kibble is a tool to collect, aggregate and visualize data about any software project.",
        long_description=get_long_description(),
        long_description_content_type="text/markdown",
        license="Apache License 2.0",
        version=version,
        packages=find_packages(include=["kibble*"]),
        package_data={"kibble": ["py.typed"], "kibble.api.yaml": ["*.yaml"]},
        include_package_data=True,
        zip_safe=False,
        entry_points={"console_scripts": ["kibble = kibble.__main__:main"]},
        install_requires=INSTALL_REQUIREMENTS,
        setup_requires=["docutils", "gitpython", "setuptools", "wheel"],
        extras_require=EXTRAS_REQUIREMENTS,
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Environment :: Console",
            "Environment :: Web Environment",
            "Intended Audience :: Developers",
            "Intended Audience :: System Administrators",
            "License :: OSI Approved :: Apache Software License",
            "Programming Language :: Python :: 3.8",
        ],
        author="Apache Software Foundation",
        author_email="dev@kibble.apache.org",
        url="https://kibble.apache.org/",
        download_url=f"https://archive.apache.org/dist/kibble/{version}",
        test_suite="setup.kibble_test_suite",
        python_requires="~=3.8",
        project_urls={
            "Documentation": "https://kibble.apache.org/docs/",
            "Bug Tracker": "https://github.com/apache/kibble/issues",
            "Source Code": "https://github.com/apache/kibble",
        },
    )


if __name__ == "__main__":
    do_setup()

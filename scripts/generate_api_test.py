import os

import yaml
from jinja2 import Template


test_case_template = '''
import os
import requests
import pytest

class TestKibbleAPI:{% filter indent(4, True) %}
base_url = "https://0.0.0.0:8080"
{% endfilter %}{% for test_name, path, method in data %}
@pytest.mark.xfail(reason="Not implemented :<")
def test{{test_name}}_{{method}}(self):
{% filter indent(4, True) %}"""
{{method | capitalize }}: {{ path }}
"""
url = os.path.join(self.base_url, "{{path}}")
response = requests.{{method}}(url)
assert response.status_code == requests.codes.ok

body = response.json()
expected_body = {}
assert body == expected_body
{% endfilter %}{% endfor %}
{% endfilter %}
'''


def render_tests(data):
    return Template(test_case_template).render(data=data)


def path_to_snake_case(path):
    symbols = ["/api/", "-", "{", "}", "/", "__"]
    for symbol in symbols:
        path = path.replace(symbol, "_")
    return path[:-1] if path[-1] == "_" else path


def read_openapi_spec():
    openapi_yaml = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        os.pardir,
        "api",
        "yaml",
        "openapi.yaml"
    )
    with open(openapi_yaml) as f:
        content = yaml.load(f)

    data = []
    for path, methods in content["paths"].items():
        data.extend([(path_to_snake_case(path), path, method) for method in methods])
    return data


if __name__ == '__main__':
    data = read_openapi_spec()

    test_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        os.pardir,
        "tests",
        "api",
        "test_handler.py"
    )
    with open(test_file, "w+") as f:
        f.write(render_tests(data))


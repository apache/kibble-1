# Building Kibble #

Kibble needs a few pieces put together before you can live-test changes:

 - cd to `ui/js/coffee/` and run `bash combine.sh` if you changes coffee
 - cd to `api/yaml/openapi` and run `python3 combine.py` for API changes,
   or your new API endpoints won't be registered in the openapi.yaml.
   Do __NOT__ modify openapi.yaml by hand, edit the right schema file or
   script comments to set API specs.

![Logo](/ui/images/kibble-logo.png)

# Kibble UI and Database Service

## Requirements

 * Python >= 3.4 (with elasticsearch, yaml, certifi libs)
 * A web server of your choice (apache, nginx, lighttp etc)
 * A WSGI capable server (apache with mod_wsgi, gunicorn etc)
 * An ElasticSearch instance

## Installation instructions

 * Make sure you have an ElasticSearch server set up first
 * Download the Kibble package (release or master, what do we care)
 * For new installations, cd to the `setup/` and run: `python3 setup.py` to set up the DB
 * Assuming you install in /var/www/kibble:
 * * Create a virtual host (apache, nginx etc) and point it to /var/www/kibble/ui/
 * * Set up WSGI for the /api/ directory, using /var/www/kibble/api/handler.py:application as mount point.
 * Enjoy!

### Using gunicorn for WSGI:
 
 You can use gunicorn (gunicorn3) for the WSGI application, by following these steps:
 * Add the following to your HTTPd vhost configuration: ProxyPass /api/ http://localhost:8080
 * in /var/www/kibble/api, run: `gunicorn3 -b 127.0.0.1:8080 -w 10 -t 120 -D handler:application`

Visiting $yourhost/api/ should now fire off WSGI via gunicorn.


# Kibble UI and Database Service

## Installation instructions

 * Download the Kibble package (release or master, what do we care)
 * Assuming you install in /var/www/kibble:
 * * Create a virtual host (apache, nginx etc) and point it to /var/www/kibble/ui/
 * * Set up WSGI for the /api/ directory, using /var/www/kibble/api/handler.py:application as mount point.
 * * Run /var/www/kibble/tools/setup.py on first setup
 * Enjoy!
 
### Using gunicorn for WSGI:
 
 You can use gunicorn (gunicorn3) for the WSGI application, by following these steps:
 * Add the following to your HTTPd vhost configuration: ProxyPass /api/ http://localhost:8080
 * in /var/www/kibble/api, run: 'gunicorn3 -b 127.0.0.1:8080 -w 10 -D handler:application`

Visiting $yourhost/api/ should now fire off WSGI via gunicorn.


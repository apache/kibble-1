# Usage Documentation #
## Setting Up the Base ##
### Understanding the Components ###
Kibble consists of two major components:

The Kibble Server (kibble)
   This is the main database and UI Server. It serves as the hub for the
   scanners to connect to, and provides the overall management of
   sources as well as the visualizations and API end points.
   
The Kibble Scanner Applications (kibble-scanners)
   This is a collection of scanning applications each designed to work
   with a specific type of resource (a git repo, a mailing list, a JIRA
   instance etc) and push copmpiled data objects to the Kibble Server.
   Some resources only have one scanner plugin, while others may have
   multiple plugins capable of dealing with specific aspects of a
   resource.
   
### Component Requirements ###
#### Server Component ####
As said, the main Kibble Server is a hub for scanners, and as such, is
only ever needed on one machine. It is recommended that, for large
instances of kibble, you place the application on a machine or VM with
sufficient resources to handle the database load and memory requirements.

As a rule of thumb, the Server does not require a lot of disk space
(enough to hold the compiled database), but it does require CPU and RAM.
The scanners require more disk space, but can operate with limited CPU
and RAM.

As an example, let os examine the Apache Kibble demo instance:

- 100 sources (git repos, mailing lists, bug trackers and so on)
- 3,5 million source objects currently (commits, emails, tickets etc)
- 10 concurrent users (actual people uing the web UI)

The recommended minimal specs for the Server component on an instance of
this size would be approximately 4-8GB RAM, 4 cores and at least 10GB
disk space. As this is a centralized component, you will want to spec
this to be able to efficiently deal with the entire database in memory
for best performance.

#### Scanner Component ####
The scanner components can either consist of one instance, or be spread
out in a clustered setup. Thus, the requirements can be spread out on
multiple machines or VMs. Scanners will auto-adjust the scanning speed
to match the number of CPU cores available to it; a scanner with two
cores available will run two simultaneous jobs, whereas a scanner with
eight cores will run eight simultaneous jobs to speed up processing.
A scanner will typically require somewhere between 512 and 1GB of memory,
and thus can safely run on a VM with 2GB memory (or less).

### Source Code Location ### 
*Apache Kibble does not currently have any releases.*
*You are however welcome to try out the development version.*

For the time being, we recommend that you use the ``master`` branch for
testing Kibble. This applies to both scanners and the server.

The Kibble Server can be found via our source repository at
https://github.com/apache/kibble

The Kibble Scanners can be found at
https://github.com/apache/kibble-scanners

### Installing the Server ### 
#### Prerequisits ####
Before you install the Kibble Server, please ensure you have the
following components installed and set up:

- An ElasticSearch instance, version 5.x or newer (5.x is currently
  preferred). Does not have to be on the same machine, but it may help
  speed up processing.
- A web server of your choice (Apache HTTP Server, NGINX, lighttp etc)
- Python 3.4 or newer with the following libraries installed:
- - elasticsearch
- - certifi
- - pyyaml
- - bcrypt
- Gunicorn for Python 3.x (often called gunicorn3) or mod_wsgi
#### Configuring and Priming the Kibble Instance ####
Once you have the components installed and Kibble downloaded, you will
need to prime the ElasticSearch instance and create a configuration file.

Assuming you wish to install kibble in /var/www/kibble, you would set it
up by issuing the following:

- ``git clone https://github.com/apache/kibble.git /var/www/kibble``
- ``cd /var/www/kibble/setup``
- ``python3 setup.py``
- Enter the configuration parameters the setup process asks for

This will set up the database, the configuration file, and create your
initial administrator account for the UI. You can later on do additional
configuration of the data server by editing the ``api/yaml/kibble.yaml``
file.

#### Setting up the Web UI ####
Once you have finished the initial setup, you will need to enable the
web UI. Kibble is built as a WSGI application, and as such you can
use mod_wsgi for apache, or proxy to Gunicorn. In this example, we will
be using the Apache HTTP Server and proxy to Gunicorn:

- Make sure you have mod_proxy and mod_proxy_http loaded (on
  debian/ubuntu, you would run: `a2enmod proxy_http`)
- Set up a virtual host in Apache:

::
  <VirtualHost *:80>
      # Set this to your domain, or add kibble.localhost to /etc/hosts
      ServerName kibble.localhost
      DocumentRoot /var/www/kibble/ui/
      # Proxy to gunicorn for /api/ below:
      ProxyPass /api/ http://localhost:8000/api/
   </VirtualHost> 
- Launch gunicorn as a daemon on port 8000:
``
   cd /var/www/kibble/api/
   gunicorn -w 10 -b 127.0.0.1:8000 handler:application -t 120 -D
``

Once httpd is (re)started, you should be able to browse to your new
Kibble instance.

### Installing Scanners ###
#### Pre-requisites ####

.. _cloc: https://github.com/AlDanial/cloc

The Kibble Scanners rely on the following packages:

- Python >= 3.4 with the following packages:
- - python3-yaml
- - python3-elasticsearch

The scanners require the following optional components if you wish to enable
git repository analysis:

- git binaries (GPL License)
- cloc_ version 1.70 or later (GPL License)

#### Configuring a Scanner Node ####

First, check out the scanner source in a file path of your choosing:

``git clone https://github.com/apache/kibble-scanners.git``

Then edit the ``conf/config.yaml`` file to match both the ElasticSearch
database used by the Kibble UI, as well as whatever file layout (data
and scratch dir) you wish to use on the scanner machine.
Remember that the scanner must have enough disk space to fully store
any resources you may be scanning. If you are scanning a large git repository,
the scanner should have sufficient disk space to store it locally.

If you plan to make use of the optional text analysis features of
Kibble, you should also configure the API service you will be using
(Watson/Azure/picoAPI etc).

#### Balacing Load Across Machines #### 

If you wish to spread out the analysis load over several machines/VMs,
you can do so by specifying a ``scanner.balance`` on each node. The balance
directive uses the syntax X/Y, where Y is the total number of nodes in
your scanner cluster, and X is the ID of the current scanner. Thus, if
you have decided to use four machines for scanning, the first would have
a balance of 1/4, the next would be 2/4, then 3/4 and finally 4/4 on the
last machine. This will balance the load and storage requirements evenly
across all machines.


.. _runscan:

### Running a Scan ###

Once you have both scanners and the data server set up, you can begin
scanning resources for data. Please refer to :ref:`configdatasources`
for how to set up various resources for scanning via the Web UI.

Scans can be iniated manually, but you may want to set up a cron job to
handle daily scans of resources. To start a scan on a scanner machine,
run the following: ``python3 src/kibble-scanner.py``

This will load all plugins and use them in a sensible order on each
resource that matches the appropriate type. The collected data will be
pushed to the main data server and be available for visualizations
instantly.

It may be worth your while to run the scanner inside a timer wrapper,
as such: ``time python3 src/kibble-scanner.py`` in order to gauge the
amount of time a scan will take, and adjusting your cron jobs to match
this.

## Set Up the Organization ##
Once you have Kibble and the Kibble Scanners set up. Open up the Kibble UI and log in 
with the email and password used set up Kibble. Once logged in, you will need to set up 
an Organization.

The first thing you will need to set up, in order to use Kibble, is an organisation that
will contain the projects you wish to survey. You can have multiple organisations in Kibble, 
and all organisations will be scanned, but the UI will only display statistics for the 
current (default) organisation you are using. You may switch between organisations at your 
leisure in the UI.

To create your first organisation, go to the “Organisation” tab in the top menu. In the 
Create a new organisation field set, you can then create a new organisation by filling in 
the required data. The organisation id is optional, but may be useful for helping users 
identify the organisation. Click the Create organisation button.This will set up a new 
organisation and set it as your default (current) one.

Once an organisation has been created, you can then add resources and users to it.

## Add Sources ##

After you have created an organisation, you can add sources to it. A source is a 
destination to scan; it can be a git repository, a JIRA instance, a mailing list 
and so on. To start adding sources, click on the Sources tab in the left hand menu 
on the Organisation page.

With all resource types, you can speed up things by adding multiple sources in one 
go by simply adding one source per line in the source text field.

The currently supported resource types are: GitHub, Git, PiperMail, Pony Mail, Gerrit, 
BugZilla, JIRA, Twitter, Jenkins CI, and Buildbot CI.

#### GitHub ####
This resource consists of GitHub repositories as well as issues/PRs that are contained within. Currently, you will need to add the full URL to the repo, including the .git part of it, such as: `https://github.com/apache/clerezza.git`. NOTE: If you intend to use more than 60 API calls per hour, which you probably do, you will need to add the credentials of a GitHub user to the source, in order to get a higher rate limit of 6,000 API calls per hour. You may use any anonymous account for this.

#### Git ####
This is a plain git repository (such as those served by the standard git daemon), and only scans repositories, not PRs/Issues. If basic auth is required, fill our the user/pass credentials, otherwise leave it blank.
#### PiperMail ####
This is the standard MailMan 2.x list service. The URL should be the full path to the directory that shows the various months

#### Pony Mail ####
This is a Pony Mail list. It should be in the form of list.html?foo@bar.baz and you should include a session cookie in order to bypass email address anonymization where applicable. If the Pony Mail instance does not apply anonymization, you may leave the cookie blank.

#### Gerrit ####
This is a gerrit code review resource, and will scan for tickets, authors etc.

#### BugZilla ####
This is a BugZilla ticket instance. You should add one source for each BugZilla project you wish to scan. It should point to the JSONRPC CGI file followed by the project you wish to scan. If you wish to just add everything as one source, you can do so by pointing it at jsonrpc.cgi * which will scan everything in the BugZilla database. If you want to be able to look at individual projects, it’s recommended that you scan them individually.

#### JIRA ####
This is a JIRA project. Most JIRA instances will require the login credentials of an anonymous account in order to perform API calls.

#### Twitter #### 
This is a Twitter account. Currently not much done there. WIP.

#### Jenkins CI ####
This is a Jenkins CI instance. One URL is required, and all sources will be scanned.

#### Buildbot CI ####
This is a Buildbot instance. One URL is required, and all sources will be scanned in one go.

## Browse Projects ##

## Grab Data ## 

## Assessing Project/Community Health ## 

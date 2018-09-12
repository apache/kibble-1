Managing Apache Kibble
======================

.. toctree::
   :maxdepth: 2
   :caption: Contents:


************************
Creating an Organisation
************************

The first thing you will need to set up, in order to use Kibble, is an
organisation that will contain the projects you wish to survey. You can
have multiple organisations in Kibble, and all organisations will be
scanned, but the UI will only display statistics for the current
(default) organisation you are using. You may switch between
organisations at your leisure in the UI.

To create your first organisation:

1. Go to the "Organisation" tab in the top menu
2. Locate the Create a new organisation` field set
3. Enter the details required for the new organsation

This will set up a new organisation and set it as your default (current)
one.

Once an organisation has been created, you can then add resources and
users to it.

.. _configdatasources:

************************
Configuring Data Sources
************************

After you have created an organisation, you can add sources to it.
A source is a destination to scan; it can be a git repository, a
JIRA instance, a mailing list and so on. To start adding sources, click
on the `Sources` tab in the left hand menu on the `Organisation` page.

With all resource types, you can speed up things by adding multiple
sources in one go by simply adding one source per line in the source
text field.

The currently supported resource types are:

GitHub
   This resource consists of GitHub repositories as well as issues/PRs
   that are contained within. Currently, you will need to add the full
   URL to the repo, including the `.git` part of it, such as:
   ``https://github.com/apache/clerezza.git``.
   **NOTE**: If you intend to use more than 60 API calls per hour, which
   you probably do, you will need to add the credentials of a GitHub
   user to the source, in order to get a higher rate limit of 6,000 API
   calls per hour. You may use any anonymous account for this.

Git
   This is a plain git repository (such as those served by the standard
   git daemon), and only scans repositories, not PRs/Issues. If basic
   auth is required, fill our the user/pass credentials, otherwise leave
   it blank.

PiperMail
   This is the standard MailMan 2.x list service. The URL should be the
   full path to the directory that shows the various months

Pony Mail
   This is a Pony Mail list. It should be in the form of
   `list.html?foo@bar.baz` and you *should* include a session cookie in
   order to bypass email address anonymization where applicable. If the
   Pony Mail instance does not apply anonymization, you may leave the
   cookie blank.

Gerrit
   This is a gerrit code review resource, and will scan for tickets,
   authors etc.

BugZilla
   This is a BugZilla ticket instance. You should add one source for
   each BugZilla project you wish to scan. It should point to the
   JSONRPC CGI file followed by the project you wish to scan.
   If you wish to just add everything as one source,
   you can do so by pointing it at ``jsonrpc.cgi *`` which will scan
   everything in the BugZilla database. If you want to be able to
   look at individual projects, it's recommended that you scan them
   individually.

JIRA
   This is a JIRA project. Most JIRA instances will require the login
   credentials of an anonymous account in order to perform API calls.
   
Twitter
   This is a Twitter account. Currently not much done there. WIP.

Jenkins CI
   This is a Jenkins CI instance. One URL is required, and all sources
   will be scanned.

Buildbot CI
   This is a Buildbot instance. One URL is required, and all sources
   will be scanned in one go.

Once you have added the resource URLs you wish to analyse, you
can obtain data by following the instructions in the chapter
:ref:`runscan`.

****************
Adding New Users
****************

MORE TODO

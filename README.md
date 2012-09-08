Ansible Commander
=================

Ansible Commander is an optional REST API and user interface for Ansible.

A.C. is in early development.  You should not use it yet.

Features
========

* ...

Dependencies
============

* python 2.6 or greater
* python-psycopg2, a Python database library
* Flask, a Python web framework
* PostgreSQL & PostgreSQL contrib (for hstore)
* optional Apache or Nginx fronting for the Flask service

Setup Instructions
==================

1) install ansible

2) run ./setup.sh to use ansible to configure ansible-commander.  It will prompt
   you for an initial database password.

3) optionally proxy the Flask service with Apache or nginx

Author/License Info
===================

Ansible-Commander is GPLv3 licensed and is Copyright (C) 2012, Michael DeHaan.


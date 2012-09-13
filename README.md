Ansible Commander
=================

Ansible Commander is an optional REST API and user interface for Ansible.

A.C. is in early development.  End-users should not use it yet.

Features
========

* Edit groups and hosts through a web interface (pending) and REST API (implemented)
* Review the latest facts for each node (pending)
* See the results of playbook runs and other shiny graphs (pending)

Not Features
============

* Ansible-playbook and /usr/bin/ansible are intended (for now) to be the main ways to execute ansible
and ansible playbooks.  The GUI does not eliminate the need to use the command line for
'serious business', but helps visualize and access information that IS better visualized
through a web interface.  It will learn more tricks over time.

Dependencies
============

* python 2.6 or greater
* python-psycopg2, a Python database library
* Flask, a Python web framework
* PostgreSQL server
* optional Apache or Nginx fronting for the Flask service

Setup The Database
==================

As you probably have already seen,  Ansible is pretty easy to set up stock.  

Using the REST layer, since it involves a database and an inventory plugin that must be configured, requires just a few more steps.  

Again, this is an optional component, so if learning Ansible, don't feel the need to get this going immediately, but you should be able to get things rolling in just a few minutes!  We've kept software requirements reasonably minimal, so this is mostly about configuration.  There's a playbook to take you most of the way, but we also make some choices as we don't want to edit a few important files automatically.  Hence the few more steps.  We also want you to understand what's going on should you want to tweak things later.

1. Install ansible if you haven't done so already.  Also install postgresql, postgresql-contrib, postgreqsql-server, and python-flask.

2. Change the inventory secret key.  edit config/config.j2 to set a secret key that will be used by the inventory script. This is not usable for REST API logins and is only a basic measure to make sure host variables aren't exposed to machines/users that don't need to see them -- particularly if you are setting any non-encrypted password variables.  It is used for no other purpose. If you want to change the secret later, it's in /etc/ansible/commander.cfg in the [inventory] section of the config file.

3. Configure the database.  run ./setup.sh to use an ansible-playbook (as root) to configure ansible-commander.  It will prompt you for an initial database password.  This playbook does not use SSH to run, your ansible inventory setup won't matter, and will only adjust your local machine.  Pay attention to any error messages that occur.  If you want to make changes, you can re-run the playbook, but it will not make any changes to the database password you initially specified, so use the same one.

4. Optionally proxy the Flask service with Apache or nginx.  This is very much recommended for production usage rather than using the built-in serving capability in Flask.  (Example snippets will be provided soon).

Setup The Inventory Connection
==============================

5. Configure the local instance of ansible to talk to ansible-commander as an inventory source.  Edit /etc/ansible/ansible.cfg to set *hostfile* to /checkout_directory/acom_inventory.py

6. Configure the inventory script to know how to find ansible-commander.  Edit the value in /checkout_directory/acom_inventory.cfg to match the *secret* you set in the config file earlier.  You should also set the *server* parameter at this time as well if you are running on a different port.  

Test The Inventory Connection
=============================

7. Start the flask service (./commander.py if not proxied with Apache/nginx, otherwise just restart your web server).  The REST API is now running.

8. Test the inventory script with 'python /checkout_directory/acom_inventory.py --list'.  You should see an empty list return '{}' until you have added hosts to Ansible commander.

Change Your Admin Account Password
==================================

9. Use the web interface -- start by changing the password for the admin account.  The default login is 'admin/gateisdown', and you need
to change this password now.

Next Steps
==========

10. Play with the web interface to add/edit some groups and hosts.  When you have some hosts/groupname added, you can test ping them with: 'ansible <groupname> -m ping'

Setting Up Other Machines TO Use Ansible-Commander
==================================================

11. If you would like to point other machines with ansible clients to the ansible-commander inventory database, it's easy to do by just installing the inventory script and editing the acom_inventory.cfg file on those particular machines.  Just repeat steps 4, 5, and 7 on those other machines after copying the inventory script and configuration file over to them.

Day To Day Usage
================

All of the above was setup-related, what's the day to day workflow?

* use the web interface (or REST API) to add hosts, add groups, and add hosts to groups
* use the web interface (or REST API) to edit group and host variables
* use /usr/bin/ansible and /usr/bin/ansible-playbook as normal to run commands using data setup in the web interface
* don't edit the INI inventory file any more, as it will be ignored

API Guide
=========

While one of the main goals of ansible-commander is to provide a web interface for users, it's also a major way to achieve
API integrations with 3rd party software and non-Python scripts.

An API Guide to the REST interface will be available at ansible.github.com
in the near future.

Author/License Info
===================

Ansible-Commander is GPLv3 licensed and is Copyright (C) 2012, Michael DeHaan.


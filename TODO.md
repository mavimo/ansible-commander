Things left to do for Ansible Commander first release
=====================================================


STAGE1 REMAINING:
- comment uncommented functions
- expose groups over REST
- expose hosts over REST
- expose users over REST
- test for methods at REST layer
- write an ansible inventory (python) script that accesses the database

STAGE2:
- Foundation or Bootstrap skeleton of GUI app
- Login dialog to get username/password
- Javascript MVC widgets list users and groups
- JS to add hosts
- JS to add hosts to groups
- JS to edit host variables
- JS to add groups
- JS to add groups to groups
- JS to edit group variables
- JS to view all variables set on a host
- Logout button
- ansible callback plugin to save latest facts for each system
- JS to view/browse inventory
- modify setup playbook to install plugins
- migration script to convert inventory of YAML users (who want to) to database
- documentation page for ansible.github.com (ideally with 1 or 2 screenshots)

Completed Thus Far
==================

- README/LICENSE
- flask hello world
- initial setup playbook (mostly)
- python code to access datalayer
- basic user class
- basic auth layer wired in to user class
- full group/host data modelling
- encrypt passwords
- verify behavior when deleting groups in a chain, for hosts and groups, do _groups get cleared on hosts, etc
- ability to edit parent and group variables directly and all the right things update
- hrefs in all the objects
- established basic routes

Future releases (possible)
==========================

- browse ansible playbook results
- dashboard of overall system happiness and so forth
- browse and edit playbook content (???)
- trigger ad-hoc execution (???)
- trigger playbook execution (???)
- ...





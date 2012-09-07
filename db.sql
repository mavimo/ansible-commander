CREATE USER ansible_commander UNENCRYPTED PASSWORD '{{ database_password }}';

GRANT ALL on DATABASE ansible_commander TO ansible_commander;



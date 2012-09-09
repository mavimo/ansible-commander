run:
	./commander.py

manage:
	sudo -u postgres psql --dbname ansible_commander

managetest:
	sudo -u postgres psql --dbname ansible_commander_test

test:
	@echo "DELETE FROM thing;" | sudo -u postgres psql --dbname ansible_commander_test 1>/dev/null 2>&1
	@echo "ALTER SEQUENCE thing_id_seq RESTART;" | sudo -u postgres psql --dbname ansible_commander_test 1>/dev/null 2>&1
	@echo "ALTER SEQUENCE properties_id_seq RESTART;" | sudo -u postgres psql --dbname ansible_commander_test 1>/dev/null 2>&1
	@PYTHONPATH=. python ./acom/types/users.py
	@PYTHONPATH=. python ./acom/types/inventory.py

loc:
	sloccount acom commander.py

pep8:
	@echo "#############################################"
	@echo "# Running PEP8 Compliance Tests"
	@echo "#############################################"
	-pep8 -r --ignore=E501,E221,W291,W391,E302,E251,E203,W293,E231,E303,E201,E225,E261,E241 . acom/

pyflakes:
	pyflakes *.py acom/*

clean:
	@echo "Cleaning up byte compiled python stuff"
	find . -type f -regex ".*\.py[co]$$" -delete
	@echo "Cleaning up editor backup files"
	find . -type f \( -name "*~" -or -name "#*" \) -delete
	find . -type f \( -name "*.swp" \) -delete


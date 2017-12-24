ifdef SYSTEMROOT
	PYTHON = ./venv/Scripts/python3.6
	PIP = ./venv/Scripts/pip
else
	PYTHON = ./venv/bin/python3.6
	PIP = ./venv/bin/pip
endif

init:
	rm -rf venv
	find . -name '*.pyc' -delete
	@echo Creating venv with python3.6 `which python3.6`
	virtualenv -p `which python3.6` venv --verbose

dump_fixtures:
	$(PYTHON) manage.py dumpdata --indent 2 bookmarks.Category > fixtures/categories.json
	$(PYTHON) manage.py dumpdata --indent 2 bookmarks.Folder > fixtures/folders.json
	$(PYTHON) manage.py dumpdata --indent 2 bookmarks.Website > fixtures/websites.json
	$(PYTHON) manage.py dumpdata --indent 2 bookmarks.Keyword > fixtures/keywords.json
	$(PYTHON) manage.py dumpdata --indent 2 bookmarks.BookmarksUser > fixtures/bookmarkusers.json
	$(PYTHON) manage.py dumpdata --indent 2 bookmarks.Bookmark > fixtures/bookmarks.json
	$(PYTHON) manage.py dumpdata --indent 2 bookmarks.WebsiteType > fixtures/websitetypes.json
	$(PYTHON) manage.py dumpdata --indent 2 bookmarks.BlacklistedWebsites > fixtures/blacklistedwebsites.json
	$(PYTHON) manage.py dumpdata --indent 2 hooks.Hook > fixtures/hooks.json
	$(PYTHON) manage.py dumpdata --indent 2 friends.FriendshipRequest > fixtures/friendrequests.json
	$(PYTHON) manage.py dumpdata --indent 2 friends.Friend > fixtures/friends.json
	$(PYTHON) manage.py dumpdata --indent 2 auth.User > fixtures/users.json

start_me_up:
	find . -name '*.pyc' -delete
	rm -vf db.sqlite3
	$(PIP) install -r requirements.txt -U
	$(PYTHON) manage.py makemigrations corsheaders
	$(PYTHON) manage.py makemigrations
	$(PYTHON) manage.py migrate --run-syncdb --noinput

	$(PYTHON) manage.py loaddata fixtures/users.json
	$(PYTHON) manage.py loaddata fixtures/bookmarkusers.json
	$(PYTHON) manage.py loaddata fixtures/hooks.json
	$(PYTHON) manage.py loaddata fixtures/categories.json
	$(PYTHON) manage.py loaddata fixtures/keywords.json
	$(PYTHON) manage.py loaddata fixtures/folders.json
	$(PYTHON) manage.py loaddata fixtures/bookmarks.json
	$(PYTHON) manage.py loaddata fixtures/websitetypes.json
	$(PYTHON) manage.py loaddata fixtures/websites.json
	$(PYTHON) manage.py loaddata fixtures/blacklistedwebsites.json
	$(PYTHON) manage.py loaddata fixtures/friendrequests.json
	$(PYTHON) manage.py loaddata fixtures/friends.json

server:
	$(PYTHON) manage.py runserver

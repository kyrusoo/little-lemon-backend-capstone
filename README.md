# Little Lemon API

A Django REST Framework capstone with a MySQL backend, a restaurant home page,
menu and booking CRUD, registration, and token authentication.

**Start here: [Readme.txt](Readme.txt)** — setup, all API paths, permissions,
Insomnia examples, test commands, and validation limitations.

Run the isolated test suite:

```sh
pip install -r requirements-test.txt
python manage.py test restaurant --settings=littlelemon.test_settings
```

MySQL is the default runtime backend. SQLite is only used by the isolated test
settings. Review the documented MySQL validation step before submission.

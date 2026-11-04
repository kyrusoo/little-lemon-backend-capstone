LITTLE LEMON — BACK-END DEVELOPER CAPSTONE

Django 5.2 / Django REST Framework / MySQL 8

FEATURES
- Django renders the home page at / and /restaurant/ and serves CSS in development.
- Menu list/detail CRUD and booking list/detail CRUD.
- Public registration, password validation, token login and logout.
- All menu/booking API access requires authentication.
- Any registered user can read menu items and manage their own bookings.
- Only staff can change menu items; staff can manage all bookings.
- Pagination (20 records), input validation, password hashing, booking isolation.
- No real credentials or tokens are included.

QUICK START WITH DOCKER (MYSQL)
1. Install Docker with Compose.
2. Copy .env.example to .env. Replace DJANGO_SECRET_KEY and MYSQL_PASSWORD with
   your own local values. Choose a strong random DJANGO_SECRET_KEY.
3. Run: docker compose up --build -d
4. Run: docker compose exec web python manage.py createsuperuser
5. Open http://localhost:8000/ and http://localhost:8000/admin/.
   Add menu records through admin, or obtain a token for the staff account and
   POST to /restaurant/menu/.
6. Run tests against MySQL:
   docker compose exec web python manage.py test restaurant --keepdb
   mysql-init.sql grants access to an isolated test_littlelemon database on
   first container initialization. Existing volumes will not rerun this script;
   use your local DB administrator to grant the test-database permissions if
   you reuse an older volume. These permissions are for local testing only.
7. Stop containers: docker compose down
   The named volume preserves your data. Do not delete it unless intended.

LOCAL INSTALL WITHOUT DOCKER
Requires Python 3.12+, MySQL 8.0.11+ (8.4 recommended), and mysqlclient build tools.
On Debian/Ubuntu, install python3-dev default-libmysqlclient-dev build-essential
pkg-config. On other systems follow mysqlclient's installation instructions.

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Create an empty UTF-8 database using a local MySQL administrator:
  CREATE DATABASE littlelemon CHARACTER SET utf8mb4;
  CREATE USER 'littlelemon'@'localhost' IDENTIFIED BY '<your-local-password>';
  GRANT ALL PRIVILEGES ON littlelemon.* TO 'littlelemon'@'localhost';

Copy .env.example to .env and edit it. For a POSIX shell, load the values:
  set -a
  . ./.env
  set +a
Use shell-safe values (quote values containing shell metacharacters).
Django reads environment variables, not .env directly. Docker Compose loads .env.

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

API PATHS TO TEST (trailing slashes required)
POST /restaurant/auth/users/                Register; public
POST /restaurant/auth/token/login/          Obtain token; public
POST /restaurant/auth/token/logout/         Revoke current user's token
GET, POST /restaurant/menu/                 List; staff create
GET, PUT, PATCH, DELETE /restaurant/menu/1/  Retrieve; staff edit/delete
GET, POST /restaurant/booking/tables/        List own bookings; create
GET, PUT, PATCH, DELETE /restaurant/booking/tables/1/  Own booking CRUD
GET /                                      Static HTML home page
GET /admin/                                Staff administration
GET /auth/login/                           Browsable API session login

AUTHENTICATION AND INSOMNIA WALKTHROUGH
Create a request in Insomnia with base URL http://localhost:8000.
For POST/PATCH/PUT requests select JSON body and Content-Type application/json.
1. POST /restaurant/auth/users/
   {"username":"reviewer","email":"reviewer@example.com","password":"<choose-a-strong-password>"}
   Expected: 201, user ID/username/email, no password returned.
2. POST /restaurant/auth/token/login/
   {"username":"reviewer","password":"<the-password-you-chose>"}
   Expected: 200 and {"token":"..."}.
3. Add header Authorization: Token <returned-token> to protected requests.
   Use the literal prefix Token, not Bearer.
4. GET /restaurant/menu/ -> 200 with count/next/previous/results.
5. Log in separately as the superuser to get a staff token, then POST menu:
   {"title":"Greek Salad","price":"12.50","inventory":20}
   Expected: 201. PATCH the returned ID with {"price":"13.00"} -> 200.
   A normal user receives 403 on menu writes.
6. With the regular user's token POST /restaurant/booking/tables/:
   {"name":"Reviewer","no_of_guests":2,"booking_date":"2030-12-20T19:00:00Z"}
   Expected: 201. Owner is assigned by the server; supplied owner IDs are ignored.
7. GET that booking's detail URL -> 200; PATCH {"no_of_guests":4} -> 200;
   DELETE -> 204; GET after deletion -> 404. Use IDs returned by the API, not
   a hard-coded 1 if your database already contains rows.
8. Create a second ordinary account. Its token cannot list, retrieve, change,
   or delete the first user's reservations (detail requests return 404).
9. POST no_of_guests=0 or 21 -> 400. Negative menu price/inventory -> 400.
10. POST /restaurant/auth/token/logout/ -> 204. Reuse that token -> 401.
11. Remove Authorization entirely: protected endpoints -> 401.

Bookings accept ISO-8601 date-times; UTC is used. This capstone manages booking
records, not table capacity or a complete restaurant scheduling engine. It does
not prevent overlapping reservations or reject past dates.

AUTOMATED TESTS
Fast isolated tests, without requiring MySQL:
  pip install -r requirements-test.txt
  python manage.py test restaurant --settings=littlelemon.test_settings

The SQLite test settings are test-only and intentionally use an in-memory database
and a faster password hasher. Do not deploy with these settings.
16 tests cover models, HTML, authentication, registration, menu CRUD, validation,
booking CRUD, ownership spoofing, cross-user isolation, and staff access.

VALIDATION STATUS
All 16 tests passed with SQLite in the preparation environment. Django's system
check passed. MySQL is configured as the default database, and the Docker setup
is supplied, but a live MySQL run and Docker build were not possible in that
environment. Verify the Docker/MySQL path locally before final submission.
Insomnia steps are provided; no claim is made that Insomnia was run here.

PRODUCTION NOTES
This is a local capstone project. Development uses DJANGO_DEBUG=1 and Django's
runserver to serve static assets. For production use DEBUG=0, HTTPS, a production
WSGI server and static-file server, private database networking, and real secret
management. Token authentication requires HTTPS outside local development.
Never commit .env. Login/registration throttles are basic application controls,
not a complete brute-force defense. Back up the database before schema changes.

REFERENCES
https://docs.djangoproject.com/en/5.2/ref/databases/
https://www.django-rest-framework.org/api-guide/authentication/
https://www.django-rest-framework.org/api-guide/testing/

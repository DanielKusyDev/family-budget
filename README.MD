# Budget app

The app is divided into three parts following Hexagonal architecture pattern. FastAPI with GraphQL server sits on the
left side of the hex, when the MSSQL database serves as a main infrastructure service.
## Installation

```shell
docker-compose -f deploy/docker-compose.yml build
docker-compose -f deploy/docker-compose.yml up -d
```

For development version run:
```shell
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list \
apt-get update \
ACCEPT_EULA=Y apt-get install --no-install-recommends -y \
        build-essential \
        python3-dev \
        msodbcsql17 \
        mssql-tools \
        unixodbc-dev \
        unixodbc
curl -sSL https://install.python-poetry.org | python -
poetry install --with dev
EXPORT DB_CONNECTION_STRING=<ODBC_CONNECTION_STRING> # see docker-compose for default string for provided DB service
uvicorn app.drivers.graphql:app --port 8000 --host 127.0.0.1
```

For systems other than ubuntu please see refer to official Microsoft guide on ODBC installation:

https://learn.microsoft.com/en-us/sql/connect/odbc/microsoft-odbc-driver-for-sql-server?view=sql-server-ver15

## Quality checks
```shell
pytest
flake8
mypy app
```
### Note about tests

Since the form of development of this application is very similar to POC, no real and full tests were created. I used
this (very short) time I had to create a POC-like application. With more time available the following testing approaches
would be used:

- all helpers and "small" functions, not related to the actual domain would be tested using pytest + hypothesis
- domain services such as list views would be tested using BDD methodology (Behave). In-Memory database would be use
  for that purpose.
- infrastructure would be tested through pytest and fake database running in a docker container (MSSQL Express)
- driver application would be tested using pytest and Starlette's test client
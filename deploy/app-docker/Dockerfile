FROM python:3.10 as python-base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"


ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

FROM python-base as builder-base
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install --no-install-recommends -y \
        build-essential \
        python3-dev \
        msodbcsql17 \
        mssql-tools \
        unixodbc-dev \
        unixodbc

RUN curl -sSL https://install.python-poetry.org | python -
ENV PATH="${PATH}:/root/.local/bin"


WORKDIR $PYSETUP_PATH
RUN python -m venv $VENV_PATH
RUN . $VENV_PATH/bin/activate
COPY poetry.lock pyproject.toml ./
RUN poetry install

FROM python-base as production
ENV FASTAPI_ENV=production
COPY --from=builder-base $VENV_PATH $VENV_PATH
COPY --from=builder-base /etc/apt/trusted.gpg /etc/apt/trusted.gpg
COPY --from=builder-base /etc/apt/sources.list.d/mssql-release.list /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update \
    && ACCEPT_EULA=Y apt-get install --no-install-recommends -y \
        msodbcsql17 \
        mssql-tools \
        unixodbc-dev \
        unixodbc
RUN . $VENV_PATH/bin/activate
WORKDIR /budget
COPY . .
ENV DISABLE_AUTH=false
CMD ["uvicorn", "app.drivers.graphql:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]
FROM mcr.microsoft.com/mssql/server:2019-latest

USER root


COPY wait-for-db.sh /scripts/
COPY setup.sql /scripts/
COPY entrypoint.sh /scripts/

RUN chmod a+x /scripts/wait-for-db.sh
RUN chmod a+x /scripts/setup.sql
RUN chmod a+x /scripts/entrypoint.sh

USER mssql

CMD "/scripts/entrypoint.sh"
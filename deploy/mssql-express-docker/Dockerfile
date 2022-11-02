FROM mcr.microsoft.com/mssql/server:2019-latest

USER root

# Creating database snapshots was not working on OSX as it was failing to write
# to disk. The fix was to create a writeable snapshots volume and write them
# there.
RUN mkdir /snapshots && chmod 777 /snapshots

USER mssql
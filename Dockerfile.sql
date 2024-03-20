FROM mcr.microsoft.com/mssql/server:2022-latest

ENV ACCEPT_EULA=Y \
    MSSQL_PID=Express \
    SA_USERNAME=sa \
    SA_PASSWORD=PyTH0n_R3C1P3_

USER root

RUN mkdir -p /var/opt/sqlserver

USER mssql

WORKDIR /var/opt/sqlserver


COPY ./recipe_db.bak /var/opt/sqlserver/recipe_db.bak

EXPOSE 1433

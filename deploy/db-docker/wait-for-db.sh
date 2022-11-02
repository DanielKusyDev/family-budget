#!/bin/bash

while [[ "$#" -gt 0 ]]; do
    echo $1
    case $1 in
        -i) sql_script="$2"; shift ;;
        -Q) query="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

SETUP_CMD=(
  /opt/mssql-tools/bin/sqlcmd
  -S "tcp:$SQL_SERVER,$SQL_SERVER_PORT"
  -U "$SQL_USERNAME"
  -P "$SQL_PASSWORD"
  )

if [ -z "$sql_script" ] ; then
  SETUP_CMD+=("-Q$query")
else
  SETUP_CMD+=("-i$sql_script")
fi

echo "========= starting setup process"

for _ in {1..50};
do
  echo "${SETUP_CMD[@]}"
  "${SETUP_CMD[@]}"
  if [ $? -eq 0 ]
  then
    echo "========= setup completed"
    break
  else
    echo "========= not ready yet..."
    sleep 1
  fi
done
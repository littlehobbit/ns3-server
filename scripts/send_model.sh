#! /bin/bash
# USAGE: send_model [URL] [FILE]

args_count=$#
if [ $args_count -ne 2 ]; then
  echo "USAGE: send_model [URL] [FILE]" 
  exit 1
fi

echo "Send ${2} to http://${1}/start"
cat $2 | curl -X POST -H "Content-Type: application/xml" -d "@-" http://$1/start

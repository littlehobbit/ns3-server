#! /bin/bash
# USAGE: send_model [URL] [FILE]

args_count=$#
if [ $args_count -ne 1 ]; then
  echo "USAGE: stop [URL]" 
  exit 1
fi

echo "Stop http://${1}/start"
curl -X GET http://$1/stop

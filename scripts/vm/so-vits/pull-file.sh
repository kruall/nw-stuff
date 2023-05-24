#!/usr/bin/bash -e

scp -r $("`dirname $0`"/get_host_ip.sh $1):"$2" "$3"

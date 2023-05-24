#!/usr/bin/bash -e

ssh -A $("`dirname $0`"/get_host_ip.sh $1)

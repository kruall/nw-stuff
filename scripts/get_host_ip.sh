#!/usr/bin/bash -e

echo $(yc compute instance get $1  | grep "        address:" | awk -e '$0 ~ // {print $2}')
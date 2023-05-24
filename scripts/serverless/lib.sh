#!/usr/bin/bash -e

function get_value {
    path_to_function="$1"
    variable="$2"

    if [ ! -f $path_to_function/.config/$variable ] ; then
        return 1
    fi

    cat $path_to_function/.config/$variable
    return 0
}

function clear_pycache {
    path=$1
    if [ -d $path/__pycache__ ] ; then
        rm -rf $path/__pycache__
    fi
}

function join_list {
    sep=$1
    list="$2"
    acc=""
    for line in $list ; do
        if [[ "$acc" == "" ]] ; then
            acc="${line}"
        else
            acc="${acc}${sep}${line}"
        fi
    done
    echo "$acc"
}

function make_additional_args {
    path_to_function="$1"


    timeout="`get_value $path_to_function timeout`"
    env="`get_value $path_to_function env`"
    secret="`get_value $path_to_function secret`"

    additional_args=""
    # add timeout for args
    if [[ "$timeout" != "" ]] ; then 
        additional_args="${additional_args} --execution-timeout=${timeout}"
    fi

    # add environment variables
    if [ "$env" != "" ] ; then 
        additional_args="${additional_args} --environment=`join_list , "$env"`"
    fi

    # add secrets
    if [ "$secret" != ""  ] ; then 
        additional_args="${additional_args} --secret=`join_list " --secret=" "$secret"`"
    fi

}

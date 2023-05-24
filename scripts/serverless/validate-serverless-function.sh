#!/usr/bin/bash -e

project=$1
function_name=$2

pushd `dirname "$0"`/../.. > /dev/null

    path_to_project="code/${project}"
    path_to_function="${path_to_project}/serverless/${function_name}"

    if [ ! -d "$path_to_project" ] ; then
        >&2 echo "ERROR: can't find project '${project}' by path '$path_to_project'"
        exit 1
    fi

    if [ ! -d "$path_to_function" ] ; then
        >&2 echo "ERROR: can't find serverless function '$function_name' for project '${project}' by path '$path_to_function'"
        exit 1
    fi

popd > /dev/null



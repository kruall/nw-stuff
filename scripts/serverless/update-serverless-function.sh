#!/usr/bin/bash -e

project=$1
function_name=$2


pushd `dirname "$0"` > /dev/null
    ./validate-serverless-function.sh $project $function_name
    . lib.sh
popd


pushd `dirname "$0"`/.. > /dev/null

    path_to_project="code/${project}"
    path_to_function="${path_to_project}/serverless/${function_name}"

    if [ -f scripts/variables.sh ] ; then
        . scripts/variables.sh
    else
        echo "WARN: can't find the file with variables by path '$(readlink -f scripts/variables.sh)'"
    fi

    runtime=`get_value $path_to_function runtime`
    entrypoint=`get_value $path_to_function entrypoint`
    timeout=`get_value $path_to_function timeout`
    env="`get_value $path_to_function env`"
    secret="`get_value $path_to_function secret`"

    # prepare directories
    mkdir -p out
    mkdir -p out/${project}
    mkdir -p out/${project}/serverless
    mkdir -p out/${project}/serverless/$function_name
    rm -rf out/${project}/serverless/$function_name/*

    # copy serverless function
    cp -r $path_to_function/* out/${project}/serverless/$function_name/
    clear_pycache out/${project}/serverless/$function_name/

    # copy python libs only if it's python serverless function
    if [[ "$runtime" == "python39" ]]; then
        # copy project lib
        path_to_project_lib="$path_to_project"/lib 
        if [ -d "$path_to_project_lib" ] ; then
            cp -r "$path_to_project_lib" out/${project}/
            clear_pycache out/${project}/lib
        fi

        # copy lib
        cp -r code/lib out/
        clear_pycache out/lib
    fi

    # make archive
    archive_name="${function_name}.zip"
    pushd out > /dev/null
        zip -r "$archive_name" *
        mv "$archive_name" ../
    popd > /dev/null
    rm -rf out

    additional_args=""

    # add timeout for args
    if [ -f $path_to_function/.config/timeout ] ; then 
        echo read timeout
        timeout="`cat $path_to_function/.config/timeout`"
        additional_args="${additional_args} --execution-timeout=${timeout}"
    fi

    # add environment variables
    if [ -f $path_to_function/.config/env ] ; then 
        echo read env
        env=""
        for line in `cat $path_to_function/.config/env` ; do
            echo env_arg: $line
            if [[ "$env" == "" ]] ; then
                env="${line}"
            else
                env="${env},${line}"
            fi
        done
        additional_args="${additional_args} --environment=${env}"
    fi

    # add secrets
    if [ -f $path_to_function/.config/secret ] ; then 
        echo read secret
        for line in `cat $path_to_function/.config/secret` ; do
            echo secret: $line
            additional_args="${additional_args} --secret=$line"
        done
    fi

    echo additional_args: $additional_args

    echo yc serverless function version create \
        --function-name=$function_name \
        --runtime=$runtime \
        --entrypoint=$entrypoint \
        --service-account-id $SERVICE_ACCOUNT_ID \
        --source-path="out/serverless/${function_name}.zip" \
        $additional_args

    rm $archive_name


popd > /dev/null



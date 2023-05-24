>/dev/null pushd `dirname $0` 

read -r request

vm_name=`echo "$request" | python3 get_vm_name.py`

>&2 echo "vm_name: $vm_name"
yc --no-user-output compute instance start --cloud-id ${CLOUD_ID} --folder-id ${FOLDER_ID} ${vm_name}

echo '{"statusCode": 200}'

>/dev/null popd
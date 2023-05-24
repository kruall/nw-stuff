param ($vmName = $(throw "vmName parameter is required."))

mkdir s:\$vmName


wsl.exe --import $vmName s:\$vmName S:\backup\ubuntu22-04.tar

wsl.exe -d $vmName /bin/bash -c "echo '[user]' >> /etc/wsl.conf" 
wsl.exe -d $vmName /bin/bash -c "echo 'default=kruall' >> /etc/wsl.conf"

wsl.exe --terminate $vmName

wsl.exe -d $vmName /mnt/d/code/nw-staff/scripts/vm/wsl/init-wsl-ubuntu-22-04.sh $vmName $PASSWORD


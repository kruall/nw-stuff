param ($vmName = $(throw "vmName parameter is required."))


wsl.exe --unregister $vmName

rmdir s:\$vmName

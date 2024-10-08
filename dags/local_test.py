import json
from vmware import functions

if __name__ == "__main__":

    variables = None
    with open("../variables.json") as file:
        variables = json.load(file)

    vm_host = variables["vmhost"]
    print("vm_host", vm_host)
    vm_user = variables["vmuser"]
    print("vm_user", vm_user)
    vm_password = variables["vmpassword"]
    content = functions.vsphere_connect(vm_host, vm_user, vm_password)
    print(content)

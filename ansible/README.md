## Ansible for managing server configuration

Ansible is a python utility ran locally that uses ssh to connect and apply configuration to servers. https://docs.ansible.com/ansible/latest
## Setup

Under MacOS, Linux, or Windows WSL

```
% python3 -m virtualenv venv
% source venv/bin/activate
# (venv) % pip install -r requirements.txt

# install external plugins if we start using them
# (venv) % ansible-galaxy install -r requirements.yml
```

## Running ansible

In this ansible directory, you can do any of the following:


Check your connectivity to the servers:
```
% ansible all -m ping
```

Run ad-hoc commands:
```
% ansible all -m command -a 'uname -r'
```

Verify the state of the VM configuration:
```
% ansible-playbook site.yml --check --diff -v
```

Apply configuration:
```
% ansible-playbook site.yml
```

## Encrypting secrets with ansible-vault

It is possible to make secret information available to `ansible` and save it in this repository with `ansible-vault`.

1. assign the secret to an ansible variable in a normal, yaml-formatted variables file (such as a file in `group_vars`, a file in role's `vars` directory, or a file included in a playbook via `vars_files`)
1. encrypt the variable file using `ansible-vault encrypt path/to/file`, providing a password for ansible-vault when prompted
1. reference the varibles defined in the now encrypted file like any other ansible variable
1. include `--ask-vault-password` when you call `ansible-playbook` or set the environment variable `ANSIBLE_VAULT_PASSWORD_FILE` to a local file, add that file to your .gitignore, set restrictive permissions, and save your vault password into that file

More vault goodness
- edit the encrypted file with `ansible-vault edit path/to/file`
- change the password of an encrypted file by decrypting and encrypting the file again
- https://docs.ansible.com/ansible/latest/user_guide/vault.html

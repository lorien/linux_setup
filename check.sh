#!/bin/bash
ansible-playbook linux_setup/book.yml -i linux_setup/inventory.yml --check --diff

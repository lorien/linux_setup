#!/bin/bash
ansible-playbook ansible/book.yml -i inventory.yml --check --diff

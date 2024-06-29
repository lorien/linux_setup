# Linux Setup Project

This document describes my method of installing linux into a new blank machine.

I use most recent Debian release.

Most steps are described as ansible rules and may be executed by ansible.

## Preparing USB Stick

Download netinst ISO image from https://www.debian.org/releases/stable/debian-installer/

Simplest method to put image to usb stick is:

    cp debian.iso /dev/sdX # must be whole-disk device
    sync

Other option is to use Ventoy ([https://ventoy.net](https://ventoy.net/)) to prepare multiple iso bootable USB stick.

## Initial Installation

On partition disks stage the "Guided - use entire disk and set up encrypted LVM" must be selected.

On software selection stage only the "laptop" option must be selected.

## OS Configuration

Main installation steps are described as ansible rules in [tasks_install.yml](tasks_install.yml) file.

To use these rules run as root this command `ansible-playbook -i inventory.yml book_install.yml`.

To install ansible use command `apt install ansible`.

God knows why, I've implemented a [rendering code in python](render_html.py) which converts ansible rules
into fancy HTML which you can check at [lorien.github.io/linux_setup/html/install.html](https://lorien.github.io/linux_setup/html/install.html).

## WIFI Adapter Issues

Possible issues and solutions to fix unsupported WIFI adapter is described in [wifi_fix.md](wifi_fix.md) document.

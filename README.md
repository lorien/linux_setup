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

On software selection stage only "Standard system utilities" option must be selected.

## Main Installation

Main installation steps are described as ansible rules in [linux_setup/tasks.yml](linux_setup/tasks.yml) file.

First download repository to your machine:

- `su # you must be root`
- `apt install ansible`
- `apt install git`
- `cd ~ && git clone https://github.com/lorien/linux_setup`
- `cd ~/linux_setup`

Now you have to update `linux_setup/vars.yml`:

- Update `setup_user` with username of user you have created during initial installation stage
- Update `setup_ssh_authorized_key` to URL where your public SSH key is located.

Now you can run installation: `./install.sh`

God knows why, I've implemented a [rendering code in python](render_html.py) which converts ansible rules
into fancy HTML which you can check at [lorien.github.io/linux_setup/html/install.html](https://lorien.github.io/linux_setup/html/install.html).

## WIFI Adapter Issues

Possible issues and solutions to fix unsupported WIFI adapter is described in [wifi_fix.md](wifi_fix.md) document.

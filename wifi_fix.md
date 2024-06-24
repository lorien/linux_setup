## Issues and Solutions related to WIFI adapters

Usefull documentation: [wiki.debian.org/WiFi/HowToUse](https://wiki.debian.org/WiFi/HowToUse)

## Unsupported WIFI Adapter on OS Installation Stage

If WIFI adapter is not supported from the box at initial os installation stage then there are two ways.

One way is to install most newer ilnux-image from "stable-backports" repository

Another way is to use "testing" repository which contains newer kernel than "stable-backports" repo.
In sources.list use specific name like "bookworm" instead of "testing". After changing sources.list
run "apt update" and "apt full-upgrade".

## Blocked WIFI Adapter

WIFI adapter might be blocked by some actor. Use rfkill to check its state and unblock.

To install rfkill: "apt install rfkill". If you have to do it at initial installation stage you
might download rfkill deb package and safe it to USB stick.

Check for "soft blocked: yes" in output of "rfkill list".

Run "rfkill unblock wifi"

## Tools to control WIFI adapter

Dependencies for wpasupplicant package:
 - libdbus-1-3
 - libnl-3-200
 - libnl-genl-3-200
 - libnl-route-3-200
 - libpcsclite1
 - libssl1.1

To connect to password protected wifi with builtin network service
edit file "/etc/network/interfaces":

    allow-hotplug wlp2s0
    iface wlp2s0 inet dhcp
        wpa-ssid ESSID
        wpa-psk PASSWORD

Then run commands:
- "ifup wlp2s0"
- "iw wlp2s0 link"
- "ip a"

The name "wlp2s0" is used as name of WIFI adapter. This name depends on model of adapter.

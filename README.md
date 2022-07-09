# nxpydocs
Automated NXOS Business Ready Documents from th guestshell Python

## Setting up guestshell
### Enable guestshell
```console
switch# guestshell enable
```
Wait until the guestshell becomes active

### Resize guestshell diskspace
```console
guestshell resize rootfs 2000
guestshell resize memory 2688
guesthshell reboot
```

### Update DNS
```console
[cisco@guestshell ~]sudo vi /etc/resolv.conf
nameserver <dns server IP address>
domain <domain that matches NX-OS configured domain>
```

### Install Git
```console
[cisco@guestshell ~]sudo yum install git
```

### Conigure Git
```console
[cisco@guestshell ~]git config --global user.name "Your Name Here"
[cisco@guestshell ~]git config --global user.email johndoe@example.com
[cisco@guestshell ~]git config --global push.default matching
```

## Install the application
```console
[cisco@guestshell ~]pip install nxpydocs
```

## Run nxpydocs
### Get Help
You can add --help to see the help information
```console
[cisco@guestshell ~]nxpydocs --help

```

### Run nxpydocs interactively
You can simply run nxpydocs and it will prompt you for the required input values
```console
[cisco@guestshell ~]nxpydocs

```
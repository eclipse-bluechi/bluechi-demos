# Workshop - October 2024

Complementary slides for this demo can be found [here](./slides.pdf).

## Preparations

### Setup AutoSD VM

1. Download AutoSD image `auto-osbuild-qemu-autosd9-developer-regular` from

```
https://autosd.sig.centos.org/AutoSD-9/nightly/sample-images/
```

2. Run image with

```bash
# get image name
$ AUTOSD_IMAGE_NAME="$(curl https://autosd.sig.centos.org/AutoSD-9/nightly/sample-images/ | grep -oE 'auto-osbuild-qemu-autosd9-developer-regular-x86_64-[0-9]+\.[A-Za-z0-9]+\.qcow2\.xz' | head -n 1)"

# download and decompress the image
$ wget \
    -O auto-osbuild-qemu-autosd9-developer-regular-x86_64.qcow2.xz \
    https://autosd.sig.centos.org/AutoSD-9/nightly/sample-images/$AUTOSD_IMAGE_NAME
$ xz -d auto-osbuild-qemu-autosd9-developer-regular-x86_64.qcow2.xz

# run the image
$ /usr/bin/qemu-system-x86_64 \
    -drive file=/usr/share/OVMF/OVMF_CODE.fd,if=pflash,format=raw,unit=0,readonly=on \
    -drive file=/usr/share/OVMF/OVMF_VARS.fd,if=pflash,format=raw,unit=1,snapshot=on,readonly=off \
    -smp 20 \
    -enable-kvm \
    -m 2G \
    -machine q35 \
    -cpu host \
    -device virtio-net-pci,netdev=n0 \
    -netdev user,id=n0,net=10.0.2.0/24,hostfwd=tcp::2222-:22,hostfwd=tcp::8420-:8420 \
    -drive file=auto-osbuild-qemu-autosd9-developer-regular-x86_64.qcow2,index=0,media=disk,format=qcow2,if=virtio,snapshot=off
```

3. Login and enable ssh access for root:

```bash
$ vim /etc/ssh/sshd_config
...
PasswordAuthentication yes
PermitRootLogin yes
...
```

### Setup everything

Copy the [demo directory](./demo/) to the VM:

```bash
$ scp -r -P 2222 demo/  root@127.0.0.1:/root/
```

SSH to the VM and run the [setup.sh](./demo/setup.sh) (might need a reboot and another run due to the `kernel-automotive-modules-extra` package for vcan):

```bash
$ ssh -P 2222 root@127.0.0.1
root@127.0.0.1's password:
****

[root@localhost ~]# chmod +x ./demo/setup.sh
[root@localhost ~]# ./demo/setup.sh
```

### Run the demo

After running the [setup script](#setup-everything), run the demo inside the VM:

```bash
$ ./demo/run.sh
...
```

#!/usr/bin/bash
#
# Copyright Contributors to the Eclipse BlueChi project
#
# SPDX-License-Identifier: MIT-0

CURRDIR=$(dirname "$(readlink -f "$0")")

set -x
set -e

##########################
# Installing packages
#
dnf install --nodocs epel-release -y
dnf install python3-pip \
            python3-gobject \
            can-utils \
            kernel-automotive-modules-extra \
    -y

dnf copr enable @centos-automotive-sig/bluechi-snapshot -y
dnf install bluechi-controller \
            bluechi-agent \
            bluechi-ctl \
            bluechi-selinux \
    --repo copr:copr.fedorainfracloud.org:group_centos-automotive-sig:bluechi-snapshot \
    -y

pip3 install bluechi python-can Flask Flask-Cors Werkzeug requests

##########################
# Installing applications and services in VM
#

# setup vcan
bash "${CURRDIR}/scripts/create-vcan.sh"

mkdir -p /var/demo/
cp "${CURRDIR}/applications/manager.py" /var/demo/
cp "${CURRDIR}/applications/tire-sensor.py" /var/demo/
cp "${CURRDIR}/applications/set-cpu-weight.py" /var/demo/

cp "${CURRDIR}/services/demo-manager.service" /etc/systemd/system/
cp "${CURRDIR}/services/demo-tire-sensor.service" /etc/systemd/system/
systemctl daemon-reload

##########################
# Building and starting bluechi worker image
#
podman build -t bluechi-worker -f "${CURRDIR}/container/worker" "${CURRDIR}"
podman run -d --network host --name worker bluechi-worker

##########################
# Building tire monitor image and install quadlet for it
#
podman build -t tire-monitor -f "${CURRDIR}/container/monitor" "${CURRDIR}"
cp -f "${CURRDIR}/services/demo-quadlet-monitor.container" /etc/containers/systemd/
systemctl daemon-reload

##########################
# Copying BlueChi configuration
#
cp -f "${CURRDIR}/bluechi-config/controller.conf" /etc/bluechi/controller.conf.d/
cp -f "${CURRDIR}/bluechi-config/agent-vm.conf" /etc/bluechi/agent.conf.d/agent.conf

##########################
# Starting BlueChi
#
systemctl restart bluechi-controller
systemctl restart bluechi-agent

podman exec -it worker systemctl start bluechi-agent

##########################
# Have demo script executable
#
chmod +x "${CURRDIR}/run.sh"

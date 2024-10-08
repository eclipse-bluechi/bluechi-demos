#!/usr/bin/bash
#
# Copyright Contributors to the Eclipse BlueChi project
#
# SPDX-License-Identifier: MIT-0

#######################
# Colors for terminal
RED='\033[0;31m'    
NC='\033[0m'    # No Color

CURRDIR=$(dirname "$(readlink -f "$0")")

function print_cmd() {
    echo -e "${RED}\$ ${1}${NC}"
}

function wait() {
    read -rs -n1 key
}

function run_and_wait() {
    print_cmd "$1"
    OUTPUT="$($1)"
    wait
    echo "${OUTPUT}"
    echo ""
    read -rsp $'Press any key to continue...\n' -n1 key
    echo ""
}

# setup vcan
bash "${CURRDIR}/scripts/create-vcan.sh"

#######################
# Show BlueChi configuration
run_and_wait "cat /etc/bluechi/controller.conf.d/controller.conf"
run_and_wait "cat /etc/bluechi/agent.conf.d/agent.conf"
run_and_wait "podman exec worker cat /etc/bluechi/agent.conf.d/agent.conf"

#######################
# Show system state
run_and_wait "systemctl status bluechi-controller"
run_and_wait "bluechictl status"
# in other terminal: 
# connect with laptop
run_and_wait "bluechictl status"
# in other terminal: 
# disconnect with laptop
run_and_wait "bluechictl status"
# in other terminal: 
# reconnect with laptop
run_and_wait "bluechictl status"

#######################
# Show bluechictl and proxy service use case
run_and_wait "bluechictl list-units"
run_and_wait "bluechictl list-units --filter=*.target"
run_and_wait "bluechictl list-unit-files --filter=*demo-*"

run_and_wait "cat /etc/systemd/system/demo-tire-sensor.service"
run_and_wait "cat /etc/systemd/system/demo-manager.service"
run_and_wait "podman exec worker cat /etc/systemd/system/demo-monitor.service"

run_and_wait "bluechictl start worker demo-monitor.service"
run_and_wait "bluechictl status worker demo-monitor.service bluechi-proxy@vm_demo-manager.service"
run_and_wait "bluechictl status vm demo-manager.service demo-tire-sensor.service bluechi-dep@demo-manager.service"

run_and_wait "journalctl -r -n 10 -u demo-tire-sensor.service"
run_and_wait "journalctl -r -n 10 -u demo-manager.service"
run_and_wait "podman exec worker journalctl -r -n 10 -u demo-monitor.service"

#######################
# Show BlueChi with Quadlets
run_and_wait "systemctl status demo-quadlet-monitor.service"
run_and_wait "cat /etc/containers/systemd/demo-quadlet-monitor.container"
run_and_wait "systemctl cat demo-quadlet-monitor.service"
run_and_wait "bluechictl start vm demo-quadlet-monitor.service"
run_and_wait "bluechictl status vm demo-quadlet-monitor.service"
run_and_wait "journalctl -r -n 10 -u demo-quadlet-monitor.service"
run_and_wait "podman container ls"
run_and_wait "bluechictl stop vm demo-quadlet-monitor.service"
run_and_wait "bluechictl status vm demo-quadlet-monitor.service"
run_and_wait "podman container ls"

#######################
# Show custom application
run_and_wait "cat /var/demo/set-cpu-weight.py"
run_and_wait "python3 /var/demo/set-cpu-weight.py vm demo-tire-sensor.service 10"
run_and_wait "systemctl cat demo-tire-sensor.service"

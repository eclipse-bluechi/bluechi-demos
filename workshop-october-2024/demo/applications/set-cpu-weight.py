#
# Copyright Contributors to the Eclipse BlueChi project
#
# SPDX-License-Identifier: MIT-0

import sys
from bluechi.api import Node, Variant


def set_cpu_weight(node_name: str, unit_name: str, cpu_weight: int):
    node = Node(node_name)
    if node.status != "online":
        print("Node {node_name} not online, aborting...")
        return

    node.set_unit_properties(
        unit_name, True, [("CPUWeight", Variant("t", cpu_weight))])


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f"Usage: python3 {sys.argv[0]} node_name unit_name cpu_weight")
        sys.exit(1)

    node_name = sys.argv[1]
    unit_name = sys.argv[2]
    value = int(sys.argv[3])

    set_cpu_weight(node_name, unit_name, value)

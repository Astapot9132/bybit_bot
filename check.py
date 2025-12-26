import asyncio
import math
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from pprint import pprint
from typing import Optional

result_dict = defaultdict(list)

@dataclass
class Node:
    value: str
    right: Optional["Node"] = None
    left: Optional["Node"] = None


def get_pairs(root: "Node"):
    global result_dict

    values = {root.value}

    if root.left:
        values = values.union(get_pairs(root.left))

    if root.right:
        values = values.union(get_pairs(root.right))

    result_dict[tuple(sorted(values))].append(root)

    return values



A = Node(value='A')
B = Node(value="B", right=A)
A2 = Node(value="A")
C = Node(value="C", right=B, left=A2)
A4 = Node(value="A")

A3 = Node(value="A", right=C, left=A4)


get_pairs(A3)
pprint(result_dict)


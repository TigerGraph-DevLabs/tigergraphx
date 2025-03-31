# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

import os
from tigergraphx import Graph


def main():
    os.environ["TG_HOST"] = "http://127.0.0.1"
    os.environ["TG_USERNAME"] = "tigergraph"
    os.environ["TG_PASSWORD"] = "tigergraph"

    G = Graph.from_db("RetailGraph")
    G.drop_graph()


if __name__ == "__main__":
    main()

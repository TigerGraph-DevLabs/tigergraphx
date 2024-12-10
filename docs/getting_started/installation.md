# Installation Guide

Follow this guide to install and set up **TigerGraphX** in your environment.

---

## Requirements

This project requires **Python 3.12** and **TigerGraph**. Ensure you meet the following prerequisites before proceeding:

### **1. Python 3.12**
- Please ensure Python 3.12 is installed on your system.
- You can download and install it from the [official Python website](https://www.python.org/downloads/).

### **2. TigerGraph**
TigerGraph is required for this project and can be set up in one of the following ways:
- **TigerGraph DB**: Install and configure a local instance of TigerGraph.
- **TigerGraph Cloud**: Use a cloud-hosted instance of TigerGraph.

Refer to the official [TigerGraph Documentation](https://docs.tigergraph.com/home/) for detailed installation and configuration instructions.

### **Connecting to TigerGraph**
Ensure that your Python environment can connect to your TigerGraph instance. You will need:
- **TigerGraph host address**.
- **API tokens** for authentication.

---

## Installing Dependencies

This project uses **Poetry** to manage dependencies. If you don’t already have Poetry installed, you can install it by following the instructions on the [Poetry website](https://python-poetry.org/docs/#installation).

Once Poetry is installed, navigate to the root directory of the project and run one of the following commands depending on your needs:

### **Option 1: Install Only TigerGraphX Core**
If you only want to use TigerGraphX without unit/integration tests and applications like GraphRAG, run:
```bash
poetry install --without dev
```

This command will:
- Read the `pyproject.toml` file.
- Install only the required dependencies needed for TigerGraphX.

---

### **Option 2: Install with Development Dependencies**
If you want to include development features such as unit/integration tests and applications like GraphRAG, run:
```bash
poetry install --with dev
```

This command will:
- Install all core dependencies.
- Include development dependencies specified in the `[tool.poetry.group.dev.dependencies]` section of `pyproject.toml`.

---

## Verifying the Installation

Once the dependencies are installed, you can verify your setup by running the following command:
```bash
poetry show --with dev
```

This will list all the installed dependencies in your environment.

---

## Next Steps

- [Quick Start](quick_start.md): Learn how to build your first graph with TigerGraphX.
- [GraphRAG Overview](../graphrag/overview.md): Explore GraphRAG workflows with TigerGraph.
- [API Reference](../reference/api.md): Dive into the TigerGraphX API.

---

Start unlocking the power of graph analytics with **TigerGraphX** today!

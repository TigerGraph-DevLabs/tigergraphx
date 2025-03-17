# Installation Guide

Follow this guide to install and set up **TigerGraphX** in your environment.

---

## Requirements

This project requires **Python 3.10, 3.11 or 3.12** and **TigerGraph**. Ensure you meet the following prerequisites before proceeding:

### **1. Python**
- Please ensure Python 3.10, 3.11 or 3.12 is installed on your system.
- You can download and install it from the [official Python website](https://www.python.org/downloads/).

### **2. TigerGraph**

TigerGraph is required for this project and can be set up in one of the following ways:

- **TigerGraph DB**: Install and configure a local instance of TigerGraph.
- **TigerGraph Cloud**: Use a cloud-hosted instance of TigerGraph.
- **TigerGraph Docker**: Use a Docker container to run TigerGraph.

It is recommended to use **TigerGraph LTS (Long-Term Support) Versions**, which can be downloaded from the [TigerGraph Downloads page](https://dl.tigergraph.com/). To enable support for **TigerVector** and leverage advanced features like hybrid retrieval, ensure you are using **TigerGraph 4.2 or above**.

Refer to the official [TigerGraph Documentation](https://docs.tigergraph.com/home/) for detailed installation and configuration instructions.

---

## Installation Steps


### **Option 1: Install from PyPI**

The simplest way to get started with **TigerGraphX** is by installing it directly from PyPI. Using a virtual environment is recommended to ensure a clean and isolated setup.

To install TigerGraphX, run:
```bash
pip install tigergraphx
```

This allows you to quickly start using the library without needing the source code.

#### **Verify Installation**

After installing, verify that TigerGraphX is installed correctly by running:
```bash
python -c 'import tigergraphx; print("TigerGraphX installed successfully!")'
```

If the installation was successful, you will see:
```
TigerGraphX installed successfully!
```

This ensures that the library is properly installed and ready for use.

---

### **Option 2: Build from Source Code**

If you want to modify or explore the source code, you can install TigerGraphX from its GitHub repository. The source code is available here: [TigerGraphX on GitHub](https://github.com/tigergraph/tigergraphx).

This project uses **Poetry** to manage dependencies. If you don’t have Poetry installed, follow the instructions on the [Poetry website](https://python-poetry.org/docs/#installation).

Once Poetry is installed, clone the repository, navigate to the project’s root directory, and use the following steps to set up your environment:

#### **1. Set Python Version**

Make sure to use Python 3.10–3.12:
```bash
poetry env use python3.12  # Replace with your Python version (3.10–3.12)
```

#### **2. Install Dependencies**

Choose one of the following commands based on your needs:

##### **Core Installation**
If you need only the core functionality of TigerGraphX (without running application examples like GraphRAG, unit tests, or integration tests), run:
```bash
poetry install --without dev
```

##### **Development Installation**
If you’re contributing to the project or want to use advanced features like running the GraphRAG examples or test cases, run:
```bash
poetry install --with dev
```

This will:

- Install all core dependencies.
- Include development dependencies defined under `[tool.poetry.group.dev.dependencies]` in `pyproject.toml`.

#### **3. Activate the Virtual Environment**

After installation, activate the Poetry-managed virtual environment:
```bash
eval $(poetry env activate)
```

---

## Next Steps

- [TigerGraphX Quick Start](quick_start_graph.ipynb): Learn how to build your first graph with TigerGraphX.

---

Start unlocking the power of graphs with **TigerGraphX** today!

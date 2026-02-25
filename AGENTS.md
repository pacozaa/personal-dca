## Code Organization

Breakdown the code into smaller file in appropriate subfolder. This is to maintain a clean and organized codebase. For example, you can create a `config` folder for configuration-related files, a `utils` folder for utility functions, and so on. This will help in better maintainability and readability of the code.

## Package Management
To install new packages,

run
```bash
source .venv/bin/activate
```

then
```bash
pip install <package-name>
```

then update `pyproject.toml` with the new package and its version

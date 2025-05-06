# Contributing to ebay_rest

Thank you for your interest in contributing to `ebay_rest`! We appreciate contributions from the community and look forward to collaborating with you.

## Table of Contents
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Code Guidelines](#code-guidelines)
- [Testing](#testing)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Release Steps](#release-steps)
- [License](#license)

---

## Getting Started
Before contributing, please take a moment to:

1. **Read the Project Overview:** Review the [README.md](README.md) to understand the purpose and structure of `ebay_rest`.
2. **Follow the Code of Conduct:** Please adhere to the [Code of Conduct](CODE_OF_CONDUCT.md) in all interactions.

---

## Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/matecsaj/ebay_rest.git
cd ebay_rest
```

### 2. Create and Activate a Virtual Environment
- On Linux/macOS:
  ```bash
  python -m venv venv
  source venv/bin/activate
  ```
- On Windows:
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```

### 3. Install Dependencies
```bash
pip install -e '.[complete,dev]'
playwright install chromium
```

### 4. Install Swagger Codegen (Optional, for API updates)
- **macOS (Homebrew):**
  ```bash
  brew install swagger-codegen
  ```

### 5. Set Up Configuration
Copy the example config file:
```bash
cp tests/ebay_rest_sample.json tests/ebay_rest.json
```
Then, follow the instructions inside `ebay_rest.json`.

### 6. Verify Installation
Check if dependencies are installed correctly:
```bash
black --version  # Should print the installed version
```

---

## How to Contribute
We welcome various types of contributions:

- **Bug Fixes**: If you find a bug, consider fixing it and submitting a pull request.
- **New Features**: Submit an issue or a pull request with your proposed enhancement.
- **Documentation**: Improvements to documentation are always welcome.

### Contribution Tips
- Review error codes in the `Error` class.
- Check for `README.md` files in subdirectories; they may contain additional information.
- Follow test-driven development: modify `tests/ebay_rest.py` while implementing changes.
- Run `/scripts/generate_code.py` periodically to sync with eBay API updates.
- Some unit tests may fail due to eBay's sandbox resetting daily—retry the next day if needed.

---

## Code Guidelines

### Formatting
This project uses `black` for code formatting. Before submitting a pull request, format your code:
```bash
black .
```

### Testing
Run the test suite before submitting changes:
```bash
python -m unittest discover
```

---

## Submitting a Pull Request

1. **Fork the repository** on GitHub.
2. **Create a new branch** for your feature/fix:
   ```bash
   git checkout -b my-feature-branch
   ```
3. **Make and commit your changes**:
   ```bash
   git commit -m "Describe your change concisely"
   ```
4. **Push to your fork**:
   ```bash
   git push origin my-feature-branch
   ```
5. **Open a Pull Request** on GitHub.

---

## Release Steps

1. **Update dependencies and tools:**
   ```bash
   brew update && brew upgrade && brew cleanup  # macOS only
   python -m pip install --upgrade pip && python -m pip install --upgrade -e ".[complete,dev]"
   playwright install chromium
   pipreqs --print src  # Lists required dependencies
   ```

2. **Update `pyproject.toml`**:
   - Update dependencies based on `pipreqs` output.
   - Increment the [Semantic Version](https://semver.org/) accordingly.

3. **Validate changes:**
   - Regenerate code from the latest eBay OpenAPI contracts. This updates [a_p_i.py](src/ebay_rest/a_p_i.py) and the [api](src/ebay_rest/api) package:
   ```bash
   /scripts/generate_code.py
   ```
   - Run all unit tests:
   ```bash
   pytest tests/ --tb=short -q
   ```
   - Fix any issues without modifying the generated code directly.

4. **Build and publish the package:**
   ```bash
   black .
   python3 -m build
   python3 -m twine upload dist/*X.Y.Z*
   ```
   Replace `X.Y.Z` with the new version number and provide credentials when prompted.

---

## License
By contributing to `ebay_rest`, you agree that your contributions will be licensed under the [MIT License](LICENSE).


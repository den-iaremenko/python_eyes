![Logo](python_eyes_logo.jpeg)


# Python Eyes
[![PyPI version](https://badge.fury.io/py/python-eyes.svg)](https://badge.fury.io/py/python-eyes)
[![MIT License](https://img.shields.io/apm/l/atomic-design-ui.svg?)](https://github.com/tterb/atomic-design-ui/blob/master/LICENSEs)

Python package for Automation to compare expected UI on page or Mobile app screen with actual screen.

# Notice

**Since v0.0.1 only Python 3 is supported**

# Getting the Python Eye

1. Install from [PyPi](https://pypi.org), as
['python_eyes'](https://pypi.org/project/python-eyes/).

```bash
pip install python_eyes
```

# Development

- Docstring style: Google Style
    - Refer [link](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)

# Run tests

```bash
pipenv run pytest
```

# Usage

```python
from python_eyes import PythonEyes


eyes = PythonEyes(driver, "screenshots", "results")
eyes.verify_screen("login_page_no_text.png")
eyes.verify_screen("login_page_error.png", hard_assert=False, timeout=2)
```


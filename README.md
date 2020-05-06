![Logo](https://drive.google.com/file/d/1FmE9jmJAv5rx8ltqQJVSN4hSsHZopMsH/view?usp=sharing)


#Python Eye

[![PyPI version](https://badge.fury.io/py/python-eyes.svg)](https://badge.fury.io/py/python-eyes)
[![MIT License](https://img.shields.io/apm/l/atomic-design-ui.svg?)](https://github.com/tterb/atomic-design-ui/blob/master/LICENSEs)

Python package for Automation to compare expected UI on page or Mobile app screen with actual screen.

# Notice

**Since v0.0.1 only Python 3 is supported**

# Getting the Python Eye

1. Install from [PyPi](https://pypi.org), as
['python_eyes'](https://pypi.org/project/python-eyes/).

```shell
pip install python_eyes
```

# Development

- Docstring style: Google Style
    - Refer [link](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)


# Run tests


```
$ pytest
```

You also can run particular tests like below.

```
$ pytest test/unit
```

Run with `pytest-xdist`

```
$ pytest -n 2 test/unit
```

# Usage

```python
from python_eyes import PythonEyes


eyes = PythonEyes(driver, "screenshots", "results")
eyes.find_difference("screenshot.png")
```

# Build & Release 

```bash
sudo python3.8 setup.py sdist bdist_wheel

twine upload --repository pypi dist/*
```
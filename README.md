Python Eye
====================

Python package for Automation to compare expected UI on page or Mobile app screen with actual screen.

# Notice

**Since v0.0.1 only Python 3 is supported**

# Getting the Python Eye

1. Install from [PyPi](https://pypi.org), as
['python_eye'](https://pypi.org/project/python-eye/).

```shell
pip install python_eye
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
from python_eye.python_eye import PythonEye
```

# Build & Release 

```bash
sudo python3.8 setup.py sdist bdist_wheel

twine upload --repository pypi dist/*
```
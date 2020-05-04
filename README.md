Python Eye
====================

Python package for Automation to compare expected UI on page or Mobile app screen with actual screen.

# Notice

**Since v1.0.0 only Python 3 is supported**

# Getting the Python Eye

1. Install from [PyPi](https://pypi.org), as
['Python_eye'](https://pypi.org/project/Python_Eye/).

```shell
pip install python_eye
```


# Development

- Docstring style: Google Style
    - Refer [link](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)




## Run tests


```
$ pytest
```

You also can run particular tests like below.

### Unit

```
$ pytest test/unit
```

Run with `pytest-xdist`

```
$ pytest -n 2 test/unit
```

# Usage

```python
from python_eye import PythonEye
```

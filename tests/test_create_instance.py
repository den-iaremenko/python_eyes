from python_eye import PythonEye


def test_create_python_eye():
    p_e = PythonEye("test", "test", "test")
    assert isinstance(p_e, PythonEye), "Instance is not created"

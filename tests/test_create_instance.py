from python_eyes import PythonEyes


def test_create_python_eye():
    p_e = PythonEyes("test", "test", "test")
    assert isinstance(p_e, PythonEyes), "Instance is not created"

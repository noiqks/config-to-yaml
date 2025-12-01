from src.main import tokenize, parse, resolve_constants

def test_simple_array():
    code = "arr is { 0o1, 0o2, 0o3 };"
    tokens = tokenize(code)
    parsed, errors = parse(tokens)
    resolved, resolve_errors = resolve_constants(parsed)
    assert resolved["arr"] == [1, 2, 3]
    assert not errors
    assert not resolve_errors

def test_nested_array():
    code = "matrix is { { 0o1, 0o2 }, { 0o3, 0o4 } };"
    tokens = tokenize(code)
    parsed, errors = parse(tokens)
    resolved, resolve_errors = resolve_constants(parsed)
    assert resolved["matrix"] == [[1, 2], [3, 4]]
    assert not errors
    assert not resolve_errors

def test_array_with_reference():
    code = """
    a is 0o10;
    b is { 0o1, [a], 0o3 };
    """
    tokens = tokenize(code)
    parsed, errors = parse(tokens)
    resolved, resolve_errors = resolve_constants(parsed)
    assert resolved["a"] == 8
    assert resolved["b"] == [1, 8, 3]
    assert not errors
    assert not resolve_errors

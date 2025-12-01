from src.main import tokenize, parse, resolve_constants

def test_integers():
    code = "x is 0o10;\ny is 0o20;"
    tokens = tokenize(code)
    parsed, errors = parse(tokens)
    resolved, resolve_errors = resolve_constants(parsed)
    assert resolved["x"] == 8
    assert resolved["y"] == 16
    assert not errors
    assert not resolve_errors

def test_mixed_numbers_and_reference():
    code = """
    a is 0o5;
    b is 0o12;
    c is [a];
    """
    tokens = tokenize(code)
    parsed, errors = parse(tokens)
    resolved, resolve_errors = resolve_constants(parsed)
    assert resolved["a"] == 5
    assert resolved["b"] == 10
    assert resolved["c"] == 5
    assert not errors
    assert not resolve_errors

def test_nested_numbers_array():
    code = "nums is { { 0o1, 0o2 }, { 0o3, 0o4 } };"
    tokens = tokenize(code)
    parsed, errors = parse(tokens)
    resolved, resolve_errors = resolve_constants(parsed)
    assert resolved["nums"] == [[1, 2], [3, 4]]
    assert not errors
    assert not resolve_errors

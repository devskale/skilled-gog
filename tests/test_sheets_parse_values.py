from google_workspace_tools.sheets import parse_values_arg


def test_parse_single_value():
    assert parse_values_arg(["A"]) == [["A"]]


def test_parse_pipe_values():
    assert parse_values_arg(["A|B|C"]) == [["A", "B", "C"]]


def test_parse_comma_values():
    assert parse_values_arg(["A,B,C"]) == [["A", "B", "C"]]


def test_parse_multiple_args():
    assert parse_values_arg(["A", "B", "C"]) == [["A", "B", "C"]]

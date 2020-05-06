from coronabot import data

def test_get_global_cases():
    response = data.get_global_cases()
    assert isinstance(response["cases"], dict)
    assert isinstance(response["deaths"], dict)
    assert isinstance(response["recovered"], int)

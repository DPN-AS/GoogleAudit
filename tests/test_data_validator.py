import data_validator


def test_validate_email():
    assert data_validator.validate_email('user@example.com')
    assert not data_validator.validate_email('invalid')


def test_validate_domain():
    assert data_validator.validate_domain('example.com')
    assert not data_validator.validate_domain('no spaces')


def test_sanitize_filename():
    name = data_validator.sanitize_filename('bad/name\\file.txt')
    assert '/' not in name and '\\' not in name

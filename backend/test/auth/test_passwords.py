from backend.auth.passwords import hash_password, verify_password


def test_hash_verify_round_trip():
    hashed = hash_password("secret")
    assert verify_password("secret", hashed)


def test_wrong_password_fails():
    hashed = hash_password("secret")
    assert not verify_password("wrong", hashed)

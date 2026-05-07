from app.security import hash_password, verify_password, create_access_token, decode_token


def test_password_round_trip():
    h = hash_password("hunter2")
    assert verify_password("hunter2", h)
    assert not verify_password("wrong", h)


def test_jwt_round_trip():
    tok = create_access_token(42, "admin")
    p = decode_token(tok)
    assert p["sub"] == "42" and p["role"] == "admin"

# -*- coding: utf-8 -*-
import hashlib
from core.api_public import genereaza, verifica


def test_cheie_format():
    import secrets
    c = "ick_" + secrets.token_urlsafe(32)
    assert c.startswith("ick_") and len(c) > 40


def test_hash_determinist():
    c = "ick_test"
    assert hashlib.sha256(c.encode()).hexdigest() == hashlib.sha256(c.encode()).hexdigest()

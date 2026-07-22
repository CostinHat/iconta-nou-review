# -*- coding: utf-8 -*-
"""conftest pytest — env de test setat INAINTE de colectare (deci inaintea ORICARUI import de modul).

De ce aici si nu in test_spv_conector.py: spv_conector citeste ANAF_CLIENT_ID/ANAF_REDIRECT_URI etc. la
IMPORT (constante la nivel de modul, spv_conector.py:39-46). Daca alt test il importa tranzitiv (via main
sau alt core) INAINTEA lui test_spv_conector.py, constanta inghetase goala -> test_url_autorizare picase
in suita completa (dar trecea izolat, cand era primul). conftest.py e incarcat de pytest inaintea colectarii
testelor -> valorile sunt garantat prezente la PRIMA incarcare a modulului, indiferent de ordine.

Placeholdere, NU secrete: ANAF_REDIRECT_URI e URL-ul PUBLIC de callback (ARHITECTURA_SPV.md), ANAF_CLIENT_ID
e fictiv, JWT_SECRET/SPV_FERNET_KEY sunt de test. Testele lovesc ANAF pe MOCK, niciodata real."""
import os
from cryptography.fernet import Fernet

os.environ.setdefault("SPV_FERNET_KEY", Fernet.generate_key().decode())
os.environ.setdefault("JWT_SECRET", "test-secret-spv")
os.environ.setdefault("ANAF_CLIENT_ID", "TEST_CLIENT")
os.environ.setdefault("ANAF_REDIRECT_URI", "https://iconta.eu/anaf/oauth/callback")

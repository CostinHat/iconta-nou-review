# -*- coding: utf-8 -*-
"""GARD edge SEO/crawler (_edge_canonic_head din main.py):
  #1 www.iconta.eu -> 301 permanent catre forma canonica (fara www), PASTRAND calea+query;
  #2 HEAD pe rutele GET -> 200 (FastAPI nu adauga HEAD implicit -> era 405; Googlebot foloseste HEAD).
Face imposibila reaparitia: duplicat www/non-www (semnal SEO impartit) si 405 pe HEAD (buget crawl irosit).
In-process (TestClient), fara server; / si /ghid nu ating DB. Aserturi ASCII."""
import os
from fastapi.testclient import TestClient
import main

C = TestClient(main.app)
CANONIC = "https://iconta.eu"


def test_head_pe_rute_get_da_200_nu_405():
    for path in ("/", "/ghid", "/ghid/casare-mijloc-fix"):
        r = C.head(path)
        assert r.status_code == 200, "HEAD %s -> %s (asteptat 200; FastAPI fara HEAD da 405)" % (path, r.status_code)


def test_head_are_content_length_ca_get():
    # HEAD trebuie sa raporteze aceeasi lungime ca GET (Googlebot compara ca sa decida re-descarcarea)
    rh = C.head("/")
    rg = C.get("/")
    assert rh.headers.get("content-length") == rg.headers.get("content-length"), \
        "Content-Length HEAD != GET: %s vs %s" % (rh.headers.get("content-length"), rg.headers.get("content-length"))


def test_www_redirect_301_catre_canonic():
    r = C.get("/", headers={"Host": "www.iconta.eu"}, follow_redirects=False)
    assert r.status_code == 301, "www / -> %s (asteptat 301 permanent)" % r.status_code
    assert r.headers.get("location") == CANONIC + "/", "Location=%s" % r.headers.get("location")


def test_www_redirect_pastreaza_calea_si_query():
    r = C.get("/ghid/casare-mijloc-fix", headers={"Host": "www.iconta.eu"}, follow_redirects=False)
    assert r.status_code == 301
    assert r.headers.get("location") == CANONIC + "/ghid/casare-mijloc-fix", \
        "calea nu e pastrata: %s" % r.headers.get("location")
    r2 = C.get("/ghid?x=1", headers={"Host": "www.iconta.eu"}, follow_redirects=False)
    assert r2.headers.get("location") == CANONIC + "/ghid?x=1", "query nu e pastrat: %s" % r2.headers.get("location")


def test_non_www_ramane_200_fara_redirect():
    r = C.get("/", headers={"Host": "iconta.eu"}, follow_redirects=False)
    assert r.status_code == 200, "non-www / -> %s (nu trebuie redirectat)" % r.status_code


def test_www_redirect_si_pe_head():
    r = C.head("/ghid", headers={"Host": "www.iconta.eu"}, follow_redirects=False)
    assert r.status_code == 301 and r.headers.get("location") == CANONIC + "/ghid"

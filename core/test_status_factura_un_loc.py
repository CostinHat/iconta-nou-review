# -*- coding: utf-8 -*-
"""GARDĂ: stările unei FACTURI trăiesc într-un singur loc. (22.08.2026, după reparația de prag 1)

DE CE. Lista stărilor nedeclarabile era scrisă **textual în trei locuri** (`d300.py:52`, `d300.py:1095`,
`d300_reconciliere.py:80`), iar `de_preluat` era clasat *staging* deși `facturi_api.emite_factura` îl
produce ca stare a unei facturi EMISE. Efect măsurat înainte de reparație: **4 facturi emise, 3
plătitori de TVA, 3.052,00 lei TVA colectată, în afara decontului**. După: aceleași ferestre dau
t003 0 → 889,00 · t005 0 → 2.100,00 · t013 315,00 → 378,00.

CE FACE IMPOSIBIL: o listă de stări de FACTURĂ scrisă din nou în alt modul · schimbarea tăcută a
deciziei `de_preluat = declarabilă` · o clauză SQL care nu corespunde nomenclatorului.

CE NU FACE, declarat: nu verifică dacă decizia e CORECTĂ — e o interpretare (P11), consemnată în
antetul nomenclatorului cu varianta respinsă numită, de confirmat de Costin. Garda o face doar
imposibil de schimbat fără să se vadă.

CUM S-A CALIBRAT, cu cele două forme de orbire prinse în construcție:
  1. prima formă citea și DOCSTRINGURILE — se aprindea pe `export_winmentor.py:162` și
     `export_saga.py:157`, care DESCRIU regula în proză. Reparat cu `scan_ancore.domenii_docstring`,
     instrumentul care există deja pentru fix clasa asta (a fost scris după ce un gard a „găsit"
     coloane într-un docstring);
  2. a doua formă clasifica NUMELE, nu OBIECTUL: `ciorna` și `descarcata` sunt și stări ale tabelei
     `efactura_primite` — alt obiect, alt nomenclator. Trei false pozitive (`main.py`,
     `spv_receive.py`, `migrare_efactura_primite.py`). Discriminatorul corect e `de_preluat`, care
     apare NUMAI la facturi.
"""
import io
import os

import pytest

from core import nomenclator_status_factura as nsf
from core import scan_ancore

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOMENCLATOR = os.path.join("core", "nomenclator_status_factura.py")
STARI = tuple(nsf.STARI)
DISCRIMINATOR = "de_preluat"      # apare numai la facturi; `ciorna`/`descarcata` sunt si la e-Factura


def test_nomenclatorul_chiar_are_stari():
    """ANTI-VACUU: fără el, testele de mai jos ar trece pe un nomenclator golit."""
    assert len(nsf.STARI) >= 5, "doar %d stări — nomenclatorul s-a golit?" % len(nsf.STARI)
    assert DISCRIMINATOR in nsf.STARI and "ciorna" in nsf.STARI


def test_decizia_de_preluat_nu_se_schimba_tacut():
    """Decizia de interpretare, PINATĂ. Dacă cineva o întoarce, pică aici — nu peste trei luni, pe o
    firmă reală, cu TVA colectată lipsă din decont."""
    assert nsf.e_declarabila("de_preluat"), (
        "`de_preluat` a redevenit nedeclarabilă. E starea în care `facturi_api.emite_factura` produce "
        "o factură EMISĂ, iar nimic din repo nu o scoate de acolo — deci varianta asta face orice "
        "factură emisă de aplicație invizibilă în D300 (măsurat: 3.052,00 lei). Dacă schimbarea e "
        "voită, se schimbă ÎNTÂI decizia din antetul nomenclatorului, cu motivul.")
    assert nsf.e_declarabila("emisa") and nsf.e_declarabila("importata")
    assert not nsf.e_declarabila("ciorna") and not nsf.e_declarabila("anulata")


def test_clauza_sql_corespunde_nomenclatorului():
    c = nsf.clauza_sql("f")
    exclus = c.split("NOT IN", 1)[1]
    for s in nsf.nedeclarabile():
        assert "'%s'" % s in exclus, "starea %r lipsește din lista exclusă" % s
    for s in nsf.declarabile():
        assert "'%s'" % s not in exclus, "starea declarabilă %r apare printre excluse" % s
    assert nsf.clauza_sql(None).startswith("COALESCE(status")


def _linii_de_cod(cale):
    """Liniile care NU sunt docstring. Se folosește `scan_ancore.domenii_docstring` — instrumentul
    care există deja pentru clasa asta, în loc de unul nou (METODA §5, pasul 5)."""
    t = io.open(cale, encoding="utf-8", errors="replace").read()
    proza = set()
    for a, b in scan_ancore.domenii_docstring(t):
        proza.update(range(a, (b or a) + 1))
    for i, ln in enumerate(t.splitlines(), 1):
        if i in proza or ln.lstrip().startswith("#"):
            continue
        yield i, ln


def test_nimeni_nu_mai_scrie_lista_de_stari_de_factura():
    """Un adevăr scris în două locuri dă două răspunsuri la prima divergență — și a dat."""
    rele = []
    for r, _d, fis in os.walk(RAD):
        if "/venv" in r or "/.git" in r:
            continue
        for x in fis:
            if not x.endswith(".py"):
                continue
            rel = os.path.relpath(os.path.join(r, x), RAD)
            if rel == NOMENCLATOR or rel.startswith("core/test_"):
                continue
            for i, ln in _linii_de_cod(os.path.join(r, x)):
                if ("'%s'" % DISCRIMINATOR) not in ln and ('"%s"' % DISCRIMINATOR) not in ln:
                    continue
                alte = [s for s in STARI if s != DISCRIMINATOR
                        and ("'%s'" % s in ln or '"%s"' % s in ln)]
                if alte:
                    rele.append("  %s:%d — %s + %s" % (rel, i, DISCRIMINATOR, ", ".join(alte)))
    assert not rele, (
        "liste de stări de FACTURĂ scrise în afara nomenclatorului (%d):\n%s\n"
        "Se citesc din `core/nomenclator_status_factura.py` (clauza_sql / e_declarabila)."
        % (len(rele), "\n".join(rele[:15])))


def test_gardul_ar_prinde_forma_veche():
    """ANTI-VACUU pe INSTRUMENT: proba că tiparul chiar potrivește lista de dinainte de reparație.
    Fără ea, testul de mai sus ar putea trece fiindcă nu poate potrivi nimic."""
    vechi = ("COALESCE(f.status, 'emisa') NOT IN "
             "('ciorna', 'de_preluat', 'descarcata', 'anulata', 'stornata')")
    alte = [s for s in STARI if s != DISCRIMINATOR and "'%s'" % s in vechi]
    assert ("'%s'" % DISCRIMINATOR) in vechi and len(alte) >= 3


@pytest.mark.parametrize("modul", ["core/d300.py", "core/d300_reconciliere.py"])
def test_cei_doi_consumatori_citesc_registrul(modul):
    """Nu e destul ca NUMELE modulului să apară: un import nefolosit nu e o citire. Se cere APELUL.

    Prins de RED-proof: mutația care aliaza importul (`_nsf = _x_nsf`) trecea de prima formă a
    testului, fiindcă șirul „nomenclator_status_factura" rămânea în fișier."""
    t = io.open(os.path.join(RAD, modul), encoding="utf-8").read()
    assert "nomenclator_status_factura" in t, "%s nu importă nomenclatorul" % modul
    assert "clauza_sql(" in t, (
        "%s importă nomenclatorul dar nu-l APELEAZĂ — un import nefolosit nu e o citire" % modul)

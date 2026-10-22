# -*- coding: utf-8 -*-
"""Lotul 11, deficiența 440 pe nota contabilă (comanda Costin 11.1 pct.16, verbatim): „toate erorile apar deodată, fiecare cu textul ei,
în casetă și lângă câmp.” Subagentul W1, lista U0 „SERVER” pct.B33 (`jurnal_api.creeaza` -> `_data_valida` + `_linii_valide`) și B34
(`jurnal_api.editeaza`).

Cauza: validarea notei (data, apoi fiecare linie, apoi fiecare câmp al liniei) se oprea la PRIMA problemă (`return _refuz(...)` în buclă),
iar `uc_comun._jurnal_rez` trimitea ecranului un singur câmp. O notă cu două linii greșite se refuza de patru ori la rând, câte o problemă.
Acum colectorul unic al formularelor (`core.erori.ErorileFormularului`, prin `jurnal_api._ErorileNotei`) adună toate problemele și refuzul
le poartă pe toate: `mesaj` (fiecare cu textul ei, rând cu rând) și `erori_campuri` cu id-urile câmpurilor din editorul notei
(`je-data`, `je-deb-i`, `je-cre-i`, `je-sum-i`, `je-pcui-i`, `je-pnume-i` — `static/js/ecrane/firme.js`, `ecranJurnal`).

Temeiurile refuzurilor (neschimbate, citate de fiecare problemă): Legea 82/1991 art.5 alin.(1) („[...] au obligatia sa conduca
contabilitatea in partida dubla [...]”) și art.6 alin.(1) („Orice operatiune economico-financiara efectuata se consemneaza in momentul
efectuarii ei intr-un document [...]”) — `jurnal_api.TEMEI_PARTIDA_DUBLA` / `TEMEI_CONSEMNARE`, sursa `anaf_surse/legea_82_1991_consolidat.txt`.

CE FACE IMPOSIBIL:
  1. validarea notei oprită la prima linie / primul câmp (creare și editare);
  2. lista erorilor pierdută între producător și ecran (`_jurnal_rez` care o înlocuiește cu un singur câmp);
  3. o sumă care nu e număr ieșind 500 în loc de refuz numit.
"""
import pytest

from core import db as _db, jurnal_api as _j, tenant_provisioning as _tp
from core.test_jurnal_refuz import _ConnFals

_SCHEMA = "test_lot11_w1_440"

#: două linii, patru probleme: (1) contul debitor din afara planului și contul creditor lipsă; (2) suma negativă și 401 fără partener
_LINII_RELE = [{"debit": "9999", "credit": "", "suma": 100},
               {"debit": "401", "credit": "5121", "suma": -5}]
_CAMPURI_RELE = ["je-deb-0", "je-cre-0", "je-sum-1", "je-pnume-1"]


def _campuri(r):
    return [c["camp"] for c in (r or {}).get("erori_campuri") or []]


def test_liniile_cu_patru_probleme_dau_un_refuz_cu_toate_patru():
    """1. MUTAȚIE: în `_erori_linii`, `continue` după contul lipsă -> `return` (oprire la prima) -> o singură eroare -> pică."""
    r = _j._linii_valide(_ConnFals(), "ztest", _LINII_RELE)
    assert _campuri(r) == _CAMPURI_RELE, r                      # 440: „toate erorile apar deodată”
    m = r["eroare"]
    assert m.startswith("Nota nu s-a salvat:\n"), m
    for bucata in ("linia 1: Contul 9999", "linia 1 n-are contul creditor", "linia 2 are suma -5", "linia 2 e pe contul 401"):
        assert bucata in m, (bucata, m)                         # 440: „fiecare cu textul ei”
    # fiecare text din listă e și în `mesaj` (caseta / zona ecranului îl arată întreg, câmpul îl primește pe al lui)
    assert all(c["mesaj"] in m for c in r["erori_campuri"])
    # Legea 82/1991 art.5 alin.(1) (partida dublă) și art.6 alin.(1) (consemnarea) — ambele temeiuri, câte o dată
    assert r["temei"] == "%s; %s" % (_j.TEMEI_PARTIDA_DUBLA, _j.TEMEI_CONSEMNARE), r["temei"]
    assert r["linia"] == 1


def test_crearea_numeste_data_si_liniile_deodata():
    """1. Data proastă nu mai oprește verificarea liniilor. MUTAȚIE: în `creeaza`, `if er: return er.refuz()` mutat imediat după
    `_erori_data` -> numai „je-data” -> pică. Fără bază: refuzul pleacă înainte de orice scriere."""
    r = _j.creeaza(_ConnFals(), "ztest", "Notă 440", "ieri", _LINII_RELE)
    assert not r.get("ok") and _campuri(r) == ["je-data"] + _CAMPURI_RELE, r
    # primul rând al refuzului e data, întreagă (core/test_garzi_pe_text.py), urmată de liniile greșite
    assert r["eroare"].split("\n— ")[:2] == [
        "Nota nu s-a salvat:", "data 'ieri' nu e in formatul AAAA-LL-ZZ. Se cere o data calendaristica, fiindca inregistrarea se face la "
        "momentul operatiunii, iar ordinea cronologica a registrului-jurnal atarna de ea"], r["eroare"]


def test_o_singura_problema_pastreaza_textul_ei_exact():
    """Anti-vacuu pe formă: cu o singură problemă, mesajul e textul ei (fără titlul listei) — ca înainte."""
    r = _j._linii_valide(_ConnFals(), "ztest", [{"debit": "4111", "credit": "704", "suma": 0, "partener_nume": "PARTENER PROBA SRL"}])
    assert r["eroare"].startswith("linia 1 are suma 0:") and _campuri(r) == ["je-sum-0"], r


@pytest.mark.parametrize("suma", [None, "abc", "", "NaN"])
def test_suma_care_nu_e_numar_e_refuz_numit_nu_500(suma):
    """3. MUTAȚIE: `except (InvalidOperation, ValueError)` scos -> `InvalidOperation` (500) -> pică."""
    r = _j._linii_valide(_ConnFals(), "ztest", [{"debit": "4111", "credit": "704", "suma": suma, "partener_nume": "PARTENER PROBA SRL"}])
    assert _campuri(r) == ["je-sum-0"], r


def test_linia_care_nu_e_dict_e_refuz_nu_500():
    r = _j._linii_valide(_ConnFals(), "ztest", ["x", {"debit": "4111", "credit": "", "suma": 5, "partener_nume": "P"}])
    assert "linia 1 nu are forma unei linii de notă" in r["eroare"] and _campuri(r) == ["je-cre-1"], r


def test_stratul_use_case_trece_lista_intreaga_spre_ecran():
    """2. `uc_comun._jurnal_rez` (refuzul tradus pentru HTTP) nu înlocuiește lista cu un singur câmp. MUTAȚIE: `_ErorileNotei.refuz`
    pune `camp` = primul câmp (forma veche) -> `_jurnal_rez` scrie un singur câmp -> pică."""
    from core import erori as _erori, uc_comun
    r = _j._linii_valide(_ConnFals(), "ztest", _LINII_RELE)
    with pytest.raises(_erori.CerereGresita) as e:
        uc_comun._jurnal_rez(r)
    det = e.value.detaliu
    assert [c["camp"] for c in det["erori_campuri"]] == _CAMPURI_RELE and det["mesaj"] == r["eroare"], det


def test_campurile_numite_exista_in_editorul_notei():
    """Contractul cu ecranul: prefixele din `_CAMP_LINIE` și `je-data` sunt clasele / id-urile editorului notei din firme.js (altfel
    refuzul ar numi câmpuri pe care ecranul nu le are)."""
    import io
    import os
    from core.arbore_js import arbore_js, elemente_html
    src = io.open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "js", "ecrane", "firme.js"),
                  encoding="utf-8").read()
    arb, _cod = arbore_js("firme.js")   # câmpul datei ca element HTML cu id-ul lui, nu șir în sursă (core/test_garzi_pe_text.py)
    assert [tag for tag, at in elemente_html(arb) if at.get("id") == "je-data"] == ["input"]
    for pref in _j._CAMP_LINIE.values():
        assert 'class="camp-input %s"' % pref in src, pref


# ── editarea (B34), pe o schemă efemeră din tenant_template ────────────────────────────────────────────────────────────────────────
def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
            cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
            cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)   # pe tranzacție (core/test_lot10_search_path_pool.py)
        try:
            yield c
        finally:
            c.rollback()
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
            c.commit()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_editarea_numeste_data_si_toate_liniile_si_nu_schimba_nota(conn):
    """1 (B34). MUTAȚIE: în `editeaza`, verificarea liniilor sărită când data e greșită (`if data is not None: ... ; if er: return`)
    -> numai „je-data” -> pică. Nota rămâne neatinsă (refuzul pleacă înainte de DELETE / INSERT)."""
    r = _j.creeaza(conn, _SCHEMA, "Chirie 440", "2026-10-03", [{"debit": "612", "credit": "5121", "suma": 100}], "Contract 440")
    assert r.get("ok"), r
    e = _j.editeaza(conn, _SCHEMA, r["id"], data="03.10.2026", linii=_LINII_RELE)
    assert _campuri(e) == ["je-data"] + _CAMPURI_RELE, e
    with conn.cursor() as cur:
        cur.execute("SELECT cont_debit, cont_credit, suma::text FROM inregistrari_linii WHERE inregistrare_id = %s", (r["id"],))
        assert cur.fetchall() == [("612", "5121", "100.00")]

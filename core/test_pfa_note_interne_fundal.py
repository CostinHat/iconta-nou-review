# -*- coding: utf-8 -*-
"""GARD — deficiența 368 pe drumurile FĂRĂ middleware (decizia Costin 19.10.2026, verbatim în DECIZII „Închiderea lotului 9”): „Se
validează automat — la PFA nota scrisă în fundal (Casă, Bancă, facturi, Z, salarii) se validează automat la scriere, ca «notă internă»,
cu documentul ei (regula R3)”.  # TEMEI LIBER: citat verbatim al deciziei

Middleware-ul (`main._autor_si_note_in_coada`) validează notele cererilor `Bearer` pe `/tenants/{id}/…`. Trei drumuri scriu note fără
el, deci își cheamă singure `uc_coada.note_interne_schema(schema, None, de_la)` după commitul scrierii (notele lor n-au autor):
  · `uc_api.apiv1_factura_emite`            — POST /api/v1/firme/{tid}/facturi, cheie API (`X-Api-Key`, nu `Bearer`);
  · `facturi_recurente.emite_scadente`      — cronul facturilor recurente, per firmă;
  · `woocommerce.sincronizeaza`             — cronul de la 07:30 (și ruta din ecran, unde îl dublează inofensiv middleware-ul).

Ce fac imposibil, pe fiecare drum: nota facturii unei PFA rămasă ciornă; validarea internă la partidă dublă; un refuz al validării (nota
fără document, R3) care rupe drumul sau rămâne nespus; o eroare a validării interne care rupe emiterea. Partea externă e simulată (modelul
AI, magazinul WooCommerce prin HTTP, ANAF pentru tert), logica nu. Probele rulează pe schema efemeră din `core/test_pfa_note_interne.py`
(tenant_template), în tranzacție anulată.

Temei: OMFP 170/2015 (partida simplă: evidența e registrul de încasări și plăți, nota poartă TVA-ul pentru D300 / D394); Legea 82/1991
art.6 alin.(1) (documentul justificativ — regula de fond R3 din bază, aplicată și aici, nu ocolită).
"""
import datetime as _dt
import json

import pytest

from core.test_pfa_note_interne import SCH, _lume, _stari   # fixtura și ajutoarele, refolosite, nu copiate

_RASPUNS_AI = '{"cota": 21, "categorie": "standard", "tip": "servicii", "justificare": "regula standard", "incredere": "mare"}'
_AZI = _dt.date(2026, 10, 10)
_LINIE = {"descriere": "Mentenanta platforma web", "cantitate": 1, "pret_unitar": 100, "um": "buc"}
DRUMURI = ("api", "recurente", "woocommerce")


def _fundal(conn, monkeypatch):
    """Lumea unui drum de fundal: fără autor pe conexiune (cheia API / cronul nu au utilizator -> `creat_de_id` NULL), serie de facturi,
    modelul AI și ANAF simulate (externe)."""
    from core import ai_client, facturi_api, uc_comun
    with conn.cursor() as cur:
        cur.execute("SELECT set_config('iconta.utilizator', '', false)")
        # `now()` e începutul tranzacției fixturii (schema e creată în ea); în producție fiecare scriere își are tranzacția ei, deci
        # `creat_la` e momentul scrierii — aici la fel, ca proba să nu depindă de cât a durat crearea schemei
        cur.execute("ALTER TABLE inregistrari ALTER COLUMN creat_la SET DEFAULT clock_timestamp()")
    facturi_api.seteaza_numerotare(conn, serie="PF", numar_start=1)
    monkeypatch.setattr(ai_client, "disponibil", lambda: True)
    monkeypatch.setattr(ai_client, "genereaza_text", lambda *a, **k: _RASPUNS_AI)
    monkeypatch.setattr(uc_comun, "_platitor_tva_tert", lambda *a, **k: None)
    monkeypatch.setattr(uc_comun, "_api_schema", lambda *a, **k: SCH)


@pytest.fixture()
def pfa(monkeypatch):
    for conn, uid in _lume("pfa", monkeypatch):
        _fundal(conn, monkeypatch)
        yield conn


@pytest.fixture()
def srl(monkeypatch):
    for conn, uid in _lume("srl", monkeypatch):
        _fundal(conn, monkeypatch)
        with conn.cursor() as cur:   # factura unui SRL cere forma juridică și capitalul (Legea 31/1990 art.74 alin.(3))
            cur.execute("UPDATE firma_profil SET forma_juridica = 'SRL', capital_subscris = 200")
        yield conn


def _ruleaza(drum, conn, monkeypatch):
    """Rulează drumul cu o factură de 100 lei; -> (rezultatul drumului, note_interne din rezultat sau None)."""
    if drum == "api":
        from core import uc_api
        r = uc_api.apiv1_factura_emite(1, {"linii": [dict(_LINIE)], "tert_nume": "Client Fundal SRL", "tert_cui": "14399840",
                                           "data_emitere": _AZI.isoformat()}, {"firm": 1})
        return r, r.get("note_interne")
    if drum == "recurente":
        from core import facturi_recurente as fr
        with conn.cursor() as cur:
            cur.execute("INSERT INTO %s.facturi_recurente (id, tert_nume, tert_cui, linii, zi_emitere) VALUES (1, 'Client Fundal SRL', "
                        "'14399840', %%s, 1)" % SCH, (json.dumps([_LINIE]),))
        r = fr.emite_scadente(SCH, _AZI)
        note = [x["note_interne"] for x in r if "note_interne" in x]
        return r, (note[0] if note else None)
    from core import woocommerce
    comanda = {"number": 701, "date_created": "2026-10-09T10:00:00", "currency": "RON", "total": "100",
               "billing": {"first_name": "Ana", "last_name": "Pop"},
               "line_items": [{"name": "Mentenanta platforma web", "quantity": 1, "total": "100"}]}
    monkeypatch.setattr(woocommerce, "comenzi", lambda *a, **k: [comanda])   # magazinul (HTTP), simulat
    with conn.cursor() as cur:
        cur.execute("UPDATE %s.firma_profil SET wc_url='https://magazin.invalid', wc_ck='ck', wc_cs='cs'" % SCH)
    r = woocommerce.sincronizeaza(SCH)
    return r, r.get("note_interne")


def _emise(drum, r):
    """Câte facturi a emis drumul (din rezultatul lui)."""
    if drum == "api":
        return 1 if r.get("factura_id") else 0
    if drum == "recurente":
        return sum(1 for x in r if x.get("factura") is not None and "eroare" not in x)
    return len(r["importate"])


def _note_facturilor(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM inregistrari WHERE factura_id IS NOT NULL ORDER BY id")
        return [x[0] for x in cur.fetchall()]


# ── PFA: nota facturii se validează ca notă internă ──────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("drum", DRUMURI)
def test_la_pfa_nota_drumului_ajunge_validata(drum, pfa, monkeypatch):
    """Nota de contare a facturii emise pe drum (fără autor) ajunge `validata`, iar drumul spune ce s-a validat. MUTAȚIA (pe fiecare
    drum): apelul `note_interne_schema` scos -> nota rămâne ciornă -> ROȘU."""
    r, ni = _ruleaza(drum, pfa, monkeypatch)
    note = _note_facturilor(pfa)
    print("368 fundal", drum, "->", ni, _stari(pfa, note))
    assert _emise(drum, r) == 1, r
    assert len(note) == 1, note
    assert _stari(pfa, note) == {note[0]: "validata"}
    assert ni is not None and len(ni["interne"]) == 1 and ni["refuzate"] == [], ni


# ── partidă dublă: nota rămâne a contabilului ────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("drum", DRUMURI)
def test_la_partida_dubla_nota_drumului_ramane_ciorna(drum, srl, monkeypatch):
    """La SRL nimic nu se validează singur, iar rezultatul drumului nu poartă cheia `note_interne`. MUTAȚIA: validarea directă
    (`jurnal_api.valideaza_interne` pe `ciorne_din_cerere`, fără `partida_simpla`) în locul lui `note_interne_schema` -> ROȘU."""
    r, ni = _ruleaza(drum, srl, monkeypatch)
    note = _note_facturilor(srl)
    assert _emise(drum, r) == 1, r
    assert len(note) == 1 and _stari(srl, note) == {note[0]: "ciorna"}, _stari(srl, note)
    assert ni is None, ni


# ── refuzul validării: nota rămâne ciornă, drumul merge, refuzul se spune ───────────────────────────────────────────────────
@pytest.mark.parametrize("cu_nota_facturii", (True, False), ids=("si_nota_facturii", "numai_refuzul"))
@pytest.mark.parametrize("drum", DRUMURI)
def test_refuzul_lasa_nota_ciorna_si_nu_rupe_drumul(drum, cu_nota_facturii, pfa, monkeypatch):
    """Drumul scrie, pe lângă factură, o notă FĂRĂ document (R3): factura e emisă, nota fără document rămâne ciornă, iar refuzul
    (textul regulii, întreg) ajunge în rezultat. Două variante: cu nota facturii (se validează) și fără ea (contarea facturii refuzată —
    singurul lucru de spus e refuzul). MUTAȚII: `if ni["refuzate"]: raise …` după validare (refuzul rupe drumul) -> ROȘU;
    `if ni["interne"] or ni["refuzate"]:` -> `if ni["interne"]:` (refuzul nespus) -> ROȘU pe `numai_refuzul`."""
    from core import contare_facturi, facturi_api, jurnal_api
    emite = facturi_api.emite_factura

    def _cu_nota_fara_document(conn, *a, **k):
        r = emite(conn, *a, **k)
        jurnal_api.creeaza(conn, SCH, "Fără document", "2026-10-06", [{"debit": "612", "credit": "401", "suma": 50,
                                                                       "partener_nume": "PARTENER PROBA SRL"}])
        return r
    monkeypatch.setattr(facturi_api, "emite_factura", _cu_nota_fara_document)
    if not cu_nota_facturii:   # contarea facturii refuzată (refuz declarat, `RefuzContare`): factura se emite fără notă
        def _refuz(*a, **k):
            raise contare_facturi.RefuzContare("FARA_COTA", "cota liniei nu e cunoscută")
        monkeypatch.setattr(contare_facturi, "contabilizeaza", _refuz)
    r, ni = _ruleaza(drum, pfa, monkeypatch)
    with pfa.cursor() as cur:
        cur.execute("SELECT id FROM inregistrari WHERE descriere = 'Fără document'")
        (fara_doc,), = cur.fetchall()
    nota = _note_facturilor(pfa)
    print("368 fundal refuz", drum, cu_nota_facturii, "->", ni)
    assert _emise(drum, r) == 1, r
    assert _stari(pfa, nota + [fara_doc]) == {**{n: "validata" for n in nota}, fara_doc: "ciorna"}
    assert len(nota) == (1 if cu_nota_facturii else 0), nota
    # R3, regula de fond din bază (`core/migrare_reguli_fond.py`; Legea 82/1991 art.6 alin.(1): documentul justificativ)
    assert [x["motiv"] for x in ni["refuzate"]] == [
        "Nota din 06.10.2026 n-are documentul justificativ: o notă nu se validează fără documentul din care provine."], ni
    assert len(ni["interne"]) == len(nota), ni


# ── o eroare a validării interne nu rupe drumul și nu e tăcută ────────────────────────────────────────────────────────────
@pytest.mark.parametrize("drum", DRUMURI)
def test_eroarea_validarii_interne_nu_rupe_drumul(drum, pfa, monkeypatch):
    """`note_interne_schema` aruncă: factura e emisă, nota rămâne ciornă, eroarea ajunge în `observare.esec_secundar`. MUTAȚIA:
    `try/except` scos din jurul apelului -> excepția iese din drum -> ROȘU."""
    from core import observare, uc_coada
    vazute = []

    def _cade(*a, **k):
        raise RuntimeError("baza a căzut la validarea internă")
    monkeypatch.setattr(uc_coada, "note_interne_schema", _cade)
    monkeypatch.setattr(observare, "esec_secundar", lambda eticheta, e, **k: vazute.append((eticheta, str(e))))
    r, ni = _ruleaza(drum, pfa, monkeypatch)
    note = _note_facturilor(pfa)
    assert _emise(drum, r) == 1, r
    assert ni is None and _stari(pfa, note) == {note[0]: "ciorna"}
    assert [e for _et, e in vazute] == ["baza a căzut la validarea internă"], vazute


# ── începutul scrierii: o ciornă de fundal mai veche nu e a drumului ──────────────────────────────────────────────────────
def test_ciorna_de_fundal_mai_veche_nu_se_atinge(pfa, monkeypatch):
    """`de_la` e începutul scrierii drumului: o ciornă fără autor născută cu o oră înainte (alt job) nu se validează. MUTAȚIA:
    `de_la = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)` în `emite_scadente` -> nota veche se validează -> ROȘU."""
    from core import jurnal_api
    veche = jurnal_api.creeaza(pfa, SCH, "Veche", "2026-10-02", [{"debit": "612", "credit": "401", "suma": 10,
                                                                 "partener_nume": "PARTENER PROBA SRL"}], document_ref="F 1")["id"]
    with pfa.cursor() as cur:
        cur.execute("UPDATE inregistrari SET creat_la = now() - interval '1 hour' WHERE id = %s", (veche,))
    _r, ni = _ruleaza("recurente", pfa, monkeypatch)
    note = _note_facturilor(pfa)
    assert _stari(pfa, note + [veche]) == {note[0]: "validata", veche: "ciorna"}
    assert len(ni["interne"]) == 1, ni

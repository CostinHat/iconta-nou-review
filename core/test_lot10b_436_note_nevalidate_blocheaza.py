# -*- coding: utf-8 -*-
"""[lotul 10, deficiența 436 (grav), comanda Costin 10.2 pct.6, verbatim în DECIZII] „la F2, D100 pe T3/2026 avertizează că amortizarea
01–07/2026 (1.400 lei) e nevalidată, deci profitul și impozitul ies mai mari, dar «Pune în De depus» rămâne oferit. Decizie: când declarația
știe că are cifra greșită din note nevalidate, depunerea se blochează până la validare, cu motivul lângă buton, la toate declarațiile. În
plus, 08 și 09/2026 sunt încheiate, dar fără amortizare generată, iar D100 pe T3 nu semnalează.”

(a) Declarațiile care ȘTIU (`coada_api.DECLARATII_DIN_EVIDENTA`: calculate din evidența validată, cu generatorul care numește notele
    nevalidate — `d101.avertismente_evidenta`) au UN refuz (`coada_api.blocaj_note_nevalidate`), cerut pe patru drumuri: pasul 2 din
    Declarații (`uc_declaratii.blocaj_depunere`: butonul inactiv, motivul sub el), intrarea în coadă (`uc_coada.coada_adauga`), rândul din
    „De depus” (`lista_coada`, „blocaj_depunere”) și depunerea (`marcheaza_depusa`).
(b) Amortizarea lunilor încheiate negenerată se spune la D100, D101 și — generalizarea pe clasă — la bilanț (`bilant_api`).
Schemă efemeră din tenant_template, ROLLBACK la final. Proba pe ecran: `frontend_test/e2e/e2e_lot10b_declaratii.py::test_def_436_…`."""
import ast
import datetime as _dt
import inspect
import json
import os
import re
import textwrap

import pytest

from core import coada_api, d100, declaratii_api
from core import db as _db, tenant_provisioning as _tp

_SCHEMA = "test_lot10b_436"
RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AZI = _dt.date(2026, 10, 20)


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _schema(cur):
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
    cur.execute(_tp.parametrizeaza_template(open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), _SCHEMA))
    cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
    cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,regim_fiscal,platitor_tva,tip_decont,"
                "declarant_nume,declarant_prenume,declarant_functie) VALUES (1,'PROBA 436 SRL','14399840','Str 1','Buc','B','6202',"
                "'BCR','RO49RNCB0000000000000001','profit',true,'T','Pop','Ion','administrator')")
    _nota(cur, "2026-01-15", "validata", "5311", "704", 10000)
    # cazul F2, refăcut: mijloc fix 12.000 lei, PIF 15.01.2025, 60 de luni -> 200 lei/lună din 02/2025; soldul preluat al lui 2813 (2.200)
    # acoperă 02–12/2025; amortizarea 01–07/2026 generată și nevalidată (ciornă), 08–09/2026 negenerată
    cur.execute("INSERT INTO mijloace_fixe (cod,denumire,cont_imobilizare,cont_amortizare,valoare,dnf_luni,data_pif,metoda) "
                "VALUES ('MF1','Laptop','2131','2813',12000,60,'2025-01-15','liniara')")
    cur.execute("INSERT INTO solduri_initiale (cont,sold_creditor,data_referinta) VALUES ('2813',2200,'2025-12-31')")
    return [_nota(cur, "2026-%02d-28" % luna, "ciorna", "6811", "2813", 200, "amortizare") for luna in range(1, 8)]


def _nota(cur, data, stare, deb, cre, suma, sursa="t"):
    cur.execute("INSERT INTO inregistrari (data,status,sursa,descriere,document_ref) VALUES (%s,%s,%s,'N','AM') RETURNING id",
                (data, stare, sursa))
    nid = cur.fetchone()[0]
    cur.execute("INSERT INTO inregistrari_linii (inregistrare_id,cont_debit,cont_credit,suma) VALUES (%s,%s,%s,%s)", (nid, deb, cre, suma))
    return nid


@pytest.fixture
def firma(monkeypatch):
    if not _db_ok():
        pytest.skip("DB indisponibil")
    from core import common
    monkeypatch.setattr(common, "azi_ro", lambda acum=None: AZI)
    monkeypatch.setattr(d100._repo, "d100_depuse_an", lambda cur, schema, an: [])
    with _db.get_conn() as c:
        with c.cursor() as cur:
            ciorne = _schema(cur)
        try:
            yield c, ciorne
        finally:
            c.rollback()
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
            c.commit()


# ── (a) refuzul, pur ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
_NOTA = {"nota_id": 7, "data": "2026-01-28", "eticheta": "nota din 28.01.2026 — AM, 200,00 lei"}


def test_refuzul_numeste_notele_si_drumul():
    r = coada_api.blocaj_note_nevalidate("d100", [_NOTA])
    # comanda 10.2 pct.6: „depunerea se blochează până la validare, cu motivul lângă buton”
    assert r == {"ok": False, "cod": "NOTE_NEVALIDATE", "note": [_NOTA], "mesaj": (
        "Declarația nu se depune până la validarea notelor: cifra ei nu cuprinde 1 notă nevalidată din perioada ei — nota din 28.01.2026 "
        "— AM, 200,00 lei. Validează-le în Registrul jurnal, apoi generează din nou.")}, r


def test_CALIBRARE_fara_note_sau_pe_o_declaratie_care_nu_stie_nu_se_blocheaza():
    """Fără note -> nimic. La D300 (TVA: cunoașterea e poarta balanței, decizia R36) și la o declarație din formular (D207) -> nimic."""
    assert coada_api.blocaj_note_nevalidate("d100", []) is None
    assert coada_api.blocaj_note_nevalidate("d300", [_NOTA]) is None
    assert coada_api.blocaj_note_nevalidate("d207", [_NOTA]) is None


def test_lista_e_exact_a_generatoarelor_care_numesc_notele():
    """Gard: „declarația știe” = generatorul ei cheamă `avertismente_evidenta` (numește notele nevalidate ale ferestrei). Un generator nou
    care începe să le numească fără să intre în `DECLARATII_DIN_EVIDENTA` (deci fără blocaj) -> ROȘU; la fel unul scos de acolo."""
    modul = {t: ("bilant_api" if t in declaratii_api.SITUATII_FINANCIARE else t)
             for t in dict(declaratii_api.DECLARATII, **declaratii_api.SITUATII_FINANCIARE)}
    stiu = set()
    for tip, m in modul.items():
        cale = os.path.join(RAD, "core", m + ".py")
        txt = open(cale, encoding="utf-8").read() if os.path.exists(cale) else ""
        if re.search(r"\bavertismente_evidenta(_an)?\(", txt):
            stiu.add(tip)
    assert stiu == set(coada_api.DECLARATII_DIN_EVIDENTA), sorted(stiu ^ set(coada_api.DECLARATII_DIN_EVIDENTA))


def _apeluri(f):
    out = set()
    for n in ast.walk(ast.parse(textwrap.dedent(inspect.getsource(f)))):
        if isinstance(n, ast.Call):
            out.add(n.func.id if isinstance(n.func, ast.Name) else getattr(n.func, "attr", None))
    return out


def test_cele_patru_drumuri_cer_acelasi_refuz():
    """Pasul 2 (`uc_declaratii.blocaj_depunere` -> `blocaj_declaratie`), intrarea în coadă, lista „De depus” și depunerea cheamă aceeași
    funcție — o singură regulă, nu patru. MUTAȚIA: apelul scos din `coada_adauga` -> ROȘU."""
    from core import uc_coada, uc_declaratii
    # operator de mulțime pe numele apelate (AST): `>=` crapă pe un șir, în loc să treacă tăcut ca `in`
    assert {"blocaj_declaratie"} <= _apeluri(uc_declaratii.blocaj_depunere)
    assert {"blocaj_depunere"} <= _apeluri(uc_declaratii.declaratie_valideaza) & _apeluri(uc_declaratii.declaratie_genereaza)
    assert {"blocaj_note_nevalidate"} <= _apeluri(uc_coada.coada_adauga)
    assert {"blocaj_note_nevalidate"} <= _apeluri(coada_api.lista_coada)
    assert {"refuz_note_nevalidate"} <= _apeluri(coada_api.marcheaza_depusa)
    assert {"blocaj_note_nevalidate"} <= _apeluri(coada_api.blocaj_declaratie)


# ── (a) pe evidența reală ───────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_d100_T3_cu_amortizarea_in_ciorna_nu_se_depune(firma):
    """Cazul F2: D100 pe T3/2026 cu amortizarea 01–07 în ciornă -> refuzul numește cele 7 note. MUTAȚIA: `blocaj_note_nevalidate` întoarce
    None -> ROȘU."""
    from core import uc_declaratii
    c, ciorne = firma
    r = uc_declaratii.blocaj_depunere(c, _SCHEMA, "d100", {"an": 2026, "trim": 3})
    assert r["cod"] == "NOTE_NEVALIDATE" and [n["nota_id"] for n in r["note"]] == ciorne, r
    assert r["mesaj"].startswith("Declarația nu se depune până la validarea notelor: cifra ei nu cuprinde 7 note nevalidate din perioada "
                                 "ei — nota din 28.01.2026 — AM, 200,00 lei;"), r["mesaj"]


def test_CALIBRARE_dupa_validare_refuzul_dispare(firma):
    from core import uc_declaratii
    c, ciorne = firma
    with c.cursor() as cur:
        cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = ANY(%s)", (ciorne,))
    assert uc_declaratii.blocaj_depunere(c, _SCHEMA, "d100", {"an": 2026, "trim": 3}) is None


def test_depunerea_elementului_din_coada_e_refuzata_cat_timp_notele_sunt_nevalidate(firma, monkeypatch):
    """O declarație intrată în coadă înainte de regulă (sau cu o notă trecută înapoi în ciornă): `marcheaza_depusa` refuză cu
    NOTE_NEVALIDATE și nu scrie. Element sintetic (tenant negativ, ROLLBACK), cu firma lui pe schema efemeră.
    MUTAȚIA: `refuz_note_nevalidate` scos din `marcheaza_depusa` -> „depusa” -> ROȘU."""
    import functools
    c, ciorne = firma
    monkeypatch.setattr(coada_api, "schema_firmei", lambda cur, tid: _SCHEMA)
    monkeypatch.setattr(coada_api, "perioada_neincheiata", functools.partial(coada_api.perioada_neincheiata, azi=_dt.date(2100, 1, 1)))
    with c.cursor() as cur:
        cur.execute("INSERT INTO public.accounting_firms (nume, patru_ochi_activ) VALUES ('ZTEST 436', false) RETURNING id")
        fid = cur.fetchone()[0]
        cur.execute("INSERT INTO public.users (email, password_hash, nume, rol, accounting_firm_id, activ, poate_valida, poate_depune) "
                    "VALUES ('ztest_436@invalid','x','ZTest','angajat',%s,true,true,true) RETURNING id", (fid,))
        uid = cur.fetchone()[0]
        surse = {"de_la": "2026-01-01", "pana_la": "2026-10-01"}
        surse["amprenta"] = coada_api.amprenta_surse(cur, _SCHEMA, surse["de_la"], surse["pana_la"])   # nedepășită: aceleași documente
        # fixtura-sintetica-ok: tenant_id NEGATIV (spațiu imposibil în producție) + rollback; perioada sintetică 2099
        cur.execute("INSERT INTO public.declaratii_coada (cabinet_id, tenant_id, tip, perioada, stare, payload, creat_de, creat_de_id) "
                    "VALUES (%s,-436,'d100','2099-T3','la_senior',%s,%s,%s) RETURNING id",
                    (fid, json.dumps({"xml": "<x/>", "_an": 2099, "_trim": 3, "_surse": surse}),
                     str(uid), uid))
        cid = cur.fetchone()[0]
    coada_api.scrie_verdict(c, cid, {"stare": "valid", "erori": ""}, "test-validator", "<x/>")
    coada_api.aproba(c, cid, "ztest", aprobat_de_id=uid)
    r = coada_api.marcheaza_depusa(c, cid, depus_de="ztest", depus_de_id=uid)
    assert r["ok"] is False and r["cod"] == "NOTE_NEVALIDATE" and [n["nota_id"] for n in r["note"]] == ciorne, r
    with c.cursor() as cur:
        cur.execute("SELECT stare FROM public.declaratii_coada WHERE id=%s", (cid,))
        assert cur.fetchone()[0] == "aprobata"


# ── (b) lunile încheiate fără amortizare generată ───────────────────────────────────────────────────────────────────────────────────────
def _linia(linii, inceput):
    gasite = [x for x in linii if x.startswith(inceput)]
    assert len(gasite) == 1, (inceput, linii)
    return gasite[0]


def test_d100_T3_semnaleaza_si_lunile_fara_amortizare_generata(firma):
    """„08 și 09/2026 sunt încheiate, dar fără amortizare generată, iar D100 pe T3 nu semnalează.” Refăcut cu datele F2 (soldul preluat al
    lui 2813, ciornele 01–07): D100 pe T3 spune AMBELE — ciorna 01–07 și lunile 08–09 neînregistrate."""
    c, _ = firma
    xml, res = declaratii_api.genereaza(c, _SCHEMA, "d100", {"an": 2026, "trim": 3})
    av = [a for a in res.avertismente if a.startswith("Amortizarea")]
    assert av == [
        "Amortizarea pe 01–07/2026 (contul 2813, 1.400,00 lei) e generată, dar nevalidată: D100 pe T3/2026 se calculează fără ea, deci "
        "profitul și impozitul ies mai mari. Validează notele de amortizare în Registrul jurnal, apoi generează din nou.",
        "Amortizarea pe 08–09/2026 (contul 2813, 400,00 lei) e neînregistrată: D100 pe T3/2026 se calculează fără ea, deci profitul și "
        "impozitul ies mai mari. Generează-o din Închidere lună („Generează amortizarea restantă”) și valideaz-o, apoi generează din nou."], av


def test_bilantul_semnaleaza_amortizarea_lunilor_incheiate(firma):
    """Generalizarea pe clasă: bilanțul (din balanța notelor validate) spune și el amortizarea lipsă a anului, cu efectul lui (nu un
    impozit). MUTAȚIA: `av.extend(avertismente_evidenta_an(...))` scos din `bilant_api.genereaza` -> ROȘU (generatorul complet cere
    profilul bilanțului; aici se cheamă funcția, iar prezența apelului în ambele generatoare e păzită mai jos)."""
    from core import bilant_api
    c, _ = firma
    with c.cursor() as cur:
        cur.execute("DELETE FROM solduri_initiale")
    av = bilant_api.avertismente_evidenta_an(c, _SCHEMA, 2025)
    assert _linia(av, "Amortizarea") == (
        "Amortizarea pe 02–12/2025 (contul 2813, 2.200,00 lei) e neînregistrată: Bilanțul pe 2025 se calculează fără ea, deci rezultatul "
        "exercițiului și valoarea netă a imobilizărilor ies mai mari. Generează-o din Închidere lună („Generează amortizarea restantă”) și "
        "valideaz-o, apoi generează din nou."), av
    assert {"avertismente_evidenta_an"} <= _apeluri(bilant_api.genereaza) & _apeluri(bilant_api.genereaza_s1003)


def test_ecranul_pasului_2_tine_butonul_inactiv_cu_motivul_sub_el():
    """Pasul 2 din Declarații: cu `blocaj_depunere`, „Trimite în coadă” e `disabled` și descris de caseta motivului (`#dec-blocaj`), în
    zona de mesaj a barei fixe (DS v2.92: „Acțiunea principală și mesajul ei se văd mereu”). MUTAȚIA: `disabled` scos -> ROȘU."""
    from core.arbore_js import apeluri, arbore_js, elemente_html, functia, noduri
    arb, cod = arbore_js("declaratii.js")
    pas2 = functia(arb, "pas2")
    # cu `blocaj_depunere` (`_blocaj`), bara fixă are „Trimite în coadă” inactiv, descris de caseta motivului (`#dec-blocaj`, role=status),
    # scrisă în zona de mesaj a barei; notele din motiv sunt legături
    c = [x for x in noduri(pas2, "ConditionalExpression") if cod(x["test"]) == "_blocaj"]
    assert [elemente_html(x["consequent"]) for x in c] == [
        [("div", {"class": "dec-bara"}),
         ("button", {"class": "buton-primar", "id": "dec-trimite", "data-actiune": "POST /coada", "disabled": None,
                     "aria-describedby": "dec-blocaj"})],
        [("div", {"class": "caseta-atentie", "id": "dec-blocaj", "role": "status"}), ("div", {"class": "ca-mesaj"})]], [cod(x) for x in c]
    assert set(apeluri(pas2, cod, "legaturiNote")) >= {('corp.querySelector("#dec-blocaj .ca-mesaj")', "S.tenant_id", "_blocaj.note")}
    # „De depus” (validat.js): cu `blocaj_depunere`, motivul pe rând (scăpat), iar ramura lui nu oferă depunerea
    arb, cod = arbore_js("validat.js")
    motiv = [x for x in noduri(arb, "ConditionalExpression") if cod(x["test"]) == "c.blocaj_depunere"]
    assert [[cod(e) for e in x["consequent"]["expressions"]] for x in motiv] == [
        ['c.perioada_neincheiata ? "val-neincheiata" : "val-blocaj-note"', "esc(c.blocaj_depunere)"]], [cod(x) for x in motiv]
    daca = [x for x in noduri(arb, "IfStatement") if cod(x["test"]) == "c.blocaj_depunere"]
    assert [x["consequent"]["body"] for x in daca] == [[]], [cod(x) for x in daca]   # nicio acțiune de depunere pe ramura blocată

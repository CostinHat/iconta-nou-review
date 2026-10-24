# -*- coding: utf-8 -*-
"""Lotul 12, pachetul firme1 — Bancă: 479 (grav), 478, 480.

479 (Costin, comanda 12.1): „Bancă: Linie dublă importată; notă 5121=5121 propusă (grav).”
  Cauza 1 — limita declarată la 277 (DECIZII „Lotul 6, comanda 1”): aceeași mișcare venită o dată din MT940 (cu contul băncii) și o dată
  din extrasul în tabel (fără cont) nu era recunoscută: se adăuga a doua oară și se propunea la contat.
  Cauza 2 — învățarea din validare reținea „debitul primei linii”; pe încasare (5121 = 4111) asta e banca, deci dublura (fără factură
  deschisă, descrierea cu aceleași cuvinte) primea sugestia 5121 -> nota 5121 = 5121.
478: „Extras .xlsx valid refuzat.” — data dintr-o celulă Excel de tip dată ajungea ca `datetime`, iar parserul recunoștea numai textul
  „zz.ll.aaaa”: niciun rând nu era tranzacție -> „Nu s-au găsit tranzacții”.
480: „Încasare cu cod TVA străin și «factura F1A7» în descriere rămâne fără potrivire automată.” — potrivirea căuta numai CUI-ul românesc
  (RO… / CUI …), nici codul de TVA al altui stat, nici numărul facturii scris în descriere.

Temei: N/A pentru 478 / 480 (citirea extrasului); 479: OMFP 1802/2014, funcțiunea contului 512 (contrapartida încasării e contul stins,
nu banca). Probe pe schema efemeră din template, ștearsă la ieșire.
"""
import datetime
import io
import json
from decimal import Decimal

import pytest

from core import db as _db
from core import tenant_provisioning as _tprov
from core import reconciliere_api as _rec
from core import ai_incredere as _ai
from core import banca as _bk
from core import banca_parser as _bp
from core import reconciliere as _m

_SCH = "efemer_l12_firme1_banca"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


_DB = _db_ok()
db_necesar = pytest.mark.skipif(not _DB, reason="DB indisponibil")


@pytest.fixture()
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), _SCH))
            cur.execute("SET LOCAL search_path TO %s, public" % _SCH)
            # CUI 14399840 (DANTE INTERNATIONAL SA) — cifra de control verificată (CLAUDE.md §10)
            cur.execute("""INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,email,telefon,caen,
                           declarant_nume,declarant_prenume,declarant_functie,platitor_tva)
                           VALUES (1,'L12 SRL','14399840','s','B','B','e@x.ro','07','4690','P','I','A',true)""")
        c.commit()
    with _db.get_conn(_SCH) as c:
        yield c
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
        c.commit()


#: extrasul MT940 din comanda Costin la 277 (F1, 16.10.2026)
MT940_277 = b""":20:EXTRAS20261016
:25:RO49AAAA1B31007593840000
:28C:00010/001
:60F:C261015RON10000,00
:61:2610161016C242,00NTRFNONREF
:86:Incasare FISCALOS ICONTA SRL CUI 55229657 contravaloare factura F1A4 din 16.10.2026
:61:2610161016D12,50NCHGNONREF
:86:Comision administrare cont octombrie
:62F:C261016RON10229,50
"""
#: aceleași două mișcări, din extrasul aceleiași zile în tabel (CSV: fără contul băncii)
CSV_277 = ("Data;Detalii;Debit;Credit\n16.10.2026;Incasare FISCALOS ICONTA SRL CUI 55229657 contravaloare factura F1A4 din 16.10.2026;;242,00\n"
           "16.10.2026;Comision administrare cont octombrie;12,50;\n").encode("utf-8")


def _importa(conn, continut, nume):
    """Același drum ca ruta `POST /banca/reconciliere/import` (`uc_tenants.banca_rec_import`): citirea, regula contului, importul."""
    e = _bp.citeste_extras(continut, nume)
    for t in e["tranzactii"]:
        r = _bk.regula_cont({"sens": "debit" if t["suma"] < 0 else "credit", "suma": abs(t["suma"]), "descriere": t.get("detalii", "")})
        t["cui"], t["tip"], t["nota"], t["tip_detectat"] = r.get("cui"), r.get("tip"), r.get("nota"), r.get("tip_detectat")
    rez = _rec.importa_extras(conn, _SCH, e["tranzactii"], nume, continut, cont=e["cont"])
    conn.commit()
    return rez


# ── 479: funcțiile pure ──────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_479_aceeasi_miscare_din_alt_format_e_probabil_aceeasi():
    v = {"data": datetime.date(2026, 10, 16), "suma": Decimal("242.00"), "tip": "incasare", "cont": "RO49AAAA1B31007593840000"}
    assert _rec.probabil_aceeasi_miscare({"data": "2026-10-16", "suma": "242", "tip": "incasare", "cont": None}, v) is True
    # regula lui 277 rămâne: contul cunoscut pe amândouă (egal sau nu) sau pe niciuna -> numai cheia întreagă hotărăște
    assert _rec.probabil_aceeasi_miscare(dict(v, cont="RO66BACX0000001234567890"), v) is False
    assert _rec.probabil_aceeasi_miscare(dict(v), v) is False
    assert _rec.probabil_aceeasi_miscare(dict(v, cont=None), dict(v, cont=None)) is False
    assert _rec.probabil_aceeasi_miscare({"data": "2026-10-16", "suma": "242.01", "tip": "incasare", "cont": None}, v) is False
    assert _rec.probabil_aceeasi_miscare({"data": "2026-10-16", "suma": "242", "tip": "plata", "cont": None}, v) is False
    assert _rec.probabil_aceeasi_miscare({"data": "2026-10-17", "suma": "242", "tip": "incasare", "cont": None}, v) is False


def test_479_se_invata_contrapartida_bancii_nu_banca():
    """OMFP 1802/2014, funcțiunea contului 512: contrapartida încasării (5121 = 4111) e 4111; a plății (401 = 5121), 401."""
    assert _ai.cont_de_invatat("5121", "4111") == "4111"
    assert _ai.cont_de_invatat("5124", "766") == "766"
    assert _ai.cont_de_invatat("401", "5121") == "401"
    assert _ai.cont_de_invatat("627", "5121") == "627"
    assert _ai.cont_de_invatat("5311", "4111") == "4111"
    assert _ai.cont_de_invatat("5121", "5311") is None, "bancă = casă: nimic de învățat ca propunere pentru extras"
    assert _ai.cont_de_invatat("5121.01", "5121") is None


# ── 479: drumul real (F1, 16.10 -> 22.10) ────────────────────────────────────────────────────────────────────────────────────────
@db_necesar
def test_479_extrasul_in_tabel_dupa_mt940_nu_dubleaza_liniile_si_nu_propune_5121_5121(conn):
    """Pașii lui Costin pe F1: MT940-ul din 16.10 (cu contul băncii) importat, încasarea contată și validată; apoi extrasul aceleiași zile
    în tabel (fără cont). Înainte: două linii noi, la contat; încasarea dublată propunea 5121 = 5121 (sugestia învățată = banca).
    Acum: cele două linii sunt puse deoparte („Ignorată”, cu motivul și «readu»), niciuna propusă la contat; învățarea a reținut 4111."""
    from core import jurnal_api
    r1 = _importa(conn, MT940_277, "extras_16_10.sta")
    assert (r1["rezumat"]["noi"], r1["rezumat"].get("probabil_deja")) == (2, None), r1["rezumat"]
    assert [x["tip"] for x in r1["linii"]] == ["incasare", "plata"], "sensul liniei în răspunsul importului (nu „reconciliere extras”)"
    inc = next(x for x in r1["linii"] if x["suma"] == "242.00")
    rc = _rec.conteaza(conn, _SCH, inc["id"])
    assert rc["nota"] == "5121=4111", rc
    assert jurnal_api.valideaza(conn, _SCH, rc["inregistrari"][0]) == {"ok": True}
    conn.commit()
    with conn.cursor() as cur:
        cur.execute("SELECT cont_final FROM ai_corectii ORDER BY id")
        assert [r[0] for r in cur.fetchall()] == ["4111"], "învățat din 5121 = 4111: contrapartida (înainte: 5121)"
    r2 = _importa(conn, CSV_277, "extras_16_10.csv")
    assert (r2["rezumat"]["noi"], r2["rezumat"]["deja"], r2["rezumat"]["probabil_deja"], r2["linii"]) == (0, 0, 2, []), r2["rezumat"]
    with conn.cursor() as cur:
        cur.execute("SELECT suma, status, nota_propusa, alocari FROM extras_linii WHERE fisier_sursa = 'extras_16_10.csv' ORDER BY id")
        rows = cur.fetchall()
    assert [(str(s), st, np) for s, st, np, _a in rows] == [("242.00", "ignorat", None), ("12.50", "ignorat", None)], rows
    assert rows[0][3]["motiv"].startswith("pare aceeași mișcare ca linia din 16.10.2026 importată deja din «extras_16_10.sta»"), rows[0][3]
    assert rows[0][3]["motiv"].endswith("Dacă e altă mișcare, apasă «readu».")
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM extras_linii WHERE status = 'nou'")
        assert cur.fetchone()[0] == 1, "rămâne la contat numai comisionul din MT940 (încă necontat)"


@db_necesar
def test_479_sugestia_veche_pe_banca_nu_mai_da_5121_5121(conn):
    """Datele existente: rândul învățat înainte de reparație (5121, de pe o încasare) nu mai e propunere; nota propusă rămâne a regulii
    (5121 = 4111, client presupus din sens). Nota 5121 = 5121 nu se mai poate conta (refuz numit)."""
    with conn.cursor() as cur:
        for _ in range(3):
            cur.execute("INSERT INTO ai_corectii (context, cont_propus, cont_final, corectat) VALUES (%s, '5121', '5121', false)",
                        (_ai.normalizeaza("Incasare ALFA SRL plata 1"),))
    conn.commit()
    assert _ai.sugestie(conn, _SCH, "Incasare ALFA SRL plata 2") is None
    r = _rec.importa_extras(conn, _SCH, [{"data": "2026-03-10", "detalii": "Incasare ALFA SRL plata 2", "suma": 100.0,
                                          "nota": {"debit": "5121", "credit": "4111"}, "tip_detectat": False}], "a.csv")
    conn.commit()
    with conn.cursor() as cur:
        cur.execute("SELECT nota_propusa FROM extras_linii WHERE id = %s", (r["linii"][0]["id"],))
        assert cur.fetchone()[0] == {"debit": "5121", "credit": "4111"}
        cur.execute("UPDATE extras_linii SET nota_propusa = %s WHERE id = %s",
                    (json.dumps({"debit": "5121", "credit": "5121"}), r["linii"][0]["id"]))
    rc = _rec.conteaza(conn, _SCH, r["linii"][0]["id"])
    assert rc["eroare"].startswith("Nota propusă are același cont pe debit și pe credit (5121 = 5121)"), rc


@db_necesar
def test_479_migrarea_curata_liniile_vechi(conn):
    """Liniile importate înainte de reparație: nota 5121 = 5121 propusă se scoate (cu „sugestie învățată” din motiv); dublura necontată
    din alt format se pune deoparte; cea contată se numește; a doua rulare nu mai găsește nimic."""
    from core import migrare_extras_dubluri_trezorerie as mig
    cont = "RO49AAAA1B31007593840000"
    with conn.cursor() as cur:
        def ins(data, suma, tip, cont_e, status, np=None, motiv="fără CUI în descriere"):
            cur.execute("INSERT INTO extras_linii (data, descriere, suma, tip, status, alocari, nota_propusa, fisier_sursa, cont_extras) "
                        "VALUES (%s, 'x', %s, %s, %s, %s, %s, 'f', %s) RETURNING id",
                        (data, suma, tip, status, json.dumps({"status_match": "rosu", "alocari": [], "motiv": motiv, "incredere": "probabil"}),
                         json.dumps(np) if np else None, cont_e))
            return cur.fetchone()[0]
        a = ins("2026-10-16", 242, "incasare", cont, "contat")
        b = ins("2026-10-16", 242, "incasare", None, "nou", {"debit": "5121", "credit": "5121"},
                "niciun document deschis; sugestie învățată: 5121 (probabil, 1 validare)")
        c = ins("2026-10-16", 12.5, "plata", cont, "contat")
        d = ins("2026-10-16", 12.5, "plata", None, "contat")
        e = ins("2026-10-17", 50, "plata", None, "nou", {"debit": "401", "credit": "5121"})
        # [dovada pe F1] dublura IGNORATĂ de contabil înainte de reparație, cu nota 5121 = 5121 încă propusă: „readu” o aducea înapoi
        g = ins("2026-10-18", 99, "incasare", cont, "contat")
        f = ins("2026-10-18", 99, "incasare", None, "ignorat", {"debit": "5121", "credit": "5121"},
                "niciun document deschis; sugestie învățată: 5121 (probabil, 1 validare)")
    conn.commit()
    assert mig.verifica(conn, _SCH) is False
    rez = mig.aplica(conn, _SCH)
    conn.commit()
    assert rez == {"note_scoase": 2, "dubluri": 2, "contate": [(d, c)]}, rez
    with conn.cursor() as cur:
        cur.execute("SELECT id, status, nota_propusa, alocari->>'motiv', alocari->>'dublura_de' FROM extras_linii ORDER BY id")
        st = {r[0]: r[1:] for r in cur.fetchall()}
    assert st[b][0:2] == ("ignorat", None) and st[b][3] == str(a) and st[b][2].startswith("pare aceeași mișcare"), st[b]
    assert st[e] == ("nou", {"debit": "401", "credit": "5121"}, "fără CUI în descriere", None), st[e]
    assert st[f][0:2] == ("ignorat", None) and st[f][3] == str(g) and st[f][2].startswith("pare aceeași mișcare"), st[f]
    assert mig.verifica(conn, _SCH) is True
    assert mig.aplica(conn, _SCH) == {"note_scoase": 0, "dubluri": 0, "contate": [(d, c)]}
    # „readu” pe o linie ignorată cu nota pe același cont (rămasă de dinainte, fără migrare): linia revine fără notă propusă
    from core import repo_banca
    with conn.cursor() as cur:
        cur.execute("UPDATE extras_linii SET nota_propusa = %s WHERE id = %s", (json.dumps({"debit": "5121", "credit": "5121"}), f))
        assert repo_banca.readuce_linia_de_extras(cur, _SCH, f)
        cur.execute("SELECT status, nota_propusa FROM extras_linii WHERE id = %s", (f,))
        assert cur.fetchone() == ("nou", None)


# ── 478: extrasul .xlsx cu datele ca dată Excel ─────────────────────────────────────────────────────────────────────────────────────
def _xlsx(randuri):
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    for r in randuri:
        ws.append(r)
    b = io.BytesIO()
    wb.save(b)
    return b.getvalue()


def test_478_xlsx_cu_data_ca_data_excel_se_citeste():
    """Un extras .xlsx valid (antet Data / Detalii / Debit / Credit, data scrisă de Excel ca dată, sumele ca numere). Înainte:
    „Nu s-au găsit tranzacții în extras” — data venea `datetime`, iar parserul aștepta textul „zz.ll.aaaa”."""
    x = _xlsx([["Extras de cont", None, None, None], ["Data", "Detalii", "Debit", "Credit"],
               [datetime.datetime(2026, 10, 16), "Incasare FISCALOS ICONTA SRL factura F1A4", None, 242],
               [datetime.date(2026, 10, 17), "Comision administrare cont", 12.5, None]])
    tz = _bp.parse_extras(x, "extras.xlsx")
    assert tz == [{"data": "16.10.2026", "detalii": "Incasare FISCALOS ICONTA SRL factura F1A4", "suma": 242.0},
                  {"data": "17.10.2026", "detalii": "Comision administrare cont", "suma": -12.5}], tz
    assert _rec._data_iso(tz[0]["data"]) == "2026-10-16"


def test_478_xls_cu_data_ca_numar_de_serie_excel():
    """Același lucru în .xls (xlrd dă data ca număr de serie Excel, cu celula de tip dată)."""
    import xlrd  # noqa: F401 — formatul vechi; scrierea .xls nu e în dependențe, deci se probează conversia
    assert _bp._celula_text(46311.0, data_excel=True, datemode=0) == "16.10.2026"
    assert _bp._celula_text(datetime.datetime(2026, 10, 16, 0, 0)) == "16.10.2026"
    assert _bp._celula_text("16.10.2026") == "16.10.2026"
    assert _bp._celula_text(242.0) == 242.0


# ── 480: codul de TVA străin și numărul facturii din descriere ─────────────────────────────────────────────────────────────────────
#: coduri de TVA din alt stat, cu cifra de control verificată (DE: ISO 7064 MOD 11,10 — 136695976 -> 6; AT: U + 8 cifre — 1358562 -> 7)
_DE, _AT = "DE136695976", "ATU13585627"
_FD = [{"id": 7, "tert_cui": _DE, "directie": "emisa", "data_emitere": "2026-10-20", "sold": Decimal("500.00"), "serie": "F1A", "numar": "7"},
       {"id": 17, "tert_cui": "14399840", "directie": "emisa", "data_emitere": "2026-10-21", "sold": Decimal("500.00"),
        "serie": "F1A", "numar": "F1A17"},
       {"id": 8, "tert_cui": _DE, "directie": "primita", "data_emitere": "2026-10-20", "sold": Decimal("500.00"), "serie": "F1A",
        "numar": "7"}]


def test_480_incasarea_cu_numarul_facturii_in_descriere_se_potriveste():
    """Pașii lui Costin: încasare de la un client din alt stat, descrierea „… factura F1A7”, cu un cod de TVA străin (altul decât cel din
    fișă). Înainte: „niciun document deschis” / „fără CUI în descriere” -> roșu. Acum: factura F1A 7 deschisă, emisă, cu soldul egal ->
    potrivire exactă; cu soldul mai mare -> parțial pe ea, de confirmat."""
    r = _m.potriveste_linie({"suma": 500, "tip": "incasare", "cui": _AT, "descriere": "Incasare %s factura F1A7" % _AT}, _FD)
    assert (r["status"], r["alocari"]) == ("verde", [{"factura_id": 7, "suma": Decimal("500")}]), r
    assert r["motiv"] == "potrivire după numărul facturii din descriere (F1A 7)", r["motiv"]
    r = _m.potriveste_linie({"suma": 200, "tip": "incasare", "cui": None, "descriere": "plata fact. F1A nr. 7 / 2026"}, _FD)
    assert (r["status"], r["alocari"]) == ("galben", [{"factura_id": 7, "suma": Decimal("200")}]), r
    assert r["motiv"].endswith("suma nu e soldul facturii: alocare parțială, de confirmat"), r["motiv"]
    assert _m.potriveste_linie({"suma": 500, "tip": "incasare", "cui": None, "descriere": "factura F1A77"}, _FD)["status"] == "rosu"
    r = _m.potriveste_linie({"suma": 500, "tip": "incasare", "cui": None, "descriere": "F1A-0017"}, _FD)
    assert r["alocari"] == [{"factura_id": 17, "suma": Decimal("500")}], "numărul emis cu seria în față (F1A17) e F1A 17"
    r = _m.potriveste_linie({"suma": 500, "tip": "plata", "cui": None, "descriere": "plata F1A7"}, _FD)
    assert r["alocari"] == [{"factura_id": 8, "suma": Decimal("500")}], "plata caută numai facturile primite"


def test_480_codul_de_tva_strain_din_descriere_duce_la_facturile_partenerului():
    r = _m.potriveste_linie({"suma": 500, "tip": "incasare", "cui": None, "descriere": "SEPA credit DE 136695976 GmbH"}, _FD)
    assert (r["status"], r["alocari"]) == ("verde", [{"factura_id": 7, "suma": Decimal("500")}]), r
    assert _m.cod_partener_in_descriere(_FD, "C.I.F.14399840 plata", "incasare") == "14399840"
    assert _m.cod_partener_in_descriere(_FD, "plata RO 14399840", "incasare") == "14399840"
    assert _m.cod_partener_in_descriere(_FD, "plata X14399840", "incasare") is None
    assert _m.cod_partener_in_descriere(_FD, "ref 9143998401", "incasare") is None, "o bucată dintr-un număr mai lung nu e codul"
    assert _m.cod_partener_in_descriere(_FD, "nimic", "incasare") is None


@db_necesar
def test_480_importul_potriveste_incasarea_dupa_numarul_facturii(conn):
    """Drumul real: factura emisă F1A 7 către un client din alt stat (cod de TVA DE…), deschisă; extrasul (MT940) aduce încasarea cu
    „factura F1A7” și alt cod în descriere. Linia iese „Potrivire exactă”, la contat pe factura ei."""
    with conn.cursor() as cur:
        cur.execute("INSERT INTO facturi (numar, serie, data_emitere, tert_nume, tert_cui, directie, total, total_lei, status) "
                    "VALUES ('7', 'F1A', '2026-10-20', 'ALFA GMBH', %s, 'emisa', 500, 500, 'emisa') RETURNING id", (_DE,))
        fid = cur.fetchone()[0]
    conn.commit()
    mt = MT940_277.replace(b"C242,00NTRFNONREF", b"C500,00NTRFNONREF").replace(
        b"Incasare FISCALOS ICONTA SRL CUI 55229657 contravaloare factura F1A4 din 16.10.2026", ("Incasare ALFA GMBH %s factura F1A7" % _AT).encode())
    r = _importa(conn, mt, "extras_f1a7.sta")
    inc = next(x for x in r["linii"] if x["suma"] == "500.00")
    assert (inc["status"], inc["status_match"], [a["factura_id"] for a in inc["alocari"]]) == ("potrivit", "verde", [fid]), inc


# ── 251 (clasa, pe extrasul bancar): CSV în Windows-1250 ─────────────────────────────────────────────────────────────────────────
def test_251_extrasul_csv_windows_1250_isi_pastreaza_diacriticele():
    """Clasa 251 („CSV Windows-1250 strică diacriticele”), la extrasul bancar: citirea trece prin mecanismul unic al importurilor
    (`import_tabel.decodeaza`). Înainte: UTF-8 cu `errors="replace"` -> „�ncasare �tef�nescu”."""
    # Windows-1250 are literele cu sedilă (Ş ş Ţ ţ — virgula de dedesubt, Ș ș Ț ț, nu există în el)
    csv = "Data;Detalii;Suma\n16.10.2026;Încasare Ştefănescu şi fiii — ţesături ăâî;100,00\n".encode("cp1250")
    assert _bp.parse_extras(csv, "extras.csv") == [{"data": "16.10.2026", "detalii": "Încasare Ştefănescu şi fiii — ţesături ăâî", "suma": 100.0}]
    assert _bp.parse_extras("Data;Detalii;Suma\n16.10.2026;Plată ăâîșț;-5\n".encode("utf-8"), "e.csv")[0]["detalii"] == "Plată ăâîșț"


# ── C121: extrasul altei firme ───────────────────────────────────────────────────────────────────────────────────────────────────
def test_c121_ibanul_din_antetul_tabelului():
    rand = [["Extras de cont", "IBAN: RO49 AAAA 1B31 0075 9384 0000"], ["Data", "Detalii", "Debit", "Credit"],
            ["16.10.2026", "Plata catre RO66BACX0000001234567890", "10", ""]]
    assert _bp.iban_din_antet(rand) == "RO49AAAA1B31007593840000"
    assert _bp.iban_din_antet(rand[1:]) is None, "IBAN-ul din rândurile tranzacțiilor e al partenerului, nu al contului"
    assert _bp.iban_din_antet([["Cont RO49 AAAA 1B31 0075 9384 0000 SOLD 100"], ["Data", "Suma"]]) == "RO49AAAA1B31007593840000"
    csv = "Titular: L12 SRL;Cont RO49AAAA1B31007593840000\nData;Detalii;Suma\n16.10.2026;Incasare;5\n".encode("utf-8")
    assert _bp.citeste_extras(csv, "e.csv")["cont"] == "RO49AAAA1B31007593840000"


@db_necesar
def test_c121_extrasul_altui_cont_cere_confirmarea_si_nu_scrie_nimic(conn):
    """Firma are în Date firmă IBAN-ul RO66BACX0000001234567890; extrasul MT940 e al contului RO49AAAA1B31007593840000. Înainte: liniile
    intrau fără întrebare. Acum: răspunsul cere confirmarea (mesajul numește ambele conturi), nimic scris; confirmat -> 2 linii. Același
    cont (sau contul firmei necunoscut) -> fără întrebare."""
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET iban = 'RO66 BACX 0000 0012 3456 7890' WHERE id = 1")
    conn.commit()
    e = _bp.citeste_extras(MT940_277, "x.sta")
    r = _rec.importa_extras(conn, _SCH, e["tranzactii"], "x.sta", MT940_277, cont=e["cont"])
    assert r["cere_confirmare"]["cod"] == _rec.COD_CONT_ALTA_FIRMA and r["linii"] == [], r
    cc = r["cere_confirmare"]
    assert (cc["cont_extras"], cc["cont_firma"]) == ("RO49AAAA1B31007593840000", "RO66BACX0000001234567890"), cc
    # prima propoziție a mesajului numește ambele conturi, în forma lor fără spații
    assert cc["mesaj"].split(". ")[0] == ("Extrasul pare al altui cont: în el scrie contul RO49AAAA1B31007593840000, iar contul firmei "
                                         "(Date firmă) e RO66BACX0000001234567890"), cc["mesaj"]
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM extras_linii")
        assert cur.fetchone()[0] == 0
    r = _rec.importa_extras(conn, _SCH, e["tranzactii"], "x.sta", MT940_277, cont=e["cont"], cont_confirmat=True)
    assert r["rezumat"]["noi"] == 2 and "cere_confirmare" not in r, r
    assert _rec.cont_alta_firma(conn, _SCH, "RO66BACX0000001234567890") is None
    assert _rec.cont_alta_firma(conn, _SCH, None) is None
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET iban = NULL WHERE id = 1")
    assert _rec.cont_alta_firma(conn, _SCH, "RO49AAAA1B31007593840000") is None, "contul firmei necunoscut: nimic de comparat"

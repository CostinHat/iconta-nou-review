# -*- coding: utf-8 -*-
"""[lotul 12, pachetul `bilant`] C143 (găsită de pachetul `decl` la C119) și 151 / 187 — cifrele bilanțului.

C143 — F20 / F30 (contul de profit și pierdere) citeau numai CREDITUL conturilor de venituri (numai debitul celor de cheltuieli). Nota
Raportului Z trece brutul pe venit și scoate TVA-ul cu o a doua linie (`5311 = 707` 5.826,00, `707 = 4427` 126,00 — forma scrisă de
aplicație, `raport_z.mesaj_plata_diferita`: „5311 + 5125 = 707 dă totalul încasat, iar TVA-ul se scoate din totalul pe cote”), deci cifra de
afaceri din bilanț ieșea 5.826 cu TVA-ul în ea, iar profitul din F20 nu mai era cel închis în 121 (închiderea pe SOLD, `motor.inchidere_
din_solduri`: 5.700). Reparația e în citirea rulajelor (`bilant._valoare_termen(rulaj=True)`, `f20_complet_din_rulaje`): rulajul NET al
contului pe latura rândului — venituri credit − debit, cheltuieli debit − credit, fără închiderea în 121 (C15, `bilant_api.rulaje_67`),
aceeași regulă ca D100 / D101 / centrele de cost (C119). Acoperă S1005 F20 + F30 cap.XIX, S1003 F20 și categoria de mărime (`categorie_
marime.indicatori` citește cifra de afaceri din `f20_din_rulaje`). Notele Z deja validate nu se rescriu: bilanțul se calculează din ele la
generare.

TEMEI: OMFP 1802/2014 pct.8 pct.5 — „cifră de afaceri netă înseamnă sumele obținute din vânzarea de produse și prestarea de servicii după
deducerea reducerilor comerciale și a taxei pe valoarea adăugată și a altor impozite direct legate de cifra de afaceri”. Judecătorul
formei: DUK regula F10_0432 = F20_0082 (S1005Validator v13, `F10.class`: „F10_0432 (@0@) = F20_0082 (@1@)” — profitul din bilanț, soldul
lui 121, e profitul din contul de profit și pierdere).

151 / 187 — TVA-ul din prețul de raft (`stocuri.CONT_TVA_STOC`, 4428.02) intră numai la stocuri (F10 rd.05, „− din ct. 4428”), nu și la
datorii (rd.13); TVA-ul neexigibil la încasare (4428 sintetic) rămâne la datorii. Proba pe ecran (187) e în
`frontend_test/e2e/e2e_lot12_bilant.py::test_def_187_proba_pe_ecran_pentru_151`.

Schemă efemeră din `tenant_template.sql`, ROLLBACK. CUI-ul firmei 14399840 (DANTE INTERNATIONAL SA) — cifra de control verificată
(`test_cui_fixturii_are_cifra_de_control`)."""
import datetime
import re
from decimal import Decimal

import pytest
from psycopg2.extras import RealDictCursor

from core import bilant as b, bilant_api as ba, db as _db, tenant_provisioning as _tp

_SCHEMA = "ztest_lot12_bilant_c143"
_CAB = "INSERT INTO public.accounting_firms (nume, calit_intocmit, nume_intocmit) VALUES ('Cabinet sintetic', 12, 'IONESCU MARIA') RETURNING id"
_31_12 = datetime.date(2025, 12, 31)


def _cui_valid(cui):
    ch = [7, 5, 3, 2, 1, 7, 5, 3, 2]
    c = str(cui).strip()
    corp, ctrl = c[:-1].rjust(9, "0"), int(c[-1])
    r = (sum(int(corp[i]) * ch[i] for i in range(9)) * 10) % 11
    return (0 if r == 10 else r) == ctrl


def test_cui_fixturii_are_cifra_de_control():
    assert _cui_valid("14399840")


@pytest.fixture
def cur():
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as c:
                c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                c.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                c.execute(_CAB)   # cabinetul sintetic care ține firma, cu întocmitorul bilanțului (antetul îl cere)
                c.execute("INSERT INTO public.tenants (schema_name, nume, accounting_firm_id, creat_la) VALUES (%s, 'PROBA SRL', %s, "
                          "'2020-01-01')", (_SCHEMA, c.fetchone()["id"]))
                c.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
                c.execute("INSERT INTO firma_profil (id, nume, cui) VALUES (1, 'PROBA SRL', '14399840') ON CONFLICT (id) DO NOTHING")
                # primul exercițiu (înființată în 2025): coloana „An precedent” e legal goală
                c.execute("UPDATE firma_profil SET data_infiintare = '2025-01-10', reg_com = 'J40/1/2025', caen = '4711', adresa = 'Str 1', "
                          "oras = 'Buc', judet = 'B', declarant_nume = 'Popescu', declarant_prenume = 'Ion', "
                          "declarant_functie = 'ADMINISTRATOR', mare_contribuabil = false, forma_proprietate = '35', interes_public = false "
                          "WHERE id = 1")
                yield c
        finally:
            conn.rollback()


def _nota(c, zi, linii, sursa="t", descriere="Probă"):
    """Nota ciornă -> rândurile -> validată (ordinea pe care o cere `regula_linii_nota`)."""
    c.execute("INSERT INTO inregistrari (data, status, sursa, descriere, document_ref) VALUES (%s, 'ciorna', %s, %s, %s) RETURNING id",
              (zi, sursa, descriere, descriere))   # documentul justificativ: fără el nota nu se validează (`regula_nota`)
    nid = c.fetchone()["id"]
    for debit, credit, suma in linii:
        c.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, %s, %s, %s)",
                  (nid, debit, credit, Decimal(str(suma))))
    c.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (nid,))


def _anul_2025_cu_raport_z(c):
    """Raportul Z din 30.09.2025 (forma notei scrise de aplicație): 5311 = 707 5.826,00 (brutul încasat) și 707 = 4427 126,00 (TVA-ul
    colectat); mărfurile 3.000 (607 = 401); regularizarea TVA (4427 = 4423 126,00); închiderea pe sold la 31.12 (707 = 121 5.700, 121 = 607
    3.000 — `motor.inchidere_din_solduri`)."""
    _nota(c, datetime.date(2025, 9, 30), [("5311", "707", 5826), ("707", "4427", 126)], sursa="raport_z", descriere="Raport Z 1")
    _nota(c, datetime.date(2025, 9, 30), [("607", "401", 3000)])
    _nota(c, _31_12, [("4427", "4423", 126)], descriere="Regularizarea TVA")
    _nota(c, _31_12, [("707", "121", 5700), ("121", "607", 3000)], descriere="Închiderea")


def test_def_c143_s1005_cifra_de_afaceri_fara_tva_ul_din_raportul_z_si_valid_pe_duk(cur):
    """C143, S1005. Rulajul lui 707 pe 2025: debit 126 (TVA-ul scos din Z), credit 5.826. F20 rd.01 cifra de afaceri = 5.826 − 126 = 5.700
    (până la C143: 5.826), rd.06 = 3.000, rd.08 profit = 2.700 = F10 rd.43 (121); F30 cap.XIX rd.169 (707) = 5.700, rd.167 = 5.700, rd.235
    = 2.700 — și VALID pe DUK S1005. MUTAȚIE: ramura `rulaj` scoasă din `_valoare_termen` -> rd.01 = 5.826, rd.08 = 2.826 ≠ rd.43 2.700
    -> DUK „F10_0432 = F20_0082” -> pică."""
    from core import duk
    _anul_2025_cu_raport_z(cur)
    rl = ba._rulaje_67(cur, _SCHEMA, 2025)
    assert rl["707"] == (Decimal("126"), Decimal("5826")), rl   # închiderea în 121 nu e rulaj (C15)
    xml, _av = ba.genereaza(cur.connection, _SCHEMA, 2025)
    f10 = {int(r): int(v) for r, v in re.findall(r'\bF10_(\d{3})2="(-?\d+)"', xml)}
    f20 = {int(r): int(v) for r, v in re.findall(r'\bF20_(\d{3})2="(-?\d+)"', xml)}
    f30 = {int(r): int(v) for r, v in re.findall(r'\bF30_(\d{3})2="(-?\d+)"', xml)}
    # OMFP 1802/2014 pct.8 pct.5: cifra de afaceri netă — „după deducerea [...] taxei pe valoarea adăugată”
    assert (f20.get(1), f20.get(6), f20.get(8), f20.get(9, 0)) == (5700, 3000, 2700, 0), f20
    assert (f30.get(167), f30.get(169), f30.get(186), f30.get(235)) == (5700, 5700, 3000, 2700), f30
    # DUK regula F10_0432 = F20_0082: profitul din bilanț (121) = profitul din contul de profit și pierdere
    assert (f10.get(43), f10.get(8), f10.get(13)) == (2700, 5826, 3126), f10
    v = duk.valideaza(xml, "s1005", an=2025, luna=12)
    assert v["stare"] == "valid", v


def test_def_c143_s1003_cifra_de_afaceri_fara_tva_ul_din_raportul_z_si_valid_pe_duk(cur):
    """C143, S1003 (entitățile mici): F20 rd.03 (707) = 5.700, rd.01 = 5.700, rd.20 (607) = 3.000, rd.69 profitul net = 2.700 = F10 rd.43
    — VALID pe DUK S1003. MUTAȚIE: `f20_complet_din_rulaje` înapoi pe creditul / debitul simplu -> rd.03 = 5.826 -> pică."""
    from core import duk
    _anul_2025_cu_raport_z(cur)
    xml, _av = ba.genereaza_s1003(cur.connection, _SCHEMA, 2025)
    f10 = {int(r): int(v) for r, v in re.findall(r'\bF10_(\d{3})2="(-?\d+)"', xml)}
    f20 = {int(r): int(v) for r, v in re.findall(r'\bF20_(\d{3})2="(-?\d+)"', xml)}
    # OMFP 1802/2014 pct.8 pct.5: cifra de afaceri netă fără TVA
    assert (f20.get(1), f20.get(3), f20.get(20), f20.get(69), f20.get(70, 0)) == (5700, 5700, 3000, 2700, 0), f20
    assert f10.get(43) == 2700, f10
    v = duk.valideaza(xml, "s1003", an=2025, luna=12)
    assert v["stare"] == "valid", v


def test_c143_rulajul_net_pe_fiecare_latura_a_formularului():
    """C143, clasa: fiecare citire de rulaj a bilanțului e NETĂ pe latura rândului — venit cu debit (707 = 4427), reducerile acordate 709
    cu credit (stornate), cheltuială cu credit (607 stornat), reducerile primite 609 cu debit —, pe S1005 F20, F30 și S1003 F20.
    707: D 126 / C 5.826 -> 5.700; 709: D 80 / C 30 -> 50 scăzut; 607: D 3.000 / C 200 -> 2.800; 609: D 5 / C 25 -> 20 scăzut.
    MUTAȚIE: oricare din cele două ramuri net scoasă -> pică."""
    D = Decimal
    rl = {"707": (D("126"), D("5826")), "709": (D("80"), D("30")), "607": (D("3000"), D("200")), "609": (D("5"), D("25"))}
    f20 = b.f20_din_rulaje(rl)
    assert (f20[1], f20[3], f20[6], f20[8]) == (5650, -20, 2800, 2870), f20     # rd.01 = 5.700 − 50; rd.03 = − 609 (20); rd.08 = 5.650 + 20 − 2.800
    f30 = b.f30_din_rulaje(rl)
    assert (f30[169], f30[170], f30[167], f30[186], f30[187], f30[235]) == (5700, 50, 5650, 2800, 20, 2870), f30
    s3 = b.f20_complet_din_rulaje(rl)
    assert (s3[3], s3[4], s3[1], s3[20], s3[21], s3[69]) == (5700, 50, 5650, 2800, 20, 2870), s3


def test_c143_categoria_de_marime_citeste_cifra_de_afaceri_neta(monkeypatch):
    """C143, clasa: criteriul „cifra de afaceri netă” al categoriei de mărime (OMFP 1802/2014 pct.9 / pct.15, `categorie_marime.indicatori`)
    e F20 rd.01 din `f20_din_rulaje` — aceeași citire netă, deci fără TVA-ul din Z. Garda: indicatorii nu au o citire proprie a rulajelor —
    pe rulajele 707 D 126 / C 5.826 și 709 D 80 / C 30, criteriul e 5.650 (rd.01 = 5.700 − 50), nici creditul brut 5.826, nici 5.700.
    MUTAȚIE: în `indicatori`, `f20.get(1)` -> `f20.get(2)` sau o citire proprie a creditului 707 -> pică."""
    import contextlib
    from core import categorie_marime as cm
    D = Decimal
    rl = {"707": (D("126"), D("5826")), "709": (D("80"), D("30"))}
    monkeypatch.setattr(ba, "_rulaje_67", lambda cur, schema, an: rl)
    monkeypatch.setattr(ba, "sold_la", lambda cur, schema, zi: {})
    monkeypatch.setattr(cm, "nr_mediu_salariati", lambda cur, schema, an: 3)

    class _Conn:
        def cursor(self, **k):
            return contextlib.nullcontext(None)
    ind = cm.indicatori(_Conn(), "tenant_c143", 2025)
    assert (ind["cifra_afaceri_neta"], b.f20_din_rulaje(rl)[1]) == (5650, 5650), ind
    assert b.f20_din_rulaje({"707": (Decimal("126"), Decimal("5826"))})[1] == 5700


def test_def_151_tva_ul_din_pretul_de_raft_numai_la_stocuri():
    """151. NIR fără factură, global-valoric: 371 = 800,00; 378 = 111,16 (adaosul); 4428.02 = 138,84 (TVA-ul din prețul de raft); 408 =
    665,50; plus TVA neexigibil la încasare 4428 (sintetic) 100,00 C și banca 215,50 (bilanțul egal: 766 = 766). F10 rd.05 stocuri = 800 − 111,16 − 138,84 = 550 (formularul: „… 371
    +/- 378 … − din ct. 4428”); rd.13 datorii = 408 665,50 + 4428 100,00 = 765,50 -> 766 (fără 4428.02). MUTAȚIE: `_fara_tva_stoc` scos din
    `_randuri_din_nomenclator` -> rd.13 = 904 (+ 138,84) -> pică."""
    D = Decimal
    s = {"371": (D("800.00"), D("0")), "378": (D("0"), D("111.16")), "4428.02": (D("0"), D("138.84")), "408": (D("0"), D("665.50")),
         "4428": (D("0"), D("100.00")), "5121": (D("215.50"), D("0"))}
    f10 = b.f10_din_balanta(s)
    assert (f10[5], f10[13]) == (550, 766), f10   # OMFP 1802/2014 pct.451, rd.05 „− din ct. 4428”; rd.13 „4428***”

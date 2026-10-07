# -*- coding: utf-8 -*-
"""GARD — două fapte DA/NU din Date firmă fără implicit în schemă (lotul 07.10 B, comanda Costin A.3).

Comanda: „cont_venit_implicit 707 rămâne. Cele două fapte Da/Nu, pe firmele unde nu le-a ales nimeni, se cer o dată la prima
folosire relevantă, ca seria și metoda de stoc; mecanismul îl alegi tu.” Mecanismul: coloana fără implicit (NULL = neales,
`core/migrare_fapte_date_firma.py`), ecranul arată „— alege —”, salvarea îl lasă nul, iar refuzul numit (cu buton spre Date
firmă) vine la prima folosire: chitanța fără factură și D394 cu chitanțe fără cotă (exceptarea AMEF, OUG 28/1999 art.2), D301
(înregistrarea art.317 decide pers_inreg).

CE FACE IMPOSIBIL: ca schema să pună iar „Nu” (template și migrare); ca un `false` care nu se deosebește de implicit să treacă
drept ales; ca D301 să emită pers_inreg=„1” pe o firmă care n-a răspuns; ca vectorul fiscal să întoarcă „Nu” pentru neales.
"""
import io

import pytest

from core import db as _db
from core import tenant_provisioning as _tprov

_SCH = "efemer_fapte_date_firma"


@pytest.fixture()
def conn():
    """Schemă efemeră din tenant_template.sql, ștearsă la ieșire. Nicio scriere pe date reale."""
    _db.init_pool()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), _SCH))
        c.commit()
    with _db.get_conn(_SCH) as c:
        yield c
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
        c.commit()


def _profil(cur, amef, art317):
    cur.execute("INSERT INTO firma_profil (id, nume, cui, activitate_exceptata_amef, inreg_art317) "
                "VALUES (1, 'FAPTE SRL', '14399840', %s, %s)", (amef, art317))


def test_template_fara_implicit(conn):
    """Tenant NOU: ambele coloane acceptă NULL și n-au implicit — o firmă nouă pornește „neales”."""
    from core import migrare_fapte_date_firma as M
    assert M.verifica(conn, _SCH)
    with conn.cursor() as cur:
        cur.execute("INSERT INTO firma_profil (id, nume, cui) VALUES (1, 'NOU SRL', '14399840')")
        cur.execute("SELECT activitate_exceptata_amef, inreg_art317 FROM firma_profil WHERE id = 1")
        assert cur.fetchone() == (None, None)
    conn.rollback()


@pytest.mark.parametrize("amef, art317, jurnal, asteptat", [
    (False, False, False, (None, None)),     # implicitul vechi, indistinct de o alegere -> neales
    (True, True, False, (True, True)),       # „Da” n-a fost niciodată implicit -> ales, rămâne
    (False, False, True, (None, False)),     # art.317 cu schimbare consemnată în jurnal -> ales, rămâne „Nu”
])
def test_migrarea_scoate_implicitul_si_pastreaza_alegerile(conn, amef, art317, jurnal, asteptat):
    """Tenant EXISTENT: schema veche (NOT NULL DEFAULT false) -> fără implicit; `false` nedistinct -> NULL."""
    from core import migrare_fapte_date_firma as M
    with conn.cursor() as cur:
        for col in ("activitate_exceptata_amef", "inreg_art317"):   # starea dinaintea migrării (core/migrare_d394_i2, migrare_art317)
            cur.execute("UPDATE firma_profil SET %s = false WHERE %s IS NULL" % (col, col))
            cur.execute("ALTER TABLE firma_profil ALTER COLUMN %s SET DEFAULT false" % col)
            cur.execute("ALTER TABLE firma_profil ALTER COLUMN %s SET NOT NULL" % col)
        _profil(cur, amef, art317)
        if jurnal:
            cur.execute("INSERT INTO firma_profil_jurnal (camp, valoare_veche, valoare_noua, user_id) "
                        "VALUES ('inreg_art317', 'True', 'False', 1)")
    assert not M.verifica(conn, _SCH)
    M.aplica(conn, _SCH)
    assert M.verifica(conn, _SCH)
    with conn.cursor() as cur:
        cur.execute("SELECT activitate_exceptata_amef, inreg_art317 FROM firma_profil WHERE id = 1")
        assert cur.fetchone() == asteptat
    M.aplica(conn, _SCH)                     # idempotentă
    conn.rollback()


def test_d301_cere_inregistrarea_art317_neleasa():
    """D301 pers_inreg (structura ANAF d301 poz.15: 1 neînregistrat / 2 art.317) nu se mai emite „1” în locul omului."""
    from core import d301
    baza = {"cui": "14399840", "nume": "X SRL", "banca": "BT", "iban": "RO49AAAA1B31007593840000",
            "declarant_nume": "P", "declarant_prenume": "I", "declarant_functie": "ADMIN"}
    neales, ales = d301.erori_generare(dict(baza, inreg_art317=None)), d301.erori_generare(dict(baza, inreg_art317=False))
    assert [e for e in neales if e not in ales] == [d301.MESAJ_ART317_NEALES]
    assert d301.MESAJ_ART317_NEALES not in ales


def test_vectorul_intoarce_neales_nu_nu(conn):
    from core import vector_fiscal_api as V
    with conn.cursor() as cur:
        _profil(cur, None, None)
        cur.execute("UPDATE firma_profil SET regim_fiscal = 'micro', platitor_tva = false, operatiuni_ic = false WHERE id = 1")
    assert V.citeste(conn)["inreg_art317"] is None
    conn.rollback()


def test_refuzul_amef_trimite_in_date_firma():
    """Refuzul la prima chitanță fără factură numește faptul și poartă ecranul (api.js pune butonul spre Date firmă)."""
    from core import activitati_amef as A
    e = A.refuz_nedeclarata()
    d = A.detaliu(e)
    assert (d["cod"], d["ecran"]) == (A.COD_NEDECLARATA, "date_firma")
    assert d["temei"] == A.ART2[0]                       # OUG 28/1999 art.2

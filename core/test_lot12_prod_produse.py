# -*- coding: utf-8 -*-
"""[lotul 12, deficiențele 471 și 472, comanda Costin 12.1] Nomenclatorul de produse.

471 — „Produsele venite din NIR au «cotă lipsă» fără propunere; justificarea arată «EXCEPTII_21»”:
  * articolul din stoc fără produs vine cu cota PROPUSĂ de pe rândul celui mai nou NIR al lui (`produse_api.propunere_din_nir`) — aceeași
    regulă ca NIR-ul salvat de acum (415: „preia cota de pe rândul NIR”); NIR-urile de dinainte de 415 nu trecuseră cota în nomenclator;
  * promptul potrivirii automate spune excepțiile cu cuvintele legii (CF art.291 alin.(2) lit.b) pct.1-4), nu numele constantei
    „EXCEPTII_21”, iar justificarea modelului trece prin `cote_tva.justificare_afisabila` (niciun nume intern pe ecran); justificările
    deja păstrate le rescrie `core/migrare_produse_justificare.py`, cu aceeași funcție.
472 — „Cota TVA salvată nu se mai poate corecta”: `actualizeaza` corectează cota și o CONSEMNEAZĂ în `produse_cota_jurnal` (cota și
  categoria de dinainte, cele noi, cine, când) — ca la cota de pe linia facturii (deficiența 21, decizia Costin 05.10.2026: „contabilul
  poate corecta cota; schimbarea rămâne consemnată (propus → ales, cine, când)”). Fără utilizatorul cererii, corectura se refuză.

Cotele nu se scriu din memorie: standardul și cota redusă se citesc din registru (`cote_tva.cote_regim`, CF art.291 alin.(1) și (2)).
MUTAȚII (raportate): `propunere_din_nir` întoarce {} -> pică propunerea; „vezi EXCEPTII_21” înapoi în prompt -> pică garda promptului;
`justificare_afisabila` fără înlocuire -> pică justificarea modelului și migrarea; `_consemneaza_corectura` fără INSERT -> pică jurnalul."""
import io
import os
import re

import pytest

from core import autor_cerere, cote_tva, produse_api as pa
from core import db as _db, tenant_provisioning as _tp

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCH = "efemer_lot12_prod_produse"
UID = 990012   # utilizator sintetic al cererii (jurnalul n-are legătură cu public.utilizatori, ca `factura_cota_jurnal`)


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
                cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), _SCH))
                cur.execute("SET LOCAL search_path TO %s, public" % _SCH)
            yield c
        finally:
            c.rollback()


# ── 471 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_471_articolul_din_nir_vine_cu_cota_propusa_de_pe_randul_nir(conn):
    std, red = cote_tva.cote_regim()   # CF art.291 alin.(1) și (2), din registru
    with conn.cursor() as cur:
        cur.execute("INSERT INTO articole (denumire, um) VALUES ('Marfa B', 'buc'), ('grau', 'kg')")
        cur.execute("INSERT INTO nir (numar, data) VALUES ('2', '2026-09-01'), ('3', '2026-10-12') RETURNING id")
        n2, n3 = [r[0] for r in cur.fetchall()]
        # NIR-ul mai vechi a avut altă cotă: propunerea e a celui mai nou
        cur.execute("INSERT INTO nir_linii (nir_id, denumire, cantitate, pret_achizitie, pret_vanzare, cota_tva) VALUES "
                    "(%s, 'Marfa B', 1, 10, 12, %s), (%s, 'MARFA  B', 2, 10, 12, %s)", (n2, std, n3, red))
    pe_den = {p["denumire"]: p for p in pa.lista(conn)}
    b = pe_den["Marfa B"]
    assert b["din_stoc"] and b["cota_tva"] is None, b   # în nomenclator tot fără cotă: propunerea nu scrie nimic
    assert b["propunere"] == {"cota_tva": float(red), "document": "NIR nr 3 din 12.10.2026"}, b
    assert pe_den["grau"]["propunere"] is None   # fără NIR (borderou): propunerea o dă ecranul (potrivirea automată)
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM produse")
        assert cur.fetchone()[0] == 0


def test_471_promptul_si_justificarea_fara_nume_interne(monkeypatch):
    """Promptul (regula din CF art.291 trimisă modelului) nu conține niciun nume de program (`EXCEPTII_21`, `CATEGORII_11`, …): modelul nu
    are ce copia. Răspunsul modelului care conține totuși unul iese curățat."""
    text = cote_tva.rezumat_pentru_ai()
    assert not re.findall(r"\b[A-Z][A-Z0-9]*_[A-Z0-9_]+\b", text), text
    # CF art.291 alin.(2) lit.b) pct.1-4: excepțiile de la cota redusă, cu cuvintele legii
    for cuvinte in ("bauturilor alcoolice", "NC 2202", "10 g zahar total/100 g", "Legea 56/2021"):
        assert cuvinte in text, cuvinte
    std, _red = cote_tva.cote_regim()
    from core import ai_client
    monkeypatch.setattr(ai_client, "disponibil", lambda: True)
    monkeypatch.setattr(ai_client, "genereaza_text", lambda *a, **k: '{"cota": %d, "categorie": "standard", "tip": "marfa", '
                        '"justificare": "Ciocolata e in EXCEPTII_21 (zahar adaugat), deci cota standard.", "incredere": "mare"}' % std)
    r = cote_tva.potriveste_cota("ciocolata cu lapte")
    assert r["cota"] == std and r["justificare"] == "Ciocolata e in excepțiile de la cota redusă (zahar adaugat), deci cota standard.", r


def test_471_migrarea_rescrie_justificarile_pastrate(conn):
    from core import migrare_produse_justificare as m
    std, _red = cote_tva.cote_regim()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO produse (denumire, cota_tva, justificare, sursa) VALUES "
                    "('Bomboane', %s, 'Se incadreaza in EXCEPTII_21, art. 291.', 'ai'), ('Paine', %s, 'Aliment de baza.', 'ai')", (std, std))
    assert m.aplica(conn, _SCH) == 1
    with conn.cursor() as cur:
        cur.execute("SELECT denumire, justificare, cota_tva::int, sursa FROM produse ORDER BY id")
        assert cur.fetchall() == [("Bomboane", "Se incadreaza in excepțiile de la cota redusă, art. 291.", std, "ai"),
                                  ("Paine", "Aliment de baza.", std, "ai")]
    assert m.aplica(conn, _SCH) == 0   # idempotentă


# ── 472 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_472_cota_salvata_se_corecteaza_si_corectura_e_consemnata(conn):
    std, red = cote_tva.cote_regim()
    r = pa.creeaza(conn, "Carte tehnica", cota_tva=std, confirmat=True)
    tok = autor_cerere.seteaza(UID)
    try:
        # CF art.291 alin.(2) lit.g): cărțile au cota redusă — contabilul corectează cota salvată greșit
        out = pa.actualizeaza(conn, r["id"], cota_tva=red, categorie_tva="", categorie_331="")
        assert out["ok"] and out["consemnata"], out
        # aceeași cotă din nou: nimic de consemnat
        assert pa.actualizeaza(conn, r["id"], cota_tva=red)["consemnata"] is False
    finally:
        autor_cerere.reseteaza(tok)
    with conn.cursor() as cur:
        cur.execute("SELECT produs_id, denumire, cota_veche::int, categorie_veche, cota_noua::int, categorie_noua, user_id "
                    "FROM produse_cota_jurnal")
        assert cur.fetchall() == [(r["id"], "Carte tehnica", std, None, red, None, UID)]
        cur.execute("SELECT cota_tva::int, sursa FROM produse WHERE id = %s", (r["id"],))
        assert cur.fetchone() == (red, "manual")
    rand = next(p for p in pa.lista(conn) if p["id"] == r["id"])
    assert (rand["ultima_corectare"]["cota_veche"], rand["ultima_corectare"]["cota_noua"]) == (float(std), float(red)), rand
    # o corectură fără utilizatorul cererii nu se face (n-ar fi consemnată cu autorul ei)
    with pytest.raises(ValueError, match="utilizatorul"):
        pa.actualizeaza(conn, r["id"], cota_tva=std)


def test_472_jurnalul_e_in_sablonul_firmei():
    """Sursa unică a structurii: blocul din tenant_template.sql = `migrare_produse_cota_jurnal.bloc_template()`."""
    from core import migrare_produse_cota_jurnal as m
    assert m.bloc_template() in io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read()

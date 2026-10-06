# -*- coding: utf-8 -*-
"""GARDA părții 4 din comanda Costin 06.10.2026 — povestea lunii.

  14. „În email apar marcaje «**» netransformate. Emailul se trimite fără marcaje brute.”
  15. „Cifra numită «profit» e profitul înainte de impozit. Eticheta spune exact ce e cifra.”
  16. „Decizia A (Costin): restanțele declarațiilor nu apar în povestea trimisă clientului.”

Modelul AI e SIMULAT (nu se cheamă API-ul).
"""
import os
import re
from decimal import Decimal

from core import ai_client, motor, pachete_api as P

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RZ = {"nume_firma": "ZT Firma", "venituri": 1000.0, "cheltuieli": 400.0, "rezultat": 600.0, "tip": "profit",
      "declaratii_depuse": ["D300"], "email": "x@invalid", "are_date": True}
CU_MARCAJE = "# Luna august\n**Veniturile** au fost 1.000,00 lei, iar *cheltuielile* 400,00 lei. __Rezultatul__ e profit."


# ── pct.14 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_emailul_pleaca_fara_marcaje_si_din_povestile_vechi():
    """O poveste aprobată înainte de reparație (salvată cu «**») trece prin `_html` fără marcaje.
    MUTAȚIE: `text_simplu` scos din `_html` -> «**» în email -> pică."""
    h = P._html(RZ, 2026, 8, CU_MARCAJE, "Cu salutări,")
    assert "**" not in h and "__" not in h and "# Luna" not in h and "*cheltuielile*" not in h
    corp = re.search(r"white-space:pre-wrap'>(.*?)</div>", h, re.S).group(1)
    assert corp == "Luna august\nVeniturile au fost 1.000,00 lei, iar cheltuielile 400,00 lei. Rezultatul e profit."


def test_marcajele_se_scot_la_generare_si_la_salvare(monkeypatch):
    """MUTAȚIE: `text_simplu` scos de la generare -> textul ajunge în editor cu «**» -> pică."""
    class _AI:
        def disponibil(self):
            return True

        def genereaza_text(self, *_a, **_k):
            return CU_MARCAJE
    monkeypatch.setattr(P, "ai_client", _AI())
    monkeypatch.setattr(P, "rezumat_luna", lambda *a, **k: dict(RZ))
    import core.control_fiscal_api as cf
    monkeypatch.setattr(cf, "evalueaza_firma", lambda *a, **k: {"lipsa": []})
    r = P.genereaza_poveste(None, None, 1, 2026, 8, "x")
    assert "**" not in r["text"] and not r["text"].startswith("#"), r["text"]
    assert ai_client.text_simplu("2 * 3 = 6 și 4*5") == "2 * 3 = 6 și 4*5"     # un asterisc care nu e marcaj rămâne


def test_portalul_primeste_povestea_fara_marcaje():
    """`lista_povesti_aprobate` e singura sursă a portalului. MUTAȚIE: curățarea scoasă -> pică."""
    class _Cur:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def execute(self, *a):
            pass

        def fetchall(self):
            return [{"an": 2026, "luna": 8, "text": CU_MARCAJE, "updated_at": None}]

    class _Conn:
        def cursor(self, **_k):
            return _Cur()
    assert "**" not in P.lista_povesti_aprobate(_Conn(), 1)[0]["text"]


# ── pct.15 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_rezultatul_e_inainte_de_impozit():
    """OMFP 1802/2014, funcțiunea conturilor: grupa 69 (691/698) e cheltuiala cu impozitul, grupa 79 venitul din impozit.
    Luna în care cade nota impozitului micro (698) nu-și schimbă înțelesul cifrei. MUTAȚIE: excluderea grupei 69 scoasă ->
    rezultat 590 -> pică."""
    D = Decimal
    note = [{"debit": "4111", "credit": "707", "suma": D("1000")}, {"debit": "628", "credit": "401", "suma": D("400")},
            {"debit": "698", "credit": "4418", "suma": D("10")}]
    r = motor.rezultat(note)
    assert (r["venituri"], r["cheltuieli"], r["rezultat"]) == (D("1000.00"), D("400.00"), D("600.00"))


def test_eticheta_spune_inainte_de_impozit_in_email_si_in_prompt():
    """MUTAȚIE: eticheta veche în email -> pică. Pachetul și portalul (JS) le arată proba de browser
    `frontend_test/proba_lot0610_p34.py` — o aserțiune pe sursa JS ar găsi șirul și într-un comentariu."""
    rand = re.search(r"<tr><td[^>]*>(Rezultat[^<]*)</td>\s*<td[^>]*>([^<]*)</td></tr>", P._html(RZ, 2026, 8, "x", ""))
    assert rand.groups() == ("Rezultat înainte de impozit", "600,00 lei (profit)")
    linie = next(l for l in P._prompt_poveste(RZ, 2026, 8).splitlines() if l.startswith("- Rezultat"))
    assert linie == "- Rezultat inainte de impozit: 600,00 lei (profit)"


# ── pct.16 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_restantele_nu_intra_in_povestea_pentru_client():
    """Decizia A. Promptul nu primește restanțele, chiar dacă există. MUTAȚIE: linia restanțelor repusă în prompt -> pică."""
    t = P._prompt_poveste(RZ, 2026, 8, restante_desc="D300 iulie 2026, D112 august 2026")
    assert "D112 august 2026" not in t and "RESTANTE (nedepuse" not in t


def test_un_text_care_pomeneste_restante_e_abatere():
    """Modelul (sau o editare) poate scrie oricum despre restanțe: editorul le arată ca abatere înainte de aprobare.
    MUTAȚIE: verificarea scoasă din `abateri_termeni` -> pică."""
    a = P.abateri_termeni("Veniturile au fost 1.000,00 lei. Mai sunt declarații restante: D300.", RZ)
    assert any(x.startswith("restanțe:") for x in a), a
    assert P.abateri_termeni("Veniturile au fost 1.000,00 lei, cheltuielile 400,00 lei.", RZ) == []


def test_celelalte_texte_ai_afisate_ies_fara_marcaje(monkeypatch):
    """Generalizarea pct.14: analiza tiparelor (ecranul cabinetului) și răspunsul AI la o raportare (firul utilizatorului)
    se afișau la fel, brut. MUTAȚIE: `text_simplu` scos din `tipare_api` sau din `raportari_ai` -> pică."""
    from core import raportari_ai, tipare_api
    monkeypatch.setattr(ai_client, "disponibil", lambda: True)
    monkeypatch.setattr(tipare_api, "tipare", lambda *a, **k: {"are_date": True, "motive": [{"motiv": "CIF invalid", "n": 3}],
                                                                "tipuri": [], "firme": []})
    monkeypatch.setattr(ai_client, "genereaza_text", lambda *a, **k: "**Tipar:** D300 respinsă de 3 ori")
    assert tipare_api.analiza_ai(None, 1) == {"disponibil": True, "analiza": "Tipar: D300 respinsă de 3 ori"}
    monkeypatch.setattr(ai_client, "genereaza_text",
                        lambda *a, **k: '{"decizie": "raspund", "raspuns": "**Da**, din ecranul Facturi."}')
    assert raportari_ai.triaj("x", "y") == {"decizie": "raspund", "raspuns": "Da, din ecranul Facturi."}

# -*- coding: utf-8 -*-
"""GARD — povestea lunii folosește termenii și cifrele pachetului; emailul arată cifrele (comanda Costin 05.10.2026, pct.1 și 7).

Pct.1: *„pachetul arată «Venituri 1.000 lei», iar textul spune «încasări de 1.000 de lei» și «a cheltuit mai mult decât a
câștigat». Venituri, încasări și profit sunt lucruri diferite pentru antreprenor. Textul generat folosește exact termenii și
cifrele din pachet (venituri, cheltuieli, rezultat)”*. Măsurat în browser înainte: textul AI scria „nu au existat încasări”.
Pct.7: *„Previzualizarea arată cifrele pachetului; cu povestea goală, «Trimite» rămâne inactiv cu motiv.”*

Modelul AI e SIMULAT aici (nu se cheamă API-ul): se probează ce face codul cu un text bun și cu unul care se abate.
"""
import re

from core import pachete_api as P

RZ = {"nume_firma": "ZT Firma", "venituri": 1000.0, "cheltuieli": 1200.0, "rezultat": -200.0, "tip": "pierdere",
      "declaratii_depuse": ["D300"], "email": "x@invalid", "are_date": True}


def test_promptul_cere_termenii_si_sumele_pachetului():
    t = P._prompt_poveste(RZ, 2026, 8)
    assert re.search(r"«venituri», «cheltuieli» si «rezultat»", t), "promptul nu cere termenii exacti"
    assert re.search(r"Veniturile NU sunt «incasari»", t) and re.search(r"«castig»", t)
    # sumele exact cum le arată pachetul (format românesc), nu „1000.00”
    assert len(re.findall(r"1\.000,00 lei|1\.200,00 lei|-200,00 lei", t)) == 3, t
    assert not re.search(r"\b1000\.00\b", t)
    # calificativul rezultatului = cuvântul pachetului
    assert re.search(r"spui doar «pierdere»", t)


def test_abaterile_prind_exemplul_din_comanda():
    """Textul citat de Costin: trei abateri (încasări, câștigat, profit când pachetul spune pierdere)."""
    a = P.abateri_termeni("Firma a avut încasări de 1.000 de lei și a cheltuit mai mult decât a câștigat. Un profit mic.", RZ)
    assert set(a) == {"termen: încasări", "termen: câștigat", "termen: profit (pachetul arată pierdere)"}, a


def test_un_text_pe_termenii_pachetului_nu_are_abateri():
    t = ("Veniturile lunii au fost 1.000,00 lei, iar cheltuielile 1.200,00 lei. Rezultatul este o pierdere de 200,00 lei.")
    assert P.abateri_termeni(t, RZ) == []


def test_o_suma_in_lei_care_nu_e_in_pachet_e_abatere():
    assert P.abateri_termeni("Veniturile au fost 1.000 lei; chiria a fost 350 de lei.", RZ) == ["sumă: 350 de lei (nu e în pachet)"]


class _AI:
    def __init__(self, texte):
        self.texte, self.prompturi = list(texte), []

    def disponibil(self):
        return True

    def genereaza_text(self, prompt, max_tokens=None, **_k):
        self.prompturi.append(prompt)
        return self.texte.pop(0)


def _genereaza(monkeypatch, texte):
    ai = _AI(texte)
    monkeypatch.setattr(P, "ai_client", ai)
    monkeypatch.setattr(P, "rezumat_luna", lambda *a, **k: dict(RZ))
    import core.control_fiscal_api as cf
    monkeypatch.setattr(cf, "evalueaza_firma", lambda *a, **k: {"lipsa": []})
    return P.genereaza_poveste(P.date_poveste(None, None, 1, 2026, 8, "s"), 2026, 8), ai


def test_generarea_reincearca_o_data_cu_abaterile_numite(monkeypatch):
    """MUTAȚIE: reîncercarea scoasă (o singură generare) -> textul cu „încasări” ajunge la editor -> pică."""
    bun = "Veniturile au fost 1.000,00 lei, cheltuielile 1.200,00 lei, iar rezultatul o pierdere de 200,00 lei."
    r, ai = _genereaza(monkeypatch, ["Încasări de 1.000 de lei.", bun])
    assert r["ok"] and r["text"] == bun and r["abateri"] == []
    assert len(ai.prompturi) == 2 and re.search(r"varianta anterioara a scris termen: încasări", ai.prompturi[1])


def test_daca_abaterile_raman_ajung_la_editor_numite(monkeypatch):
    r, ai = _genereaza(monkeypatch, ["Încasări de 1.000 de lei.", "Am câștigat 1.000 de lei."])
    assert r["ok"] and r["abateri"] == ["termen: câștigat"] and len(ai.prompturi) == 2


def test_emailul_arata_cifrele_pachetului_si_cu_povestea_goala():
    """Pct.7. MUTAȚIE: tabelul de cifre scos din `_html` -> pică. Previzualizarea e aceeași funcție (`preview_html`)."""
    h = P._html(dict(RZ), 2026, 8, "", "Cu salutări,")
    text = re.sub(r"<[^>]+>", " ", h)
    for eticheta, suma in (("Venituri", "1.000,00 lei"), ("Cheltuieli", "1.200,00 lei"), ("Rezultat înainte de impozit", "-200,00 lei (pierdere)")):
        assert re.search(r"%s\s+%s" % (eticheta, re.escape(suma)), text), (eticheta, text)
    assert re.search(r"Povestea lunii nu e scrisă încă", text)


def test_rezultatul_zero_nu_e_profit(monkeypatch):
    """Text fix din aceeași clasă: motorul pune `profit` pe rezultat >= 0, iar pachetul arăta „0,00 lei (profit)”."""
    monkeypatch.setattr(P, "_note_lunii", lambda *a: [{"x": 1}])
    monkeypatch.setattr(P.motor, "rezultat", lambda note: {"venituri": 500, "cheltuieli": 500, "rezultat": 0, "tip": "profit"})
    monkeypatch.setattr(P, "_profil", lambda c: {"nume": "ZT"})
    monkeypatch.setattr(P, "_declaratii_depuse", lambda *a: [])
    assert P.rezumat_luna(None, None, 1, 2026, 8)["tip"] == "neutru"


def test_trimiterea_refuza_povestea_goala(monkeypatch):
    monkeypatch.setattr(P, "rezumat_luna", lambda *a, **k: dict(RZ))
    monkeypatch.setattr(P, "get_poveste", lambda *a: {"ok": True, "exista": True, "text": "   ", "status": "aprobat"})
    assert P.pregateste(None, None, 1, 2026, 8)["cod"] == "POVESTE_GOALA"

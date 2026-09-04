# -*- coding: utf-8 -*-
"""PREDARE_LANT.md isi arata vechimea, iar avertismentul din poarta nu poate disparea tacit.

DE CE EXISTA. 24.08.2026: versiunea de atunci a predarii era din 22.08 si continea
TREI afirmatii false — starea pe alt commit, cifra 131 (invalidata intre timp) si un
front deja rezolvat. Costin: «un PREDARE_LANT care instruieste sesiunea noua sa-l
citeasca primul si contine trei afirmatii false e mai rau decat unul absent — cine il
citeste n-are cum sa stie care rand mai e adevarat.»

CE FACE IMPOSIBIL: (a) o predare fara data in cap, deci care nu-si poate arata
vechimea; (b) stergerea tacita a avertismentului de vechime din poarta.

CE NU FACE, declarat: nu verifica daca ce scrie in predare e ADEVARAT — asta nu se
poate masura. Si nu blocheaza un commit pe vechime: avertismentul din hook e un
mesaj, nu o poarta. Un /clear nu se poate garda deloc din git.
"""
import datetime
import io
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREDARE = os.path.join(RAD, "PREDARE_LANT.md")
HOOK = os.path.join(RAD, "scripts", "githooks", "pre-commit")


def _text(cale):
    return io.open(cale, encoding="utf-8").read()


def test_predarea_isi_spune_data_si_commitul():
    """Fara ele, cine o citeste nu poate sti daca descrie lumea de azi."""
    t = _text(PREDARE)
    cap = t.split("## STAREA LA PREDARE")[0]
    m = re.search(r"\*\*ultima rescriere\*\*:\s*\*\*(\d{4}-\d{2}-\d{2})\*\*", cap)
    assert m, "PREDARE_LANT.md n-are «ultima rescriere» cu data, in cap"
    datetime.date.fromisoformat(m.group(1))          # data trebuie sa fie o data reala
    assert re.search(r"\*\*pe commit\*\*:\s*`[0-9a-f]{7,40}`", cap), \
        "PREDARE_LANT.md n-are «pe commit» in cap"


def test_predarea_spune_cand_se_rescrie():
    """Regula care a lipsit: se rescrie inainte de fiecare oprire."""
    cap = _text(PREDARE).split("## STAREA LA PREDARE")[0]
    assert "înainte de fiecare oprire" in cap.lower() or "inainte de fiecare oprire" in cap.lower(), \
        "predarea nu spune CAND se rescrie"


def test_avertismentul_de_vechime_e_in_poarta():
    """ANTI-DISPARITIE. Daca cineva scoate blocul din hook, aici cade."""
    h = _text(HOOK)
    assert "PREDARE_LANT.md" in h, "hook-ul nu mai stie de PREDARE_LANT.md"
    assert re.search(r"PRAG_PREDARE=\d+", h), "hook-ul n-are pragul de vechime"
    assert "rev-list --count" in h, "hook-ul nu mai numara commiturile de la ultima rescriere"


def test_avertismentul_avertizeaza_si_NU_blocheaza():
    """Decizia scrisa: un blocaj pe vechime ar face din predare un impozit pe
    reparatiile mici. Daca cineva il transforma in `exit 1`, aici se vede."""
    h = _text(HOOK)
    bloc = h.split("PRAG_PREDARE=")[1].split("TOT=")[0]
    assert "exit 1" not in bloc, "avertismentul de vechime a devenit BLOCAJ — a fost decis ca avertisment"
    assert "NU e blocat" in bloc or "NU e blocat" in h


def test_hookul_nu_e_gol():
    """ANTI-VACUU: un hook trunchiat ar trece toate aserttiunile de mai sus pe vid."""
    h = _text(HOOK)
    assert len(h) > 2000 and "verificator_conformitate.py" in h


# Se cauta CIFRA 131, nu sirul „131": `R131`, `r131` si `test_cifra_131_…` sunt NUME, si au
# ajuns in predare pe 04.09.2026 odata cu restanta R131. Garda de dinainte se uita la PRIMA
# aparitie a sirului, deci a cazut pe un nume — clasa „aserttiune ancorata pe text"
# (METODA_VERIFICARE §23, clichetul 50). Acum se uita la TOATE aparitiile cifrei, nu la prima:
# e si mai stransa decat era, nu mai larga.
_CIFRA_131 = re.compile(r"(?<![\w.\-])131(?![\w.\-])")


def test_cifra_131_e_marcata_invalidata_nu_corectata():
    """Regula ceruta: o cifra ai carei termeni nu se mai pot reconstitui se
    INVALIDEAZA, nu se corecteaza. Predarea veche o purta ca pe o cifra buna."""
    t = _text(PREDARE)
    poz = [m.start() for m in _CIFRA_131.finditer(t)]
    assert poz, "predarea nu mai pomeneste cifra 131 — daca a fost scoasa, scoate si testul"
    rele = [p for p in poz
            if "INVALIDAT" not in t[max(0, p - 200):p + 600].upper()]
    assert not rele, (
        "cifra 131 apare in predare fara sa fie marcata invalidata, in %d loc(uri):\n  %s"
        % (len(rele), "\n  ".join(repr(t[max(0, p - 90):p + 90]) for p in rele)))


def test_CALIBRARE_garda_cifrei_131_nu_confunda_un_NUME_cu_cifra():
    """Directia «acuza pe nedrept», pe chiar greseala care a cazut pe 04.09: un nume care
    contine 131 nu e cifra 131. Si directia opusa: cifra goala TREBUIE gasita."""
    assert _CIFRA_131.findall("restanta R131, proba_r131.py, test_cifra_131_e_marcata") == []
    assert _CIFRA_131.findall("clichetul era 131 atunci") == ["131"]
    assert _CIFRA_131.findall("1310 si 2131 si 13.1") == []

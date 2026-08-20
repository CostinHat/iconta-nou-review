# -*- coding: utf-8 -*-
"""CLICHET (20.08.2026): clasa constantelor fiscale nesursate din PRODUCȚIE nu mai crește.

DE CE UN CLICHET ȘI NU UN XFAIL. Inventarul de pe 31.07 a fost scris ca `xfail` — a *înregistrat*
datoria, n-a *împiedicat-o*. Opt zile mai târziu clasa a produs a cincea apariție. Un xfail e o
notiță; un clichet e o poartă. Datoria existentă rămâne (126 la instalare), dar nu se mai poate mări,
iar arderea ei e vizibilă: fiecare scădere se coboară în BASELINE, deci progresul e ireversibil.

PER FIȘIER, nu global — altfel o reparație într-un modul ar plăti pentru o încălcare nouă în altul,
și totalul ar sta pe loc arătând verde.

CE MĂSOARĂ. `core/scan_constante.py`: literali numerici din modulele fiscale, clasificați după unde
LOCUIESC (constantă de modul / default la lookup / default de parametru / Decimal literal / nume
fiscal), apoi împărțiți după strămoșul sintactic în A=sursat (are `Temei`), B=nomenclator (cod din
XSD/algoritm), C=nesursat, D=precizie, E=temei în proză. C e ținta.

DIMENSIUNEA CLASEI: 85 vizibile în teste (inventarul 31.07) + 98 în producție. Partea invizibilă e
tot mai mare decât cea văzută. Termenele de depunere — motivul pentru care s-a pornit — sunt 3 din
98 (al patrulea, ziua 30 a lui D394, e sursat în proza antetului lui `scadente.py`).

RECALCULAT 20.08(d): prima măsurătoare a dat C=126, dar ea însăși avea o clasă nedistinsă — temei
PREZENT, dar în PROZĂ, nu ca obiect `Temei`. `cote_tva.py` reproduce art. 291 CF în antet și e pe
`_TVA_EXCLUSE` în verificator, și totuși scanul îl raporta nesursat. 28 din cele 126 erau de fapt
sursate în proză; clichetul coboară cu ele. Măsurătoarea a trebuit măsurată înainte de a arde
clichetul după ea — altfel 28 de reparații ar fi fost făcute pe cazuri care nu erau stricate.
"""
import pytest

from core import scan_constante

# Instalat 20.08.2026, COBORÂT 20.08(d) de la 126 la 98 după distingerea clasei E (temei în proză).
# Se coboară pe măsură ce constantele primesc temei. Nu se ridică.
# Ieșite complet: `cote_tva.py` (2) și `d300.py` (5) — amândouă își citează actul în antet, per
# valoare. Coborâte: d394 9->2, d212_engine 13->11, d101 8->7, d104 4->0, salarizare 19->18.
BASELINE = {
    "common.py": 8, "control_fiscal_api.py": 1, "d101.py": 7, "d101g.py": 1,
    "d108.py": 1, "d169.py": 1, "d169n.py": 1, "d205.py": 2, "d212_engine.py": 11,
    "d216.py": 1, "d300_reconciliere.py": 5, "d394.py": 2,
    "d401.py": 2, "d402.py": 3, "d403.py": 5, "d406.py": 5, "d406_active.py": 7,
    "d406_stocuri.py": 1, "d407.py": 2, "salariati_api.py": 1, "salarizare.py": 18,
    "scadente.py": 3, "stat_plata_api.py": 1, "tva_agricultori.py": 2, "tva_aur.py": 1,
    "tva_marja.py": 2, "tva_marja_turism.py": 4,
}


@pytest.fixture(scope="module")
def inv():
    return scan_constante.inventar()


def _pe_fisier(inv):
    d = {}
    for h in inv:
        if h["cls"] == "C":
            d[h["f"]] = d.get(h["f"], 0) + 1
    return d


def test_clichetul_nu_creste(inv):
    """Miezul. Un fișier nou fiscal pornește de la 0 — orice constantă nesursată în el pică."""
    acum = _pe_fisier(inv)
    crescut = []
    for f, n in sorted(acum.items()):
        lim = BASELINE.get(f, 0)
        if n > lim:
            noi = [h for h in inv if h["cls"] == "C" and h["f"] == f][lim:]
            crescut.append("  %s: %d > %d  (ex: l.%s `%s` — %s)"
                           % (f, n, lim, noi[0]["l"], noi[0]["v"], noi[0]["txt"][:60]) if noi
                           else "  %s: %d > %d" % (f, n, lim))
    assert not crescut, (
        "constante fiscale NESURSATE în plus față de clichet:\n" + "\n".join(crescut)
        + "\n\nRemediu: atașează un `Temei(...)` (vezi common.COTE) sau mută valoarea în registru."
        + "\nDacă e nomenclator (cod din XSD, pondere de checksum), botează-l ca atare — vezi"
        + " scan_constante.NOM — și scrie de unde vine.")


def test_baseline_nu_e_stat(inv):
    """Anti-datorie-stătută: dacă un fișier a coborât, BASELINE trebuie coborât cu el."""
    acum = _pe_fisier(inv)
    stat = ["  %s: clichet %d, real %d" % (f, n, acum.get(f, 0))
            for f, n in sorted(BASELINE.items()) if acum.get(f, 0) < n]
    assert not stat, (
        "clichetul e mai larg decât realitatea — coboară-l, altfel datoria poate reveni tăcut:\n"
        + "\n".join(stat))


# ─────────── ANTI-VACUU: calibrare în PATRU direcții ───────────
# O singură țintă lasă scanul să treacă pe gol în celelalte. Prima versiune a scanului a picat pe
# `25`; a doua a trecut `25` dar a pus `4050` (care ARE Temei) în nesursate; a treia a raportat
# `cote_tva.py` nesursat deși modulul reproduce art. 291 CF. Fiecare direcție a picat efectiv o dată
# în construcție — de-aia sunt toate patru aici, nu doar cea care a picat ultima.

def _clasa(inv, fisier, valoare, casa=None):
    r = [h for h in inv if h["f"] == fisier and h["v"] == valoare and (casa is None or h["casa"] == casa)]
    return r[0]["cls"] if r else None


def test_calibrare_vede_nesursatul(inv):
    """`_ZIUA.get(tip, 25)` — ziua de scadență implicită. Nu apare în NICIUN test; e cazul care a
    dovedit că inventarul de pe 31.07 era orb prin construcție."""
    assert _clasa(inv, "scadente.py", "25", "H2") == "C", \
        "scanul nu mai vede ziua 25 din _ZIUA — dacă `scadente.py` s-a schimbat, refă calibrarea"


def test_calibrare_nu_confunda_sursatul(inv):
    """`Decimal("4050")` are `Temei("HG", 1506, 2024)` alături. A raporta-o ca nesursată ar umfla
    datoria cu exact cazurile bune și ar face clichetul de neîncredere."""
    assert _clasa(inv, "common.py", "4050") == "A"


def test_calibrare_separa_nomenclatorul(inv):
    """`_JUD.get(j, 40)` — codul județului. Are sursă, dar e SIRUTA/XSD, nu Cod fiscal; se revizuiește
    altfel. Amestecat în C, ar dilua ținta."""
    assert _clasa(inv, "bilant_api.py", "40", "H2") == "B"


def test_calibrare_vede_temeiul_din_proza(inv):
    """A patra direcție, adăugată 20.08(d). `cote_tva.COTA_STANDARD = 21` NU e datorie: antetul
    citează art. 291 CF (Legea 141/2025) chiar lângă valoare, iar verificatorul are modulul pe
    `_TVA_EXCLUSE` fiindcă el e cel care reproduce legea. Raportată ca nesursată, ar fi trimis pe
    cineva să „repare" un caz bun — și ar fi stricat structura injectată în promptul AI."""
    assert _clasa(inv, "cote_tva.py", "21") == "E"
    assert _clasa(inv, "cote_tva.py", "11") == "E"


def test_proza_nu_inghite_nesursatul(inv):
    """Contra-direcția lui E, și cea care contează: o clasă care „sursează" din proză poate ȘTERGE
    datoria reală. Măsurat în construcție — regula „există o citare undeva în antetul modulului" ar
    fi mutat 100 din 126 în E, inclusiv aserțiunile din `d212_engine` și cota în float din `d216`.
    De-aia proza cere VALOAREA, iar antetul guvernează doar constantele modulului."""
    assert _clasa(inv, "scadente.py", "25", "H2") == "C", "ziua 25 din _ZIUA a fugit în E"
    assert _clasa(inv, "d216.py", "0.3") == "C", "cota în float din d216 a fugit în E"
    assert _clasa(inv, "d101.py", "16") == "C", "cota de impozit pe profit a fugit în E"
    assert sum(1 for h in inv if h["cls"] == "C" and h["f"] == "d212_engine.py") >= 11, \
        "aserțiunile cu valori din modulul de PRODUCȚIE d212_engine au fugit în E"


def test_respinsele_din_proza_nu_imbatranesc(inv):
    """Anti-vacuu pe exceptare (a doua oară în fișierul ăsta, din același motiv): o respingere care
    nu mai corespunde unui candidat e o notă despre o lume care nu mai există. Fiecare intrare din
    `PROZA_RESPINSA` trebuie să fie în continuare un caz pe care scanul L-AR muta în E."""
    moarte = []
    for f, v in scan_constante.PROZA_RESPINSA:
        cand = [h for h in inv if h["f"] == f and h["v"] == v and h["cit"]]
        if not cand:
            moarte.append("  %s `%s`" % (f, v))
        elif any(h["cls"] != "C" for h in cand):
            moarte.append("  %s `%s` — respinsă, dar nu e în C" % (f, v))
    assert not moarte, (
        "respingeri care nu mai corespund unui candidat — scoate-le din PROZA_RESPINSA:\n"
        + "\n".join(moarte))


def test_scanul_chiar_vede_toate_clasele(inv):
    """Dacă regexul de module sau parserul se rupe, listele se golesc și clichetul ar trece pe gol."""
    from collections import Counter
    c = Counter(h["cls"] for h in inv)
    assert c["A"] >= 20 and c["B"] >= 100 and c["C"] >= 50, \
        "distribuție implauzibilă — scanul s-a rupt, nu s-a reparat codul: %s" % dict(c)
    assert 10 <= c["E"] <= 60, (
        "clasa E (temei în proză) e implauzibilă: %d. Sub prag = detectorul de citări s-a rupt și "
        "clichetul e prea larg; peste = proza a devenit o pătură și șterge datorie reală." % c["E"])
    assert all(h["cit"] for h in inv if h["cls"] == "E"), \
        "un E fără citat — E trebuie să poată fi CITIT, altfel e o afirmație neverificabilă"
    assert len({h["f"] for h in inv}) >= 40, "prea puține module fiscale văzute: verifică scan_constante.FIS"


# ─────────── DOMENIUL: de ce `core/` și ce se pierde prin asta ───────────
# Memoria zilei (test_datorie.py:144) spune: când scrii domeniul de căutare, întreabă-te unde trăiește
# de fapt lucrul căutat, nu unde stă fișierul de test. Deci am MĂSURAT rădăcina, n-am presupus-o goală:
# 14 constante de clasă C în `main.py`, TOATE operaționale (praguri RAM/disc, conexiuni, cooldown,
# rate-limit, paginare, ferestre de zile). Zero fiscale. Restrângerea la `core/` n-a ascuns nimic azi.
#
# Dar gaura e structurală: o cotă scrisă mâine direct într-o rută din `main.py` n-ar fi prinsă. Testul de
# mai jos o închide îngust — fără să importe cele 14 ca datorie falsă, fiindcă n-ar fi datorie fiscală.

_RADACINA = ("main.py", "tenant_db.py", "db.py")

# Numele operaționale care conțin din întâmplare un cuvânt din `NF` („prag"). Fiecare cu ce măsoară,
# ca lista să nu devină un coș în care se ascund constante fiscale reale.
_OPERATIONALE = {
    "_PRAG_RAM_PROCENT": "procent RAM peste care se alertează — infrastructură",
    "_PRAG_DISC_PROCENT": "procent disc peste care se alertează — infrastructură",
    "_PRAG_CONEXIUNI_DB": "număr de conexiuni Postgres peste care se alertează — infrastructură",
}


def test_nicio_constanta_fiscala_in_radacina():
    """Îngust prin construcție: nu inventariază rădăcina, cere doar ca nimic FISCAL să nu apară acolo.
    Locul unei cote e registrul `common.COTE`, nu o rută."""
    import io
    import os
    import re
    rad = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rele = []
    for f in _RADACINA:
        p = os.path.join(rad, f)
        if not os.path.exists(p):
            continue
        for h in scan_constante.scan(f, io.open(p, encoding="utf-8", errors="replace").read()):
            # ȘI E, nu doar C: testul ăsta e despre LOCUL constantei, nu despre sursarea ei. O cotă
            # scrisă într-o rută rămâne în locul greșit chiar dacă are un comentariu cu articolul.
            if h["cls"] not in ("C", "E") or scan_constante._este_precizie(h):
                continue
            m = scan_constante.NF.search(h["ctx"])
            if not m:
                continue
            nume = re.search(r"`([^`]+)`", h["ctx"])
            if nume and nume.group(1).strip() in _OPERATIONALE:
                continue
            rele.append("  %s:%d `%s` — %s | %s" % (f, h["l"], h["v"], h["ctx"], h["txt"][:60]))
    assert not rele, (
        "constantă cu nume fiscal în afara lui core/:\n" + "\n".join(rele)
        + "\n\nMută valoarea în common.COTE cu Temei. Dacă e operațională (infrastructură, paginare,"
        + " rate-limit), adaug-o în _OPERATIONALE cu ce măsoară.")


def test_lista_operationale_nu_e_un_cos():
    """Anti-vacuu pe exemptare: fiecare nume exceptat trebuie să existe cu adevărat în rădăcină,
    altfel lista îmbătrânește și ascunde ce n-a fost niciodată acolo."""
    import io
    import os
    rad = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sursa = "".join(io.open(os.path.join(rad, f), encoding="utf-8", errors="replace").read()
                    for f in _RADACINA if os.path.exists(os.path.join(rad, f)))
    moarte = [n for n in _OPERATIONALE if n not in sursa]
    assert not moarte, "exceptări care nu mai există în rădăcină — scoate-le: %s" % moarte

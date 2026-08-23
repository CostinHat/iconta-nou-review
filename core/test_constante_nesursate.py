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
    # LARGIT a TREIA oara, 23.08.2026: domeniul cuprinde acum si modulele care POARTA O VALOARE din
    # registrul de cote, oricat de putin ar vorbi. Masurat la intrebarea lui Costin: dupa doua largiri,
    # 15 din cele 25 de functii cu `cota = 21` ca default erau INCA in afara (avansuri, comodat_chirii,
    # intracomunitar, inventariere, leasing, obiecte_inventar, productie, sgr). C: 135 -> 162.
    "asistenti_api.py": 3, "asociati_import_api.py": 1, "audit_preluare.py": 1, "avansuri.py": 4,
    "beneficii_api.py": 1, "casa.py": 6, "cashflow.py": 2, "common.py": 8, "comodat_chirii.py": 3,
    "contracte_speciale.py": 5, "control_fiscal_api.py": 1, "control_incrucisat.py": 1, "cor_api.py": 2,
    "d101.py": 7, "d101g.py": 1, "d108.py": 1, "d169.py": 1, "d169n.py": 1, "d205.py": 2,
    "d212_engine.py": 11, "d216.py": 1, "d394.py": 2, "d401.py": 2, "d402.py": 3, "d403.py": 5,
    "d406.py": 5, "d406_active.py": 7, "d406_stocuri.py": 1, "d407.py": 2, "decontari_asociati.py": 1,
    "deconturi.py": 1, "duk.py": 2, "efactura_send.py": 1, "factura_pdf.py": 1, "import_export.py": 1,
    "intracomunitar.py": 2, "inventariere.py": 1, "leasing.py": 3, "lichidare.py": 1,
    "monitor_fiscal.py": 1, "motor.py": 2, "notificari_scadenta.py": 2, "obiecte_inventar.py": 1,
    "ong.py": 2, "perisabilitati.py": 1, "productie.py": 2, "produse_api.py": 1, "provizioane.py": 1,
    "salariati_api.py": 1, "salariati_import_api.py": 2, "salarizare.py": 18, "scadentar.py": 2,
    "scadente.py": 3, "scan_constante.py": 1, "sgr.py": 2, "sponsorizari.py": 3, "stat_plata_api.py": 1,
    "stocuri.py": 1, "taxare_inversa.py": 1, "termene_api.py": 1, "tva_agricultori.py": 2,
    "tva_aur.py": 1, "tva_marja.py": 2, "tva_marja_turism.py": 4,
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



# ─────────── CONFRUNTAREA CELOR DOUĂ INSTRUMENTE (21.08.2026) ───────────
# Întrebarea lui Costin, după ce clasa E a scos 28 de false pozitive: *există o cale ca următorul
# inventar să afle ÎNAINTE, nu după?* Da — și n-a fost eșantionul de 30. Acela privește clasa în
# agregat, iar `COTA_STANDARD = 21` nu se deosebește de nimic într-un rând de scan. Ce a prins-o a
# fost verificarea la SURSĂ a primei intrări de pe lista de ardere: s-a deschis fișierul.
#
# Dar exista și o cale MECANICĂ, disponibilă din prima zi: **două instrumente din acest repo aveau
# opinii despre același fișier și nimeni nu le confrunta.** Verificatorul ținea `cote_tva.py` pe
# `_TVA_EXCLUSE` („aici literalii de cotă sunt așteptați"), iar scanul îl raporta cu 2 constante
# nesursate. Contradicția era vizibilă fără să deschizi nimic — trebuia doar întrebată.
#
# Testat retroactiv: ieri confruntarea ar fi dat 9 semnale (cote_tva 21/11, d300 ×4, d394 ×3) —
# exact miezul celor 28. Azi dă 5, toate datorie reală, ținute de clichetul de mai jos.

_COTE_TVA = {"21", "19", "11", "0.21", "0.19", "0.11"}

# Clichet, nu prag: intrările sunt NUMITE, ca să nu se ascundă într-un număr.
# 21.08, după prima măsurătoare: cele două din `d300_reconciliere` au IEȘIT — dar NU prin
# unificare, cum scrisesem. Duplicarea mapării acolo e DELIBERATĂ și probată de
# `test_non_tautologie_*`: cele două căi n-au voie să împartă cod, altfel gardul de conținut
# devine tautologic. Judecasem mecanismul după formă (două constante identice) fără să-i citesc
# antetul. Ce lipsea cu adevărat era TEMEIUL lângă valori; adăugat, au trecut în clasa E.
CONFRUNTARE_BASELINE = {
    ("d406.py", "21"): "`tva_procent: Decimal = Decimal(21)` — cotă ca DEFAULT de parametru; "
                       "supraviețuiește tăcut unei schimbări de cotă (clasa #2 de pe lista de ardere).",
}


def _excluse_din_verificator():
    """Citește `_TVA_EXCLUSE` din verificator ca DATE, prin `ast` — fără import: modulul își rulează
    scanul la nivel de modul, iar un test n-are voie să pornească alt instrument ca efect secundar."""
    import ast
    import io
    import os
    rad = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src = io.open(os.path.join(rad, "verificator_conformitate.py"), encoding="utf-8").read()
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.Assign) and any(getattr(t, "id", "") == "_TVA_EXCLUSE" for t in n.targets):
            return set(ast.literal_eval(n.value))
    raise AssertionError("`_TVA_EXCLUSE` nu mai există în verificator — confruntarea a rămas fără "
                         "al doilea instrument; repar-o, nu o șterge")


def _confruntare(inv):
    excl = _excluse_din_verificator()
    return [h for h in inv if h["f"] in excl and h["cls"] == "C" and h["v"] in _COTE_TVA]


def test_cele_doua_instrumente_nu_se_contrazic(inv):
    """Miezul. Un fișier pe care verificatorul îl scutește fiindcă „aici cotele sunt așteptate", dar
    în care scanul vede o cotă NESURSATĂ, e un dezacord între două măsurători ale aceluiași lucru."""
    nou = [h for h in _confruntare(inv) if (h["f"], h["v"]) not in CONFRUNTARE_BASELINE]
    assert not nou, (
        "dezacord NOU între scan și verificator:\n"
        + "\n".join("  %s:%d `%s` — %s" % (h["f"], h["l"], h["v"], h["txt"][:60]) for h in nou)
        + "\n\nOri atașezi temeiul (obiect `Temei`, sau citarea actului lângă valoare), ori scoți "
        "fișierul de pe `_TVA_EXCLUSE` dacă nu mai e un loc unde cotele sunt așteptate.")


def test_confruntarea_nu_e_stat(inv):
    """Anti-datorie-stătută, ca la clichetul principal: ce s-a reparat iese din baseline."""
    real = {(h["f"], h["v"]) for h in _confruntare(inv)}
    stat = sorted(k for k in CONFRUNTARE_BASELINE if k not in real)
    assert not stat, ("confruntarea e mai largă decât realitatea — scoate din CONFRUNTARE_BASELINE: %s"
                      % stat)


def test_confruntarea_chiar_vede_ceva(inv):
    """Anti-vacuu: dacă lista de excluse se golește sau `inv` se rupe, confruntarea ar trece pe gol,
    raportând pace între două instrumente pe care nu le mai citește."""
    excl = _excluse_din_verificator()
    assert len(excl) >= 8 and "cote_tva.py" in excl, \
        "lista de excluse a verificatorului e implauzibilă: %s" % excl
    assert any(h["f"] in excl for h in inv), "scanul nu vede niciun fișier dintre cele excluse"


# ─────────── CALIBRARE NEGATIVĂ: ce NU vede scanul (23.08.2026) ───────────
# Cerută de Costin: *„calibrează în ambele direcții — dar mai ales negativ: dacă instrumentul vede
# mai puțin decât crede, clichetul păzește un prag fals, iar direcția aia e tăcută."*
# Cele patru calibrări de mai sus sunt POZITIVE (scanul vede ce trebuie) sau contra-direcții ale
# clasei E. Niciuna nu întreba ce rămâne AFARĂ. Măsurat, două găuri, amândouă numite de docstringul
# scanului și niciuna testată până azi:
#   (1) DOMENIUL — `FIS` e o listă de NUME: 79 din 289 de module `core/`. Patru module care
#       construiesc `Temei` erau afară; clasa C a urcat 93 → 104 când au intrat.
#   (2) BOTEZUL — un nume care se potrivește cu `NOM` trimite valoarea în B, tăcut. Probat sintetic:
#       `TIP_COTA = 21` → B, `COD_COTA = 21` → B, `CATEG_PLAFON = 300000` → B.

def _module_core():
    import glob
    import io
    import os
    rad = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core")
    for p in sorted(glob.glob(os.path.join(rad, "*.py"))):
        f = os.path.basename(p)
        if f.startswith("test_"):
            continue
        yield f, io.open(p, encoding="utf-8", errors="replace").read()


def test_domeniul_prinde_orice_modul_care_CITEAZA_legea():
    """Un modul care construiește un `Temei` e fiscal prin propria lui mărturisire. Criteriul e
    mecanic, deci se întreține singur: un modul nou intră în domeniu în ziua în care citează legea,
    fără să-și amintească cineva să-l adauge în `FIS`."""
    afara = [f for f, src in _module_core()
             if scan_constante._citeaza_legea(src) and not scan_constante.in_domeniu(f, src)]
    assert not afara, "module care citează legea, dar sunt în afara domeniului scanului: %s" % afara


def test_ANTIVACUU_largirea_chiar_a_adus_module():
    """Fără module câștigate prin criteriul nou, testul de mai sus ar trece pe zero rânduri și ar
    raporta verde despre o lume pe care n-o vede."""
    castigate = [f for f, src in _module_core()
                 if not scan_constante.FIS.match(f) and scan_constante._citeaza_legea(src)]
    assert len(castigate) >= 4, (
        "criteriul «citează legea» nu mai aduce niciun modul peste `FIS` (%s) — ori s-au redenumit, "
        "ori detectorul de `Temei` s-a rupt" % castigate)


# BOTEZUL: coliziunile NOM × NF, NUMITE. Fiecare e un cod de categorie, nu o valoare fiscală —
# de-aia rămân în B. O a opta care apare NU e presupusă bună: pică, și se citește.
# NU se schimbă regula (NF peste NOM), fiindcă asta ar muta exact aceste 7 nume în C și ar umfla
# clichetul cu 15 false pozitive. Gaura e reală, dar AZI GOALĂ; ce se schimbă e că nu mai e tăcută.
BOTEZ_BASELINE = {
    ("d201.py", "_CATEG_SALARII"): "cod de categorie de venit salarial (nomenclator ANAF)",
    ("d204.py", "_CATEG_VENIT"): "coduri de categorie de venit — nomenclator, nu cote",
    ("d204.py", "act['categ_venit']"): "comparație cu codul de categorie, nu cu o valoare",
    ("d301_operatiuni_api.py", "TIPURI_ETICHETE"): "coduri de tip de operațiune",
    ("d402.py", "_TIP_VENIT"): "cod de tip de venit (nomenclator D402)",
    ("d402.py", "_PER_VENIT"): "cod de periodicitate",
    ("d403.py", "_R_TIP_BAZA"): "cod de tip de bază (nomenclator D403)",
}


def _botez(inv):
    import re
    out = {}
    for h in inv:
        if h["cls"] != "B" or not scan_constante.NF.search(h["ctx"] or ""):
            continue
        m = re.search(r"`([^`]+)`", h["ctx"] or "")
        k = (h["f"], m.group(1) if m else h["ctx"])
        out[k] = out.get(k, 0) + 1
    return out


def test_botezul_nu_mai_inghite_tacut(inv):
    """Miezul direcției negative. Un nume care se potrivește cu `NOM` scoate valoarea din țintă —
    fals negativ, pe care nimeni nu-l VEDE. Nu se poate repara prin regulă fără să strice 15
    clasificări corecte, deci se face VIZIBIL: fiecare coliziune e numită, iar una nouă pică."""
    noi = sorted(k for k in _botez(inv) if k not in BOTEZ_BASELINE)
    assert not noi, (
        "nume care se potrivesc ȘI cu nomenclatorul ȘI cu vocabularul fiscal, nedeclarate: %r. "
        "Dacă e un cod, adaugă-l în BOTEZ_BASELINE cu ce măsoară. Dacă e o VALOARE fiscală, "
        "redenumește-o — altfel scanul n-o va vedea niciodată." % (noi,))


def test_botezul_declarat_nu_imbatraneste(inv):
    """Anti-vacuu pe exceptare, a treia oară în fișierul ăsta: o coliziune declarată care nu mai
    există e o notă despre o lume care nu mai e."""
    real = _botez(inv)
    moarte = sorted(k for k in BOTEZ_BASELINE if k not in real)
    assert not moarte, "coliziuni declarate care nu mai există — scoate-le: %s" % moarte


def test_gaura_de_botez_e_REALA_probata_sintetic():
    """Calibrarea negativă propriu-zisă: se probează pe cod construit anume, fiindcă în producție
    clasa e AZI GOALĂ. Un test care așteaptă să apară o instanță reală n-ar prinde niciodată gaura."""
    def cls(linie):
        h = scan_constante.scan("proba.py", linie + "\n")
        return h[0]["cls"] if h else None

    assert cls("COTA_TVA = 21") == "C", "scanul nu mai vede nici cazul cinstit — s-a rupt"
    assert cls("TIP_COTA = 21") == "B", (
        "botezul nu mai trimite în B — dacă regula s-a schimbat deliberat, coboară BOTEZ_BASELINE "
        "și rescrie testul; dacă nu, e o schimbare tăcută de clasificare")
    assert cls("CATEG_PLAFON = 300000") == "B"
    assert cls("PLAFON_MICRO = 300000") == "C", "plafonul cinstit a fugit din țintă"


def test_domeniul_prinde_modulul_care_POARTA_o_valoare_de_registru():
    """A patra regulă (23.08.2026): un modul care ține o cotă din registru ca default de parametru e
    fiscal, oricât de puțin ar vorbi. Calibrare în ambele direcții, pe sursă construită anume."""
    cu = "def f(x, cota=21):" + chr(10) + "    return x" + chr(10)
    fara = "def f(x, n=7):" + chr(10) + "    return x" + chr(10)
    assert scan_constante._poarta_valoare_de_registru(cu) is True
    assert scan_constante._poarta_valoare_de_registru(fara) is False
    assert scan_constante.in_domeniu("modul_oarecare.py", cu) is True
    assert scan_constante.in_domeniu("modul_oarecare.py", fara) is False


def test_ANTIVACUU_valorile_de_registru_nu_sunt_goale():
    """Dacă `COTE` nu se poate citi, regula de mai sus tace și domeniul se îngustează în tăcere."""
    v = scan_constante._valori_de_registru()
    assert len(v) >= 3, "registrul de cote pare gol pentru regula de domeniu: %r" % v
    assert 21 in v, "cota standard nu se regăsește în valorile de registru: %r" % sorted(v)[:10]


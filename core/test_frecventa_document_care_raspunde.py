# -*- coding: utf-8 -*-
"""GARD [01.09.2026, R111]: frecvența nu se citește dintr-un document care nu poate răspunde.

**CE S-A REPARAT.** Axa A a interdicției **55** clasa `STABIL` orice articol fără marcaje de
consolidare. Dar „zero marcaje în articolul N" înseamnă **două** lucruri, iar instrumentul le
confunda:

  - documentul consemnează modificări în alte părți, dar nu pentru articolul ăsta → **nemodificat**;
  - documentul nu consemnează nicio modificare, nicăieri → **nu se poate ști din el**.

A doua se citea ca prima și producea `STABIL`, adică *verificat mai rar* — direcția largă — dintr-o
sursă care nu putea răspunde. **Instanța care a scos-o la iveală**: cele patru cote de TVA. Temeiul
lor pe `Legea 141/2025 art. 291` lua `STABIL` din **actul modificator**, care reproduce textul nou al
articolului dar nu poartă istoricul lui; **același articol** în forma consolidată a Codului fiscal
arată **8 marcaje = VOLATIL**. Iar `STABIL`-ul din actul modificator îl **masca** pe cel real.

**A DOUA CAUZĂ, tot mecanică:** `art. 291` era singurul număr de articol rezolvat la Codul fiscal
**condiționat** de numărul actului care îl citează (`art == "291" and "227" in nr`), când 97, 28 și
282 se rezolvă necondiționat. Iar clauza era scrisă în **două** fișiere, sub comentariul care spunea
că mulțimea fusese mutată într-un singur loc *tocmai* ca o convenție să nu se despartă în tăcere.
S-a despărțit pe jumătatea nemutată: mulțimea era importată, **regula** era copiată.

**VOLUM, măsurat înainte și după, pe 13 puncte de orizont** *(cadență confirmată de Costin 01.09)*:

    la data        GLOBAL   PER ARTICOL   pierdute
    2026-09-01          0             0   —
    2026-10-01          0        3 → 7    —
    2027-03-01         20            20   —

Cele patru în plus sunt exact cotele de TVA. **Zero alerte pierdute la niciunul dintre cele 13
puncte** — invariantul lui Costin ține prin podea, ca la R109.
"""
import datetime
import os
import re
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)

from core import articol_in_act as A  # noqa: E402
from core import scan_citate  # noqa: E402
from core import scan_pereche_act_articol as S  # noqa: E402
from core.common import COTE, cote_neconfirmate  # noqa: E402
from core.expirare_cote import _prag_luni, _prag_pentru  # noqa: E402
from core.reverificare import categorie  # noqa: E402

ORIZONT_LUNI = 13

#: Instanțele reale pe care stă gardul. Dacă vreuna dispare din corpus, testul o spune și cere
#: mutarea pe caz sintetic (METODA §29) — nu trece în tăcere despre o lume pe care n-o mai vede.
_DOC_CARE_RASPUNDE = "anaf_surse/oug_89_2025.html"
_DOC_CARE_TACE = "anaf_surse/legea_201_2025.html"


def _plus_luni(d, n):
    an, luna = d.year + (d.month - 1 + n) // 12, (d.month - 1 + n) % 12 + 1
    ultima = [31, 29 if an % 4 == 0 and (an % 100 or an % 400 == 0) else 28,
              31, 30, 31, 30, 31, 31, 30, 31, 30, 31][luna - 1]
    return datetime.date(an, luna, min(d.day, ultima))


def _alerte(la_data, prag_pentru=None):
    return {x["nume"] for x in cote_neconfirmate(_prag_luni(), la_data=la_data,
                                                 prag_pentru=prag_pentru)}


def _temeiuri_cu_articol():
    return [(c, t) for c, t, _v in scan_citate.inventar() if getattr(t, "art", None)]


# ── MIEZUL: un document care nu consemnează nimic nu produce STABIL ────────────────────────────

def test_un_document_care_nu_inregistreaza_nimic_NU_produce_STABIL():
    """Direcția pe care se pierdea adevărul. Nu se cere `NECUNOSCUT` pe un nume de fișier — se cere
    pe **proprietatea măsurată** a documentului: zero marcaje în tot corpul lui."""
    rele = []
    for _cale, t in _temeiuri_cu_articol():
        doc = S.document_tinta(t)
        if not doc or A.inregistreaza_modificari(doc):
            continue
        c = categorie(t)
        if c["frecventa"] != "NECUNOSCUT":
            rele.append("%s (%s) → %s, dintr-un document cu ZERO marcaje"
                        % (t, os.path.basename(doc), c["frecventa"]))
    assert not rele, (
        "frecvență citită dintr-un document care nu consemnează nicio modificare:%s  %s%s"
        "«Niciun marcaj» acolo nu deosebește «nemodificat» de «nu se scrie aici»."
        % (chr(10), (chr(10) + "  ").join(rele), chr(10)))


def test_ANTI_VACUU_chiar_exista_documente_care_tac():
    """Fără asta, testul de mai sus ar fi verde despre o mulțime goală."""
    tac = {os.path.basename(S.document_tinta(t)) for _c, t in _temeiuri_cu_articol()
           if S.document_tinta(t) and not A.inregistreaza_modificari(S.document_tinta(t))}
    assert tac, ("[anti-vacuu] niciun document-tăcut între temeiuri — dacă e adevărat, e o veste "
                 "bună, dar gardul de deasupra rămâne fără obiect și trebuie mutat pe caz sintetic")


# ── DIRECȚIA INVERSĂ, și e cea care contează ───────────────────────────────────────────────────

def test_un_articol_NEMODIFICAT_dintr_un_document_care_VORBESTE_ramane_STABIL():
    """**Fără proba asta, criteriul ar fi putut înghiți tot și ar fi părut că merge.** Dacă
    `inregistreaza_modificari` ar întoarce mereu `False`, fiecare STABIL ar deveni NECUNOSCUT, iar
    testul dinainte ar trece — pe o clasificare care nu mai clasifică nimic.

    Instanța e chiar decizia scrisă în antetul lui `reverificare`: OUG 89/2025 are marcaje de
    consolidare, dar **art. III — cel care poartă valorile — niciunul**. Documentul poate răspunde;
    răspunsul lui e «nemodificat». Aia e o citire reală și nu are voie să se piardă."""
    assert A.inregistreaza_modificari(_DOC_CARE_RASPUNDE), (
        "[calibrare] %s nu mai consemnează nicio modificare — proba și-a pierdut obiectul (METODA §29)"
        % _DOC_CARE_RASPUNDE)
    stabile = [str(t) for _c, t in _temeiuri_cu_articol()
               if S.document_tinta(t) == os.path.join(_RAD, _DOC_CARE_RASPUNDE)
               and categorie(t)["frecventa"] == "STABIL"]
    assert stabile, (
        "niciun STABIL rămas pe %s — criteriul a înghițit și citirile reale, nu doar pe cele care "
        "nu se puteau face" % os.path.basename(_DOC_CARE_RASPUNDE))


def test_criteriul_deosebeste_cele_doua_documente():
    """Cele două instanțe, față în față, pe proprietatea măsurată — nu pe nume."""
    assert A.inregistreaza_modificari(_DOC_CARE_RASPUNDE) is True
    assert A.inregistreaza_modificari(_DOC_CARE_TACE) is False, (
        "[calibrare] %s a început să consemneze modificări — proba și-a pierdut obiectul"
        % _DOC_CARE_TACE)


# ── `marcaje` nu mai are precondiție nescrisă ──────────────────────────────────────────────────

def test_marcaje_gaseste_un_marcaj_taiat_de_o_linie_noua():
    """Capcana în care am căzut chiar eu, măsurând clasa: `.{0,190}?` nu trece peste linia nouă.
    Mergea doar fiindcă singurul apelant colapsa spațiile la ieșire. Caz sintetic, ca proba să nu
    depindă de așezarea unui fișier din corpus."""
    intreg = "(la 01-01-2026, articolul a fost modificat de OUG 1/2026)"
    taiat = "(la 01-01-2026, articolul\na fost modificat\nde OUG 1/2026)"
    assert len(A.marcaje(intreg)) == 1
    assert len(A.marcaje(taiat)) == 1, (
        "un marcaj tăiat de linii noi nu se mai vede — precondiția nescrisă s-a întors")


def test_ANTI_VACUU_marcaje_chiar_refuza_ce_nu_e_marcaj():
    """Direcția opusă: normalizarea nu are voie să facă tiparul lacom."""
    assert A.marcaje("text fără niciun marcaj (la fel de gol)") == []
    assert A.marcaje("") == []
    assert A.marcaje(None) == []


# ── CONVENȚIA: un singur loc, și niciun articol tratat condiționat ─────────────────────────────

def test_conventia_are_o_SINGURA_implementare():
    """Mutația pe modul propriu de eșec: dacă `_cheie` din `test_vigoare_articole_registru` ar
    reimplementa regula în loc s-o cheme, aici s-ar vedea la primul articol care se despart."""
    from core import test_vigoare_articole_registru as V
    rele = [(str(t), V._cheie(t), S.cheie_articol(t.tip, t.nr, t.an, t.art))
            for _c, t in _temeiuri_cu_articol()
            if V._cheie(t) != S.cheie_articol(t.tip, t.nr, t.an, t.art)]
    assert not rele, "convenția s-a despărțit din nou în două implementări: %s" % rele[:3]


def test_niciun_articol_nu_se_rezolva_CONDITIONAT_de_actul_care_il_citeaza():
    """Ce a produs greșeala: 97, 28 și 282 se rezolvau la CF oricine le-ar cita, iar 291 numai dacă
    actul purta numărul 227. Un articol e al Codului fiscal sau nu e — nu depinde de cine îl invocă."""
    for art in sorted(S.ART_DE_COD_FISCAL):
        for nr in (227, 141, 8, None):
            assert S.cheie_articol("Legea", nr, 2025, art) == ("CF", art), (
                "art. %s se rezolvă la CF doar pentru unele acte (nr=%s) — condiționarea s-a întors"
                % (art, nr))
    assert "291" in S.ART_DE_COD_FISCAL, "291 a ieșit din mulțime; cotele de TVA se întorc la STABIL"


def test_cele_patru_cote_de_TVA_sunt_VOLATIL():
    """Condiția de închidere a lui R111, scrisă la deschiderea ei."""
    rele = [(str(t), categorie(t)["frecventa"]) for _c, t in _temeiuri_cu_articol()
            if getattr(t, "art", None) == "291" and categorie(t)["frecventa"] != "VOLATIL"]
    assert not rele, "temeiuri pe art. 291 care nu sunt VOLATIL: %s" % rele
    nume = {n for n, intrari in COTE.items()
            for it in intrari if getattr(it[2], "art", None) == "291"}
    assert nume == {"tva_standard", "tva_redusa", "tva_redusa_9", "tva_redusa_5"}, (
        "mulțimea cotelor sprijinite pe art. 291 s-a mutat: %s" % sorted(nume))


# ── VOLUMUL: mai mult e permis, mai puțin nu ───────────────────────────────────────────────────

def test_nicio_alerta_nu_DISPARE_pe_niciun_orizont():
    """Invariantul lui Costin, reverificat după ce reparația a mișcat clasificarea."""
    azi = datetime.date.today()
    pierdute = []
    for k in range(ORIZONT_LUNI):
        d = _plus_luni(azi, k)
        a, b = _alerte(d), _alerte(d, _prag_pentru)
        if a - b:
            pierdute.append("%s: %s" % (d.isoformat(), sorted(a - b)))
    assert not pierdute, ("sub pragul per-articol au DISPĂRUT alerte:%s  %s"
                          % (chr(10), (chr(10) + "  ").join(pierdute)))


def test_volumul_dupa_reparatie_e_CEL_MASURAT():
    """Pinat cu numele, nu cu numărul: **7**, din care cele patru cote de TVA sunt câștigul lui
    R111. O mutare aici înseamnă că s-a schimbat clasificarea sau vechimea confirmărilor."""
    d = _plus_luni(datetime.date.today(), 1)
    plus = _alerte(d, _prag_pentru) - _alerte(d)
    assert plus == {"impozit_dividend", "impozit_micro", "impozit_venit",
                    "tva_standard", "tva_redusa", "tva_redusa_9", "tva_redusa_5"}, (
        "volumul în plus s-a mutat: %s. Dacă e intenționat, pinează noua mulțime." % sorted(plus))


def test_niciun_prag_MAI_LARG_decat_podeaua_nu_se_aplica():
    """Regula podelei, reverificată pe clasificarea nouă: `STABIL/CALCULAT` = 12 > 6 se ignoră."""
    randuri = cote_neconfirmate(_prag_luni(), la_data=_plus_luni(datetime.date.today(), 24),
                                prag_pentru=_prag_pentru)
    assert randuri, "[anti-vacuu] niciun rând — proba n-are pe ce lucra"
    rele = [(x["nume"], x["prag_luni"]) for x in randuri if x["prag_luni"] > _prag_luni()]
    assert not rele, "praguri mai largi decât podeaua, aplicate: %s" % rele


def test_ANTI_VACUU_reparatia_chiar_a_stramtat_ceva():
    """Dacă reparația n-ar fi schimbat nimic, toate gardurile de mai sus ar fi verzi degeaba."""
    stricte = {n for n, intrari in COTE.items()
               for it in intrari
               if (categorie(it[2])["prag_luni"] or 99) < _prag_luni()}
    assert len(stricte) >= 7, (
        "[anti-vacuu] doar %d cote au prag mai strict decât podeaua — reparația n-ar schimba nimic"
        % len(stricte))
    assert {"tva_standard", "tva_redusa", "tva_redusa_9", "tva_redusa_5"} <= stricte, (
        "cotele de TVA nu mai sunt printre cele strâmtate — chiar asta a reparat R111")


def test_ANTI_VACUU_domeniul_nu_s_a_rupt():
    assert len(_temeiuri_cu_articol()) >= 20, (
        "[anti-vacuu] doar %d temeiuri cu articol — domeniul s-a rupt și tot fișierul ăsta ar fi "
        "verde despre o mulțime goală" % len(_temeiuri_cu_articol()))
    assert re.match(r"^\d+$", str(_prag_luni())), "podeaua globală nu mai e un număr"

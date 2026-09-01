# -*- coding: utf-8 -*-
"""GARD [01.09.2026, R109]: pragul de reverificare e per articol, dar nicio cotă nu iese din pază.

Interdicția **55** a produs categoria; **R109** o leagă de raportul lunar. Legarea schimbă ce
raportează un **job viu**, deci cele două reguli ale lui Costin sunt implementate literal și gardate
aici:

  1. *„Nicio cotă nu se reconfirmă mai rar decât azi."*
  2. *„Volumul de alerte măsurat înainte și după."*

**MĂSURAT ÎNAINTE DE A LEGA**, pe orizont de 12 luni (nu într-o singură zi — o zi nu spune nimic
despre un job lunar):

    la data        GLOBAL   PER ARTICOL   în plus
    2026-09-01          0             0   —
    2026-10-01          0             3   impozit_dividend, impozit_micro, impozit_venit
    …                   0             3   (aceleași, până în februarie)
    2027-03-01         20            20   —

**CIFRA S-A MUTAT ÎN ACEEAȘI ZI, 3 → 7 (R111).** Tabelul de mai sus e măsurătoarea **de la legare**
și rămâne scris ca atare — nu e starea de acum. Cele patru în plus sunt cotele de TVA: temeiul lor
lua `STABIL` dintr-un act modificator care nu poartă istoric de consolidare, iar acel `STABIL` îl
masca pe cel real din Codul fiscal. Măsurătoarea curentă și gardurile ei stau în
`core/test_frecventa_document_care_raspunde.py`.

*Cele trei sunt exact clasa `VOLATIL/DEPUS`: cotele care s-au mișcat de două ori în trei ani și
intră în declarații.*

**O CORECȚIE A MĂSURĂTORII MELE, scrisă fiindcă e a cincea din același soi:** prima formă prezisese
**3 alerte azi**. Realitatea e **0**. Aproximasem cu aritmetică pe luni (`vechime >= prag`), iar codul
compară **date** (`verificat_la <= azi − prag`). Cu `verificat_la = 07.08` și prag de o lună, pragul
cade pe 01.08 — deci nu alertează. *Re-implementasem regula în loc s-o chem.*
"""
import datetime
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)

from core.common import COTE, cote_neconfirmate  # noqa: E402
from core.expirare_cote import _prag_luni, _prag_pentru  # noqa: E402

#: Orizontul pe care se compară cele două regimuri. Un job lunar nu se judecă într-o zi.
ORIZONT_LUNI = 13


def _plus_luni(d, n):
    an, luna = d.year + (d.month - 1 + n) // 12, (d.month - 1 + n) % 12 + 1
    ultima = [31, 29 if an % 4 == 0 and (an % 100 or an % 400 == 0) else 28,
              31, 30, 31, 30, 31, 31, 30, 31, 30, 31][luna - 1]
    return datetime.date(an, luna, min(d.day, ultima))


def _alerte(la_data, prag_pentru=None):
    return {x["nume"] for x in cote_neconfirmate(_prag_luni(), la_data=la_data,
                                                 prag_pentru=prag_pentru)}


# ── REGULA 1: nicio cotă nu se reconfirmă mai rar ──────────────────────────────────────────────

def test_nicio_alerta_nu_DISPARE_pe_niciun_orizont():
    """MIEZUL. Se compară pe **13 date**, nu pe una: o slăbire care apare abia peste patru luni e tot
    o slăbire, iar o probă într-o singură zi n-ar vedea-o. Se cere incluziune, nu egalitate — în plus
    e permis, în minus nu."""
    azi = datetime.date.today()
    pierdute = []
    for k in range(ORIZONT_LUNI):
        d = _plus_luni(azi, k)
        a, b = _alerte(d), _alerte(d, _prag_pentru)
        if a - b:
            pierdute.append("%s: %s" % (d.isoformat(), sorted(a - b)))
    assert not pierdute, (
        "sub pragul per-articol au DISPĂRUT alerte care există azi:%s  %s%s"
        "«Nicio cotă nu se reconfirmă mai rar decât azi» — o valoare care iese din pază se "
        "reconfirmă NICIODATĂ." % (chr(10), (chr(10) + "  ").join(pierdute), chr(10)))


def test_o_cota_FARA_prag_calculabil_ramane_pe_podeaua_globala():
    """Cealaltă față a regulii 1, și e cea prin care s-ar fi strecurat încălcarea: dacă `NECUNOSCUT`
    ar însemna «fără prag», valoarea n-ar mai fi verificată **niciodată**. Rămâne pe podeaua globală,
    iar rândul o SPUNE."""
    d = _plus_luni(datetime.date.today(), 24)   # orizont care le prinde pe toate
    randuri = cote_neconfirmate(_prag_luni(), la_data=d, prag_pentru=_prag_pentru)
    necunoscute = [x for x in randuri if x["prag_sursa"].startswith("global (prag necunoscut)")]
    assert necunoscute, (
        "[anti-vacuu] nicio cotă cu prag necunoscut — dacă toate au devenit calculabile, e o veste "
        "bună, dar proba de mai jos rămâne fără obiect și trebuie mutată pe caz sintetic")
    rele = [x["nume"] for x in necunoscute if x["prag_luni"] != _prag_luni()]
    assert not rele, "cote cu prag necunoscut care NU au primit podeaua globală: %s" % rele


def test_un_prag_MAI_LARG_decat_global_se_ignora_si_se_spune():
    """Direcția inversă, pe caz sintetic: dacă tabelul ar da vreodată un prag mai larg decât podeaua
    (azi nu dă — `INFORMATIV` e clasă vidă), el **nu** se aplică. O slăbire cere o decizie scrisă, nu
    un tabel."""
    d = datetime.date.today()
    randuri = cote_neconfirmate(_prag_luni(), la_data=_plus_luni(d, 24),
                                prag_pentru=lambda _n, _t: 99)
    assert randuri, "[anti-vacuu] niciun rând — proba n-are pe ce lucra"
    rele = [(x["nume"], x["prag_luni"]) for x in randuri if x["prag_luni"] != _prag_luni()]
    assert not rele, "un prag mai larg decât podeaua a fost aplicat: %s" % rele
    fara_motiv = [x["nume"] for x in randuri if "ignorat" not in x["prag_sursa"]]
    assert not fara_motiv, (
        "pragul mai larg a fost ignorat în tăcere, fără să se scrie pe rând: %s" % fara_motiv[:5])


# ── COMPATIBILITATE: fără argument, comportamentul e cel dinainte ──────────────────────────────

def test_FARA_prag_pentru_comportamentul_e_identic():
    """Contractul vechi nu se rupe: `cote_neconfirmate(luni)` fără al treilea argument face exact ce
    făcea. Altfel, orice alt apelant ar fi primit tăcut alt răspuns."""
    for k in (0, 6, 24):
        d = _plus_luni(datetime.date.today(), k)
        randuri = cote_neconfirmate(_prag_luni(), la_data=d)
        assert all(x["prag_sursa"] == "global" for x in randuri)
        assert all(x["prag_luni"] == _prag_luni() for x in randuri)


# ── ANTI-VACUU: legarea chiar face ceva ────────────────────────────────────────────────────────

def test_ANTI_VACUU_legarea_chiar_stramteaza_ceva():
    """Dacă `_prag_pentru` ar întoarce `None` pentru tot, totul ar cădea pe podea, iar gardurile de
    mai sus ar trece pe o legare care nu leagă nimic."""
    praguri = {}
    for nume in COTE:
        t = sorted(COTE[nume], key=lambda r: r[0], reverse=True)[0][2]
        praguri[nume] = _prag_pentru(nume, t)
    calculate = {n: p for n, p in praguri.items() if p is not None}
    assert len(calculate) >= 10, (
        "[anti-vacuu] doar %d cote au prag calculat — legarea n-ar schimba nimic" % len(calculate))
    mai_strict = {n: p for n, p in calculate.items() if p < _prag_luni()}
    assert mai_strict, (
        "[anti-vacuu] nicio cotă nu primește un prag mai strict decât podeaua: legarea ar fi un "
        "no-op costisitor. Praguri calculate: %s" % sorted(set(calculate.values())))


def test_volumul_in_plus_e_CEL_MASURAT():
    """Pinat: peste o lună, exact **șapte** cote intră în alertă, toate din clasa VOLATIL/DEPUS.
    O mutare aici înseamnă că s-a schimbat clasificarea sau vechimea confirmărilor — amândouă merită
    văzute, niciuna nu trebuie să treacă tăcut.

    **A FOST 3, ȘI PINUL A CĂZUT CORECT** când R111 a reparat axa în aceeași zi. Cele patru cote de
    TVA nu sunt volum nou: erau `VOLATIL` și înainte, în Codul fiscal, dar un `STABIL` venit din
    actul modificator le masca. Cadența lunară pentru ele e confirmată de Costin (01.09.2026)."""
    d = _plus_luni(datetime.date.today(), 1)
    plus = _alerte(d, _prag_pentru) - _alerte(d)
    assert plus == {"impozit_dividend", "impozit_micro", "impozit_venit",
                    "tva_standard", "tva_redusa", "tva_redusa_9", "tva_redusa_5"}, (
        "volumul în plus s-a mutat: %s. Dacă e intenționat (o confirmare reînnoită, o clasificare "
        "schimbată), pinează noua mulțime." % sorted(plus))

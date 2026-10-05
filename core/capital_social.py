# -*- coding: utf-8 -*-
"""core/capital_social.py — capitalul social pe factură (lot 19, defectul 12, 03.10.2026). PUR, fără DB.

Legea 31/1990 art.74 alin.(3): „În documentele prevăzute la alin. (1), dacă acestea provin de la o societate cu
răspundere limitată, se va menționa și capitalul social, iar dacă ele provin de la o societate pe acțiuni sau în
comandită pe acțiuni, se vor menționa atât capitalul social subscris, cât și cel vărsat.” Alin.(1) numește „orice
factură, ofertă, comandă, tarif, prospect și alte documente întrebuințate în comerț”.

Decizia lui Costin (03.10.2026): câmpuri pe profilul firmei; factura unui SRL/SA/SCA fără capitalul completat e
REFUZATĂ la emitere, iar refuzul păstrează factura tastată, spune ce lipsește în termenii contabilului, trimite la
Date firmă și citează art.74 alin.(3). PFA/II/IF nu intră sub regulă.

Forma juridică e câmp propriu: `tip_firma` are doar „srl” (umbrelă pentru orice persoană juridică în partidă dublă:
SRL, SA, ONG, SNC...) și „pfa”. Fără formă, regula nu se poate aplica corect — un ONG sau un SNC n-au obligația, un SA
are două cifre de menționat. Forma necompletată la o persoană juridică = refuz cu cererea formei (nu se ghicește).

[comanda Costin 05.10.2026 pct.2] „Forma juridică se precompletează din ANAF / denumire unde e neechivocă.” — `forma_propusa`:
din câmpul `forma_juridica` al ANAF (numai valorile citite pe un răspuns REAL, 05.10.2026) sau din sufixul denumirii, numai
când toate sursele indică ACEEAȘI formă. O propunere, nu o decizie: contabilul o confirmă în Date firmă; ce nu e neechivoc
rămâne necompletat (tot nu se ghicește).
"""
import re
from decimal import Decimal, InvalidOperation

TEMEI = ("Legea 31/1990 art.74 alin.(3)", "anaf_surse/legea_31_1990_societatile.txt",
         "În documentele prevăzute la alin. (1) , dacă acestea provin de la o societate cu răspundere limitată, se va "
         "menționa și capitalul social, iar dacă ele provin de la o societate pe acțiuni sau în comandită pe acțiuni, se "
         "vor menționa atât capitalul social subscris, cât și cel vărsat.")

#: forma juridică -> (eticheta din ecran, ce cere art.74 alin.(3): None | "social" | "subscris_varsat")
FORME = {
    "SRL": ("Societate cu răspundere limitată (SRL)", "social"),
    "SA": ("Societate pe acțiuni (SA)", "subscris_varsat"),
    "SCA": ("Societate în comandită pe acțiuni (SCA)", "subscris_varsat"),
    "SNC": ("Societate în nume colectiv (SNC)", None),
    "SCS": ("Societate în comandită simplă (SCS)", None),
    "ALTA": ("Altă entitate (ONG, cooperativă, regie etc.)", None),
}
COD_REFUZ = "CAPITAL_SOCIAL_LIPSA"


def _suma(v):
    if v is None or str(v).strip() == "":
        return None
    try:
        d = Decimal(str(v).replace(" ", "").replace(",", "."))
    except InvalidOperation:
        return None
    return d if d > 0 else None


# Valori `date_generale.forma_juridica` din răspunsul REAL ANAF PlatitorTvaRest v9 (05.10.2026, CUI 40410000 și 14399840; câmpul e
# documentat în doc_WS_V9.txt). Alte valori (SNC, SCS, SCA, ONG…) n-au fost văzute pe un răspuns real -> nu se mapează.
_FORMA_ANAF = {"SOCIETATE COMERCIALA CU RASPUNDERE LIMITATA": "SRL", "SOCIETATE COMERCIALA PE ACTIUNI": "SA"}
_SUFIXE = (("SRL", r"S\.?\s?R\.?\s?L\.?(?:\s?-\s?D\.?)?"), ("SA", r"S\.?\s?A\.?"), ("SNC", r"S\.?\s?N\.?\s?C\.?"),
           ("SCS", r"S\.?\s?C\.?\s?S\.?"), ("SCA", r"S\.?\s?C\.?\s?A\.?"))


def _fara_diacritice(t):
    return (t or "").upper().translate(str.maketrans("ĂÂÎȘŞȚŢ", "AAISSTT")).strip()


def forma_din_denumire(denumire):
    """Forma din sufixul denumirii („… SRL”, „… S.R.L.”, „… SRL-D”, „… S.A.”), sau None."""
    t = _fara_diacritice(denumire)
    for forma, rx in _SUFIXE:
        if re.search(r"(?:^|[\s,.])(?:%s)\s*$" % rx, t):
            return forma
    return None


def forma_propusa(forma_anaf=None, *denumiri):
    """(forma, sursa) când TOATE sursele disponibile spun același lucru; (None, None) altfel."""
    gasite = {}
    if forma_anaf:
        f = _FORMA_ANAF.get(re.sub(r"\s+", " ", _fara_diacritice(forma_anaf)))
        if f:
            gasite.setdefault(f, "ANAF")
    for d in denumiri:
        f = forma_din_denumire(d)
        if f:
            gasite.setdefault(f, "denumire")
    if len(gasite) == 1:
        (f, sursa), = gasite.items()
        return f, sursa
    return None, None


def lipsa(profil):
    """[ce lipsește, în termenii contabilului] pentru ca factura să poată fi emisă; [] = nimic. PFA/II/IF -> []."""
    if profil.get("tip_firma") == "pfa":   # coloana e NOT NULL (implicit „srl”); fără ea: societate -> se cere forma, nu se scutește
        return []
    forma = profil.get("forma_juridica")
    if not forma:
        return ["forma juridică a firmei (SRL, SA etc.)"]
    cere = FORME.get(forma, (None, None))[1]
    if cere == "social" and _suma(profil.get("capital_subscris")) is None:
        return ["capitalul social"]
    if cere == "subscris_varsat":
        out = []
        if _suma(profil.get("capital_subscris")) is None:
            out.append("capitalul social subscris")
        if _suma(profil.get("capital_varsat")) is None:
            out.append("capitalul social vărsat")
        return out
    return []


def mesaj_la_deschidere(lipsuri, forma_propusa=None, sursa=None):
    """[comanda Costin 05.10.2026 pct.2] Ce se spune la DESCHIDEREA emiterii, înainte ca omul să completeze ceva: ce lipsește din
    Date firmă și de ce blochează emiterea; cu forma propusă, dacă se poate propune neechivoc."""
    if not lipsuri:
        return None
    ce = ", ".join(lipsuri)
    temei = "Legea 31/1990 art. 74 alin. (3): pe factura unei societăți se menționează capitalul social"
    prop = ""
    if forma_propusa:
        prop = " Forma propusă: %s (din %s) — confirm-o în Date firmă." % (forma_propusa, "ANAF" if sursa == "ANAF" else "denumirea firmei")
    return ("Înainte de a emite: în Date firmă lipsește %s, iar fără ea factura nu se poate emite (%s).%s "
            "Poți completa factura acum — ce scrii rămâne pe ecran cât completezi Date firmă." % (ce, temei, prop))


def mesaj_refuz(lipsuri):
    if lipsuri and lipsuri[0].startswith("forma juridică"):
        return ("Factura nu s-a emis: în Date firmă lipsește forma juridică a firmei — de ea depinde ce capital social "
                "trebuie trecut pe factură (Legea 31/1990 art. 74 alin. (3): la SRL capitalul social, la SA și SCA "
                "capitalul subscris și cel vărsat). Completează forma și capitalul în Date firmă și apasă din nou "
                "«Emite» — factura rămâne așa cum ai scris-o.")
    return ("Factura nu s-a emis: în Date firmă lipsește %s, pe care legea cere să-l treci pe factură (Legea 31/1990 "
            "art. 74 alin. (3)). Completează-l în Date firmă și apasă din nou «Emite» — factura rămâne așa cum ai "
            "scris-o." % " și ".join(lipsuri))


def refuz(lipsuri):
    """Excepția refuzului de emitere, cu motivul ca DATĂ (cod + temei + ce lipsește) — construită AICI, ca modulul de
    facturare să n-aibă nevoie de numele temeiului (R151: un nume TEMEI mută tot modulul în datoria refuzurilor)."""
    e = ValueError(mesaj_refuz(lipsuri))
    e.cod, e.temei, e.lipsa = COD_REFUZ, TEMEI[0], list(lipsuri)
    return e


def detaliu(e):
    """Corpul refuzului structurat (HTTP 422) ca AFIRMAȚIE TIPATĂ (`neconformitate`: profilul nu satisface art.74
    alin.(3)); ecranul de emitere citește `cod`, `mesaj`, `lipsa`, `ecran` și deschide caseta spre Date firmă."""
    from core import afirmatii as _af
    return _af.afirmatie("neconformitate", "factura", str(e), unde="Date firmă", regula=e.temei,
                         cod=e.cod, mesaj=str(e), temei=e.temei, lipsa=e.lipsa, ecran="date_firma")


def detaliu_metoda_stoc(e):
    """[06.10.2026 §6.3] Același corp de refuz spre Date firmă, pentru metoda de stoc (`core.metoda_stoc`): ecranul de emitere
    păstrează factura și oferă „Deschide Date firmă”, ca la capital."""
    from core import afirmatii as _af
    return _af.afirmatie("neconformitate", "factura", str(e), unde="Date firmă", regula="metoda de stoc (comanda Costin 06.10.2026)",
                         cod=e.cod, mesaj=str(e), ecran="date_firma")


def _lei(d):
    s = "{:,.2f}".format(d).replace(",", "X").replace(".", ",").replace("X", ".")
    return s + " lei"


def text_factura(profil):
    """Rândul de pe factură, sau None când forma nu cere nimic (ori PFA). Presupune `lipsa(profil) == []`."""
    if profil.get("tip_firma") == "pfa":   # coloana e NOT NULL (implicit „srl”); fără ea: societate -> se cere forma, nu se scutește
        return None
    cere = FORME.get(profil.get("forma_juridica") or "", (None, None))[1]
    if cere == "social":
        return "Capital social: " + _lei(_suma(profil.get("capital_subscris")))
    if cere == "subscris_varsat":
        return "Capital social subscris: %s, vărsat: %s" % (_lei(_suma(profil.get("capital_subscris"))),
                                                          _lei(_suma(profil.get("capital_varsat"))))
    return None


def valideaza(date):
    """Erori [(câmp, mesaj)] la salvarea din Date firmă; date = valorile trimise (doar cheile prezente)."""
    er = []
    forma = (date.get("forma_juridica") or "").strip().upper() if "forma_juridica" in date else None
    if forma and forma not in FORME:
        er.append(("forma_juridica", "Forma juridică %r nu e în listă." % forma))
    for k, et in (("capital_subscris", "Capitalul social"), ("capital_varsat", "Capitalul vărsat")):
        v = date.get(k)
        if v not in (None, "") and _suma(v) is None:
            er.append((k, "%s trebuie să fie o sumă mai mare decât zero, în lei." % et))
    s, v = _suma(date.get("capital_subscris")), _suma(date.get("capital_varsat"))
    if s is not None and v is not None and v > s:
        er.append(("capital_varsat", "Capitalul vărsat nu poate depăși capitalul subscris."))
    return er

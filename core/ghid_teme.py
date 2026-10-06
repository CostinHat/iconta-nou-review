# -*- coding: utf-8 -*-
"""core/ghid_teme.py — temele ghidurilor publice: cuprinsul /ghid, paginile de temă și ghidurile înrudite.

Comanda Costin 06.10.2026, partea 2: „6. Pagina /ghid are 2,3 MB și 6.559 de linkuri pe o singură pagină. Se împarte pe teme
(salarii, TVA, declarații etc.), fiecare temă cu pagina ei; /ghid rămâne cuprinsul temelor. 7. Ghidurile au un singur link
intern (/ghid). Fiecare ghid primește linkuri spre ghidurile înrudite și spre pagina temei lui.”

SURSA UNICĂ a temelor (`TEME`: cheie, slug, titlu, descriere, în ordinea cuprinsului).

Încadrarea unui ghid, în ordine:
  1. categoria lui din registrul titlurilor (`index_titluri_ghid.csv`, coloana `categorie`, pe `slug_publicat`) — 5.652 de ghiduri,
     în afară de categoria „altele”, care trece la pasul 2;
  2. altfel, REGULA de mai jos pe cuvintele din slug și titlu (prima temă care se potrivește) — ghidurile publicate fără rând în
     registru;
  3. altfel, „Alte teme”.
E o GRUPARE DE NAVIGARE, nu o încadrare fiscală: nu decide nimic despre conținut, doar unde se listează pagina.

Ghidurile înrudite: aceeași temă, ordonate după numărul de cuvinte comune din titlu (fără cuvinte de legătură), apoi după slug —
determinist, fără nicio sursă externă.
"""
import re
import unicodedata

from core.cache_declarat import Declaratie as _Dec

#: indexul pe teme al ghidurilor publicate: {"cheie", "pe_slug", "pe_tema"} (vezi `index`)
_CACHE = {"cheie": None}
_CACHE_DECLARATIE = _Dec(
    rol="indexul pe teme al celor ~6.500 de ghiduri publicate (tema fiecăruia, cuvintele titlului), ca /ghid, paginile de "
        "temă și „Ghiduri înrudite” să nu recitească și să nu reîncadreze toate fișierele la fiecare cerere",
    sursa="fișierele `ghid/*.md` (versionate) și registrul `index_titluri_ghid.csv` (versionat); aplicația nu le scrie",
    motiv="citirea a ~6.500 de fișiere + încadrarea lor pe calea unei cereri publice",
    invalidare="la schimbarea cheii: mtime-ul directorului `ghid/` (adăugare/ștergere/înlocuire) și mtime-ul registrului; "
               "plus repornirea procesului, pe care `post-commit` o face necondiționat la orice commit",
    dovada="core/test_cache_declarat.py::test_ghid_teme_se_reconstruieste_identic",
)

#: (cheie din registru, slug-ul paginii de temă, titlul, descrierea) — ordinea cuprinsului
TEME = (
    ("tva", "tva", "TVA", "Cote, exigibilitate, deduceri, D300 și D394, taxare inversă, regimuri speciale."),
    ("salarizare", "salarii", "Salarii și contribuții", "Salarii, CAS, CASS, impozit, D112, concedii, contracte de muncă."),
    ("profit", "impozit-pe-profit", "Impozit pe profit", "Cheltuieli deductibile, D101, provizioane, ajustări, pierderi fiscale."),
    ("micro", "microintreprinderi", "Microîntreprinderi", "Condițiile regimului micro, impozitul pe venit, D100, trecerea la profit."),
    ("declaratii_speciale", "declaratii", "Declarații", "Termene și completarea declarațiilor fiscale, rectificative, declarații speciale."),
    ("mijloace_fixe", "mijloace-fixe", "Mijloace fixe și amortizare", "Încadrare, durate, metode de amortizare, reevaluare, casare."),
    ("stocuri", "stocuri", "Stocuri și gestiune", "NIR, adaos, descărcarea gestiunii, inventar, perisabilități."),
    ("casierie", "casa-si-banca", "Casă și bancă", "Registrul de casă, plafoane de numerar, chitanțe, extrase și plăți."),
    ("ic_ue", "operatiuni-ue", "Operațiuni intracomunitare și import-export", "Livrări și achiziții UE, VIES, D390, Intrastat, vamă."),
    ("spv", "spv-e-factura", "SPV, e-Factura și e-Transport", "Spațiul Privat Virtual, e-Factura, e-Transport, SAF-T, RO e-TVA."),
    ("pfa", "pfa", "PFA și persoane fizice", "PFA, II, profesii liberale, D212, venituri din chirii și investiții."),
    ("infiintare", "infiintare-si-asociati", "Înființare, asociați și dividende",
     "Înființarea firmei, capital social, asociați, dividende, suspendare, lichidare."),
    ("control_fiscal", "control-fiscal", "Control fiscal și relația cu ANAF",
     "Inspecții, contestații, executare silită, eșalonare, amenzi și prescripție."),
    ("greseli", "greseli-si-corectii", "Greșeli și corecții", "Erori frecvente în contabilitate și declarații și cum se corectează."),
    ("industrii", "domenii-de-activitate", "Domenii de activitate", "Reguli specifice pe domenii: HoReCa, construcții, agricultură, ONG-uri."),
    ("situatii_financiare", "bilant-si-situatii-financiare", "Bilanț și situații financiare",
     "Bilanțul, situațiile financiare anuale și interimare, închiderea exercițiului, corectarea erorilor."),
    ("taxe_locale", "impozite-si-taxe-locale", "Impozite și taxe locale",
     "Impozitul pe clădiri, terenuri și mijloace de transport, taxe de urbanism și alte taxe locale."),
    ("contabilitate", "inregistrari-contabile", "Înregistrări contabile",
     "Cum se contabilizează operațiunile curente: conturi, note contabile, documente justificative."),
    ("altele", "alte-teme", "Alte teme", "Subiecte care nu intră în temele de mai sus."),
)
CHEI = tuple(t[0] for t in TEME)
DUPA_CHEIE = {t[0]: t for t in TEME}
DUPA_SLUG = {t[1]: t for t in TEME}

#: regula pentru ghidurile fără categorie în registru: (cheie, cuvinte/rădăcini în slug sau titlu normalizat), în ordine
REGULA = (
    ("greseli", ("greseal", "greseli", "eroare", "erori", "gresit", "rectificativ")),
    ("situatii_financiare", ("bilant", "situatii financiare", "situatiile financiare", "inchiderea exercitiului",
                             "inchiderea anului", "1174", "raportari contabile")),
    ("taxe_locale", ("taxe locale", "impozitul pe cladiri", "impozit pe cladiri", "impozit cladire", "impozitul pe teren",
                     "certificatul de urbanism", "autorizatia de construire", "taxa pe teren", "primarie")),
    ("spv", ("spv", "efactura", "e factura", "factura electronica", "facturi electronice", "etransport", "e transport", "saf t", "saft", "d406", "ro e tva", "etva")),
    ("ic_ue", ("intracomunitar", "extracomunitar", "vies", "intrastat", "import", "export", "d390", " ue ", " din ue", "vama")),
    ("tva", ("tva", "taxare invers", "d300", "d394", "marja")),
    ("salarizare", ("salar", "angajat", "concediu", "munca", "d112", "cass", " cas ", "pontaj", "demisi", "concedi", "preaviz",
                    "diurn", "tichet", "reges", "revisal", "somaj")),
    ("mijloace_fixe", ("mijloc", "amortiz", "imobiliz", "autoturism", "casare", "reevaluare")),
    ("stocuri", ("stoc", "marfa", "marfuri", "gestiun", "nir", "inventar", "adaos", "depozit", "ambalaj", "sgr")),
    ("micro", ("micro", "d100")),
    ("profit", ("profit", "d101", "deductibil", "provizion", "ajustari", "depreciere", "grup fiscal")),
    ("pfa", ("pfa", "persoana fizica", "d212", "profesii", "chirie", "chirii", "cedare")),
    ("infiintare", ("infiint", "asociat", "parti sociale", "dividend", "capital social", "lichidare", "dizolv", "radier",
                    "inchidere srl", "suspendar")),
    ("casierie", ("casa", "casier", "numerar", "banca", "chitant", "cash", "plata", "5311", "card", "dispozitia de")),
    ("control_fiscal", ("control", "inspect", "contestat", "executare", "sanctiun", "amend", "penalitat", "prescript", "esalon",
                        "anaf", "somati", "dobanz", "notificar", "proces verbal", "fisa sintetica", "fisa anaf")),
    ("declaratii_speciale", ("declarati", "termen", "depun", "d10", "d20", "d70", "d30")),
    ("industrii", ("horeca", "constructii", "agricol", "agricult", "transport", "asociatii de proprietari", "ong", "fundati",
                   "cabinet medical", "avocat", "notar", "santier", "bucatarie", "restaurant", "magazin online", "ecommerce")),
    ("contabilitate", ("contabiliz", "contul ", "inregistr", "nota contabil", "document justificativ", "factur", "retur",
                       "avans", "cheltuial", "venit", "sold")),
)

_LEGATURA = frozenset("care este cum cand unde ceea pentru prin dupa intre catre fara peste sunt este poate trebuie sau din ale "
                      "unei unui unor acest aceasta acesta atunci daca firma firmei firmelor".split())


def norm(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode().lower()
    return " " + re.sub(r"[^a-z0-9]+", " ", t).strip() + " "


def incadreaza(slug, titlu, categorie_registru=None):
    """Cheia temei unui ghid (vezi ordinea din docstringul modulului)."""
    # „altele” din registru NU e o încadrare: e lipsa ei — cade pe regulă (măsurat 06.10.2026: 1.575 de ghiduri în „Alte teme”,
    # pagina temei 558 KB, adică exact lista plată pe care împărțirea o desființa)
    if categorie_registru in DUPA_CHEIE and categorie_registru != "altele":
        return categorie_registru
    text = norm(slug.replace("-", " ") + " " + (titlu or ""))
    for cheie, cuvinte in REGULA:
        if any(c in text for c in cuvinte):
            return cheie
    return "altele"


def cuvinte(titlu):
    return frozenset(w for w in norm(titlu).split() if len(w) >= 4 and w not in _LEGATURA)


def indexeaza(ghiduri, categorii_registru):
    """`ghiduri` = [{slug, titlu, descriere, ...}] (sursa: lista paginilor publicate). Întoarce {slug: {..., tema, cuvinte}} și
    {tema: [slug, ...]} (ordonat după titlu)."""
    pe_slug, pe_tema = {}, {k: [] for k in CHEI}
    for g in ghiduri:
        t = incadreaza(g["slug"], g.get("titlu"), categorii_registru.get(g["slug"]))
        pe_slug[g["slug"]] = dict(g, tema=t, cuvinte=cuvinte(g.get("titlu")))
        pe_tema[t].append(g["slug"])
    for t in pe_tema:
        pe_tema[t].sort(key=lambda s: norm(pe_slug[s].get("titlu") or s))
    return pe_slug, pe_tema


def inrudite(slug, pe_slug, pe_tema, n=6):
    """Cele mai apropiate `n` ghiduri din aceeași temă (cuvinte comune în titlu, apoi slug). Fără ghidul însuși."""
    g = pe_slug.get(slug)
    if not g:
        return []
    cand = []
    for s in pe_tema.get(g["tema"], []):
        if s == slug:
            continue
        comune = len(g["cuvinte"] & pe_slug[s]["cuvinte"])
        if comune:
            cand.append((-comune, s))
    cand.sort()
    return [s for _c, s in cand[:n]]


def index(cheie, ghiduri, categorii_registru):
    """`indexeaza` ținut în `_CACHE` cât timp `cheie` (starea surselor) nu se schimbă. `ghiduri` și `categorii_registru` sunt
    funcții fără argumente — se cheamă numai la reconstrucție."""
    if _CACHE.get("cheie") != cheie or "pe_slug" not in _CACHE:
        _CACHE["pe_slug"], _CACHE["pe_tema"] = indexeaza(ghiduri(), categorii_registru())
        _CACHE["cheie"] = cheie
    return _CACHE["pe_slug"], _CACHE["pe_tema"]

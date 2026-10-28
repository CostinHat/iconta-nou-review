"""
core/declaratii_api.py — dispatch pentru TOATE declarațiile pe care le produce aplicația.
Registrul DECLARATII (mai jos) = SURSA UNICĂ a tipurilor produse (numărul lor îl dă dicționarul; formularele înlocuite de Declarația unică stau în FORMULARE_INLOCUITE), fiecare cu
periodicitate + adaptor către core/<tip>.py::genereaza(). O singură rută în main.py cheamă aici;
diferențele de semnătură genereaza() stau în ADAPTOARE, izolate, ca ruta să fie uniformă.
Cele 9 periodice GENERICE (tipuri() = DECLARATII − _DOAR_API: d100 d101 d112 d205 d300 d301
d390 d394 d406) apar în selectorul per-firmă; restul (41) sunt _DOAR_API (parametri manuali /
fără ecran dedicat, stare AMÂNAT în FUNCTIONALITATI.csv). Coerența cod↔CSV↔CHEIE_DUK↔generator
e gardată de core/test_registru_functionalitati.py.

Periodicitate — cele 9 generice (din realitatea declarațiilor, nu forțată uniform):
  lunar      : d112, d300, d301, d390, d394, d406
  trimestrial: d100
  anual      : d101, d205

Parametri speciali (în body, opționali):
  manual     : d300, d390, d394  (rânduri TVA introduse de contabil)
  cota       : d100
  date_extra, ca_an_precedent_eur : d101

CALCUL+DB stau în module (au pull+genereaza). Aici doar: validare cerere (pură)
+ alegere adaptor. Se dovedește pe server: apelul real genereaza pe schema tenant.
"""
from __future__ import annotations

from core import (d100, d101, d104, d107, d110, d307, d112, d177, d205, d207, d230, d300, d301, d311, d390, d394, d406, d710,
                  d120, d204, d208, d216, d393, d395, d397,
                  d106, d108, d114, d130, d318, d603,
                  d119, d169n, d213, d214, d401, d402,
                  d101g, d169, d398, d399, d403, d407,
                  d212)
from core.common import Perioada
from core import perioada_fiscala_tva as _pft

REGULI = "2026.1"
MODUL = "declaratii_api"


# ============================================================
#  ADAPTOARE — un loc unde se absoarbe diferența de semnătură.
#  Fiecare primește (conn, schema, body) și cheamă genereaza corect.
# ============================================================
def _d100(conn, schema, b):
    return d100.genereaza(conn, schema, Perioada(b["an"], trim=b["trim"]),
                          {"cota": b["cota"]} if b.get("cota") is not None else None)

def _d101(conn, schema, b):
    # d101.genereaza() a fost rescris 16.07.2026 pe ANAF structura D101 VERSIUNE NECUNOSCUTA
    # individual (nu D101G grup) - semnatura noua: (conn, schema, an, manual=None).
    # manual = suprascrieri optionale (venituri_totale, cheltuieli_totale etc.)
    manual = dict(b.get("date_extra") or {})
    if b.get("ca_an_precedent_eur"):
        manual.setdefault("ca_an_precedent_eur", b["ca_an_precedent_eur"])
    return d101.genereaza(conn, schema, Perioada(b["an"]), manual or None)

def _d112(conn, schema, b):
    return d112.genereaza(conn, schema, Perioada(an=b["an"], luna=b["luna"]))

def _d205(conn, schema, b):
    # [lotul 10, decizia Costin B: „Da, cu completare manuală”] beneficiarii scriși de contabil (firma preluată: dividendele plătite
    # înainte de preluare n-au notele lor) — calea `manual["beneficiari"]` a generatorului, până acum nelegată
    return d205.genereaza(conn, schema, Perioada(b["an"]), b.get("manual"))

def _d300(conn, schema, b):
    return d300.genereaza(conn, schema, Perioada(b["an"], luna=b["luna"]), b.get("manual"))

def _d301(conn, schema, b):
    return d301.genereaza(conn, schema, Perioada(b["an"], luna=b["luna"]))

def _d390(conn, schema, b):
    return d390.genereaza(conn, schema, b["an"], b["luna"], b.get("manual"))

def _d394(conn, schema, b):
    return d394.genereaza(conn, schema, Perioada(b["an"], luna=b["luna"]), b.get("manual"))

def _d406(conn, schema, b):
    return d406.genereaza(conn, schema, b["an"], b["luna"])

def _d710(conn, schema, b):
    # D710 = rectificativa a D100 (corectie obligatii). `obligatii` = corectiile aduse
    # de contabil (ce a declarat gresit vs corect), nu se recalculeaza automat.
    return d710.genereaza(conn, schema, Perioada(b["an"], trim=b["trim"]), {"obligatii": b["obligatii"]})


def _s1005(conn, schema, b):
    # [decizia Costin 07.10.2026, C11] „Bilanțul trece prin coadă: pregătit → validat → depus, cu aceleași drepturi ca la
    # celelalte declarații.” Generatorul e cel al ecranului Bilanț (`bilant_api`), neschimbat; aici doar intră în dispecer, deci în
    # coadă (poarta validatorului, patru ochi, depunerea, persistarea). Avertismentele lui merg ca la orice declarație.
    from core import bilant_api
    return bilant_api.genereaza(conn, schema, b["an"])


def _s1003(conn, schema, b):
    from core import bilant_api
    return bilant_api.genereaza_s1003(conn, schema, b["an"])


# tip -> (periodicitate, adaptor). Adăugarea unei declarații = o linie aici.
def _d177(conn, schema, b):
    # D177 e MANUALA (redirectionare impozit profit -> ONG) - beneficiari + sume din corp cerere.
    return d177.genereaza(conn, schema, Perioada(b["an"], luna=b.get("luna") or 6), b.get("manual") or {})


def _d104(conn, schema, b):
    # D104 e MANUALA (distribuire venituri/cheltuieli intre asociati - asociere fara PJ).
    # Trimestrial cumulat + definitivare (trim 4 -> luna 12). manual: profit_pierd + asociati[] (+ asociere).
    return d104.genereaza(conn, schema, Perioada(b["an"], trim=b["trim"]), b.get("manual") or {})


def _d107(conn, schema, b):
    # D107 e MANUALA (informativa beneficiari sponsorizari/mecenat/burse) - lista de beneficiari din corp cerere.
    return d107.genereaza(conn, schema, Perioada(b["an"]), b.get("manual") or {})


def _d207(conn, schema, b):
    # D207 e MANUALA (informativa impozit retinut nerezidenti) - lista de beneficiari din corp cerere.
    return d207.genereaza(conn, schema, Perioada(b["an"], luna=b.get("luna") or 12), b.get("manual") or {})


def _d110(conn, schema, b):
    # D110 e MANUALA (regularizare/restituire impozit pe venit retinut la sursa). Lunara (luna+an).
    return d110.genereaza(conn, schema, Perioada(b["an"], luna=b["luna"]), b.get("manual") or {})





def _d230(conn, schema, b):
    # D230 e MANUALA integral (redirectionare pana la 3,5% din impozit catre ONG) - fara pull automat.
    # ANUALA (an = anul venitului); luna de raportare = 12 (structura, fix).
    return d230.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d307(conn, schema, b):
    # D307 e MANUALA (ajustare/corectie/regularizare TVA). Lunara (luna+an). operatiuni tip A/L/C.
    return d307.genereaza(conn, schema, Perioada(b["an"], luna=b["luna"]), b.get("manual") or {})


def _d311(conn, schema, b):
    # D311 e MANUALA integral (TVA in situatii speciale, dupa anularea codului de TVA) -
    # fara pull automat; `manual` = bazele/TVA pe situatii + Data_A + d_anul1/d_anul2.
    return d311.genereaza(conn, schema, Perioada(b["an"], luna=b["luna"]), b.get("manual") or {})


def _d393(conn, schema, b):   # informativa bilete transport international (anuala)
    return d393.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d395(conn, schema, b):   # informativa trimiteri postale contra ramburs (lunara)
    return d395.genereaza(conn, schema, Perioada(b["an"], luna=int(b["luna"])), b.get("manual") or {})


def _d397(conn, schema, b):   # informativa transport alternativ (lunara)
    return d397.genereaza(conn, schema, Perioada(b["an"], luna=int(b["luna"])), b.get("manual") or {})




def _d204(conn, schema, b):   # venit asocieri fara personalitate juridica (anuala)
    return d204.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d208(conn, schema, b):   # transfer proprietati imobiliare - notari (LUNARA, CF art.113)
    # [Lot 19 defect 8, 03.10.2026] Era „semestriala” cu `luna or 12`: ecranul nu trimitea luna, deci orice D208
    # iesea pe decembrie. CF art.113 (forma din 01.01.2024, OUG 115/2023): notarii depun „lunar, până la data de
    # 25 inclusiv a lunii următoare celei în care a avut loc autentificarea”. Luna o cere valideaza_cerere.
    return d208.genereaza(conn, schema, Perioada(b["an"], luna=int(b["luna"])), b.get("manual") or {})


def _d216(conn, schema, b):   # impozit special bunuri de valoare mare (anuala)
    return d216.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d120(conn, schema, b):   # decont accize (anual)
    return d120.genereaza(conn, schema, Perioada(b["an"], luna=int(b.get("luna") or 12)), b.get("manual") or {})



def _d106(conn, schema, b):   # informativa dividende actionari de stat (anuala); header din firma_profil
    return d106.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d108(conn, schema, b):   # impozit pe reprezentanta (anuala)
    return d108.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d114(conn, schema, b):   # contributia asiguratorie pentru munca - CAM (lunara)
    return d114.genereaza(conn, schema, Perioada(b["an"], luna=int(b["luna"])), b.get("manual") or {})


def _d130(conn, schema, b):   # decont impozit titei productie interna (anuala)
    return d130.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d318(conn, schema, b):   # rambursare TVA din alt stat membru UE (la cerere/anuala)
    return d318.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d603(conn, schema, b):   # exceptare CASS - declaratie pe propria raspundere (anuala)
    return d603.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d119(conn, schema, b):   # declaratie speciala BNR - obligatii buget din venituri nete (lunara)
    return d119.genereaza(conn, schema, Perioada(b["an"], luna=int(b["luna"])), b.get("manual") or {})


def _d169n(conn, schema, b):  # neconcordante beneficiar real fiducie - AML (anuala)
    return d169n.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d213(conn, schema, b):   # instrainare pachet control - terenuri agricole extravilan (anuala/eveniment)
    return d213.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d214(conn, schema, b):   # instrainare teren agricol extravilan prin hotarare judecatoreasca (anuala/eveniment)
    return d214.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d401(conn, schema, b):   # informativa proprietati imobiliare - schimb automat DAC (anuala)
    return d401.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d402(conn, schema, b):   # informativa venituri salariale nerezidenti - DAC1 (anuala)
    return d402.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d101g(conn, schema, b):  # impozit profit grup fiscal consolidat (anuala)
    return d101g.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d169(conn, schema, b):   # inregistrare contracte de fiducie (anuala)
    return d169.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d398(conn, schema, b):   # TVA regim special OSS (UE/non-UE), trimestriala
    # [lotul 13, 595] înregistrarea OSS e un răspuns al firmei, în Date firmă (nu al formularului): citit aici, unde generarea are
    # conexiunea (`d398.pull` nu atinge baza de date); refuzul trimite la câmpul din Date firmă
    from core import repo_declaratii as _repo
    from core.erori import RefuzGenerare as _RefuzGenerare
    with conn.cursor() as cur:
        _motiv = d398.refuz_oss(_repo.inregistrat_oss(cur))
    if _motiv:
        raise _RefuzGenerare(_motiv, ecran=d398.ECRAN_OSS, camp_ecran=d398.CAMP_OSS)
    return d398.genereaza(conn, schema, Perioada(b["an"], luna=int(b.get("luna") or 12)), b.get("manual") or {})


def _d399(conn, schema, b):   # TVA regim special import IOSS, trimestriala
    return d399.genereaza(conn, schema, Perioada(b["an"], luna=int(b.get("luna") or 12)), b.get("manual") or {})


def _d403(conn, schema, b):   # informativa asigurari de viata - DAC2/CRS (anuala)
    return d403.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d407(conn, schema, b):   # informativa institutii financiare raportoare (semestriala)
    # luna 6 sau 12 o cere valideaza_cerere (ramura „semestrial”); fara `or 12` tacut — semestrul I iesea pe decembrie
    return d407.genereaza(conn, schema, Perioada(b["an"], luna=int(b["luna"])), b.get("manual") or {})


def _d212(conn, schema, b):   # declaratia unica (PFA/II/IF - venituri persoane fizice), anuala
    return d212.genereaza(conn, schema, Perioada(b["an"]), b.get("manual") or {})


DECLARATII = {
    "d100": ("trimestrial", _d100),
    "d101": ("anual",       _d101),
    "d104": ("trimestrial", _d104),
    "d107": ("anual",       _d107),
    "d110": ("lunar",       _d110),
    "d112": ("lunar",       _d112),
    "d177": ("anual",       _d177),
    "d205": ("anual",       _d205),
    "d207": ("anual",       _d207),
    "d230": ("anual",       _d230),
    "d300": ("lunar",       _d300),
    "d301": ("lunar",       _d301),
    "d307": ("lunar",       _d307),
    "d311": ("lunar",       _d311),
    "d390": ("lunar",       _d390),
    "d394": ("lunar",       _d394),
    "d406": ("lunar",       _d406),
    # d710 = rectificativa (corecteaza D100 trimestrial). "trimestrial" pentru parametrul
    # `trim`; cere in plus `obligatii` (vezi valideaza_cerere). NU e obligatie periodica -
    # nu intra in semaforul de restante (control_fiscal_api / termene_api): e la cerere,
    # depusa doar cand exista o eroare de corectat. Vezi DECIZII 20.07.
    "d710": ("trimestrial", _d710),   # perioada D100-ului corectat; pe ecran: `ETICHETA_PERIODICITATE`
    "d393": ("anual",       _d393),
    "d395": ("lunar",       _d395),
    "d397": ("lunar",       _d397),
    "d204": ("anual",       _d204),
    "d208": ("lunar",       _d208),
    "d216": ("anual",       _d216),
    "d120": ("anual",       _d120),
    "d106": ("anual",       _d106),
    "d108": ("anual",       _d108),
    "d114": ("lunar",       _d114),
    "d130": ("anual",       _d130),
    "d318": ("anual",       _d318),
    "d603": ("anual",       _d603),
    "d119": ("lunar",       _d119),
    "d169n": ("anual",      _d169n),
    "d213": ("anual",       _d213),
    "d214": ("anual",       _d214),
    "d401": ("anual",       _d401),
    "d402": ("anual",       _d402),
    "d101g": ("anual",      _d101g),
    "d169": ("anual",       _d169),
    "d398": ("trimestrial", _d398),
    "d399": ("trimestrial", _d399),
    "d403": ("anual",       _d403),
    "d407": ("semestrial",  _d407),
    "d212": ("anual",       _d212),
}


# Tipuri disponibile DOAR prin API/dispecer, nu in selectorul generic din UI: cer parametri
# pe care ecranul generic (an/luna/trim) nu ii poate furniza. d710 (rectificativa) cere
# `obligatii` = corectiile contabilului -> flux dedicat viitor, nu selectorul generic (altfel
# ar aparea in dropdown si ar esua la generare). Ramane in DECLARATII (dispecer + test cheie DUK).
_DOAR_API = frozenset((
                       "d393", "d395", "d397", "d120",
                       "d106", "d108", "d130",
                       "d119", "d169n", "d213", "d214", "d401", "d402",
                       "d101g", "d169", "d399", "d403", "d407"))


# [lotul 13, deficiența 660, comanda Costin 13.1: „Code verifică la sursă fiecare formular din aplicație dacă mai e în vigoare; cele
# abrogate nu se mai oferă la nicio firmă (nici PFA).”] Formularele persoanelor fizice înlocuite de Declarația unică (D212): obligația pe
# care o declarau trece, în Codul fiscal în vigoare, prin declarația unică — textele de mai jos sunt cele din
# `anaf_surse/cod_fiscal_227_2015_consolidat.html` (forma consolidată din corpus). Nu mai sunt în dispecer (`DECLARATII`), deci nici în
# selector, nici în coadă; o cerere pe tipul lor primește motivul de aici (`valideaza_cerere`). Generatoarele `core/<tip>.py`, repository-urile
# și testele lor au fost ȘTERSE (decizia Costin 26.10.2026; actele de abrogare în mesajul commitului „Lotul 13: șterse generatoarele …”);
# nomenclatorul categoriilor de venit al registrului de evidență fiscală (`registru_evidenta_fiscala.CATEGORII_VENIT_PF`) nu depindea de ele.
# Garda: `core/test_lot13_decl_logica.py` (testele `test_660_*`).
FORMULARE_INLOCUITE = {
    "d200": ("D200 (veniturile realizate din România de persoanele fizice)", "CF art.122 alin.(1)",
             "Contribuabilii au obligația depunerii Declarației unice privind impozitul pe venit și contribuțiile sociale la organul fiscal "
             "competent, pentru fiecare an fiscal, în cazul în care realizează, individual sau într-o formă de asociere, venituri/pierderi"),
    "d201": ("D201 (veniturile realizate din străinătate de persoanele fizice)", "CF art.130 alin.(4)",
             "Contribuabilii care obțin venituri din străinătate conform dispozițiilor alin. (1) au obligația să le declare în Declarația "
             "unică privind impozitul pe venit și contribuțiile sociale datorate de persoanele fizice"),
    "d220": ("D220 (venitul estimat / norma de venit a persoanelor fizice)", "CF art.120, abrogat de OUG 128/2024",
             "Articolul 120 Abrogat."),
    "d221": ("D221 (veniturile agricole pe norme de venit)", "CF art.107 alin.(2)",
             "Contribuabilul care desfășoară o activitate agricolă prevăzută la art. 103 alin. (1) pentru care venitul se determină pe baza "
             "normei anuale de venit are obligația de a depune anual, pentru veniturile anului anterior, Declarația unică privind impozitul "
             "pe venit și contribuțiile sociale datorate de persoanele fizice"),
    "d223": ("D223 (venitul estimat al asocierilor fără personalitate juridică)", "CF art.125 alin.(4)",
             "Asocierile au obligația să depună la organul fiscal competent, până în ultima zi a lunii februarie inclusiv a anului următor "
             "celui de realizare a venitului, declarația anuală de venit"),
    "d600": ("D600 (venitul estimat pentru CAS și baza CASS)", "CF art.151 alin.(1)",
             "depun Declarația unică privind impozitul pe venit și contribuțiile sociale datorate de persoanele fizice până la termenul legal "
             "prevăzut la art. 122 alin. (3)"),
}


def refuz_inlocuita(tip):
    """Motivul pentru care un formular din `FORMULARE_INLOCUITE` nu se mai generează (text pentru contabil), sau None."""
    r = FORMULARE_INLOCUITE.get(str(tip or "").lower())
    if not r:
        return None
    den, act, text = r
    if tip == "d223":
        return ("%s nu se mai depune: Codul fiscal cere asocierii numai declarația anuală de venit (D204), iar venitul estimat nu se mai "
                "declară — %s: „%s”." % (den, act, text))
    if tip == "d220":
        return ("%s nu se mai depune: venitul estimat nu se mai declară (%s), iar veniturile anului se declară în Declarația unică (D212)."
                % (den, act))
    return "%s nu se mai depune: se declară în Declarația unică (D212) — %s: „%s”." % (den, act, text)


# [lotul 13, deficiențele 650, 595, 635] Declarațiile pe care REGIMUL DE TVA al firmei nu le poate datora — gri în selector, cu motivul,
# și refuzate la generare (aceeași poartă ca neaplicabilele din `control_fiscal_api.neaplicabile_selector`, căreia i se adaugă). Textul
# legii, din `anaf_surse/`:
#  - D311, CF art.324 alin.(10): „Persoanele impozabile al căror cod de înregistrare în scopuri de TVA a fost anulat potrivit prevederilor
#    art. 316 alin. (11) lit. a)-e) și h) trebuie să depună o declarație privind taxa colectată care trebuie plătită” — firma
#    înregistrată în scopuri de TVA n-are codul anulat (650: la F1, plătitoare, D311 apărea „lunar”, ca datorată);
#  - D398, CF art.315 alin.(4): „În cazul în care România este statul membru de înregistrare, codul de înregistrare utilizat de persoana
#    impozabilă este cel care i-a fost atribuit conform art. 316 sau art. 317” — fără cod de TVA românesc nu există regimul special (595);
#  - D318, HG 1/2016 pct.73 alin.(15) lit.c: „Organul fiscal competent din România nu înaintează cererea statului membru de rambursare în
#    cazul în care, pe parcursul perioadei de rambursare, solicitantul […] beneficiază de scutirea pentru întreprinderi mici prevăzută la
#    art. 310 din Codul fiscal” — firma neînregistrată în scopuri de TVA (635).
NEAPLICABILE_REGIM = {
    "d311": ("D311 nu se datorează — firma e înregistrată în scopuri de TVA, iar D311 o depune numai firma căreia i s-a anulat codul de "
             "TVA (CF art.324 alin.(10))."),
    "d398": ("D398 nu se datorează — firma n-are cod de TVA românesc (nici plătitoare, nici înregistrată conform art.317), iar regimul "
             "special OSS se aplică numai cu codul atribuit conform art.316 sau art.317 (CF art.315 alin.(4))."),
    "d318": ("D318 nu se depune — firma nu e înregistrată în scopuri de TVA: ANAF nu înaintează cererea de rambursare a firmei care aplică "
             "scutirea pentru întreprinderile mici (HG 1/2016 pct.73 alin.(15) lit.c)."),
}


def neaplicabile_regim(vector):
    """{tip: motiv} — din `NEAPLICABILE_REGIM`, după vectorul fiscal (`platitor_tva`, `inreg_art317`, `inregistrat_oss`). Vector necompletat (None) -> nimic
    blocat: un gol nu e un răspuns (ca `control_fiscal_api.neaplicabile_selector`)."""
    v = vector or {}
    platitor, art317 = v.get("platitor_tva"), v.get("inreg_art317")
    out = {}
    if v.get("inregistrat_oss") is False:   # [595.1, 14.2] răspunsul „Nu” din Date firmă: D398 gri, cu același motiv ca la generare
        out["d398"] = d398.MOTIV_OSS_NU
    if platitor is True:
        out["d311"] = NEAPLICABILE_REGIM["d311"]
    if platitor is False:
        out["d318"] = NEAPLICABILE_REGIM["d318"]
        if not art317:
            out["d398"] = NEAPLICABILE_REGIM["d398"]
    return out


# [C11, 07.10.2026] Situațiile financiare anuale (bilanțul) trec prin aceeași coadă ca declarațiile — generare, poarta
# validatorului, patru ochi, depunere, persistare —, dar NU sunt declarații fiscale: nu intră în `DECLARATII` (lista declarațiilor din
# pagina publică și din selector), iar intrarea lor e ecranul Bilanț (categoria de mărime se alege acolo).
SITUATII_FINANCIARE = {
    "s1005": ("anual", _s1005),   # bilanțul microentităților
    "s1003": ("anual", _s1003),   # bilanțul entităților mici
}


def _inregistrare(tip):
    """(periodicitate, adaptor) — din declarații sau din situațiile financiare; None dacă tipul e necunoscut."""
    return DECLARATII.get(tip) or SITUATII_FINANCIARE.get(tip)


def tipuri():
    """Lista tipurilor pentru selectorul generic din UI (periodice, an/luna/trim)."""
    return sorted(k for k in DECLARATII if k not in _DOAR_API)


#: [18.10.2026, comanda Costin 8.1 pct.6: „D710 «trimestrial»”] ce scrie ecranul lângă tip, unde periodicitatea-parametru (perioada aleasă) nu
#: e un termen: D710 nu se depune periodic, ci la cerere, când se corectează un D100 — pe perioada acelui D100 (în iConta: impozitul micro,
#: 121, și impozitul pe profit, 103, amândouă trimestriale). „D710 · trimestrial” se citea ca o obligație trimestrială.
ETICHETA_PERIODICITATE = {"d710": "la cerere — corectează un D100 (pe trimestrul lui)"}


def periodicitate(tip):
    """'lunar'|'trimestrial'|'anual' sau None dacă tip necunoscut."""
    rec = _inregistrare(tip)
    return rec[0] if rec else None



# [R167, 06.09.2026] Temeiul periodicitatii TVA sta in `core/perioada_fiscala_tva.py`, NU aici.
# Decizia 73 (R151): un singur nume `TEMEI*` muta fisierul intreg in datorie la clichetul
# refuzurilor, iar `declaratii_api` amesteca refuzuri de forma cu refuzuri normative. Modulul isi
# poarta temeiul ca date; dispecerul doar lipeste fraza la refuzul lui.
#
# Setul TVA-decont vine de acolo: apartenenta la el E chiar conditia ca art. 322 sa fie temeiul
# potrivit, deci lista traieste langa temei, nu in doua locuri.
_TVA_PERIODIC = _pft.SET_TVA_DECONT


def periodicitate_firma(tip, prof=None):
    """Periodicitatea AFISATA in selector si ceruta de dispecer. `prof` = vectorul fiscal al firmei (cel putin `tip_decont` si
    `platitor_tva`). D300/D394 urmeaza tip_decont-ul (L->lunar, T->trimestrial), ca semaforul (emite_tva); D406 urmeaza perioada
    SAF-T (`common.perioada_d406_tip` — sursa unica cu fereastra datelor: neplatitorul si S/A depun trimestrial, OPANAF 1783/2021
    anexa 4 pct.2-3; deficienta C2, 10.10.2026: neplatitorului i se oferea D406 lunar). Fara profil sau cu vectorul TVA incomplet
    -> mapul static (generatorul refuza apoi cu motivul lui). #2 plimbare vizuala 14.08.2026 (afisa 'lunar' si pt firme trimestriale)."""
    baza = periodicitate(tip)
    if tip not in _TVA_PERIODIC or prof is None:
        return baza
    from core.common import perioada_tva_tip, perioada_d406_tip, DECONT_LUNG
    try:
        d = perioada_d406_tip(prof) if tip == "d406" else perioada_tva_tip(prof)
    except ValueError:
        return baza
    return DECONT_LUNG.get(d, baza)


# ============================================================
#  VALIDARE CERERE — PURĂ (testabilă fără DB)
# ============================================================
def valideaza_cerere(tip, body, per_efectiv=None):
    """
    Verifică tip + parametrii ceruți de periodicitate. Întoarce listă erori
    (gol = ok). Nu atinge DB. [C7] per_efectiv: periodicitatea REALĂ a firmei — setul
    TVA-decont (d300/d394/d406) urmează tip_decont-ul (ca /declaratii/tipuri și wizardul);
    fără ea, o firmă trimestrială (care trimite `trim`) pică pe periodicitatea statică.
    """
    erori = []
    if refuz_inlocuita(tip):   # [lotul 13, 660] formularul înlocuit de Declarația unică: motivul lui, nu „tip necunoscut”
        return [refuz_inlocuita(tip)]
    per = periodicitate(tip)
    if per is None:
        return ["tip declarație necunoscut: %r (suportate: %s)"
                % (tip, ", ".join(tipuri()))]
    per = per_efectiv or per   # [C7] efectivă bate statica pentru setul TVA-decont

    an = body.get("an")
    if not isinstance(an, int) or an < 2020 or an > 2100:
        erori.append("an invalid: %r (se așteaptă întreg 2020-2100)" % (an,))

    # [probare invalid, 03.09.2026] O valoare TRIMISĂ și greșită se spune pe numele ei, chiar
    # dacă periodicitatea firmei n-o cere. Instanța: pe o firmă cu TVA trimestrial, `luna=13`
    # producea „trimestru invalid: None (aștept 1-4)" — un refuz care numește ALT câmp decât
    # cel greșit, iar omul caută trimestrul pe care nu l-a scris.
    luna_trimisa, trim_trimis = body.get("luna"), body.get("trim")
    if luna_trimisa is not None and (not isinstance(luna_trimisa, int)
                                     or luna_trimisa < 1 or luna_trimisa > 12):
        erori.append("luna invalidă: %r (se așteaptă 1-12)" % (luna_trimisa,))
    if trim_trimis is not None and (not isinstance(trim_trimis, int)
                                    or trim_trimis < 1 or trim_trimis > 4):
        erori.append("trimestru invalid: %r (se așteaptă 1-4)" % (trim_trimis,))

    if per == "lunar":
        luna = body.get("luna")
        if not isinstance(luna, int) or luna < 1 or luna > 12:
            if luna is None and isinstance(trim_trimis, int):
                erori.append("declarația %s se depune lunar pentru firma asta: trimite luna "
                             "(1-12), nu trimestrul%s" % (tip, _pft.norma(tip, "lunar") or ""))
            elif luna_trimisa is None:
                erori.append("luna invalidă: %r (se așteaptă 1-12)" % (luna,))
    elif per == "trimestrial":
        trim = body.get("trim")
        if not isinstance(trim, int) or trim < 1 or trim > 4:
            if trim is None and luna_trimisa is not None:
                erori.append("firma depune %s trimestrial: trimite trimestrul (1-4), nu luna%s"
                             % (tip, _pft.norma(tip, "trimestrial") or ""))
            elif trim_trimis is None:
                erori.append("trimestru invalid: %r (se așteaptă 1-4)" % (trim,))
    elif per == "semestrial":
        # [Lot 19 defect 8] „semestrial” n-avea ramura: cererea fara luna trecea, iar adaptorul punea 12 in tacere.
        # FORMĂ — DUK regula RLuna (D407): luna de raportare e 6 sau 12.
        if body.get("luna") not in (6, 12):
            erori.append("declarația %s e semestrială: trimite luna 6 (semestrul I) sau 12 (semestrul II); "
                         "s-a primit %r" % (tip, body.get("luna")))
    # 'anual' nu cere nimic în plus față de an

    # d177 (redirectionare impozit profit -> ONG/cult, MANUALA anuala): cere manual.beneficiari. Mesaj de
    # CONTABIL (formularul manual din UI trimite mereu beneficiari -> aici cade doar apelul API gol). Detaliile
    # pe beneficiar (tip/cod fiscal/IBAN/contract/suma) si plafoanele le da d177.genereaza.
    if tip == "d177":
        m = body.get("manual")
        if not isinstance(m, dict) or not m.get("beneficiari"):
            erori.append("D177 nu are ce genera: adaugă în formular cel puțin un beneficiar către care "
                         "redirecționezi o parte din impozitul pe profit.")

    # d207 (informativa nerezidenti, MANUALA anuala): cere manual.beneficiari. Mesaj de CONTABIL (formularul
    # manual din UI trimite mereu beneficiari -> aici cade doar apelul API gol). Detaliile pe beneficiar
    # (tip venit/stat/cod fiscal/baza/impozit/act normativ) le da d207.genereaza.
    if tip == "d207":
        m = body.get("manual")
        if not isinstance(m, dict) or not m.get("beneficiari"):
            erori.append("D207 nu are ce genera: adaugă în formular cel puțin un beneficiar nerezident căruia "
                         "i-ai plătit venituri cu reținere la sursă (dividende, dobânzi, redevențe etc.).")

    # d212 (Declaratia unica, persoane fizice, MANUALA anuala): cere identitate (cif/nume_c/adresa_c).
    # Formularul strange identitatea; cu `din_rip` serverul completeaza subsectiunea I.1.1 (cap11, sistem
    # real) din registrul RIP (D212 Etapa 2, d212.cap11_din_rip). oblig_realizat (impozit/CAS/CASS) = Etapa 4.
    # Mesaj de CONTABIL (formularul din UI trimite mereu identitatea -> aici cade doar apelul API gol).
    # Regulile pe camp (CNP valid, nerezident) le da d212.erori_generare.
    if tip == "d212":
        m = body.get("manual")
        if not isinstance(m, dict) or not (m.get("nume_c") and m.get("adresa_c") and m.get("cif")):
            erori.append("D212 nu are ce genera: completează în formular datele de identificare ale "
                         "persoanei fizice (CNP, nume și adresă).")

    # d204 (asociere fara personalitate juridica, PF, MANUALA anuala): asociere + reprezentant + activitate + asociati.
    # Mesaj de CONTABIL (formularul din UI trimite mereu datele -> aici cade doar apelul API gol).
    # Regulile pe camp (CUI/CNP valide, judet numeric, contract, Sigma cota=100, Sigma venit=net3) le da d204.erori_generare.
    if tip == "d204":
        m = body.get("manual")
        aso = (m or {}).get("asociere") or {}
        if not isinstance(m, dict) or not (aso.get("den") or aso.get("nume")) or not (m.get("asociati") or m.get("activitati")):
            erori.append("D204 nu are ce genera: completează asocierea (denumire, CUI), reprezentantul și cel puțin "
                         "o activitate cu asociați (cotele însumând 100).")

    # d216 (impozit special bunuri de valoare mare, MANUALA anuala): antet + cel putin un bun.
    # Mesaj de CONTABIL (formularul din UI trimite mereu datele -> aici cade doar apelul API gol).
    # Regulile pe camp (valoare>plafon, cota, coduri SIRUTA) le da d216.erori_generare.
    if tip == "d216":
        m = body.get("manual")
        if not isinstance(m, dict) or not m.get("nume") or not (m.get("imobile") or m.get("mobile")):
            erori.append("D216 nu are ce genera: completează datele contribuabilului și adaugă cel puțin "
                         "un bun (imobil rezidențial sau mobil) de valoare mare, cu valoarea impozabilă și plafonul.")

    # d208 (transfer proprietati imobiliare - notari, MANUALA semestriala): antet + tranzactie cu imobil.
    # Mesaj de CONTABIL (formularul din UI trimite mereu datele -> aici cade doar apelul API gol).
    # Regulile pe camp (Sigma cote=100, cotaImpozit in {0,1,3}) le da d208.erori_generare.
    if tip == "d208":
        m = body.get("manual")
        if not isinstance(m, dict) or not m.get("nume") or not (m.get("tranzactii") or m.get("imobile")):
            erori.append("D208 nu are ce genera: completează biroul notarial și adaugă cel puțin o tranzacție "
                         "cu un imobil, beneficiarii (cote însumând 100) și celelalte părți contractante.")

    # d603 (exceptare CASS, PF, MANUALA anuala): identitate + categorie + stat asigurare + perioada.
    # Mesaj de CONTABIL (formularul din UI trimite mereu datele -> aici cade doar apelul API gol).
    # Regulile pe camp (CNP, statAsigurare!=RO, cod exceptare 2/3/4, date) le da d603.erori_generare.
    if tip == "d603":
        m = body.get("manual")
        if not isinstance(m, dict) or not m.get("numeContrib") or not m.get("statAsigurare") or not m.get("exceptare"):
            erori.append("D603 nu are ce genera: completează persoana fizică (CNP, nume), categoria de "
                         "exceptare, statul de asigurare (diferit de RO) și perioada de exceptare.")

    # d114 (CAM pentru situatii ne-D112, MANUALA lunara): declarant + cel putin un contract (lucrator).
    # Mesaj de CONTABIL (formularul din UI trimite mereu datele -> aici cade doar apelul API gol).
    # Regulile pe camp (cui_lucrator, venit/contributie > 0, campuri obligatorii) le da d114.erori_generare.
    if tip == "d114":
        m = body.get("manual")
        if not isinstance(m, dict) or not m.get("cif_declarant") or not m.get("contracte"):
            erori.append("D114 nu are ce genera: completează declarantul (CIF, denumire, adresă) și adaugă "
                         "cel puțin un lucrator (contract) cu venitul și contribuția CAM.")

    # d318 (rambursare TVA din alt stat membru UE - Directiva 2008/9/CE, MANUALA / la cerere): perioada +
    # solicitant + IBAN de rambursare + activitate NACE + cel putin o factura de achizitie sau de import.
    # [lotul 13, deficiența 637] refuzul numește NUMAI ce lipsește (până la 637 cerea perioada, CUI-ul și IBAN-ul și când erau completate).
    # Regulile pe camp (annual R5, referenceNumber R9, semne/vatAmount pe factura R50/R80) le da d318.erori_generare.
    if tip == "d318":
        m = body.get("manual")
        m = m if isinstance(m, dict) else {}
        lipsa = [ce for ce, ok in (("CUI-ul solicitantului", m.get("cui")), ("IBAN-ul contului de rambursare", m.get("iban")),
                                   ("cel puțin o factură de achiziție sau de import din statul de rambursare",
                                    m.get("achizitii") or m.get("importuri"))) if not ok]
        if lipsa:
            erori.append("D318 nu are ce genera: completează %s." % " și ".join(lipsa))

    # d398 (OSS - TVA regimuri speciale UE/non-UE/import, MANUALA trimestriala): regim + identitate + livrari.
    # Mesaj de CONTABIL (formularul din UI trimite mereu datele -> aici cade doar apelul API gol).
    # Regulile pe camp (regim, cod TVA, state, supply_type/trade_type, cote) le da d398.erori_generare.
    # [lotul 13, deficiența 595] D398 o depune numai firma înregistrată în regimul special: CF art.315 alin.(3) — „În cazul în care România
    # este statul membru de înregistrare, persoana impozabilă respectivă trebuie să depună în format electronic o declarație de începere a
    # activității sale supuse regimului special la organul fiscal competent.” Înregistrarea OSS se întreabă în Date firmă (nu în formular) și
    # se verifică la generare (`_d398`, care are conexiunea); aici rămâne numai forma cererii.
    if tip == "d398":
        m = body.get("manual")
        if not isinstance(m, dict) or not m.get("name") or not m.get("vat_id_no") or not m.get("ms"):
            erori.append("D398 nu are ce genera: completează regimul, denumirea și codul de TVA, apoi adaugă "
                         "pentru fiecare stat de consum livrările (bunuri/servicii) cu cota și baza impozabilă.")

    # d104 (distribuire venituri asocieri f.PJ, MANUALA trimestriala): declarant + asociere + asociati + profit_pierd.
    # Mesaj de CONTABIL (formularul din UI trimite mereu datele -> aici cade doar apelul API gol).
    # Regulile pe camp (cota, CUI, cif1 unic, totaluri) le da d104.erori_generare.
    if tip == "d104":
        m = body.get("manual")
        if not isinstance(m, dict) or not m.get("asociati") or m.get("profit_pierd") is None:
            erori.append("D104 nu are ce genera: completează asocierea și profitul/pierderea, apoi adaugă "
                         "asociații cu cota și sumele (venit, cheltuieli, impozit) de distribuit.")

    # d107 (informativa sponsorizari/mecenat/burse, MANUALA anuala): cere manual.beneficiari. Mesaj de CONTABIL
    # (formularul manual din UI trimite mereu beneficiari -> aici cade doar apelul API gol). Detaliile pe
    # beneficiar (denumire/cod fiscal/adresa/sume) le da d107.genereaza.
    if tip == "d107":
        m = body.get("manual")
        if not isinstance(m, dict) or not m.get("beneficiari"):
            erori.append("D107 nu are ce genera: adaugă în formular cel puțin un beneficiar al "
                         "sponsorizării, mecenatului sau bursei.")

    # d110 (regularizare/restituire impozit retinut la sursa, MANUALA lunara): cel putin o obligatie.
    # Mesaj de CONTABIL (formularul din UI trimite mereu datele -> aici cade doar apelul API gol).
    # Identitatea platitorului vine din firma_profil; regulile pe camp (cod_oblig, sume, d_temei) le da d110.erori_generare.
    if tip == "d110":
        m = body.get("manual")
        if not isinstance(m, dict) or not m.get("obligatii"):
            erori.append("D110 nu are ce genera: adaugă cel puțin o obligație (cod obligație + impozit datorat "
                         "și impozit reținut) de regularizat; pentru restituire alege tipul „cerere de restituire” + IBAN.")

    # d230 (redirectionare 3,5% din impozit catre ONG, PF, MANUALA anuala): cere identitate + entitate.
    # Mesaj de CONTABIL (formularul din UI trimite mereu datele -> aici cade doar apelul API gol).
    # Regulile pe camp (CNP valid, IBAN, procent<=3.5, valabilitate 1/2) le da d230.erori_generare.
    if tip == "d230":
        m = body.get("manual")
        if not isinstance(m, dict) or not (m.get("nume_c") and m.get("cif_c") and m.get("den_entitate")):
            erori.append("D230 nu are ce genera: completează datele persoanei fizice (CNP, nume) și "
                         "entitatea nonprofit beneficiară (denumire, CIF, IBAN) către care redirecționezi 3,5%.")

    # d307 (ajustare TVA, MANUALA lunara): cere manual.operatiuni. Mesaj de CONTABIL (formularul manual din
    # UI trimite mereu operatiuni -> aici cade doar apelul API gol). Detaliile pe operatiune le da d307.genereaza.
    if tip == "d307":
        m = body.get("manual")
        if not isinstance(m, dict) or not m.get("operatiuni"):
            erori.append("D307 nu are ce genera: adaugă în formular cel puțin o operațiune de ajustare TVA "
                         "(transfer de active, leasing, sau anularea codului de TVA).")

    # d311 (TVA situatii speciale, MANUALA): cere `manual`. Mesaj de CONTABIL (formularul manual din UI
    # trimite mereu `manual` populat -> aici cade doar apelul API gol). Detaliile de camp le da d311.genereaza.
    if tip == "d311":
        if not isinstance(body.get("manual"), dict) or not body.get("manual"):
            erori.append("D311 nu are ce genera: completează în formular data anulării codului de TVA, "
                         "motivul anulării și sumele pe operațiuni.")

    # d710 (rectificativa): cere lista de corectii `obligatii` [{cod_oblig, suma_dat_i, suma_dat_c}]
    if tip == "d710":
        obl = body.get("obligatii")
        if not isinstance(obl, list) or not obl:
            erori.append("D710 cere cel puțin o obligație corectată.")

    return erori


def refuza_perioada_neincheiata(tip, body):
    """[lotul 10, deficiența 383, comanda Costin 10.2 pct.1, verbatim în DECIZII] „la F1, alegând manual luna octombrie, D300 pe 10/2026 se
    generează pe 20.10 și «Pune în De depus» e oferit. O declarație pe o perioadă neîncheiată se refuză la generare, cu motivul scris, la
    toate declarațiile.” Dispecerul (`genereaza`) e drumul COMUN al generării — Declarații pasul 2, „Trimite în coadă”, „Generează din nou”,
    reluarea după validarea notelor, API —, deci refuzul stă aici o dată, cu aceeași regulă ca depunerea (`coada_api.perioada_neincheiata`),
    PRIMUL: înaintea formularului manual și a citirii firmei (perioada aleasă greșit se spune înainte de „completează formularul”). O
    cerere cu forma greșită (anul sau luna în afara intervalului) trece mai departe, la refuzul ei de formă (`valideaza_cerere`). PURĂ."""
    an, luna, trim = body.get("an"), body.get("luna"), body.get("trim")
    if not (periodicitate(tip) and isinstance(an, int) and 2020 <= an <= 2100
            and (luna is None or (isinstance(luna, int) and 1 <= luna <= 12)) and (trim is None or (isinstance(trim, int) and 1 <= trim <= 4))):
        return
    from core import coada_api as _coada
    from core.erori import RefuzGenerare as _RefuzGenerare
    motiv = _coada.perioada_neincheiata(an, luna, trim, tip=tip, manual=body.get("manual"))
    if motiv:
        raise _RefuzGenerare(motiv)


# ============================================================
#  DISPATCH — alege adaptorul, cheamă genereaza. Parte DB (pe server).
# ============================================================
def genereaza(conn, schema, tip, body):
    """
    Validează cererea, apoi cheamă adaptorul potrivit.
    Întoarce (xml, rezultat) de la modul.
    Ridică ValueError cu erorile dacă cererea e invalidă.
    """
    refuza_perioada_neincheiata(tip, body)
    # [C7] periodicitatea EFECTIVĂ a firmei pentru setul TVA-decont (d300/d394/d406): urmează
    # tip_decont (ca /declaratii/tipuri și wizardul). Fără asta, firma trimestrială trimite `trim`,
    # iar validatorul static (lunar) cere `luna` -> "luna invalidă: None (aștept 1-12)".
    per_ef = None
    if tip in _TVA_PERIODIC:
        with conn.cursor() as cur:
            cur.execute(f"SELECT tip_decont, platitor_tva FROM {schema}.firma_profil WHERE id = 1")
            _rd = cur.fetchone()
        per_ef = periodicitate_firma(tip, {"tip_decont": _rd[0], "platitor_tva": _rd[1]} if _rd else None)
    erori = valideaza_cerere(tip, body, per_ef)
    if erori:
        raise ValueError("; ".join(erori))
    # [G1] POARTA DE APLICABILITATE: tipul pe care firma NU-l datoreaza -> refuz cu TEMEI, nu XML gol.
    # UI-ul dezactiveaza optiunea; backendul DECIDE (o firma nu poate depune ce n-o priveste).
    #
    # [R94 06.09.2026] Poarta consulta acum `neaplicabile_selector`, nu `neaplicabile_forma`. Pana azi
    # ecranul si generatorul raspundeau DIFERIT la aceeasi intrebare: ecranul stia forma + vectorul TVA,
    # poarta stia doar forma. Masurat pe cele 19 firme: 8 divergente - D300 si D394 ieseau `valid` pe cele
    # patru firme NEPLATITOARE de TVA, desi ecranul le declara neaplicabile CU TEMEI (art. 316). D300-ul
    # nul purta nota «Un platitor depune nul pe luna fara activitate», afirmatie falsa despre firma pe
    # care o descrie. O aplicabilitate care se decide in doua locuri se decide, de fapt, in niciunul.
    #
    # `ic_fapt` se trece MAI DEPARTE, nu se lasa pe implicit: fara el D390/D301 s-ar bloca pe bifa, iar
    # tiparul tenant_006 (vectorul zice fara IC, firma are achizitii intracomunitare reale) ar deveni un
    # refuz de generare - exact obligatia pe care contabilul trebuie sa o poata depune. Faptul bate vectorul
    # si in poarta, nu doar in ecran; altfel poarta ar fi mai stricta decat ecranul care o anunta.
    # Sursa unica de excludere = control_fiscal_api (aceeasi ca semaforul/termene). DECIZII 23.07.
    from core import control_fiscal_api as _cf
    from core.common import azi_ro as _azi
    with conn.cursor() as cur:
        cur.execute("SELECT tip_firma, platitor_tva, operatiuni_ic, regim_fiscal, inreg_art317 "
                    f"FROM {schema}.firma_profil WHERE id = 1")
        _row = cur.fetchone()
    _vec = ({"tip_firma": _row[0], "platitor_tva": _row[1], "operatiuni_ic": _row[2],
             "regim_fiscal": _row[3], "inreg_art317": _row[4]} if _row else {})
    _neap = _cf.neaplicabile_selector(
        _vec, ic_fapt=(lambda: _cf.ic_fapt_din_db(conn, schema, _azi().year)))
    _neap = {**neaplicabile_regim(_vec), **_neap}   # [lotul 13, 650/595/635] regimul de TVA: D311, D398, D318
    if tip in _neap:
        raise ValueError(_neap[tip])
    # [C7] setul TVA trimestrial: wizardul trimite `trim`; generatoarele d300/d394/d406 sunt ancorate
    # pe LUNĂ (agregă trimestrul din ultima lună). Convertim într-un SINGUR loc, după validare:
    # T1->luna 3, T2->6, T3->9, T4->12 (DUK regula R18: trimestrial cere luna în 03/06/09/12).
    if per_ef == "trimestrial" and body.get("trim") and body.get("luna") is None:
        body = {**body, "luna": int(body["trim"]) * 3}
    _per, adaptor = _inregistrare(tip)
    # [lotul 11, C77] formularele cu bifa „rectificativă” în `manual`: bifa o pun depunerile înregistrate pe perioadă
    from core import rectificativa as _rect
    body, _st_rect = _rect.pe_cerere(conn, schema, tip, body)
    xml, res = adaptor(conn, schema, body)
    return xml, _rect.pe_rezultat(res, _st_rect)


# ============================================================
#  CATE OPERATIUNI ARE DECLARATIA (27.07.2026)
# ============================================================
def numar_operatiuni(tip, res):
    """Numarul de operatiuni din declaratia generata. None = NU se poate numara.

    DE CE: o declaratie goala LEGITIMA (firma fara activitate) si una goala pentru ca
    s-a rupt un query arata IDENTIC - acelasi XML valid structural, aceleasi zero randuri.
    DUKIntegrator nu poate face diferenta: un D390 cu zero operatiuni e corect structural.
    Toata ziua de 27.07 a fost despre exact clasa asta de defect.

    Numarul urca la UI, care pune o POARTA inainte de trimiterea in coada: omul confirma
    ca firma chiar n-a avut activitate. Nu blocheaza depunerea pe zero - e obligatie reala
    pentru multe declaratii - dar nu o mai lasa sa treaca tacut.

    None, NU zero, pentru ce nu se poate numara: d112 intoarce o LISTA de avertismente (nu
    dataclass), iar d101 n-are notiunea de operatiuni (lucreaza pe solduri). "Nu stiu" nu se
    falsifica in "zero" - aceeasi regula ca verdictul GRI de la validator.
    """
    if res is None or isinstance(res, list):
        return None
    t = (tip or "").lower()
    if t in ("d100", "d710"):
        return len(getattr(res, "obligatii", None) or [])
    if t == "d205":
        return len(getattr(res, "beneficiari", None) or [])
    if t == "d104":
        return int(getattr(res, "nr_asociati", 0) or 0)
    if t == "d110":
        return int(getattr(res, "nr_obligatii", 0) or 0)
    if t == "d307":
        return int(getattr(res, "nr_operatiuni", 0) or 0)
    if t == "d107":
        return (int(getattr(res, "nr_beneficiari", 0) or 0) +
                int(getattr(res, "nr_neindividualizati", 0) or 0))
    if t == "d301":
        return len(getattr(res, "operatiuni", None) or [])
    if t == "d390":
        return int(getattr(res, "nr_opi", 0) or 0)
    if t == "d394":
        return int(getattr(res, "op_efectuate", 0) or 0)
    if t == "d406":
        return (len(getattr(res, "note", None) or []) +
                len(getattr(res, "facturi_vanzare", None) or []) +
                len(getattr(res, "facturi_cumparare", None) or []))
    # [R105, 30.08.2026] d112 CONTINUA sa intoarca None, si acum e o ALEGERE, nu o consecinta a
    # motorului: de la R105 declaratia are si obligatii, si asigurati, deci s-ar putea numara. Nu se
    # numara fiindca ecranul pune o POARTA la `operatiuni === 0` („declaratia nu contine nicio
    # operatiune"), iar la D112 zero asigurati NU inseamna declaratie goala: angajatorul poate datora
    # la buget si fara niciun salariat in luna. Un contor aici ar aprinde poarta pe o declaratie
    # legitima. LIMITA DECLARATA: pentru D112, ecranul arata componentele fara contor.
    if t == "d300":
        R = getattr(res, "R", None)
        if not isinstance(R, dict):
            return None
        return sum(1 for v in R.values() if v)      # randuri completate, nenule
    return None

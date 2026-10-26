# -*- coding: utf-8 -*-
"""Operatiuni intracomunitare - motor PUR + client VIES.
Surse: Cod fiscal art. 268 (AIC), 278 al. 2 (servicii B2B locul beneficiarului),
294 al. 2 lit. a (LIC scutita cu drept de deducere - conditii: cod TVA valid al
cumparatorului comunicat furnizorului + dovada transportului in alt SM),
308-309 (obligat la plata = beneficiarul la AIC/servicii primite), norme pct. 109
(taxare inversa 4426=4427, valabil pentru orice situatie de taxare inversa).
VIES REST oficial: https://ec.europa.eu/taxation_customs/vies/rest-api/ms/{MS}/vat/{nr}."""
import json
import re
import urllib.request
from decimal import Decimal, ROUND_HALF_UP

B = Decimal("0.01")
VIES_URL = "https://ec.europa.eu/taxation_customs/vies/rest-api/ms/{ms}/vat/{vat}"
TARI_UE = {"AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "EL", "ES", "FI", "FR",
           "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PL", "PT", "RO",
           "SE", "SI", "SK", "XI"}  # XI = Irlanda de Nord (VIES post-Brexit)

def desparte_cod_tva(cod):
    """'DE 123456789' -> ('DE', '123456789'). Grecia pe VIES = EL."""
    c = re.sub(r"[^A-Z0-9]", "", (cod or "").upper())
    tara, nr = c[:2], c[2:]
    if tara == "GR":
        tara = "EL"
    if tara not in TARI_UE:
        # [R147] Forma veche tipărea `tara '' nu este...` când codul lipsea — arăta o valoare
        # goală în loc să spună că lipsește codul. Cele două cazuri se deosebesc.
        if not tara:
            raise ValueError("Codul de TVA al partenerului lipsește. El începe cu prefixul "
                             "de țară (RO, DE, FR…), care spune în ce stat e înregistrat.")
        raise ValueError("Prefixul '%s' nu e al unui stat membru UE, deci codul nu se poate "
                         "verifica în VIES. O livrare intracomunitară cere un partener "
                         "înregistrat într-un stat membru." % tara)
    if not nr:
        raise ValueError("Codul de TVA al partenerului are doar prefixul de țară (%s), fără "
                         "numărul de după el. Un cod complet arată ca %s123456789 — "
                         "completează-l de pe factura furnizorului." % (tara, tara))
    return tara, nr

def _vies_simulat(cod_tva):
    """[lotul 11, C78 — plasa e2e] Răspunsul VIES pregătit în `<ICONTA_ANAF_SIMULAT>/vies.json` (aceeași cheie ca ANAF simulat,
    `anaf_api.CHEIE_SIMULAT`): numai pe un mediu care se dovedește de test (`mediu_test.motive`), altfel refuz. None = VIES real."""
    import os
    d = os.environ.get("ICONTA_ANAF_SIMULAT")
    if not d:
        return None
    from core import mediu_test
    m = mediu_test.motive()
    if m:
        raise RuntimeError("ICONTA_ANAF_SIMULAT e setat pe un mediu care nu e de test (%s) — refuz răspunsurile VIES pregătite"
                           % ", ".join(x.cod for x in m))
    cale = os.path.join(d, "vies.json")
    dupa_cod = {}
    if os.path.exists(cale):
        with open(cale, encoding="utf-8") as fh:
            dupa_cod = json.load(fh)
    tara, nr = desparte_cod_tva(cod_tva)
    r = dupa_cod.get(tara + nr)
    return dict(r, tara=tara, numar=nr) if r else {"valid": False, "nume": "", "adresa": "", "tara": tara, "numar": nr,
                                                    "eroare": "INVALID_INPUT"}


#: [lotul 13, deficiența 550] Răspunsurile VIES care spun că codul NU e valid. Orice altă eroare (MS_UNAVAILABLE — „serviciu indisponibil
#: în statul membru”, MS_MAX_CONCURRENT_REQ, SERVICE_UNAVAILABLE, TIMEOUT, GLOBAL_MAX_CONCURRENT_REQ …) înseamnă că verificarea NU s-a
#: făcut: VIES întoarce atunci tot `isValid: false`, dar cu codul erorii în `userError`. Proba lui Costin: pentru IE6388047V aplicația a
#: spus „invalid în VIES — facturează cu TVA românesc”, deși site-ul VIES răspundea „Serviciu indisponibil în statul membru”.
VIES_INVALID = ("INVALID", "INVALID_INPUT")


def stare_vies(valid, eroare):
    """„valid” | „invalid” | „indisponibil” — din `isValid` și `userError` ale răspunsului VIES. PURĂ."""
    if valid:
        return "valid"
    return "invalid" if (eroare or "INVALID") in VIES_INVALID else "indisponibil"


def verifica_vies(cod_tva, timeout=15):
    """Interogheaza VIES oficial. Returneaza {valid, stare, nume, adresa, tara, numar, eroare}; `stare` deosebește codul invalid de
    VIES indisponibil (`stare_vies`), ca o livrare scutită să nu fie taxată cu TVA românesc din cauza unui serviciu căzut."""
    s = _vies_simulat(cod_tva)
    if s is not None:
        return dict(s, stare=stare_vies(s.get("valid"), s.get("eroare")))
    tara, nr = desparte_cod_tva(cod_tva)
    req = urllib.request.Request(VIES_URL.format(ms=tara, vat=nr),
                                 headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.loads(r.read())
    valid, eroare = bool(d.get("isValid")), (d.get("userError") if not d.get("isValid") else None)
    return {"valid": valid, "stare": stare_vies(valid, eroare), "nume": d.get("name") or "",
            "adresa": (d.get("address") or "").strip(), "tara": tara, "numar": nr, "eroare": eroare}


def mesaj_vies_indisponibil(cod_tva, eroare=None):
    """[550] Textul pentru contabil când VIES n-a răspuns pentru statul membru: nu e un cod invalid, verificarea se reîncearcă."""
    tara = str(cod_tva or "")[:2].upper()
    return ("VIES n-a putut verifica acum codul %s: serviciul statului membru (%s) e indisponibil%s. Asta NU înseamnă că codul e "
            "invalid — încearcă din nou peste câteva minute; până la verificare nu trata operațiunea ca taxabilă în România."
            % (cod_tva, tara, (" (%s)" % eroare) if eroare else ""))

def tva_taxare_inversa(baza, cota=None):
    """AIC bunuri/servicii primite: TVA prin taxare inversa 4426 = 4427."""
    if cota is None:
        raise ValueError("Cota de TVA nu s-a dat. Nu se folosește o valoare implicită: o cotă scrisă în cod se rupe tăcut de lege la prima schimbare, iar o operațiune veche are altă cotă decât una de azi. Declară cota operațiunii.")
    b = Decimal(str(baza))
    if b <= 0:
        raise ValueError("Valoarea achiziției trebuie să fie un număr pozitiv — o achiziție "
                         "consemnează o operațiune efectuată. Pentru o corecție în minus se face "
                         "o stornare, nu o valoare negativă.")
    return (b * Decimal(str(cota)) / 100).quantize(B, rounding=ROUND_HALF_UP)

def note_taxare_inversa(cont, val, tva, beneficiar_platitor):
    """Liniile notei pentru o achizitie intracomunitara (taxare inversa), CONSTIENTE de platitor.
    - platitor de TVA (art.316): TVA simultan colectata SI deductibila -> 4426 = 4427 (net zero).
    - NEplatitor (inregistrat doar art.317): TVA datorata (D301) dar NEDEDUCTIBILA (deducerea cere
      art.316 + drept de deducere, CF art.297) -> intra in COSTUL bunului/serviciului (acelasi cont
      cu principalul), 446 = TVA de plata catre stat. Oglindeste modul "cost" de la extracomunitar.
    Intoarce (linii, mentiune). Fara valoare implicita de platitor: apelantul o citeste din profil."""
    val = Decimal(str(val)); tva = Decimal(str(tva))
    baza = (cont, "401", val)
    if beneficiar_platitor:
        return [baza, ("4426", "4427", tva)], "taxare inversa 4426=4427 (deductibila, art.297)"
    return [baza, (cont, "446", tva)], ("neplatitor art.317 - TVA nedeductibila in costul "
                                        "achizitiei (CF art.297: deducerea cere art.316)")


# [lotul 12, C84, decizia Costin 12.3 pct.7] „livrarea intracomunitară de bunuri fără dovada transportului primește avertisment la
# emitere, nu refuz”. Livrarea de bunuri se emite din „Emite factură” (decizia C84 (b), 23.10.2026); întrebarea vine acolo, după ce
# liniile au trecut (`facturi_api.emite_factura`, `COD_INTREABA_DOVADA`). Fosta `valideaza_lic` (refuzul „fără dovada transportului [...]
# facturează cu TVA”) n-avea niciun apelant de la C84 (b): Operațiuni nu mai livrează bunuri — s-a scos, odată cu refuzul.
# TEMEI: CF art.294 alin.(2) lit.a (scutirea livrării intracomunitare, cu bunurile expediate sau transportate în alt stat membru);
# CF art.294 alin.(3) — „Prin ordin al ministrului finanțelor publice se stabilesc, acolo unde este cazul, documentele necesare pentru a
# justifica scutirea de taxă pentru operațiunile prevăzute la alin. (1) și (2)”; HG 1/2016 pct.65 — „Scutirile cu drept de deducere
# prevăzute la art. 294, 295 și 296 din Codul fiscal sunt aplicate în măsura în care persoanele impozabile pot justifica scutirea cu
# documentele prevăzute de instrucțiuni aprobate de ministrul finanțelor publice.”
INTREBARE_DOVADA_TRANSPORT = ("Ai dovada transportului bunurilor în alt stat membru? Scutirea livrării intracomunitare se aplică numai "
                              "dacă o poți justifica cu documentele de transport.")
AVERTISMENT_LIC_FARA_DOVADA = (
    "Factura s-a emis cu scutirea livrării intracomunitare (art.294 alin.(2) lit.a din Codul fiscal), dar nu ai încă dovada transportului "
    "bunurilor în alt stat membru. Scutirea se aplică numai dacă o justifici cu documentele de transport (art.294 alin.(3) din Codul "
    "fiscal; HG 1/2016 pct.65): păstrează-le la dosar când le primești. Fără ele scutirea nu se aplică, iar livrarea se facturează cu TVA "
    "(stornezi factura și emiți una cu TVA).")
#: [lotul 12, C197] livrarea intracomunitară de bunuri emisă pe un drum care nu poate întreba (factura recurentă, emisă automat de cron):
#: aplicația nu știe dacă dovada există, deci nu spune „nu ai dovada” (ar fi o afirmație pe care n-o poate face), ci ce trebuie verificat.
#: Temeiul, ca mai sus: CF art.294 alin.(2) lit.a (scutirea) și CF art.294 alin.(3) („Prin ordin al ministrului finanțelor publice se
#: stabilesc, acolo unde este cazul, documentele necesare pentru a justifica scutirea”).
AVERTISMENT_LIC_NEINTREBAT = (
    "Factura s-a emis automat cu scutirea livrării intracomunitare (art.294 alin.(2) lit.a din Codul fiscal), fără ca aplicația să te poată "
    "întreba dacă ai dovada transportului bunurilor în alt stat membru. Scutirea se aplică numai dacă o justifici cu documentele de "
    "transport (art.294 alin.(3) din Codul fiscal): verifică-le și păstrează-le la dosar. Fără ele scutirea nu se aplică, iar livrarea se "
    "facturează cu TVA (stornezi factura și emiți una cu TVA).")

#: [C128, lotul 12] refuzul achiziției intracomunitare de la un furnizor cu cod de TVA românesc
MESAJ_AIC_RO = ("Codul de TVA al furnizorului începe cu RO, deci furnizorul e înregistrat în România: cumpărarea de la el nu e achiziție "
                "intracomunitară (fără taxare inversă, fără D390) — înregistreaz-o ca factură primită obișnuită. Dacă furnizorul e "
                "dintr-un alt stat membru, scrie codul lui de TVA de acolo (ex. DE123456789).")


def valideaza_aic(cod_tva_furnizor):
    """Achiziția intracomunitară (bunuri: CF art.273 alin.(1) — bunurile ajung „către un stat membru, altul decât cel de plecare”; servicii:
    CF art.307 alin.(2) — prestatorul „nu este stabilit[ă] pe teritoriul României”) cere un furnizor dintr-un ALT stat membru: codul lui
    de TVA nu poate fi românesc. -> (țara, număr) sau ValueError (`MESAJ_AIC_RO`). Oglinda refuzului clientului din RO la livrare (`categorii_tva.verifica_linii`, livrare_ic)."""
    tara, nr = desparte_cod_tva(cod_tva_furnizor)
    if tara == "RO":
        raise ValueError(MESAJ_AIC_RO)
    return tara, nr


def valideaza_prestare_ic(cod_tva_client, cod_valid_vies):
    """Prestare servicii B2B catre PI din alt SM (art. 278 al. 2): neimpozabila
    in RO, locul = beneficiarul; se declara in D390 (S)."""
    tara, _ = desparte_cod_tva(cod_tva_client)
    if tara == "RO":
        raise ValueError("Clientul are cod de TVA din România: prestarea către el e o operațiune internă, cu TVA (regim normal), nu una intracomunitară.")
    if not cod_valid_vies:
        raise ValueError("codul de TVA al clientului e invalid în VIES - nu e persoană impozabilă dovedită, "
                         "serviciul se facturează cu TVA românesc (art. 278 alin.(3))")
    return True, "neimpozabil in RO - art. 278 alin. (2) Cod fiscal (locul = beneficiarul)"

# -*- coding: utf-8 -*-
"""[274b] Categoria de TVA a unei linii cu cota 0% — sursa unică (factura emisă, XML-ul e-Factura, D300, formularul de emitere).

Decizia Costin 16.10.2026 (răspunsul la raportul lotului 6 pct.1, verbatim în DECIZII): „Categoria e obligatorie pe orice linie cu 0%:
taxare inversă (AE), scutit cu drept de deducere (E), scutit fără drept de deducere (E), livrare intracomunitară scutită (K), export (G),
în afara sferei TVA. «Neplătitor» (O) nu e opțiune în listă; vine automat din regimul firmei neplătitoare.”

TEMEI (verificat la sursă, `anaf_surse/`):
- Ghidul MF al codurilor e-Factura v2.9, cap.3 (mf_ghid_coduri_facturi_efactura_v2_9.txt): „E” = „operațiuni scutite de TVA, indiferent
  dacă acestea sunt scutite cu drept de deducere sau fără drept de deducere, sau pentru operațiuni care nu sunt cuprinse în baza de
  impozitare a TVA (ex. penalități [...], dobânzi pentru plata cu întârziere) sau care nu sunt cuprinse în sfera de aplicare a TVA (ex.
  garanții SGR, garanții de bună execuție GBE)”, cu BT-120 (motivul) sau BT-121 (cod VATEX); „AE” = art.331, VATEX-EU-AE; „O” =
  „utilizat exclusiv de către persoane impozabile neînregistrate în scopuri de TVA”, VATEX-EU-O. Deci „în afara sferei TVA” = E + motivul.
- K / G: SR EN 16931-1 (UNCL 5305: K = livrare intracomunitară scutită, G = export în afara UE; VATEX-EU-IC / VATEX-EU-G); RO_CIUS
  (OMF 1366/2021, modificat — MO nr.1148) nu le restrânge.
- D300 (OPANAF 174/2026, anaf_surse/opanaf_174_2026_d300.txt): rd.1 = „livrările intracomunitare de bunuri, scutite conform art. 294
  alin. (2) lit. a) şi d)”; rd.13 = livrările „pentru care furnizorii/prestatorii aplică măsurile de simplificare prevăzute la art. 331”;
  rd.14 = „livrările de bunuri/prestările de servicii scutite cu drept de deducere, prevăzute la art. 294 alin. (1), art. 295 şi 296”
  (exportul e art.294 alin.(1) lit.a); rd.15 = „livrările de bunuri scutite fără drept de deducere, prevăzute la art. 292”. O operațiune
  în afara sferei / bazei TVA nu are rând în decont.
"""

#: cod intern -> {eticheta (formular), ubl (BT-151), vatex (BT-121), mentiune (motivul scutirii, BT-120; și mențiunea de pe PDF), rand_d300,
#: temei} — nomenclator, nu afirmație despre datele firmei
CATEGORII = {
    "taxare_inversa": {
        "eticheta": "Taxare inversă (art.331)", "ubl": "AE", "vatex": "VATEX-EU-AE",
        "mentiune": "Taxare inversă, art.331 din Legea nr.227/2015 privind Codul fiscal", "rand_d300": "R13",
        "temei": "CF art.331; OPANAF 174/2026 D300 rd.13"},
    "scutit_cu_drept": {
        "eticheta": "Scutit cu drept de deducere (art.294 alin.(1), 295, 296)", "ubl": "E", "vatex": None,
        "mentiune": "Scutit cu drept de deducere, art.294 alin.(1), art.295 și art.296 din Legea nr.227/2015 privind Codul fiscal",
        "rand_d300": "R14", "temei": "CF art.294 alin.(1), art.295, art.296; OPANAF 174/2026 D300 rd.14"},
    "scutit_fara_drept": {
        "eticheta": "Scutit fără drept de deducere (art.292)", "ubl": "E", "vatex": None,
        "mentiune": "Scutit fără drept de deducere, art.292 din Legea nr.227/2015 privind Codul fiscal", "rand_d300": "R15",
        "temei": "CF art.292; OPANAF 174/2026 D300 rd.15"},
    "livrare_ic": {
        "eticheta": "Livrare intracomunitară scutită (art.294 alin.(2))", "ubl": "K", "vatex": "VATEX-EU-IC",
        "mentiune": "Livrare intracomunitară scutită, art.294 alin.(2) din Legea nr.227/2015 privind Codul fiscal", "rand_d300": "R1",
        "temei": "CF art.294 alin.(2) lit.a, d; OPANAF 174/2026 D300 rd.1"},
    "serviciu_extern": {
        # [17.10.2026, decizia Costin pct.1, verbatim în DECIZII] prestările cu locul în afara României (art.278 alin.(2)): D300 rd.3 (+ rd.3.1
        # la clientul din UE — OPANAF 174/2026: „prestate către persoane impozabile nestabilite în România, dar stabilite în Uniunea
        # Europeană”), D390 cu P — amândouă din AXA facturii („servicii”, pusă de categorie), nu din codul UBL. UBL (BT-151): la clientul din
        # UE, AE + „taxare inversă” (EN 16931 / UNCL 5305 AE = taxa datorată de cumpărător; CF art.319 alin.(20) lit.m: „în cazul în care
        # clientul este persoana obligată la plata TVA, mențiunea «taxare inversă»”); la clientul din afara UE, E cu motivul (Ghidul MF v2.9
        # cap.3.2: operațiuni „care nu sunt cuprinse în sfera de aplicare a TVA”) — `descriere(cod, tara)`.
        "eticheta": "Prestare de servicii cu locul în afara României (art.278 alin.(2))", "ubl": "AE", "vatex": "VATEX-EU-AE",
        "mentiune": "Taxare inversă — prestare de servicii cu locul în alt stat membru, art.278 alin.(2) din Legea nr.227/2015 privind Codul "
                    "fiscal", "rand_d300": "R3", "temei": "CF art.278 alin.(2); OPANAF 174/2026 D300 rd.3, rd.3.1; D390 cod P",
        "non_ue": {"ubl": "E", "vatex": None, "mentiune": "Prestare de servicii cu locul în afara Uniunii Europene, art.278 alin.(2) din "
                                                         "Legea nr.227/2015 privind Codul fiscal"}},
    "export": {
        "eticheta": "Export (art.294 alin.(1) lit.a)", "ubl": "G", "vatex": "VATEX-EU-G",
        "mentiune": "Export, scutit cu drept de deducere, art.294 alin.(1) lit.a din Legea nr.227/2015 privind Codul fiscal",
        "rand_d300": "R14", "temei": "CF art.294 alin.(1) lit.a; OPANAF 174/2026 D300 rd.14"},
    "in_afara_sferei": {
        "eticheta": "În afara sferei / bazei de impozitare a TVA (garanții, penalități, dobânzi)", "ubl": "E", "vatex": None,
        "mentiune": "Operațiune care nu intră în sfera de aplicare sau în baza de impozitare a TVA", "rand_d300": None,
        "temei": "Ghidul MF e-Factura v2.9 cap.3.2 (categoria E); fără rând în D300"},
}
#: categoria pusă AUTOMAT pe liniile unei firme neplătitoare (nu e o alegere în formular)
NEPLATITOR = {"cod": "neplatitor", "ubl": "O", "vatex": "VATEX-EU-O",
              "mentiune": "Neplătitor de TVA, art.310 din Legea nr.227/2015 privind Codul fiscal"}
#: toate valorile admise în `factura_linii.categorie_tva` (migrare_categorie_tva_linie)
VALORI = tuple(CATEGORII) + (NEPLATITOR["cod"],)

COD_LIPSA = "CATEGORIE_TVA_LIPSA"
MESAJ_LIPSA = "Linia are cota 0%: alege categoria (taxare inversă, scutit cu sau fără drept de deducere, livrare intracomunitară, export " \
              "sau în afara sferei TVA). Ea decide codul din e-Factura și rândul din D300."


#: [17.10.2026] axa facturii (bunuri / servicii) pe care o pune categoria: din ea, nu din codul UBL, se iau D390 (L / P) și D300 (rd.1 /
#: rd.14 la bunuri, rd.3 / rd.3.1 la servicii)
AXA = {"livrare_ic": "bunuri", "export": "bunuri", "serviciu_extern": "servicii"}


def descriere(cod, tara=None):
    """{ubl, vatex, mentiune, ...} pentru un cod din `VALORI` (și țara clientului, pentru prestările cu locul în afara României); None pentru
    linia taxabilă (fără categorie)."""
    if cod == NEPLATITOR["cod"]:
        return NEPLATITOR
    d = CATEGORII.get(cod)
    if d and d.get("non_ue") and tara:
        from core.d390 import TARI_UE
        if (tara or "RO").strip().upper() not in TARI_UE:
            return dict(d, **d["non_ue"])
    return d


def axa_facturii(linii):
    """Axa pe care o pun categoriile liniilor (None: nicio categorie cu axă). Ridică ValueError dacă liniile cer două axe: D390 și D300 iau
    axa de pe document, deci bunurile și serviciile către un client din altă țară se emit pe facturi separate."""
    axe = {AXA[l["categorie_tva"]] for l in linii if l.get("categorie_tva") in AXA}
    if len(axe) > 1:
        e = ValueError("Factura are și bunuri (livrare intracomunitară / export), și servicii cu locul în afara României: D390 și D300 iau "
                       "natura operației de pe document, deci emite-le pe facturi separate.")
        e.cod = "CATEGORII_AXE_DIFERITE"
        raise e
    return axe.pop() if axe else None


#: [lotul 12, C154] felul venitului liniei (cheile din `facturi.VENIT`, OMFP 1802/2014: 701 / 703 / 707 bunuri, 704 servicii) -> axa
_AXA_FEL = {"marfa": "bunuri", "produse": "bunuri", "reziduale": "bunuri", "servicii": "servicii", "prestari": "servicii"}


def _axa_linie(linie):
    """[lotul 12, C154 / C156] Axa unei linii din contul ei de venit (bunuri / servicii), None când felul contului nu se știe (706, 708 …)."""
    from core import facturi as _fc
    fel = {cont: tip for tip, cont in _fc.VENIT.items()}
    return _AXA_FEL.get(fel.get(str(linie.get("cont_venit") or "").strip()[:3]))


def client_ic(tert_tara, tert_cui):
    """[lotul 12, C156 / C157] Clientul e o persoană impozabilă dintr-un ALT stat membru: țara lui e în UE (nu RO) și i-a dat furnizorului
    un cod de TVA cu prefixul unui stat membru (aceeași clasificare ca D390, `d390._clasifica_partener`: fără cod de TVA partenerul nu intră
    în declarația recapitulativă). Fără cod (persoană fizică, firmă fără cod de TVA), serviciul are locul în România (CF art.278 alin.(3))."""
    from core.d390 import TARI_UE, _clasifica_partener
    tara = (tert_tara or "RO").strip().upper() or "RO"
    return tara != "RO" and tara in TARI_UE and _clasifica_partener(tert_cui)[0] == "ic"


def axa_neplatitor(linii, tert_tara):
    """[lotul 12, C154] Axa facturii emise de firma NEPLĂTITOARE către un client din altă țară (None: nu se poate spune).

    Liniile neplătitorului poartă toate „neplatitor” (O), categorie fără axă, deci `axa_facturii` nu găsea nimic și D390 lua implicitul
    „bunuri” (`d390._tip_din_axa` -> L): un serviciu emis din „Emite factură” către un client din DE ieșea livrare intracomunitară de
    bunuri, nu prestare (P). Felul liniei e cel din contul ei de venit, pus la emitere în aceeași ordine ca la plătitor (contul ales de
    contabil, apoi cuvântul-cheie din denumire, apoi modelul — `facturi_api._potriveste_linii`; ecranul plătitorului propune din același
    fel categoria art.278 alin.(2), deficiența 326). Contul fără fel cunoscut (706, 708 …), liniile cu feluri diferite sau clientul din
    România: None, ca înainte (nimic ghicit).
    TEMEI: CF art.325 alin.(1) lit.c — înregistratul art.317 declară „prestările de servicii prevăzute la art. 278 alin. (2) efectuate în
    beneficiul unor persoane impozabile nestabilite în România, dar stabilite în Uniunea Europeană”."""
    tara = (tert_tara or "RO").strip().upper() or "RO"
    if tara == "RO" or not linii or any(l.get("categorie_tva") != NEPLATITOR["cod"] for l in linii):
        return None
    axe = {_axa_linie(l) for l in linii}
    return axe.pop() if len(axe) == 1 and None not in axe else None


#: [lotul 12, C156] categoria liniei de servicii a neplătitorului înregistrat art.317 către clientul din alt stat membru (AE, „taxare
#: inversă”, D390 P din axa ei) — aceeași ca la plătitor: locul prestării e la client (CF art.278 alin.(2)), deci nu e scutirea art.310
PRESTARE_IC_317 = "serviciu_extern"

COD_NEPLATITOR_317_MIXT = "CATEGORII_NEPLATITOR_317_MIXT"
MESAJ_NEPLATITOR_317_MIXT = (
    "Factura are și prestări de servicii către clientul din alt stat membru (cu codul de TVA art.317 al firmei și mențiunea „taxare "
    "inversă”), și alte linii (bunuri sau alte venituri, scutite ca neplătitor, art.310). Pe aceeași factură nu pot sta amândouă: liniile "
    "neplătitorului nu poartă codul de TVA al firmei. Emite prestările pe o factură separată.")


def verifica_linii(linii, platitor, tert_tara="RO", prefix="em-l", art317=None, tert_cui=None):
    """Pune `categorie_tva` pe fiecare linie și întoarce refuzurile pe câmp ([{camp, eticheta, mesaj}], ca `linii_campuri_lipsa`).

    - linie cu cotă > 0: fără categorie (taxabilă, S);
    - firmă neplătitoare: „neplatitor” (O) pe toate, automat — nu e o alegere; [lotul 12, C156, decizia Costin 12.3 pct.3] la neplătitorul
      ÎNREGISTRAT art.317 (`art317` True), linia de servicii (contul de venit) către clientul din alt stat membru cu cod de TVA (`client_ic`)
      primește `PRESTARE_IC_317` (AE, „taxare inversă”, codul RO art.317 pe factură, D390 P); stornarea păstrează categoria originalului
      (marca `categorie_istoric`, pusă numai de `facturi_api.storneaza`): factura veche rămâne cum a fost emisă (pct.10);
    - plătitor, cotă 0: categoria obligatorie, din `CATEGORII`; livrarea intracomunitară cere un client dintr-un alt stat membru, exportul
      un client din afara UE, taxarea inversă (art.331) un client din România."""
    from core.d390 import TARI_UE
    tara = (tert_tara or "RO").strip().upper() or "RO"
    prestare_317 = platitor is False and art317 is True and client_ic(tara, tert_cui)
    rele = []
    for i, l in enumerate(linii):
        n, camp = i + 1, "%s%d-categorie" % (prefix, i)
        cota = l.get("cota_tva")
        try:
            zero = cota is not None and float(cota) == 0
        except (TypeError, ValueError):
            zero = False
        if not zero:
            l["categorie_tva"] = None
            continue
        if platitor is False:
            if "categorie_istoric" in l and l.get("categorie_tva") in (NEPLATITOR["cod"], PRESTARE_IC_317):
                continue   # stornarea: categoria liniei stornate
            # serviciul: din contul de venit al liniei, sau declarat de apelant (prestarea din Operațiuni, `uc_tenants.vanzare_ic`)
            serviciu = l.get("categorie_tva") == PRESTARE_IC_317 or _axa_linie(l) == "servicii"
            l["categorie_tva"] = PRESTARE_IC_317 if prestare_317 and serviciu else NEPLATITOR["cod"]
            continue
        if l.get("categorie_istoric") and not l.get("categorie_tva"):
            # stornarea unei linii de dinainte de categorie (`facturi_api.storneaza`): rămâne fără, ca originalul — nimic ghicit
            l["categorie_tva"] = None
            continue
        cat = (l.get("categorie_tva") or "").strip() or None
        if cat not in CATEGORII:
            rele.append({"camp": camp, "eticheta": "Linia %d: categoria de TVA" % n, "cod": COD_LIPSA,
                         "mesaj": MESAJ_LIPSA if cat is None else "Categoria %r nu e una din listă. %s" % (cat, MESAJ_LIPSA)})
            continue
        if cat == "livrare_ic" and (tara == "RO" or tara not in TARI_UE):
            rele.append({"camp": camp, "eticheta": "Linia %d: categoria de TVA" % n, "cod": "CATEGORIE_TVA_TARA",
                         "mesaj": "Livrarea intracomunitară scutită cere un client dintr-un alt stat membru UE (țara clientului: %s)." % tara})
        elif cat == "export" and (tara == "RO" or tara in TARI_UE):
            rele.append({"camp": camp, "eticheta": "Linia %d: categoria de TVA" % n, "cod": "CATEGORIE_TVA_TARA",
                         "mesaj": "Exportul cere un client din afara Uniunii Europene (țara clientului: %s)." % tara})
        elif cat == "serviciu_extern" and tara == "RO":
            rele.append({"camp": camp, "eticheta": "Linia %d: categoria de TVA" % n, "cod": "CATEGORIE_TVA_TARA",
                         "mesaj": "Prestarea de servicii cu locul în afara României cere un client din altă țară (țara clientului: RO)."})
        elif cat == "taxare_inversa" and tara != "RO":
            rele.append({"camp": camp, "eticheta": "Linia %d: categoria de TVA" % n, "cod": "CATEGORIE_TVA_TARA",
                         "mesaj": "Taxarea inversă din art.331 se aplică între persoane înregistrate în scopuri de TVA în România "
                                  "(țara clientului: %s)." % tara})
        l["categorie_tva"] = cat
    if platitor is False:
        cats = [l.get("categorie_tva") for l in linii]
        if PRESTARE_IC_317 in cats and NEPLATITOR["cod"] in cats:
            # Ghidul MF e-Factura v2.9 cap.5: factura cu o linie „nu face obiectul TVA” (O) „trebuie să NU conţină identificatorul de TVA
            # al Vânzătorului (BT-31) [...] sau identificatorul de TVA al Cumpărătorului (BT-48)” — iar prestarea art.317 îi cere pe amândoi
            i = cats.index(NEPLATITOR["cod"])
            rele.append({"camp": "%s%d-categorie" % (prefix, i), "eticheta": "Linia %d: categoria de TVA" % (i + 1),
                         "cod": COD_NEPLATITOR_317_MIXT, "mesaj": MESAJ_NEPLATITOR_317_MIXT})
    return rele


def cod_tva_art317(platitor, linii):
    """[lotul 12, C156] Factura neplătitorului poartă codul de TVA RO atribuit după art.317 (în loc de CIF): liniile ei sunt prestările către
    clientul din alt stat membru (`PRESTARE_IC_317`, puse la emitere și înghețate pe document). TEMEI: CF art.318 alin.(1) — „Codul de
    înregistrare în scopuri de TVA, atribuit conform art. 316 și 317, are prefixul RO”; alin.(4) lit.b pct.2 — înregistrații art.317 vor
    comunica codul „beneficiarului, persoană impozabilă din alt stat membru, către care prestează servicii pentru care acesta este obligat
    la plata taxei”; CF art.319 alin.(20) lit.d — factura cuprinde „codul de înregistrare în scopuri de TVA sau, după caz, codul de
    identificare fiscală” al prestatorului."""
    return platitor is False and any(l.get("categorie_tva") == PRESTARE_IC_317 for l in (linii or []))


#: [lotul 12, C157, decizia Costin 12.3 pct.3] „fără înregistrare art. 317, avertisment la emitere, nu refuz”
AVERTISMENT_FARA_ART317 = (
    "Firma nu e înregistrată în scopuri de TVA conform art.317, iar factura are prestări de servicii către un client din alt stat membru, "
    "care plătește el taxa. Codul fiscal cere înregistrarea înainte de prestare (art.317 alin.(1) lit.b). Factura s-a emis ca neplătitor "
    "(fără cod de TVA, fără „taxare inversă”). Cere înregistrarea la organul fiscal, apoi bifează „Înregistrată art. 317” în Date firmă.")
AVERTISMENT_ART317_NEALES = (
    "Factura are prestări de servicii către un client din alt stat membru, care plătește el taxa, dar în Date firmă nu e ales dacă firma e "
    "înregistrată în scopuri de TVA conform art.317. Codul fiscal cere înregistrarea înainte de prestare (art.317 alin.(1) lit.b). Factura "
    "s-a emis ca neplătitor (fără cod de TVA, fără „taxare inversă”). Alege „Înregistrată art. 317” în Date firmă; dacă firma nu e "
    "înregistrată, cere înregistrarea la organul fiscal.")


def avertismente_emitere(platitor, art317, axa, tert_tara, tert_cui):
    """[lotul 12, C157] Avertismentele emiterii (nu refuzuri) pentru firma NEPLĂTITOARE neînregistrată art.317 (sau cu alegerea lipsă) care
    prestează servicii (axa facturii, `axa`: din contul de venit al liniilor sau declarată de apelant) către clientul din alt stat membru cu
    cod de TVA (`client_ic`). TEMEI: CF art.317 alin.(1) lit.b — are obligația să solicite înregistrarea persoana impozabilă neînregistrată
    „dacă prestează servicii care au locul în alt stat membru, pentru care beneficiarul serviciului este persoana obligată la plata taxei
    [...], înainte de prestarea serviciului”."""
    if platitor is not False or art317 is True or axa != "servicii" or not client_ic(tert_tara, tert_cui):
        return []
    return [AVERTISMENT_ART317_NEALES if art317 is None else AVERTISMENT_FARA_ART317]


def pentru_formular(platitor):
    """Ce afișează formularul de emitere: lista (cod, etichetă) în ordinea de mai sus, numai pentru plătitor."""
    return [{"cod": k, "eticheta": v["eticheta"]} for k, v in CATEGORII.items()] if platitor is not False else []

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


def descriere(cod):
    """{ubl, vatex, mentiune, ...} pentru un cod din `VALORI`; None pentru linia taxabilă (fără categorie)."""
    if cod == NEPLATITOR["cod"]:
        return NEPLATITOR
    return CATEGORII.get(cod)


def verifica_linii(linii, platitor, tert_tara="RO", prefix="em-l"):
    """Pune `categorie_tva` pe fiecare linie și întoarce refuzurile pe câmp ([{camp, eticheta, mesaj}], ca `linii_campuri_lipsa`).

    - linie cu cotă > 0: fără categorie (taxabilă, S);
    - firmă neplătitoare: „neplatitor” (O) pe toate, automat — nu e o alegere;
    - plătitor, cotă 0: categoria obligatorie, din `CATEGORII`; livrarea intracomunitară cere un client dintr-un alt stat membru, exportul
      un client din afara UE, taxarea inversă (art.331) un client din România."""
    from core.d390 import TARI_UE
    tara = (tert_tara or "RO").strip().upper() or "RO"
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
            l["categorie_tva"] = NEPLATITOR["cod"]
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
        elif cat == "taxare_inversa" and tara != "RO":
            rele.append({"camp": camp, "eticheta": "Linia %d: categoria de TVA" % n, "cod": "CATEGORIE_TVA_TARA",
                         "mesaj": "Taxarea inversă din art.331 se aplică între persoane înregistrate în scopuri de TVA în România "
                                  "(țara clientului: %s)." % tara})
        l["categorie_tva"] = cat
    return rele


def pentru_formular(platitor):
    """Ce afișează formularul de emitere: lista (cod, etichetă) în ordinea de mai sus, numai pentru plătitor."""
    return [{"cod": k, "eticheta": v["eticheta"]} for k, v in CATEGORII.items()] if platitor is not False else []

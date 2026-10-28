# -*- coding: utf-8 -*-
"""TVA la încasare (CF art.282, OUG 8/2026) — motorul exigibilității la încasare / plată.

[lotul 10, deficiența 428, comanda Costin 10.1, PRIORITAR] „Construiește regimul pe firmă, cu data de la care se aplică [...]: facturile
emise poartă mențiunea obligatorie și înregistrează TVA pe 4428; fiecare încasare (bancă, casă, compensare) legată de factură mută
automat partea încasată în 4427; D300 și D394 urmează exigibilitatea; ieșirea din sistem face regularizarea. Verifică și partea de
cumpărare (furnizor cu TVA la încasare). Formularul manual rămâne doar pentru cazuri speciale.”

TEMEIUL (citit verbatim din `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, art.282 la 01.03.2026 și art.297):
  * CF art.282 alin.(3): „exigibilitatea taxei intervine la data încasării contravalorii integrale sau parțiale a livrării de bunuri ori a
    prestării de servicii, în cazul persoanelor impozabile care optează în acest sens, denumite în continuare persoane care aplică
    sistemul TVA la încasare.”
  * CF art.282 alin.(6): „nu aplică sistemul respectiv pentru următoarele operațiuni care intră sub incidența regulilor generale privind
    exigibilitatea TVA: a) livrările de bunuri/prestările de servicii pentru care beneficiarul este persoana obligată la plata taxei
    conform art. 307 alin. (2)-(6) sau art. 331; b) livrările de bunuri/prestările de servicii care sunt scutite de TVA; c) operațiunile
    supuse regimurilor speciale prevăzute la art. 311-313; d) livrările de bunuri/prestările de servicii pentru care beneficiarul este o
    persoană afiliată furnizorului/prestatorului potrivit art. 7 pct. 26.”
  * CF art.282 alin.(7) lit.b): „în cazul facturilor pentru contravaloarea totală [...] emise înainte de data ieșirii din sistemul de TVA
    la încasare, indiferent dacă acestea sunt ori nu încasate, pentru care faptul generator de taxă intervine după ieșirea din sistemul
    TVA la încasare, se continuă aplicarea sistemului, respectiv exigibilitatea taxei intervine conform alin. (3) și (5). În cazul
    facturilor pentru contravaloarea parțială [...] emise înainte de data ieșirii [...], se vor aplica prevederile alin. (3) și (5)
    numai pentru taxa aferentă contravalorii parțiale a livrărilor/prestărilor facturate înainte de ieșirea din sistem”; lit.a) (intrarea),
    simetric: facturile totale emise ÎNAINTE de intrare rămân pe regulile generale.
  * CF art.282 alin.(8): „fiecare încasare totală sau parțială se consideră că include și taxa aferentă.”
  * CF art.282 alin.(10) lit.a) pct.1–2: la anularea totală / parțială „se operează anularea [reducerea] taxei neexigibile aferente
    contravalorii pentru care nu a intervenit exigibilitatea taxei, iar în situația în care cuantumul taxei aferente anulării depășește
    taxa neexigibilă, pentru diferență exigibilitatea taxei intervine la data anulării operațiunii”.
  * CF art.297 alin.(2): „Dreptul de deducere a TVA aferente achizițiilor efectuate de o persoană impozabilă de la o persoană impozabilă
    care aplică sistemul TVA la încasare [...] este amânat până la data la care taxa aferentă bunurilor și serviciilor care i-au fost
    livrate/prestate a fost plătită furnizorului/prestatorului său.” alin.(3): același lucru pentru achizițiile persoanei care aplică
    sistemul, „chiar dacă o parte din operațiunile realizate [...] sunt excluse [...]. Aceste prevederi nu se aplică pentru achizițiile
    intracomunitare de bunuri, pentru importuri, pentru achizițiile de bunuri/servicii pentru care se aplică taxare inversă”.
  * CF art.319 alin.(20) lit.p): pe factură, „în cazul în care exigibilitatea TVA intervine la data încasării [...], mențiunea «TVA la
    încasare»”.

DECIZIA PE DATĂ, NU PE BIFA DE AZI. Regimul unei facturi se citește la DATA EI (`regim_tva_incasare.aplica_la(data_emitere)`), iar o
stornare urmează factura stornată (alin.(10): „regimul de impozitare [...] aceleași ca și ale operațiunii de bază”). Așa se aplică
alin.(7) fără ramuri proprii: factura emisă înainte de intrare rămâne pe 4427 chiar încasată după intrare; cea emisă în sistem rămâne
pe 4428 și se mută la încasare chiar după ieșire. `firma_profil.tva_la_incasare` (bifa „aplică azi”) nu mai decide nimic aici.

UN SINGUR PUNCT pentru mutare: `linii_la_incasare(cur, schema, factura_id, suma)` — chemat de reconcilierea bancară, de casă (și de
chitanță, prin casă) și de legarea ulterioară a unei operațiuni de casă. Partea exigibilă = TVA-ul facturii × suma / totalul ei
(alin.(8); pe o factură cu o singură cotă e chiar suta mărită, `tva_din_incasare`), plafonată la TVA-ul rămas neexigibil (citit din
carte: ce s-a mutat deja și ce au anulat stornările) — ultima încasare închide restul, fără bani rătăciți pe 4428.

Citirile stau în `core/repo_tva_incasare.py`; aici nu se scrie SQL.
"""
from decimal import Decimal, ROUND_HALF_UP

from core.nomenclator_status_factura import TIP_SOLD_PRELUAT as _TIP_PRELUAT   # [lotul 12, 252] factura deschisă preluată

_BAN = Decimal("0.01")

#: CF art.319 alin.(20) lit.p) — mențiunea obligatorie pe factura emisă în sistem (PDF și BT-22 din e-Factura)
MENTIUNE = "TVA la încasare"

REGIM_GENERAL = "general"
REGIM_INCASARE = "incasare"
REGIM_STORNO = "storno_incasare"


def tva_din_incasare(suma_incasata, cota):
    """TVA exigibil dintr-o incasare (suta marita): suma x cota/(100+cota)."""
    s = Decimal(str(suma_incasata))
    c = Decimal(str(cota))
    if s <= 0:
        # [R147] Suma încasată e baza din care se extrage TVA-ul exigibil prin suta mărită;
        # o sumă nulă sau negativă n-are din ce extrage.
        raise ValueError("Suma încasată trebuie să fie mai mare decât zero: din ea se "
                         "extrage TVA-ul exigibil, prin suta mărită.")
    from core import tva_calcul as _tc   # [lotul 11, decizia 10.3] regula unică: suta mărită, o rotunjire la ban
    return _tc.tva_din_total(s, c)


def tva_exigibil_alocari(alocari):
    """alocari: [{suma, cota_tva}] (sumele incasate alocate pe facturi/cote).
    Intoarce lista [{cota, tva}] agregata pe cota + total."""
    pe_cota = {}
    for a in alocari:
        c = Decimal(str(a["cota_tva"]))
        pe_cota[c] = pe_cota.get(c, Decimal("0")) + tva_din_incasare(a["suma"], c)
    linii = [{"cota": str(c), "tva": str(v)} for c, v in sorted(pe_cota.items())]
    total = sum(pe_cota.values(), Decimal("0"))
    return {"linii": linii, "total": total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)}


def plafon_la(data_iso):
    """Plafonul TVA la incasare valabil la o data, period-aware din common.COTE (fost petic 3-tier).
    OUG 8/2026: 5M de la 03.2026, 5.5M de la 2027; 4.5M anterior (PAS 2, valoare -> registru)."""
    from core import common as _c
    from datetime import date as _d
    return _c.cota("plafon_tva_incasare", _d.fromisoformat(str(data_iso)[:10]))[0]


def aloca_pe_cote(gross, linii, total_tva):
    """Împarte suma DECONTATĂ (gross, cu TVA) pe cotele facturii, proporțional cu ponderea gross a fiecărei cote (baza_cotă ×
    (100+cotă)/100) — CF art.282 alin.(8): fiecare încasare „include și taxa aferentă”. `linii` = [(cantitate, preț, cotă[, valoare_neta])];
    fără linii, o cotă dedusă din total/TVA. Sursa unică pentru D300 (rândurile) și D394 (tvaCol / tvaDed / tvaDedAI).

    [lotul 11, C82] `valoare_neta` = valoarea liniei scrisă PE FACTURĂ (BT-131 din XML-ul e-Factura, `factura_linii.valoare_neta`): la
    factura importată ea e baza liniei — prețul unitar ținut la 2 zecimale nu o reface (1.000 × 0,004 = 4,00 lei, prețul 0,00). NULL
    (factura făcută în aplicație) -> cantitate × preț, ca până acum."""
    if linii:
        g = {}
        for (cant, pret, cota, *vn) in linii:
            if cota is None:
                continue
            ci = int(round(float(cota)))  # ROTUNJIRE PE COTA (nu pe suma): cotele fiscale RO sunt numere intregi, bancar==aritmetic
            vn = vn[0] if vn else None
            baza = Decimal(str(vn)) if vn not in (None, "") else Decimal(str(cant)) * Decimal(str(pret))   # [C82] BT-131 când linia îl are
            g[ci] = g.get(ci, Decimal(0)) + baza * (100 + ci) / 100
        tg = sum(g.values(), Decimal(0))
        if tg > 0:
            return [{"suma": gross * gc / tg, "cota": ci} for ci, gc in g.items()]
    total, tva = (total_tva or (0, 0))
    base = Decimal(str(total or 0)) - Decimal(str(tva or 0))
    ci = int(round(float(tva) / float(base) * 100)) if (base and tva) else None  # ROTUNJIRE PE COTA (nu pe suma): cotele fiscale RO sunt numere intregi, bancar==aritmetic
    return [{"suma": gross, "cota": ci}] if ci else []


# ══════════════════════════════════════════════════════════════════ REGIMUL FACTURII (pe data ei)
def motiv_excludere(f, cote):
    """De ce o factură EMISĂ a unei firme în sistem rămâne totuși pe regulile generale (CF art.282 alin.(6)), sau None.
    `cote` = cotele liniilor (procente); listă goală / None = factură fără linii (antet), judecată după TVA-ul antetului. Pur.

    Ce acoperă datele aplicației: lit.a) taxarea inversă (`facturi.taxare_inversa`); lit.b) scutirile — o factură fără nicio linie cu cotă
    pozitivă n-are TVA de amânat (liniile cu 0% ale unei facturi mixte nu ajung pe 4428 și se declară la emitere); lit.d) beneficiarul
    afiliat (`beneficiar_afiliat`, dacă factura îl poartă). Lit.c) (regimurile speciale art.311-313: agenții de turism, marja, aurul) nu
    trece pe aici: operațiunile alea au rutele lor, care scriu direct 4427, fără factură contată prin acest motor."""
    if f.get("taxare_inversa"):
        return "taxare inversă (CF art.282 alin.(6) lit.a)"
    if f.get("beneficiar_afiliat"):
        return "beneficiar afiliat (CF art.282 alin.(6) lit.d)"
    if cote and not any(c is not None and Decimal(str(c)) > 0 for c in cote):
        return "operațiune scutită / fără TVA (CF art.282 alin.(6) lit.b)"
    return None


def regim_din_date(f, cote, firma_in_sistem, regim_original=None):
    """Regimul unei facturi, din datele ei. Pur — `regim` îl cheamă cu ce a citit.

    `firma_in_sistem` = firma aplica sistemul la DATA facturii; `regim_original` = regimul facturii stornate (numai pe o stornare).
    EMISĂ: `incasare` dacă firma era în sistem la data facturii, factura are TVA pozitiv și nu e exclusă (alin.(6)); o factură cu TVA
    negativ fără factură stornată (regularizarea unui avans) rămâne pe regulile generale — avansul a fost încasat, deci TVA-ul lui era
    deja exigibil. PRIMITĂ: deducerea e amânată (`incasare`) dacă furnizorul aplică sistemul la data facturii (art.297 alin.(2)) sau
    firma îl aplică (alin.(3)), afară de taxarea inversă și de achizițiile din afara țării (intracomunitare, importuri — alin.(3) teza
    finală). STORNARE: urmează factura stornată (alin.(10)).
    [lotul 12, deficiența 252, decizia Costin 12.3 pct.5] FACTURA DESCHISĂ PRELUATĂ (`tip = 'preluata'`): regimul e hotărât o dată, la
    preluare (`solduri_parteneri_api.cu_regimul_tva`: coloana „TVA la încasare” a fișierului, altfel regimul firmei la data facturii), și
    înghețat în TVA-ul ei = TVA-ul încă neexigibil / nededus din rest. TVA pozitiv -> `incasare` (încasarea / plata îl mută și D300 / D394
    îl declară — CF art.282 alin.(3), (8); art.297 alin.(2)-(3)); 0 -> regulile generale (TVA-ul era deja exigibil în programul vechi)."""
    tip = f.get("tip") or "factura"
    tva = Decimal(str(f.get("tva_lei") if f.get("tva_lei") is not None else (f.get("tva") or 0)))
    if tip == _TIP_PRELUAT:
        return REGIM_INCASARE if tva > 0 else REGIM_GENERAL
    if tip != "factura":
        return REGIM_GENERAL
    if f.get("storno_din_id"):
        return REGIM_STORNO if regim_original == REGIM_INCASARE else REGIM_GENERAL
    if tva <= 0:
        return REGIM_GENERAL
    if f.get("directie") == "emisa":
        if not firma_in_sistem or motiv_excludere(f, cote):
            return REGIM_GENERAL
        return REGIM_INCASARE
    if f.get("taxare_inversa") or (f.get("tert_tara") or "RO").upper() != "RO":
        return REGIM_GENERAL
    return REGIM_INCASARE if (f.get("furnizor_tva_incasare") or firma_in_sistem) else REGIM_GENERAL


def firma_in_sistem_la(cur, schema, data):
    """Firma aplica sistemul la `data` — perioadele din „Date firmă” (`core/regim_tva_incasare.aplica_la`)."""
    from core import regim_tva_incasare as _rg, repo_tva_incasare as _rp
    with _rp.search_path(cur, schema):
        return _rg.aplica_la(cur, data)


def firma_in_sistem_in(cur, schema, inceput, sfarsit):
    """Firma aplica sistemul într-o zi din fereastra [inceput, sfarsit) — D394 `sistemTVA`, D300 (secțiunea A/B). Intrarea și ieșirea
    cad la începutul unei perioade fiscale (CF art.282 alin.(3^1), (5)), deci în practică perioada e întreagă într-un regim."""
    import datetime as _dt
    from core import regim_tva_incasare as _rg, repo_tva_incasare as _rp
    i = _dt.date.fromisoformat(str(inceput)[:10])
    s = _dt.date.fromisoformat(str(sfarsit)[:10]) - _dt.timedelta(days=1)
    with _rp.search_path(cur, schema):
        per = _rg.perioade(cur)
        if not per:
            # aceeași tranziție ca `regim_tva_incasare.aplica_la` (sursa unică a INTERPRETĂRII): fără nicio perioadă, indicatorul vechi
            # `firma_profil.tva_la_incasare` — altfel facturile ies „în sistem” (regimul, pe `aplica_la`) iar perioada „în afara lui”
            return _rg.aplica_la(cur, i)
    return any(p["de_la"] <= s and (p["pana_la"] is None or p["pana_la"] >= i) for p in per)


def text_regim_emitere(data, aplica, perioade, fara_data=False):
    """PURĂ. [lotul 11, deficiența 428, retestul Costin pe producție 21.10.2026] Ce spune ecranul de emitere despre sistemul TVA la încasare
    la DATA FACTURII — {aplica, mesaj} sau None (firma n-are nicio perioadă în sistem și nu-l aplică).

    De ce: pe producție (F6, 21.10.2026) perioada era „de la 01.11.2026”, iar factura din 21.10.2026 a ieșit — corect — pe regulile
    generale (4427, fără mențiune); niciun ecran nu spunea însă asta, iar „Configurare emitere” arăta sistemul numai dacă se aplica AZI.
    Temeiul:
      * CF art.282 alin.(3): „exigibilitatea taxei intervine la data încasării contravalorii integrale sau parțiale [...], în cazul
        persoanelor impozabile care optează în acest sens”;
      * CF art.282 alin.(7) lit.a): „în cazul facturilor pentru contravaloarea totală a livrării de bunuri ori a prestării de servicii
        emise înainte de data intrării în sistemul de TVA la încasare, indiferent dacă acestea sunt sau nu încasate, pentru care faptul
        generator de taxă intervine după intrarea în sistemul TVA la încasare, nu se aplică prevederile alin. (3) și (5)”;
      * CF art.319 alin.(20) lit.p): pe factură, „în cazul în care exigibilitatea TVA intervine la data încasării [...], mențiunea «TVA la
        încasare»”.
    `perioade` = [{de_la: date, pana_la: date|None}] (ordine cronologică); `aplica` = decizia motorului la `data` (`firma_in_sistem_la`,
    sursa unică — aici numai textul ei); `fara_data` = indicatorul vechi, fără perioadă scrisă."""
    import datetime as _dt
    from core.pdf_util import data_ro
    d = data if isinstance(data, _dt.date) else _dt.date.fromisoformat(str(data)[:10])
    if not perioade and not aplica:
        return None
    zi = data_ro(d)
    from core import afirmatii as _af

    def _fapt(aplica_, mesaj_):
        # [lotul 11, decizia 21.08: afirmațiile despre datele firmei sunt obiecte cu `fel`] regimul TVA al facturii la data ei — un fapt
        # despre firmă, cu domeniul (factura de la data aceea) și pe ce se sprijină; `mesaj` = același text, cheia citită de ecran
        return _af.afirmatie("fapt", "regim_tva_incasare_la_emitere", mesaj_, aplica=aplica_, mesaj=mesaj_, unde="factura din %s" % zi,
                             temei_completitudine="perioadele sistemului TVA la încasare scrise în Date firmă și decizia aplicației "
                                                  "la data facturii")
    if aplica:
        mesaj = ("Factura din %s: firma aplică sistemul TVA la încasare. TVA-ul facturii se înregistrează pe 4428 (neexigibil) și devine "
                 "exigibil la încasare; pe factură apare mențiunea „%s” (Cod fiscal art. 282 alin. (3), art. 319 alin. (20) lit. p)). Rămân "
                 "pe regulile generale taxarea inversă, livrările scutite și clientul afiliat (art. 282 alin. (6))." % (zi, MENTIUNE))
        if fara_data:
            mesaj += " Data de la care firma aplică sistemul nu e scrisă în Date firmă: scrie-o acolo."
        return _fapt(True, mesaj)
    urm = next((p for p in perioade if p["de_la"] > d), None)
    if urm:
        return _fapt(False, (
            "Factura din %s: firma aplică sistemul TVA la încasare abia de la %s. O factură emisă înainte de intrarea în sistem rămâne pe "
            "regulile generale: TVA exigibil la emitere (4427), fără mențiunea „%s” (Cod fiscal art. 282 alin. (7) lit. a)). Dacă firma "
            "aplica sistemul și la această dată, corectează perioada în Date firmă." % (zi, data_ro(urm["de_la"]), MENTIUNE)))
    ies = [p for p in perioade if p.get("pana_la") and p["pana_la"] < d]
    if ies:
        return _fapt(False, (
            "Factura din %s: firma a ieșit din sistemul TVA la încasare la %s. TVA-ul facturii e exigibil la emitere (4427), fără mențiunea "
            "„%s”; facturile emise în sistem rămân în sistem până la încasare (Cod fiscal art. 282 alin. (7) lit. b))."
            % (zi, data_ro(ies[-1]["pana_la"]), MENTIUNE)))
    return None


def refuz_nota_tva_la_emitere(cur, schema, data, ce):
    """[lotul 11, 428 — „pe TOATE drumurile de emitere”] Mesajul refuzului pentru o notă din Operațiuni care ar credita TVA-ul unei livrări
    direct în 4427 (vânzarea de produse finite, chiria încasată, refacturarea, autofactura RetuRO) la o firmă care aplică sistemul TVA la
    încasare la `data`; None dacă firma nu-l aplică. Nota n-are factură, deci nici încasarea n-o poate muta din 4428 în 4427, nici D300 /
    D394 n-o văd: livrarea intră pe drumul facturii, unde regimul, mențiunea, exigibilitatea și declarațiile funcționează. Temei: CF
    art.282 alin.(3) — „exigibilitatea taxei intervine la data încasării”, nu la emitere."""
    if not firma_in_sistem_la(cur, schema, data):
        return None
    from core.pdf_util import data_ro
    return ("Firma aplică sistemul TVA la încasare la %s: %s se înregistrează ca factură emisă (Emite factură, sau factura emisă în alt "
            "program adăugată în Facturi), nu ca notă. Pe factură TVA-ul merge pe 4428, devine exigibil la încasare și intră în D300 și "
            "D394 (Cod fiscal art. 282 alin. (3)); nota de aici l-ar pune direct pe 4427, exigibil la emitere." % (data_ro(data), ce))


def refuz_nota_tva_la_primire(cur, schema, data, linii):
    """[14.2, 714] Mesajul refuzului pentru o notă din Operațiuni care ar scrie TVA-ul unei ACHIZIȚII direct în 4426 (4426 = 401 / 404:
    factura utilităților refacturate, chiria plătită, rata de leasing) la o firmă care aplică sistemul TVA la încasare la `data`; None
    altfel. Oglinda lui `refuz_nota_tva_la_emitere`. Temei: CF art.297 alin.(3) — dreptul de deducere a TVA aferente achizițiilor unei
    persoane care aplică sistemul „este amânat până la data la care taxa […] a fost plătită furnizorului”; excepțiile (achiziții
    intracomunitare, importuri, taxare inversă) nu trec prin notele de aici. Nota n-are factură, deci plata n-o poate muta din 4428 în
    4426, iar D300 n-o vede amânată: achiziția intră pe drumul facturii primite, unde 4428 -> 4426 se face la plată, proporțional.
    `linii` = (debit, credit, suma) ale notelor de scris."""
    if not any(dd == "4426" and str(cc)[:3] in ("401", "404") for dd, cc, _s in linii):
        return None
    if not firma_in_sistem_la(cur, schema, data):
        return None
    from core.pdf_util import data_ro
    return ("Firma aplică sistemul TVA la încasare la %s: factura furnizorului se înregistrează în Facturi primite, nu ca notă. Acolo TVA-ul "
            "merge pe 4428 și se deduce (4426) abia când plătești factura, proporțional cu plata (Cod fiscal art. 297 alin. (3)); nota de "
            "aici l-ar deduce imediat." % data_ro(data))


def regim_emitere_la(cur, schema, data):
    """[lotul 11, 428] `text_regim_emitere` cu perioadele și decizia citite pe firmă — aceeași `regim_tva_incasare.aplica_la` ca motorul
    contării, nu o a doua definiție. Pentru ecranul de emitere (`facturi/numerotare?data=`)."""
    from core import regim_tva_incasare as _rg, repo_tva_incasare as _rp
    with _rp.search_path(cur, schema):
        per = _rg.perioade(cur)
        aplica = _rg.aplica_la(cur, data)
    return text_regim_emitere(data, aplica, per, fara_data=bool(aplica and not per))


#: ce citește regimul de pe antetul facturii (`repo_tva_incasare.factura`)
_CHEI_REGIM = ("directie", "tip", "data_emitere", "tva", "taxare_inversa", "tert_tara", "furnizor_tva_incasare", "storno_din_id",
               "beneficiar_afiliat")


def regim(cur, schema, f):
    """Regimul facturii `f` (dict cu antetul, sau id) la data ei. Vezi `regim_din_date`.

    [lotul 10, 428, decizia „Bifă pe client”] Un dict căruia îi lipsește vreun câmp al regimului (`_CHEI_REGIM` — ex. detaliul facturii,
    care nu selecta `beneficiar_afiliat`) se recitește din repository: regimul e al FACTURII, nu al selecției apelantului. Altfel factura
    către un client afiliat (CF art.282 alin.(6) lit.d) purta mențiunea «TVA la încasare» pe PDF deși TVA-ul ei e exigibil la emitere."""
    from core import repo_tva_incasare as _rp
    if isinstance(f, dict) and f.get("id") is not None and any(k not in f for k in _CHEI_REGIM):
        f = f["id"]
    if not isinstance(f, dict):
        f = _rp.factura(cur, schema, f)
        if not f:
            return REGIM_GENERAL
    if f.get("storno_din_id"):
        orig = _rp.factura(cur, schema, f["storno_din_id"])
        return regim_din_date(f, None, False, regim(cur, schema, orig) if orig else None)
    if f.get("tip") == _TIP_PRELUAT:   # [252, 12.3 pct.5] regimul înghețat la preluare, în TVA-ul ei (`regim_din_date`)
        return regim_din_date(f, None, False)
    if (f.get("tip") or "factura") != "factura" or not f.get("data_emitere"):
        return REGIM_GENERAL
    cote = _rp.cote_linii(cur, schema, f["id"]) if f.get("directie") == "emisa" and f.get("id") else None
    return regim_din_date(f, cote, firma_in_sistem_la(cur, schema, f["data_emitere"]))


def _tva_si_total_lei(f):
    from core import sume_lei as _sl
    total, tva = _sl.antet_lei(f)
    return total, tva


def rest_neexigibil(cur, schema, f, pana_la=None, fara_storno=None, doar_validate=False):
    """TVA-ul facturii încă neexigibil (emisă: rămas pe 4428 până la încasare) / nededus (primită: pe 4428 până la plată), citit din
    carte: TVA-ul facturii − ce s-a mutat deja (`repo.exigibil_deja`) − ce au anulat stornările ei (alin.(10)), la `pana_la` inclusiv."""
    from core import repo_tva_incasare as _rp
    _total, tva = _tva_si_total_lei(f)
    deja = _rp.exigibil_deja(cur, schema, f["id"], f["directie"], pana_la, doar_validate)
    anulat = _rp.anulat_prin_stornari(cur, schema, f["id"], f["directie"], pana_la=pana_la, fara=fara_storno)
    return tva - deja - anulat


def parte_exigibila(tva_total, total, suma, rest):
    """Partea de TVA care devine exigibilă / deductibilă la o încasare / plată de `suma` (cu TVA) — CF art.282 alin.(8): „fiecare încasare
    totală sau parțială se consideră că include și taxa aferentă” —, plafonată la `rest` (TVA-ul rămas neexigibil). Pur.
    Rotunjire aritmetică la ban (ROUND_HALF_UP)."""
    s, t, tot, r = (Decimal(str(x)) for x in (suma, tva_total, total, rest))
    if s <= 0 or t <= 0 or tot <= 0 or r <= 0:
        return Decimal(0)
    parte = (t * s / tot).quantize(_BAN, rounding=ROUND_HALF_UP)
    return min(parte, r)


def linii_la_incasare(cur, schema, factura_id, suma):
    """PUNCTUL UNIC: liniile de exigibilitate ale unei încasări / plăți de `suma` legate de factură — [(debit, credit, suma)] sau [].

    Emisă în sistem: 4428 = 4427 (CF art.282 alin.(3), (8)). Primită cu deducerea amânată: 4426 = 4428 (CF art.297 alin.(2)-(3)). Factura
    pe regulile generale (inclusiv emisă înainte de intrare, exclusă prin alin.(6), stornare) -> []. Linia intră pe nota încasării, cu
    data ei: exigibilitatea intervine la data încasării."""
    from core import repo_tva_incasare as _rp
    f = _rp.factura(cur, schema, factura_id)
    if not f or regim(cur, schema, f) != REGIM_INCASARE:
        return []
    total, tva = _tva_si_total_lei(f)
    parte = parte_exigibila(tva, total, suma, rest_neexigibil(cur, schema, f))
    if parte <= 0:
        return []
    d, c = _rp.LINIE_EMISA if f["directie"] == "emisa" else _rp.LINIE_PRIMITA
    return [(d, c, parte)]


# ══════════════════════════════════════════════════════════════════ STORNAREA (alin.(10))
def imparte_anulare(tva_anulat, rest):
    """Anularea / reducerea unei operațiuni în sistem: (partea care anulează TVA neexigibil, partea exigibilă la data anulării), ambele
    pozitive, din TVA-ul anulat și TVA-ul rămas neexigibil pe factura de bază. CF art.282 alin.(10) lit.a) pct.2: „se operează reducerea
    taxei neexigibile aferente contravalorii pentru care nu a intervenit exigibilitatea taxei, iar în situația în care cuantumul taxei
    aferente anulării depășește taxa neexigibilă, pentru diferență exigibilitatea taxei intervine la data anulării”. Pur."""
    t = abs(Decimal(str(tva_anulat)))
    r = max(Decimal(str(rest)), Decimal(0))
    neexig = min(t, r)
    return neexig, t - neexig


def note_storno(note, directie, neexigibil):
    """Notele de contare ale unei stornări în sistem (generate pe 4428, cu minus), cu TVA-ul împărțit după `imparte_anulare`: până la
    `neexigibil` rămân pe 4428 (anulează taxa neexigibilă), restul trece pe 4427 (emisă) / 4426 (primită) — exigibil / deductibil la data
    stornării. Pur; păstrează ordinea și conturile terțului."""
    ramas = abs(Decimal(str(neexigibil)))
    out = []
    for n in note:
        e_tva = (n["credit"] == "4428") if directie == "emisa" else (n["debit"] == "4428")
        if not e_tva:
            out.append(n)
            continue
        s = abs(Decimal(str(n["suma"])))
        pe_4428 = min(s, ramas)
        ramas -= pe_4428
        rest = s - pe_4428
        if pe_4428:
            out.append(dict(n, suma=-pe_4428))
        if rest:
            out.append(dict(n, suma=-rest, **({"credit": "4427"} if directie == "emisa" else {"debit": "4426"})))
    return out


def anulare_storno(cur, schema, f_storno):
    """(neexigibil anulat, exigibil la anulare) pentru o stornare în sistem, din TVA-ul ei și restul facturii stornate LA DATA stornării
    (încasările de până atunci, stornările dinaintea ei). Aceeași împărțire la contare și în D300, oricând s-ar regenera decontul."""
    from core import repo_tva_incasare as _rp
    orig = _rp.factura(cur, schema, f_storno["storno_din_id"])
    _t, tva = _tva_si_total_lei(f_storno)
    return imparte_anulare(tva, rest_neexigibil(cur, schema, orig, pana_la=f_storno["data_emitere"], fara_storno=f_storno["id"]))


# ══════════════════════════════════════════════════════════════════ IEȘIREA DIN SISTEM (alin.(7))
CE_SE_INTAMPLA_EMISA = (
    "Rămâne în sistem: TVA-ul de pe 4428 devine exigibil la încasare, și după ieșire (CF art.282 alin.(7) lit.b: „se continuă aplicarea "
    "sistemului, respectiv exigibilitatea taxei intervine conform alin. (3) și (5)”).")
CE_SE_INTAMPLA_PRIMITA = (
    "Deducerea rămâne amânată până la plată (CF art.297 alin.(2)-(3)): TVA-ul trece de pe 4428 pe 4426 la plata furnizorului.")


def neexigibile_la(cur, schema, data, clauza_status, doar_validate=False):
    """Facturile cu TVA rămas pe 4428 la `data` (inclusiv): emisele în sistem neîncasate integral și primitele cu deducerea amânată
    neplătite integral — cu restul fiecăreia și ce se întâmplă cu ea după ieșirea din sistem (alin.(7)). NU mută nimic: la ieșire,
    alin.(7) lit.b) cere continuarea sistemului pentru facturile emise înainte de ieșire, nu o regularizare a TVA-ului neexigibil.
    `clauza_status` = filtrul de facturi declarabile (`nomenclator_status_factura.clauza_sql("f")`). Sursa unică pentru lista de la
    ieșire și pentru secțiunea A/B a D300 („TVA rămasă neexigibilă [...] existentă în sold la sfârșitul perioadei”)."""
    from core import repo_tva_incasare as _rp, sume_lei as _sl
    out = []
    for fid in _rp.facturi_candidate(cur, schema, data, clauza_status):
        f = _rp.factura(cur, schema, fid)
        if regim(cur, schema, f) != REGIM_INCASARE:
            continue
        try:
            total, tva = _tva_si_total_lei(f)
        except _sl.LipsaCurs:
            continue
        deja = _rp.exigibil_deja(cur, schema, f["id"], f["directie"], data, doar_validate)
        anulat = _rp.anulat_prin_stornari(cur, schema, f["id"], f["directie"], pana_la=data)
        rest = tva - deja - anulat
        if rest <= 0:
            continue
        out.append({"factura_id": f["id"], "directie": f["directie"], "serie": f.get("serie"), "numar": f.get("numar"),
                    "data_emitere": str(f["data_emitere"])[:10], "total": str(total), "tva": str(tva), "exigibil": str(deja + anulat),
                    "rest_neexigibil": str(rest),
                    "baza_ramasa": str(((total - tva) * rest / tva).quantize(_BAN, rounding=ROUND_HALF_UP)),
                    "ce_se_intampla": CE_SE_INTAMPLA_EMISA if f["directie"] == "emisa" else CE_SE_INTAMPLA_PRIMITA})
    return out

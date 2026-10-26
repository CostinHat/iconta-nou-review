"""
core/solduri_parteneri_api.py — import solduri parteneri (defalcare 4111/401 per client/furnizor).

Citeste un fisier (.xlsx/.csv) cu coloanele: Cont, CUI, Denumire, Sold debitor, Sold creditor.
Un rand = un partener pe un cont. Se salveaza in schema tenantului (tabel solduri_parteneri).

[lotul 12, deficiența 252] Și forma PE FACTURI a situației clienților / furnizorilor (SAGA: Nr. factură, Data, Scadență, Sumă neachitată):
un rând = o factură deschisă; rândurile partenerului se adună în soldul lui (`grupeaza_pe_parteneri`), cu facturile în `documente`. La
salvare, facturile deschise intră în `facturi` cu `tip = 'preluata'` (`nomenclator_status_factura.TIP_SOLD_PRELUAT`) — din forma pe
solduri, soldul întreg al partenerului de pe 4111 / 401, ca un document „Sold la <data preluării>” (`documente_din_randuri`). Scadențarul
le arată, banca / casa / compensările le sting; nu se contează și nu intră în declarații (soldul lor e deja în soldurile inițiale).

Coerenta cu stratul 2 (solduri_initiale): suma soldurilor partenerilor pe contul sintetic
(4111, 401) se compara cu soldul sintetic din balanta (analiticele 4111.X grupate pe radacina).
Informativ, NU blocant — contabilul decide.

"""
# [E2b, 15.09.2026] Tranzactia e a APELANTULUI: `db.get_conn` comite la iesirea din bloc, iar un
# `commit` aici ar taia tranzactia lui in doua (P4). Depozitul primeste conexiunea si scrie; nu
# deschide, nu comite.
from __future__ import annotations


from core.numere import numar as _numar  # sursa unica (15.07.2026, vezi core/numere.py)
from core import pdf_util as _pu   # [lotul 11, C100] soldul cu felul lui (`pdf_util.sold`)
from core.migrare_api import respinge  # [P8/C] respingerea e o afirmatie, cu regula din nomenclator
from core.common import cate as _cate
from core import chei_unice as _chei   # [lotul 10, C73] cheia naturală dublată -> refuz numit, nu 500
from core import cui_forma as _forma_cui   # [lotul 11, decizia Costin 10.3 pct.4] CUI-ul în forma păstrată: fără „RO”, fără spații
from core.nomenclator_status_factura import TIP_SOLD_PRELUAT as _TIP_PRELUAT   # [lotul 12, 252] facturile deschise preluate


def _radacina(cont):
    """Sinteticul de baza al unui cont: '4111.ALPHA' -> '4111', '401' -> '401'."""
    return str(cont).split(".")[0].strip()


# [14.10.2026, comanda Costin „Importul din SAGA”, verbatim în DECIZII] Fișierul trece prin `core.import_tabel` (format, codare,
# antet pe unul sau două rânduri, coloane pe cuvinte întregi). Antetele SAGA vin din manualul SAGA C: ecranul Terți are „Cod
# fiscal/ CNP” și „Cont analitic” (401.00001 / 4111.00001), iar „Situație clienți / furnizori” are „Neachitat final” — soldul
# fiecărui terț, fără coloana Cont (contul îl dă ecranul din care s-a exportat: clienți sau furnizori).
from core import import_tabel as _it

CAMPURI = {
    "cont": ("cont analitic", "simbol cont", "=cont", "=simbol"),
    "cui": ("cod fiscal cnp", "cod fiscal", "cui", "cif", "cnp", "cod unic de inregistrare"),
    "denumire": ("denumire partener", "denumire tert", "denumire", "partener", "tert", "client", "furnizor", "nume"),
    "debit": ("debit*",),
    "credit": ("credit*",),
    "sold": ("neachitat final", "suma neachitata", "rest neachitat", "neachitat", "sold final", "sold", "rest de plata", "rest de incasat"),
    # [lotul 12, deficiența 252] forma PE FACTURI a situației clienților / furnizorilor (SAGA: Nr. factură, Data, Scadență, Sumă neachitată):
    # un rând = o factură deschisă a partenerului, cu restul ei neîncasat / neplătit la data preluării
    "numar_doc": ("nr factura", "numar factura", "nr document", "numar document", "nr doc", "=factura", "=document"),
    "scadenta": ("data scadenta", "data scadentei", "scadenta", "termen de plata", "termen plata"),
    "data_doc": ("data factura", "data facturii", "data document", "data documentului", "data emiterii", "data emitere", "=data"),
    # [lotul 12, deficiența 252, decizia Costin 12.3 pct.5: „coloana TVA la încasare e opțională în fișierul de preluare; dacă lipsește,
    # se ia regimul firmei la data facturii”] da / nu pe fiecare factură deschisă (sau pe soldul partenerului, în forma pe solduri)
    "tva_incasare": ("tva la incasare", "sistem tva la incasare", "tva incasare", "=tvai"),
    # [lotul 13, deficiența 252, decizia Costin 13.1, verbatim: „la facturile preluate, dacă fișierul are suma TVA, se ia suma din fișier;
    # doar unde lipsește se calculează la cota standard, iar factura e marcată «de verificat».”] suma TVA din restul facturii (opțională)
    "tva": ("=tva", "suma tva", "valoare tva", "tva neexigibil", "tva neexigibila", "tva din rest"),
}

#: [252, 12.3 pct.5] valorile acceptate în coloana „TVA la încasare” (după `import_tabel.norm`: fără diacritice, litere mici); celula
#: goală = nespus -> regimul firmei la data facturii, ca atunci când coloana lipsește
VALORI_TVA_INCASARE = {True: ("da", "d", "1", "x", "true", "yes", "y"), False: ("nu", "n", "0", "false", "no")}


def valoare_tva_incasare(text):
    """PURĂ. [252, 12.3 pct.5] Celula „TVA la încasare” -> True / False / None (goală). Altă valoare -> ValueError: nu se ghicește."""
    t = _it.norm(text)
    if not t:
        return None
    for v, forme in VALORI_TVA_INCASARE.items():
        if t in forme:
            return v
    raise ValueError(text)

# Natura contului de parteneri: pe ce parte stă soldul lui obișnuit. Folosită numai când fișierul are O SINGURĂ coloană de sold
# („Neachitat final”) — atunci partea o dă contul, iar o valoare negativă trece pe partea cealaltă.
_DEBITOARE = ("4111", "4118", "409", "4091", "4092", "4093")
_CREDITOARE = ("401", "419")
CONTURI_ALESE = ("4111", "401")      # ce se poate alege pe ecran când fișierul n-are coloana Cont (situația clienților / furnizorilor)



def _ignorat(nr, motiv, temei):
    """[comanda Costin 8.2 pct.4: „orice rând citit e afișat sau semnalat cu motiv”] rândul din fișier care nu intră, spus — o afirmație
    tipată despre rândul acela (`fapt`, domeniul `Unde("rand")`), cu ce s-a citit din el ca temei."""
    from core.afirmatii import afirmatie
    from core.unde import Unde
    return afirmatie("fapt", "rând ignorat", motiv, unde=Unde("rand", nr), rand=nr, temei_completitudine=temei)

def extrage(continut, nume_fisier="", cont_implicit=None, ignorate=None):
    """
    Intoarce [{cont, cui, denumire, debit, credit}] din fisierul de parteneri.

    Coloanele: Cont (sau `cont_implicit`, ales pe ecran, când fișierul n-are coloana), CUI / CNP, Denumire, și fie perechea
    debit / credit (la o balanță completă: perechea soldului FINAL), fie o singură coloană de sold („Neachitat final”).
    Rândurile de total și cele cu sold 0 nu sunt parteneri — nu intră.
    """
    brut = _it.citeste(continut, nume_fisier)
    if not brut or all(_it.rand_gol(r) for r in brut):
        return []
    antet, start = _it.gaseste_antet(brut, CAMPURI, obligatorii=("denumire",), nume_fisier=nume_fisier)
    i_cont = _it.coloana(antet, CAMPURI["cont"], camp="cont")
    i_cui = _it.coloana(antet, CAMPURI["cui"], exclus=(i_cont,), camp="CUI / CNP")
    # denumirea se cauta DUPA cont si cui, sarind peste coloanele lor („CUI partener” nu e denumirea)
    i_den = _it.coloana(antet, CAMPURI["denumire"], exclus=(i_cont, i_cui), camp="denumire")
    are_dc = any(_it._e_debit(h) or _it._e_credit(h) for h in antet if h)
    i_deb = i_cre = i_sold = -1
    if are_dc:
        i_deb, i_cre = _it.pereche_sold_final(antet, nume_fisier)
    else:
        i_sold = _it.coloana(antet, CAMPURI["sold"], camp="sold")
        if i_sold < 0:
            raise _it.FisierNecitit("Fișierul %s n-are nici coloane debit / credit, nici o coloană de sold („Neachitat "
                                    "final”, „Sold final”) — nu se poate citi soldul partenerilor."
                                    % ("«%s»" % nume_fisier if nume_fisier else "trimis"))
    # [252] coloana „Nr. factură” face din fiecare rând o factură deschisă; data ei e obligatorie, scadența nu
    i_nr = _it.coloana(antet, CAMPURI["numar_doc"], exclus=(i_cont, i_cui, i_den), camp="nr. factură")
    i_scad = _it.coloana(antet, CAMPURI["scadenta"], exclus=(i_cont, i_cui, i_den, i_nr), camp="scadență") if i_nr >= 0 else -1
    i_data = _it.coloana(antet, CAMPURI["data_doc"], exclus=(i_cont, i_cui, i_den, i_nr, i_scad), camp="data facturii") if i_nr >= 0 else -1
    # [252, 12.3 pct.5] coloana opțională „TVA la încasare” (pe ambele forme)
    i_tvai = _it.coloana(antet, CAMPURI["tva_incasare"], exclus=(i_cont, i_cui, i_den, i_nr, i_scad, i_data), camp="TVA la încasare")
    # [lotul 13, 252, decizia Costin 13.1] coloana opțională a sumei TVA din restul facturii (pe ambele forme)
    i_tva = _it.coloana(antet, CAMPURI["tva"], exclus=(i_cont, i_cui, i_den, i_nr, i_scad, i_data, i_tvai, i_deb, i_cre, i_sold),
                        camp="suma TVA")
    if i_nr >= 0 and i_data < 0:
        raise _it.FisierNecitit("Fișierul %s are coloana numărului facturii, dar nu și coloana „Data” a facturii. Adaugă data fiecărei "
                                "facturi și încarcă-l din nou." % ("«%s»" % nume_fisier if nume_fisier else "trimis"))
    cont_ales = str(cont_implicit or "").strip()
    if i_cont < 0 and cont_ales not in CONTURI_ALESE:
        raise _it.FisierNecitit("Fișierul %s n-are coloana „Cont”. Alege din listă contul partenerilor din fișier (4111 — "
                                "situația clienților, 401 — situația furnizorilor) și încarcă-l din nou."
                                % ("«%s»" % nume_fisier if nume_fisier else "trimis"))

    out = []
    for nr, r in enumerate(brut[start:], start=start + 1):
        if _it.rand_gol(r):
            continue
        den = _it.celula(r, i_den)
        cui = _forma_cui.stocare(_it.celula(r, i_cui)) or ""   # forma unică (înainte: `_curata_cui`, o normalizare locală paralelă)
        cont = _it.celula(r, i_cont) if i_cont >= 0 else cont_ales
        if not cui and (not den or _it.norm(den).startswith("total")):
            # rând de total / titlu, nu partener — [comanda Costin 8.2 pct.4] spus, nu sărit în tăcere
            if ignorate is not None:
                ignorate.append(_ignorat(nr, "rând de total sau de titlu („%s”) — nu e un partener" % (den or "gol"),
                                         "rândul n-are cod fiscal, iar denumirea lipsește sau începe cu „total”"))
            continue
        try:
            if i_sold >= 0:
                s = _numar(_it.valoare(r, i_sold), strict=True)
                debitor = _radacina(cont) in _DEBITOARE or (_radacina(cont) not in _CREDITOARE and s >= 0)
                deb, cre = ((s, 0.0) if s >= 0 else (0.0, -s)) if debitor else ((0.0, s) if s >= 0 else (-s, 0.0))
            else:
                deb = _numar(_it.valoare(r, i_deb), strict=True) if i_deb >= 0 else 0.0
                cre = _numar(_it.valoare(r, i_cre), strict=True) if i_cre >= 0 else 0.0
        except ValueError:
            raise _it.FisierNecitit("Rândul %d (%s): soldul nu e un număr. Corectează celula și încarcă fișierul din nou."
                                    % (nr, den or cui or "?"))
        if round(deb, 2) == 0 and round(cre, 2) == 0:  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
            # partener fără sold: nu intră în soldurile inițiale — [comanda Costin 8.2 pct.4] spus, nu sărit în tăcere
            if ignorate is not None:
                ignorate.append(_ignorat(nr, "%s: sold 0 — nu intră în soldurile inițiale" % (den or cui),
                                         "debitul și creditul citite din rând sunt amândouă 0"))
            continue
        rand = {"cont": cont, "cui": cui, "denumire": den, "debit": deb, "credit": cre, "rand_fisier": nr}
        tvai = _tva_incasare_din_rand(r, nr, den or cui, i_tvai, _it.celula(r, i_nr) if i_nr >= 0 else None)
        tva_f = _tva_din_rand(r, nr, den or cui, i_tva, _it.celula(r, i_nr) if i_nr >= 0 else None, deb, cre, cont)
        if i_nr >= 0:
            doc = _document_din_rand(r, nr, den or cui, cont, deb, cre, i_nr, i_data, i_scad, ignorate)
            if doc is None:
                continue
            if i_tvai >= 0:
                doc["tva_la_incasare"] = tvai   # cheia numai când fișierul are coloana: ecranul o arată atunci
            if i_tva >= 0:
                doc["tva_fisier"] = tva_f   # [252, 13.1] suma TVA din fișier (None = celula goală: se calculează, de verificat)
            rand["document"] = doc
        else:
            if i_tvai >= 0:
                rand["tva_la_incasare"] = tvai   # forma pe solduri: pe documentul „Sold la <data preluării>” al partenerului
            if i_tva >= 0:
                rand["tva_fisier"] = tva_f
        out.append(rand)
    if i_nr >= 0:
        out = grupeaza_pe_parteneri(out)
    # [lotul 13, deficiența 582, comanda Costin 13.1: „Verificarea dublurilor oprește tot înainte de celelalte verificări; restul greșelilor
    # apar abia la reîncărcare.”] același partener pe același cont de două ori NU mai oprește citirea: rândurile lui se resping amândouă în
    # `verifica_randuri` (ca articolul dublat, 590), iar celelalte verificări rulează pe tot fișierul, deodată. Baza are UNIQUE(cont, cui)
    # (GARZI cat.1): `importa` refuză și ea perechea dublată, înaintea scrierii.
    return out


def _tva_din_rand(r, nr, cine, i_tva, numar, deb, cre, cont):
    """[lotul 13, 252, decizia Costin 13.1] Suma TVA din coloana opțională a fișierului: Decimal, sau None (coloana lipsă / celula goală ->
    TVA-ul se calculează la cota standard, iar factura e marcată „de verificat”). O sumă care nu e număr, negativă sau mai mare decât restul
    facturii oprește citirea fișierului, cu rândul, partenerul și factura numite (nu se ghicește)."""
    from decimal import Decimal as _D
    if i_tva < 0 or not _it.celula(r, i_tva):
        return None
    unde = "Rândul %d (%s%s)" % (nr, cine, (", factura %s" % numar) if numar else "")
    try:
        v = _D(str(_numar(_it.valoare(r, i_tva), strict=True))).quantize(_D("0.01"))
    except (ValueError, ArithmeticError):
        raise _it.FisierNecitit("%s: suma TVA «%s» nu e un număr. Corectează celula și încarcă fișierul din nou." % (unde, _it.celula(r, i_tva)))
    net = _D(str(deb)) - _D(str(cre))
    rest = abs(net)
    if v < 0 or v > rest:
        raise _it.FisierNecitit("%s: suma TVA %s nu poate fi %s restul facturii (%s). Corectează celula și încarcă fișierul din nou."
                                % (unde, _pu.bani(v, "lei"), "negativă, sub" if v < 0 else "mai mare decât", _pu.bani(rest, "lei")))
    return v


def _tva_incasare_din_rand(r, nr, cine, i_tvai, numar):
    """[252, 12.3 pct.5] Valoarea coloanei „TVA la încasare” a rândului (True / False / None = nespus); o valoare necunoscută oprește
    citirea fișierului, cu rândul, partenerul, factura și valoarea numite (ca data facturii: nu se ghicește)."""
    if i_tvai < 0:
        return None
    try:
        return valoare_tva_incasare(_it.celula(r, i_tvai))
    except ValueError:
        raise _it.FisierNecitit(MESAJ_TVA_INCASARE_NECUNOSCUT % (nr, cine, (", factura %s" % numar) if numar else "", _it.celula(r, i_tvai)))


#: [252, 12.3 pct.5] refuzul valorii necunoscute din coloana „TVA la încasare”
MESAJ_TVA_INCASARE_NECUNOSCUT = ("Rândul %d (%s%s): în coloana „TVA la încasare” scrie „%s”. Se acceptă «da» sau «nu» (și 1 / 0, D / N, x); "
                                 "lasă celula goală ca să se ia regimul firmei la data facturii, din Date firmă. Corectează celula și "
                                 "încarcă fișierul din nou.")


def _document_din_rand(r, nr, cine, cont, deb, cre, i_nr, i_data, i_scad, ignorate):
    """[252] Factura deschisă a rândului din forma pe facturi: {numar, data, scadenta, suma, rand_fisier}, sau None când rândul n-are
    numărul facturii (un subtotal al partenerului: spus în `ignorate`; dacă era o factură, suma partenerilor nu mai dă soldul contului,
    iar confruntarea cu balanța — `coerenta` — oprește contul). `suma` = restul de încasat (4111) / de plătit (401), pe natura contului:
    pozitivă = document deschis; zero sau negativă (avans, plată în plus) rămâne în soldul partenerului, dar nu devine document."""
    numar = _it.celula(r, i_nr)
    if not numar:
        if ignorate is not None:
            ignorate.append(_ignorat(nr, "%s: rând fără numărul facturii — nu e o factură (subtotal?), nu intră" % cine,
                                     "forma pe facturi: fiecare factură are numărul ei în coloana „Nr. factură”"))
        return None
    zi = _it.data(_it.valoare(r, i_data))
    if not zi:
        raise _it.FisierNecitit("Rândul %d (%s, factura %s): data facturii %s. Corectează celula și încarcă fișierul din nou."
                                % (nr, cine, numar, "lipsește" if not _it.celula(r, i_data) else "nu e o dată din calendar"))
    scad = _it.data(_it.valoare(r, i_scad)) if i_scad >= 0 else None
    if i_scad >= 0 and _it.celula(r, i_scad) and not scad:
        raise _it.FisierNecitit("Rândul %d (%s, factura %s): scadența nu e o dată din calendar. Corectează celula și încarcă fișierul din nou."
                                % (nr, cine, numar))
    from decimal import Decimal as _D
    net = _D(str(deb)) - _D(str(cre))
    suma = net if _radacina(cont) not in _CREDITOARE else -net
    return {"numar": numar, "data": zi, "scadenta": scad, "suma": float(suma), "rand_fisier": nr}


def grupeaza_pe_parteneri(randuri):
    """PURĂ. [252] Forma pe facturi: rândurile aceluiași partener pe același cont (CUI, altfel denumirea) devin UN rând de sold — suma
    netă a facturilor lui — cu facturile în `documente`; rândul partenerului e primul lui rând din fișier."""
    from decimal import Decimal as _D
    grup, ordine = {}, []
    for x in randuri:
        k = (x["cont"], x["cui"] or "~" + _it.norm(x["denumire"]))
        g = grup.get(k)
        if g is None:
            g = grup[k] = {"cont": x["cont"], "cui": x["cui"], "denumire": x["denumire"], "_net": _D(0), "rand_fisier": x["rand_fisier"],
                           "documente": []}
            ordine.append(k)
        g["_net"] += _D(str(x["debit"])) - _D(str(x["credit"]))
        g["documente"].append(x["document"])
    out = []
    for k in ordine:
        g = grup[k]
        net = g.pop("_net")
        g["debit"], g["credit"] = (float(net), 0.0) if net >= 0 else (0.0, float(-net))
        out.append(g)
    return out


#: [252] contul partenerului -> direcția facturii lui deschise (4111 clienți: emisă, de încasat; 401 furnizori: primită, de plătit). Pe
#: celelalte conturi de terți (409, 419, 4118…) soldul nu e o factură de stins prin bancă: rămâne numai sold pe partener.
DIRECTIE_DOCUMENT = {"4111": "emisa", "401": "primita"}


def documente_din_randuri(randuri, data_referinta=None):
    """PURĂ. [252] Facturile deschise pe care le scrie salvarea, din rândurile care intră: forma pe facturi -> facturile rândului
    (`documente`); forma pe solduri -> soldul partenerului întreg, ca un document „Sold la <data preluării>”, fără scadență (nu se
    inventează una). Numai pe 4111 / 401 și numai suma pozitivă (de încasat / de plătit).
    -> (documente, neconvertite): documente = [{directie, tert_cui, tert_nume, numar, data, scadenta, suma, cont, tva_la_incasare}] (suma
    în Decimal; `tva_la_incasare` = coloana fișierului: True / False / None = nespus, hotărât la scriere de `cu_regimul_tva`),
    neconvertite = [text] — ce nu devine document și de ce (spus, nu sărit)."""
    from decimal import Decimal as _D, ROUND_HALF_UP as _SUS
    from core.pdf_util import bani as _b, data_ro as _dro
    import datetime as _dt
    docs, nec = [], []
    for r in randuri or []:
        rad = _radacina(r.get("cont"))
        cine = r.get("denumire") or r.get("cui") or "?"
        dir_ = DIRECTIE_DOCUMENT.get(rad)
        net = _D(str(r.get("debit") or 0)) - _D(str(r.get("credit") or 0))
        if dir_ is None:
            if net:
                nec.append("%s, contul %s: soldul rămâne pe partener — pe %s nu se țin facturi de încasat / de plătit" % (cine, r.get("cont"), rad))
            continue
        baza = {"directie": dir_, "tert_cui": r.get("cui") or "", "tert_nume": r.get("denumire") or "", "cont": r.get("cont")}
        if r.get("documente") is not None:
            for d in r["documente"]:
                suma = _D(str(d.get("suma") or 0)).quantize(_D("0.01"), rounding=_SUS)
                if suma <= 0:
                    nec.append("%s, factura %s: %s — nu e de %s, rămâne numai în soldul partenerului"
                               % (cine, d.get("numar"), _b(suma, "lei"), "încasat" if dir_ == "emisa" else "plătit"))
                    continue
                docs.append(dict(baza, numar=str(d.get("numar")), data=d.get("data"), scadenta=d.get("scadenta") or None, suma=suma,
                                 tva_la_incasare=d.get("tva_la_incasare"), tva_fisier=d.get("tva_fisier")))
            continue
        suma = (net if dir_ == "emisa" else -net).quantize(_D("0.01"), rounding=_SUS)
        if suma <= 0:
            if suma:
                nec.append("%s, contul %s: sold %s — nu e de %s, nu devine document deschis"
                           % (cine, r.get("cont"), "creditor" if dir_ == "emisa" else "debitor", "încasat" if dir_ == "emisa" else "plătit"))
            continue
        zi = str(data_referinta)[:10] if data_referinta else None
        # fără data preluării documentul n-are dată (nici număr): îl numără previzualizarea, iar salvarea îl spune și nu-l scrie
        docs.append(dict(baza, numar=("Sold la %s" % _dro(_dt.date.fromisoformat(zi))) if zi else None, data=zi, scadenta=None, suma=suma,
                         tva_la_incasare=r.get("tva_la_incasare"), tva_fisier=r.get("tva_fisier")))
    return docs, nec


def documente_nepotrivite(randuri):
    """PURĂ. [252] Rândurile cu facturi (`documente`) a căror sumă nu dă soldul partenerului (pe natura contului), sau cu o factură fără
    număr / cu o dată care nu e din calendar: [text]. `extrage` le scrie mereu potrivite; rândurile trimise direct pe rută, nu neapărat."""
    from decimal import Decimal as _D
    from core.pdf_util import bani as _b
    out = []
    for r in randuri or []:
        if r.get("documente") is None:
            continue
        cine = r.get("denumire") or r.get("cui") or "?"
        rau = [d for d in r["documente"] if not str(d.get("numar") or "").strip() or not _it.data(d.get("data"))
               or (d.get("scadenta") and not _it.data(d.get("scadenta")))]
        if rau:
            out.append("%s: factura %s n-are număr sau dată din calendar" % (cine, rau[0].get("numar") or "fără număr"))
            continue
        net = _D(str(r.get("debit") or 0)) - _D(str(r.get("credit") or 0))
        sold = net if _radacina(r.get("cont")) not in _CREDITOARE else -net
        suma = sum((_D(str(d.get("suma") or 0)) for d in r["documente"]), _D(0))
        if abs(suma - sold) > _D("0.005"):
            out.append("%s: facturile dau %s, soldul e %s" % (cine, _b(suma, "lei"), _b(sold, "lei")))
    return out


def documente_legate(cur):
    """[252] Facturile deschise preluate pe care le leagă deja ceva — o notă (bancă, casă), o chitanță, o compensare, o linie de extras
    potrivită pe ele: [text]. Înlocuirea soldurilor pe parteneri le-ar șterge, deci nu se face până nu se desfac legăturile."""
    from core.pdf_util import bani as _b
    cur.execute("SELECT f.id, COALESCE(f.serie, ''), f.numar, f.tert_nume, f.total FROM facturi f WHERE f.tip = %s "
                "AND (EXISTS (SELECT 1 FROM inregistrari i WHERE i.factura_id = f.id) "
                "  OR EXISTS (SELECT 1 FROM chitante c WHERE c.factura_id = f.id) "
                "  OR EXISTS (SELECT 1 FROM compensari z WHERE f.id IN (z.factura_emisa_id, z.factura_primita_id)) "
                "  OR EXISTS (SELECT 1 FROM extras_linii e WHERE e.alocari -> 'alocari' @> jsonb_build_array(jsonb_build_object('factura_id', f.id)))) "
                "ORDER BY f.id", (_TIP_PRELUAT,))
    return ["%s (%s, %s)" % ((sr + " " + nr).strip(), tn or "—", _b(t, "lei")) for _id, sr, nr, tn, t in cur.fetchall()]


def cu_regimul_tva(cur, docs):
    """[lotul 12, deficiența 252, decizia Costin 12.3 pct.5, verbatim: „coloana TVA la încasare e opțională în fișierul de preluare; dacă
    lipsește, se ia regimul firmei la data facturii”] Pe fiecare factură deschisă preluată: e TVA-ul cuprins în restul ei încă NEEXIGIBIL
    (emisă: pe 4428 până la încasare — CF art.282 alin.(3)) / NEDEDUS (primită: pe 4428 până la plată — CF art.297 alin.(2)-(3)), și cât e.
    Coloana fișierului decide; nespusă -> regimul firmei la data facturii (`regim_tva_incasare.aplica_la`, perioadele din Date firmă —
    aceeași funcție ca la factura emisă în aplicație). Cât: restul × cotă / (100 + cotă) — CF art.282 alin.(8): „fiecare încasare totală
    sau parțială se consideră că include și taxa aferentă”; cota standard la data facturii — CF art.291 alin.(5): „În cazul operațiunilor
    supuse sistemului TVA la încasare, cota aplicabilă este cea în vigoare la data la care intervine faptul generator”.
    Pune pe fiecare doc `tva` (Decimal, 0 = regulile generale) și `furnizor_tva_incasare` (primită «da» la o dată la care firma NU aplica
    sistemul: deducerea e amânată numai pentru că furnizorul îl aplica — alin.(2)). Motorul (`tva_incasare.regim`) citește TVA-ul înghețat
    aici: banca / casa / compensarea îl mută 4428 -> 4427 / 4426, D300 și D394 îl declară la încasare / plată.
    Refuză (ValueError, nimic scris) ce legea nu admite: «da» la o firmă neînregistrată în scopuri de TVA (alin.(3^1) lit.a); emisă «da» la
    o dată la care firma nu aplica sistemul (alin.(3): exigibilitatea la încasare e a persoanei care aplică sistemul; alin.(7) lit.a)."""
    from decimal import Decimal as _D
    from core import common as _c, regim_tva_incasare as _rg, tva_calcul as _tc
    from core.pdf_util import data_ro as _dro
    import datetime as _dt
    cur.execute("SELECT COALESCE(platitor_tva, false) FROM firma_profil WHERE id = 1")
    r = cur.fetchone()
    platitor = bool(r and (r["coalesce"] if isinstance(r, dict) else r[0]))
    refuz = []
    for d in docs:
        d["tva"], d["furnizor_tva_incasare"], d["tva_de_verificat"] = _D(0), False, False
        if not d.get("data"):
            continue
        zi = _dt.date.fromisoformat(str(d["data"])[:10])
        spus = d.get("tva_la_incasare")
        cine = "%s, factura %s din %s" % (d.get("tert_nume") or d.get("tert_cui") or "?", d.get("numar"), _dro(zi))
        if spus and not platitor:
            refuz.append("%s: «TVA la încasare: da», dar firma nu e înregistrată în scopuri de TVA (Date firmă)" % cine)
            continue
        # neînregistrată în scopuri de TVA -> nu poate aplica sistemul (alin.(3^1) lit.a): regulile generale, fără să mai citim perioadele
        in_sistem = platitor and _rg.aplica_la(cur, zi)
        if spus and d["directie"] == "emisa" and not in_sistem:
            refuz.append("%s: «TVA la încasare: da», dar în Date firmă firma nu aplica sistemul TVA la încasare la această dată — scrie "
                         "perioada în Date firmă sau corectează coloana" % cine)
            continue
        if not (spus if spus is not None else in_sistem):
            continue
        # [lotul 13, 252, decizia Costin 13.1, verbatim: „dacă fișierul are suma TVA, se ia suma din fișier; doar unde lipsește se calculează
        # la cota standard, iar factura e marcată «de verificat».”] Cota standard nu e a unei facturi cu cotă redusă sau scutite: suma din
        # fișier câștigă; calculată, se spune și rămâne de verificat (auditul de preluare o numește).
        if d.get("tva_fisier") is not None:
            d["tva"] = _D(str(d["tva_fisier"]))
        else:
            cota = int(_c.cota("tva_standard", zi)[0] * 100)
            d["tva"] = _tc.tva_din_total(d["suma"], cota)
            d["tva_de_verificat"] = True
        d["furnizor_tva_incasare"] = d["directie"] == "primita" and not in_sistem
    if refuz:
        raise ValueError(MESAJ_TVA_INCASARE_REFUZ % "; ".join(refuz[:6]))
    return docs


#: [252, 12.3 pct.5] coloana „TVA la încasare” contrazice firma: refuzul previzualizării (`refuz_tva_incasare`) și al salvării (nimic scris)
MESAJ_TVA_INCASARE_REFUZ = ("Coloana „TVA la încasare” nu se potrivește cu firma: %s. Soldurile pe parteneri nu se salvează până nu corectezi "
                            "fișierul (în coloană «nu», sau celula goală pentru regimul din Date firmă) și nu-l încarci din nou.")


def refuz_tva_incasare(conn, schema, randuri, data_referinta=None):
    """[252, 12.3 pct.5] Pentru previzualizare: refuzul pe care l-ar da salvarea (`cu_regimul_tva`) pe rândurile care intră, sau None —
    aceeași regulă, pe aceleași documente (`documente_din_randuri`), fără nicio scriere. `data_referinta` lipsă -> data preluării firmei
    (`bilant_api.data_soldurilor`), ca la salvare. `conn` = conexiunea pe schema firmei (search_path)."""
    import psycopg2.extras as _E
    from core import bilant_api as _bil
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        zi = data_referinta or _bil.data_soldurilor(cur, schema)
        docs = [d for d in documente_din_randuri(randuri, zi.isoformat() if hasattr(zi, "isoformat") else zi)[0] if d["data"]]
        try:
            cu_regimul_tva(cur, docs)
        except ValueError as e:
            return str(e)
    return None


def confruntare_4428(cur, docs):
    """[252, 12.3 pct.5] TVA-ul neexigibil al facturilor preluate (emise − primite) față de 4428 din balanța de deschidere — text de atenție
    sau None. Informativ, nu blocant: 4428 poate ține și TVA-ul facturilor nesosite / de întocmit, iar cota standard nu e a unei facturi cu
    cotă redusă; diferența îi arată contabilului unde să se uite. Numai când o factură e la încasare sau 4428 are sold."""
    from decimal import Decimal as _D
    from core.pdf_util import bani as _b
    em = sum((d["tva"] for d in docs if d["directie"] == "emisa"), _D(0))
    pr = sum((d["tva"] for d in docs if d["directie"] == "primita"), _D(0))
    cur.execute("SELECT count(*), COALESCE(SUM(sold_creditor - sold_debitor), 0) FROM solduri_initiale WHERE split_part(cont, '.', 1) = '4428'")
    r = cur.fetchone()
    n, sold = (r["count"], r["coalesce"]) if isinstance(r, dict) else r
    sold = _D(str(sold))
    if (not n and not (em or pr)) or abs(em - pr - sold) < _D("0.01"):
        return None
    # semnul contabilului: TVA-ul neexigibil al vânzărilor stă în creditul lui 4428, cel nededus al cumpărărilor în debit
    return ("TVA-ul neexigibil al facturilor deschise preluate: %s din facturile emise, %s din cele primite, adică 4428 %s; 4428 din "
            "balanța de deschidere: %s. Diferența de %s: verifică facturile cu altă cotă decât cea standard, cele scutite sau cu taxare "
            "inversă (în coloana „TVA la încasare”: «nu») și TVA-ul neexigibil al facturilor nesosite sau de întocmit (408 / 418)."
            % (_b(em, "lei"), _b(pr, "lei"), _pu.sold(pr - em), _pu.sold(-sold), _b(abs(em - pr - sold), "lei")))


def _scrie_documente(cur, docs):
    """[252] Facturile deschise preluate, în `facturi` (tip `preluata`, starea „importată”): totalul = restul de la preluare, fără
    linii și fără notă (soldul e deja în balanța de deschidere, cu TVA-ul lui) — nicio declarație nu le citește ca documente ale perioadei.
    [12.3 pct.5] `tva` = TVA-ul încă neexigibil / nededus din rest (`cu_regimul_tva`; 0 = regulile generale): numai pe el îl citesc motorul
    TVA la încasare și D300 / D394, la încasarea / plata facturii.
    [lotul 12, C73.1] Factura de furnizor deja în evidență (furnizor + număr: introdusă de mână, din XML, din Operațiuni, sau de două ori
    în același fișier) nu se scrie a doua oară: refuzul numit oprește toată salvarea (`ValueError`, nimic scris)."""
    from core import factura_primita_dublura as _fpd, repo_facturi as _rf
    for d in docs:
        if d["directie"] == "primita":
            ex = _rf.primite_cu_aceeasi_cheie(cur, None, d["tert_cui"], d["tert_nume"], None, d["numar"])
            if ex:
                raise _fpd.refuz(ex, sfat="Soldurile pe parteneri nu s-au salvat: scoate factura din fișier (sau adună rândurile ei) și "
                                          "încarcă-l din nou.")
        tva = d.get("tva") or 0
        # [lotul 13, 252, decizia Costin 13.1] `tva_de_verificat`: TVA-ul neexigibil calculat la cota standard (lipsea din fișier)
        cur.execute("INSERT INTO facturi (numar, data_emitere, data_scadenta, total, tva, moneda, directie, status, tert_nume, tert_cui, tip, "
                    "total_lei, tva_lei, sursa_externa, furnizor_tva_incasare, tva_de_verificat) "
                    "VALUES (%s, %s, %s, %s, %s, 'RON', %s, 'importata', %s, %s, %s, %s, %s, 'preluare', %s, %s)",
                    (d["numar"], d["data"], d["scadenta"], d["suma"], tva, d["directie"], d["tert_nume"], d["tert_cui"], _TIP_PRELUAT, d["suma"],
                     tva, bool(d.get("furnizor_tva_incasare")), bool(d.get("tva_de_verificat"))))


def rezumat_documente(docs):
    """PURĂ. [252] {n, emise, total_emise, primite, total_primite} (totalurile în float, la ban). [12.3 pct.5] + `la_incasare` (câte au TVA
    neexigibil / nededus, `cu_regimul_tva`), `tva_emise`, `tva_primite` — numai când vreuna e la încasare."""
    from decimal import Decimal as _D
    e = [d["suma"] for d in docs if d["directie"] == "emisa"]
    p = [d["suma"] for d in docs if d["directie"] == "primita"]
    out = {"n": len(docs), "emise": len(e), "total_emise": float(sum(e, _D(0))), "primite": len(p), "total_primite": float(sum(p, _D(0)))}
    cu_tva = [d for d in docs if d.get("tva")]
    if cu_tva:
        out.update(la_incasare=len(cu_tva), tva_emise=float(sum((d["tva"] for d in cu_tva if d["directie"] == "emisa"), _D(0))),
                   tva_primite=float(sum((d["tva"] for d in cu_tva if d["directie"] == "primita"), _D(0))))
    # [lotul 13, 252, decizia Costin 13.1] facturile cu TVA-ul calculat la cota standard (lipsea din fișier), marcate „de verificat”
    dv = [d for d in docs if d.get("tva_de_verificat")]
    if dv:
        out["tva_de_verificat"] = ["%s (%s)" % (d.get("numar"), d.get("tert_nume") or d.get("tert_cui") or "?") for d in dv]
    return out


#: [lotul 10, C73] același partener pe același cont — la citirea fișierului ȘI la scriere (rândurile pot veni și direct, prin API)
MESAJ_PARTENER_DUBLAT = ("Același partener apare de două ori pe același cont: %s. Un partener are un singur sold pe un cont; "
                         "adună rândurile în fișier și încarcă-l din nou.")


def parteneri_dublati(randuri):
    """PURĂ: perechile (cont, CUI) care apar pe mai multe rânduri, ca text („4111 / 14399840 (rândurile 2 și 3)”). Baza are
    UNIQUE(cont, cui) (`solduri_parteneri_cont_cui_uniq`)."""
    vazute, dubluri = {}, []
    for i, x in enumerate(randuri or [], start=2):
        k = (x.get("cont"), x.get("cui"))
        nr = x.get("rand_fisier") or i
        if x.get("cui") and k in vazute:
            dubluri.append("%s / %s (rândurile %s și %s)" % (x.get("cont"), x.get("cui"), vazute[k], nr))
        vazute.setdefault(k, nr)
    return dubluri


def _refuz_partener_scris_intre_timp(cur, e):
    """[lotul 10, C73] Rândurile de scris n-au perechea (cont, CUI) dublată (verificat înainte), deci violarea vine de la o altă salvare
    a soldurilor pe parteneri, terminată în timpul acesteia."""
    return _chei.CheieDublata("În timp ce salvai, altă salvare a scris deja soldul partenerului (cont, CUI) %s. Din soldurile tale nu "
                              "s-a scris nimic: reîncarcă pagina, verifică soldurile pe parteneri și salvează-le din nou dacă e cazul."
                              % _chei.valoarea(e), valoare=_chei.valoarea(e))


def asigura_tabel(conn):
    """Creeaza tabelul solduri_parteneri in schema curenta (search_path = tenantul)."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS solduri_parteneri (
                id SERIAL PRIMARY KEY,
                cont TEXT NOT NULL,
                cui TEXT NOT NULL DEFAULT '',
                denumire TEXT NOT NULL DEFAULT '',
                sold_debitor NUMERIC(15,2) NOT NULL DEFAULT 0,
                sold_creditor NUMERIC(15,2) NOT NULL DEFAULT 0,
                data_referinta DATE
            )
        """)


def terti_in_balanta(conn):
    """[345] Conturile de terți (`CONTURI_PARTENERI`) cu sold în balanța de deschidere a firmei; [] fără balanță."""
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('solduri_initiale')")
        if cur.fetchone()[0] is None:
            return []
        cur.execute("SELECT DISTINCT split_part(cont, '.', 1) FROM solduri_initiale WHERE (sold_debitor <> 0 OR sold_creditor <> 0) "
                    "AND split_part(cont, '.', 1) = ANY(%s) ORDER BY 1", (list(CONTURI_PARTENERI),))
        return [r[0] for r in cur.fetchall()]


def coerenta(conn, schema, randuri):
    """[deficiența 346 (grav), comanda Costin 8.2: „Promite verificarea cu balanța, dar pe F2 pune «401: fără balanță» și lasă salvarea unei
    sume [...] diferite de 401 din contabilitate”] Soldurile partenerilor, pe sintetic, față de soldul contului LA DATA PRELUĂRII, din
    aceeași sursă ca balanța (`bilant_api.sold_la`): cu balanță de deschidere e chiar soldul ei; fără ea, soldul din contabilitatea firmei
    (notele validate) la data preluării — sau azi, dacă evidența e întreagă în iConta.eu. Se confruntă și conturile de terți cu sold în
    referință care lipsesc din fișier (Σ parteneri = 0).
    -> [{cont, suma_parteneri, sold_balanta, diferenta, coincide, sursa, data}] pe fiecare sintetic de terți atins."""
    import datetime as _dt
    import psycopg2.extras as _E
    from core import bilant_api as _bil
    pe_sintetic = {}
    for r in randuri:
        rad = _radacina(r["cont"])
        pe_sintetic[rad] = pe_sintetic.get(rad, 0.0) + float(r.get("debit", 0) or 0) - float(r.get("credit", 0) or 0)
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        zi = _bil.data_soldurilor(cur, schema)
        cur.execute(f"SELECT count(*) AS n FROM {schema}.solduri_initiale" if _are_tabel(cur, f"{schema}.solduri_initiale") else "SELECT 0 AS n")
        are_balanta = (cur.fetchone()["n"] or 0) > 0
        sursa = "balanța de deschidere" if are_balanta else "contabilitatea firmei"
        zi = zi or _dt.date.today()
        sold = _bil.sold_la(cur, schema, zi, ref=None if not are_balanta else "calculeaza") or {}
    ref = {}
    for cont, (sd, sc) in sold.items():
        rad = _radacina(cont)
        if rad in CONTURI_PARTENERI:
            ref[rad] = ref.get(rad, 0.0) + float(sd) - float(sc)
    out = []
    for rad in sorted(set(pe_sintetic) | {k for k, v in ref.items() if abs(v) >= 0.01}):
        sp = round(pe_sintetic.get(rad, 0.0), 2)  # round-ok: sumă de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
        sb = round(ref.get(rad, 0.0), 2)  # round-ok: idem
        dif = round(sp - sb, 2)  # round-ok: idem
        out.append({"cont": rad, "suma_parteneri": sp, "sold_balanta": sb, "diferenta": dif, "coincide": abs(dif) < 0.01,
                    "sursa": sursa, "data": zi.isoformat()})
    return out


def _are_tabel(cur, nume):
    cur.execute("SELECT to_regclass(%s) IS NOT NULL AS e", (nume,))
    r = cur.fetchone()
    return bool(r["e"] if isinstance(r, dict) else r[0])


def respinse_coerenta(randuri, coer):
    """[346] Rândurile de pe un sintetic ale cărui solduri pe parteneri nu dau soldul contului (`coerenta`) NU intră: o sumă pe parteneri
    diferită de contabilitate ar intra în evidență ca adevărată. Fiecare rând se respinge numit, cu cifrele."""
    from core.pdf_util import bani as _b
    nepotr = {c["cont"]: c for c in coer if c.get("coincide") is False}
    er = []
    for i, r in enumerate(randuri or [], start=2):
        i = _it.nr_rand(r, i)
        c = nepotr.get(_radacina(r.get("cont")))
        if c:
            # [lotul 13, deficiența 666] mesajul (cu cifrele) rămâne întreg — îl spune o dată lista refuzurilor (grupată) și răspunsul
            # salvării; pe rândul tabelului ecranul arată motivul scurt (`migrare.js:previzualizeazaParteneri`)
            er.append(respinge(
                "sold partener", i, "parteneri_nu_dau_soldul",
                "pe %s, partenerii din fișier dau %s, iar %s la %s are %s (diferență %s) — rândurile contului nu intră până nu se potrivesc"
                % (c["cont"], _pu.sold(c["suma_parteneri"]), c["sursa"], _data_ro_iso(c["data"]), _pu.sold(c["sold_balanta"]),
                   _b(abs(c["diferenta"]), "lei")), cont=r.get("cont")))
    return er




def _data_ro_iso(s):
    from core.pdf_util import data_ro
    import datetime as _dt
    return data_ro(_dt.date.fromisoformat(s)) if s else "—"


# Conturile pe care se tin solduri pe parteneri. Restul (5121 banca, 5311 casa,
# conturi de venituri/cheltuieli) NU au parteneri: un sold pe partener acolo e o
# eroare de export, nu o realitate contabila.
CONTURI_PARTENERI = ("4111", "401", "409", "419", "4118", "4091", "4092", "4093")

# cheia oficiala de control a CUI romanesc (aceeasi ca la CNP in salariati_import_api:
# algoritm publicat, nu inventat aici)
_CHEIE_CUI = [7, 5, 3, 2, 1, 7, 5, 3, 2]


def valideaza_cui(cui):
    """(valid, motiv) - cifra de control a CUI romanesc, LOCAL (fara retea).
    anaf_api.valideaza_cui() interogheaza ANAF si e potrivit la o firma, nu la fiecare
    rand dintr-un import de sute de parteneri."""
    c = "".join(ch for ch in str(cui or "") if ch.isdigit())
    if not c:
        return False, "lipsa"
    if len(c) == 13:
        # [14.10.2026] un partener persoană fizică e identificat prin CNP (ecranul Terți SAGA: „Cod fiscal/ CNP”); CNP-ul se
        # verifică cu cheia lui oficială, nu cu a CUI-ului
        from core.salariati_import_api import valideaza_cnp
        ok, motiv = valideaza_cnp(c)
        return ok, ("ok" if ok else "CNP: " + motiv)
    if not (2 <= len(c) <= 10):
        return False, "lungime (2-10 cifre)"
    corp, ctrl = c[:-1], int(c[-1])
    corp = corp.rjust(9, "0")
    s = sum(int(corp[i]) * _CHEIE_CUI[i] for i in range(9))
    rest = (s * 10) % 11
    if rest == 10:
        rest = 0
    return (rest == ctrl), ("ok" if rest == ctrl else "cifra de control")


def verifica_randuri(randuri):
    """PURA: (erori, randuri_bune). Ce nu poate intra in evidenta si de ce.

    Pana la 15.07.2026 nu exista NICIO validare intre extrage() si importa():
    - CUI cu cifra de control gresita -> intra
    - partener fara CUI pe cont de parteneri -> intra
    - partener pe 5121 (banca) -> intra
    verifica() calcula diferentele fata de balanta si le trimitea in raspuns, ecranul
    le afisa cu ⚠, iar importa() scria oricum. Migrarea marca stratul "gata" VERDE.
    Semnalarea fara oprire e mai rea decat tacerea: da impresia ca s-a verificat.
    """
    erori, bune = [], []
    # [lotul 13, 582] perechile (cont, CUI) de pe mai multe rânduri: TOATE aparițiile se resping (nu prima intră și a doua nu — ar intra un
    # sold parțial), cu rândurile celelalte numite; restul verificărilor rulează pe celelalte rânduri
    pe_cheie = {}
    for i, r in enumerate(randuri or [], start=2):
        if str(r.get("cui") or "").strip():
            pe_cheie.setdefault((str(r.get("cont") or "").strip(), str(r.get("cui") or "").strip()), []).append(_it.nr_rand(r, i))
    for i, r in enumerate(randuri or [], start=2):   # +2: randul din fisier, cu antet
        i = _it.nr_rand(r, i)
        cont = str(r.get("cont") or "").strip()
        cui = str(r.get("cui") or "").strip()
        den = str(r.get("denumire") or "").strip()
        rad = _radacina(cont)
        if rad not in CONTURI_PARTENERI:
            erori.append(respinge(
                "sold partener", i, "cont_nepartener",
                "contul %s nu ține solduri pe parteneri (doar %s)"
                % (cont or "?", ", ".join(CONTURI_PARTENERI[:4])), cont=cont))
            continue
        ok, motiv = valideaza_cui(cui)
        if not ok:
            erori.append(respinge(
                "sold partener", i, "cui_invalid",
                ("partenerul %s nu are CUI" % (den or "?")) if motiv == "lipsa"
                else ("CNP %s invalid (%s)" % (cui, motiv[5:]) if motiv.startswith("CNP: ") else "CUI %s invalid (%s)" % (cui, motiv)),
                cont=cont, cui=cui, denumire=den))
            continue
        alte = [n for n in pe_cheie.get((cont, cui), []) if n != i]
        if alte:
            erori.append(respinge(
                "sold partener", i, "partener_dublat",
                "%s apare pe același cont %s și pe %s — un partener are un singur sold pe un cont: adună rândurile în fișier"
                % (den or cui, cont, " și pe ".join("rândul %d" % n for n in alte)),   # rândurile se enumeră, nu se numără
                cont=cont, cui=cui, denumire=den))
            continue
        bune.append(r)
    return erori, bune


def existent(conn):
    """[lotul 10, deficiența 426 — clasa] Soldurile pe parteneri deja salvate ale firmei: {randuri, total_debit, total_credit,
    data_referinta} (data = cea mai recentă a rândurilor, 'YYYY-MM-DD' sau None). Înlocuirea lor se confirmă cu cifrele astea.
    Numai citire (o cheamă și previzualizarea): fără tabel, firma n-are solduri pe parteneri.
    [lotul 12, 252] + `documente`: câte facturi deschise preluate are firma (aceeași salvare le înlocuiește)."""
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM facturi WHERE tip = %s", (_TIP_PRELUAT,))
        nd = int(cur.fetchone()[0])
        legate = documente_legate(cur) if nd else []
        cur.execute("SELECT to_regclass('solduri_parteneri')")
        if cur.fetchone()[0] is None:
            return {"randuri": 0, "total_debit": 0.0, "total_credit": 0.0, "data_referinta": None, "documente": nd, "legate": legate}
        cur.execute("SELECT count(*), COALESCE(sum(sold_debitor),0), COALESCE(sum(sold_creditor),0), max(data_referinta) "
                    "FROM solduri_parteneri")
        n, td, tc, dr = cur.fetchone()
    return {"randuri": int(n), "total_debit": float(td), "total_credit": float(tc), "documente": nd, "legate": legate,
            "data_referinta": dr.isoformat() if hasattr(dr, "isoformat") else (str(dr)[:10] if dr else None)}


def totaluri(randuri):
    """[426] Ce aduce fișierul: {randuri, total_debit, total_credit} pe rândurile care intră (sume în Decimal, fără zgomot float).
    [lotul 12, 252] + `documente`: câte facturi deschise preluate scrie salvarea (`documente_din_randuri`)."""
    from decimal import Decimal as _D
    return {"randuri": len(randuri or []), "documente": len(documente_din_randuri(randuri)[0]),
            "citite": getattr(randuri, "citite", None),   # [lotul 13, 583] câte rânduri s-au citit (`migrare_api.RanduriCareIntra`)
            "total_debit": float(sum((_D(str(r.get("debit") or 0)) for r in randuri or []), _D(0))),
            "total_credit": float(sum((_D(str(r.get("credit") or 0)) for r in randuri or []), _D(0)))}


def text_inlocuire(vechi, nou):
    """[426] „spune că există deja […], arată totalurile vechi și noi” — textul comun avertismentului din previzualizare și refuzului
    de la salvare. Soldurile pe parteneri nu stau sub nicio cifră calculată (le citesc numai confruntarea cu balanța și auditul de
    preluare), deci n-au date dependente de numit.
    [lotul 12, 252] Cu ele se înlocuiesc și facturile deschise preluate (`documente`); cele pe care le leagă deja o încasare / plată
    (`legate`, `documente_legate`) opresc înlocuirea, iar textul le numește."""
    from core.pdf_util import bani as _b

    def _parte(x, cu_documente=False):
        doc = (x.get("documente") or 0) if cu_documente else 0
        return "%s, debit %s, credit %s%s" % (_cate(x["randuri"], "partener", "parteneri"), _b(x["total_debit"], "lei"),
                                              _b(x["total_credit"], "lei"),
                                              (", cu %s" % _cate(doc, "factură deschisă preluată", "facturi deschise preluate")) if doc else "")
    # ce se ȘTERGE se numește întreg (și facturile deschise vechi); ce aduce fișierul, pe solduri (facturile lui le arată tabelul)
    from core.migrare_api import text_fisier_nou as _tfn   # [lotul 13, 583] „0 rânduri valide din 4”, nu „0 parteneri, debit 0,00”
    t = ("Firma are deja solduri pe parteneri%s: %s. Fișierul nou: %s. Salvarea le înlocuiește pe cele vechi."
         % ((" la %s" % _data_ro_iso(vechi["data_referinta"])) if vechi.get("data_referinta") else "", _parte(vechi, True),
            _tfn(_parte(nou), nou["randuri"], nou.get("citite"))))
    if vechi.get("legate"):
        t += " " + MESAJ_DOCUMENTE_LEGATE % "; ".join(vechi["legate"][:6])
    return t


#: [252] înlocuirea ar șterge facturi deschise preluate pe care le stinge deja o încasare / plată
MESAJ_DOCUMENTE_LEGATE = ("Înlocuirea nu se poate face: facturile deschise preluate %s au deja încasări, plăți, chitanțe, compensări sau "
                          "linii de extras potrivite pe ele, iar înlocuirea le-ar șterge. Desfă întâi legăturile (nota din Bancă sau Casă, "
                          "chitanța, compensarea), apoi încarcă fișierul din nou.")


def importa(conn, randuri, data_referinta=None, schema=None, inlocuieste=False):
    """Inlocuieste partenerii (DELETE + INSERT) cu randurile BUNE. Intoarce {randuri, total_debit, total_credit, respinse, inlocuita}.
    Randurile respinse (vezi verifica_randuri) nu intra si se intorc numite (decizia Costin 14.10.2026 pct.2); ValueError numai
    cand niciun rand nu poate intra.
    [lotul 10, deficiența 426 — clasa] soldurile existente se înlocuiesc NUMAI cu `inlocuieste=True` (confirmarea de pe ecran); fără
    ea -> `migrare_api.InlocuireNeconfirmata` (409), cu totalurile vechi și noi."""
    # [probare invalid, 03.09.2026 — aceeasi clasa ca importul de istoric] UN IMPORT GOL
    # STERGEA TOT, IN TACERE. Lista vida trecea de verificare (n-are ce respinge), ajungea la
    # `DELETE FROM solduri_parteneri` de mai jos, si raspundea ca un import reusit cu zero randuri. Un fisier gol,
    # unul cu numai antet (`extrage` intoarce [] pe el), sau un apel de API cu lista goala — toate
    # ajungeau acolo. *Un import care nu aduce nimic n-are voie sa stearga ce era acolo.*
    if not randuri:
        raise ValueError("nu ai trimis niciun rând. Importul ar fi șters soldurile inițiale ale "
                         "partenerilor și n-ar fi pus nimic în loc. Dacă chiar vrei să le "
                         "golești, e altă operațiune.")
    erori, bune = verifica_randuri(randuri)
    if schema and bune:
        # [346] contul ale cărui solduri pe parteneri nu dau soldul lui la data preluării nu intră (cu cifrele, pe fiecare rând)
        er2 = respinse_coerenta(bune, coerenta(conn, schema, bune))
        resp = {e["rand"] for e in er2}
        bune = [r for i, r in enumerate(bune, start=2) if _it.nr_rand(r, i) not in resp]
        erori = erori + er2
    # [decizia Costin 14.10.2026 pct.2, verbatim în DECIZII] „rândurile bune se salvează, cele refuzate se arată numite, cu motivul
    # în cuvinte” — numai un import fără niciun rând bun se refuză întreg (și atunci soldurile existente rămân neatinse).
    if not bune:
        det = "; ".join("rand %s: %s" % (e["rand"], e["mesaj"]) for e in erori[:6])
        if len(erori) > 6:
            det += " (și încă %d)" % (len(erori) - 6)
        raise ValueError(
            "%s în evidență: %s. Soldurile pe parteneri au nevoie "
            "de CUI valid (intră în D394 și SAF-T) și de un cont care ține parteneri; niciun sold n-a fost scris."
            % ("Un rând nu poate intra" if len(erori) == 1 else _cate(len(erori), "rând", "rânduri") + " nu pot intra", det))
    dubluri = parteneri_dublati(bune)   # [lotul 10, C73] înaintea scrierii: refuzul numit, nu `UniqueViolation` -> 500
    if dubluri:
        raise ValueError(MESAJ_PARTENER_DUBLAT % "; ".join(dubluri[:6]))
    nepotrivite = documente_nepotrivite(bune)   # [252] facturile trimise pe rută (nu din `extrage`) trebuie să dea soldul partenerului
    if nepotrivite:
        raise ValueError("Facturile deschise nu dau soldul partenerului: %s. Niciun sold n-a fost scris; corectează fișierul și încarcă-l "
                         "din nou." % "; ".join(nepotrivite[:6]))
    asigura_tabel(conn)
    vechi, nou = existent(conn), totaluri(bune)
    from core import migrare_api as _mig
    if vechi["legate"]:   # [252] nicio scriere: o încasare / plată stinge deja o factură deschisă pe care înlocuirea ar șterge-o
        raise ValueError(MESAJ_DOCUMENTE_LEGATE % "; ".join(vechi["legate"][:6]))
    _mig.cere_confirmarea_inlocuirii(vechi["randuri"] > 0 or vechi["documente"] > 0, inlocuieste, text_inlocuire(vechi, nou), vechi,
                                     nou)   # [426] poarta comună
    docs, neconvertite = documente_din_randuri(bune, data_referinta)   # [252]
    neconvertite += ["%s, contul %s: firma n-are data preluării (balanța de deschidere), deci soldul nu devine document deschis"
                     % (d["tert_nume"] or d["tert_cui"], d["cont"]) for d in docs if not d["data"]]
    docs = [d for d in docs if d["data"]]
    td = tc = 0.0
    with conn.cursor() as cur:
        cu_regimul_tva(cur, docs)   # [252, 12.3 pct.5] înaintea oricărei scrieri: un refuz nu lasă nimic șters
        atentie_tva = confruntare_4428(cur, docs)
        cur.execute("DELETE FROM solduri_parteneri")
        with _chei.refuza_dublura(cur, ("solduri_parteneri_cont_cui_uniq",), _refuz_partener_scris_intre_timp):
            for r in bune:
                cur.execute(
                    "INSERT INTO solduri_parteneri (cont, cui, denumire, sold_debitor, sold_creditor, data_referinta) "
                    "VALUES (%s,%s,%s,%s,%s,%s)",
                    (r["cont"], r.get("cui", ""), r.get("denumire", ""),
                     r.get("debit", 0), r.get("credit", 0), data_referinta))
                td += float(r.get("debit", 0) or 0)
                tc += float(r.get("credit", 0) or 0)
        _inlocuieste_documentele(cur, docs)
    return {"randuri": len(bune), "total_debit": round(td, 2), "total_credit": round(tc, 2), "respinse": erori,  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
            "inlocuita": vechi if (vechi["randuri"] or vechi["documente"]) else None,
            "documente": dict(rezumat_documente(docs), neconvertite=neconvertite, **({"atentie_tva": atentie_tva} if atentie_tva else {}))}


def _inlocuieste_documentele(cur, docs):
    """[252] Facturile deschise preluate vechi se șterg (nu le leagă nimic: `documente_legate`, verificat înainte) și se scriu cele noi.
    O lună închisă (triggerul perioadei blocate) sau o legătură apărută între timp opresc tot, cu refuzul numit (nimic scris)."""
    import psycopg2
    try:
        # pragurile de notificare ale facturilor șterse (fără cheie străină): nu rămân orfane
        cur.execute("SELECT to_regclass('notificari_scadenta') IS NOT NULL")
        if cur.fetchone()[0]:
            cur.execute("DELETE FROM notificari_scadenta WHERE factura_id IN (SELECT id FROM facturi WHERE tip = %s)", (_TIP_PRELUAT,))
        cur.execute("DELETE FROM facturi WHERE tip = %s", (_TIP_PRELUAT,))
        _scrie_documente(cur, docs)
    except psycopg2.errors.RaiseException as e:   # PERIOADA_BLOCATA: luna %/% este inchisa (trg_perioada_blocata_facturi)
        from core import perioada as _per   # [lotul 12] textul triggerului de perioadă, compus într-un singur loc (`text_exceptie`)
        motiv = _per.text_exceptie(e.diag.message_primary or e).rstrip(".")
        refuz = ("Facturile deschise preluate nu s-au putut scrie: %s. Soldurile pe parteneri nu s-au salvat; deschide luna sau "
                 "corectează data facturii în fișier și încarcă-l din nou." % motiv)
    except psycopg2.errors.ForeignKeyViolation:
        refuz = ("În timpul salvării, o încasare sau o plată s-a legat de o factură deschisă preluată: nimic nu s-a salvat. "
                 "Reîncarcă pagina, verifică facturile partenerului și încarcă fișierul din nou.")
    else:
        return
    # [lotul 12, clasa 440] un singur refuz, de STARE: cele două cauze se exclud (scrierea s-a oprit la prima)
    raise ValueError(refuz)


def rezumat(conn):
    """{are_parteneri, randuri, total_debit, total_credit} pentru firma curenta."""
    asigura_tabel(conn)
    with conn.cursor() as cur:
        cur.execute("SELECT count(*), COALESCE(sum(sold_debitor),0), COALESCE(sum(sold_creditor),0) FROM solduri_parteneri")
        n, td, tc = cur.fetchone()
    return {"are_parteneri": n > 0, "randuri": n, "total_debit": float(td), "total_credit": float(tc)}

# -*- coding: utf-8 -*-
"""core/mf_din_factura.py — [lotul 13, deficiența 601, decizia Costin (a), comanda 13.1 valul 4] Mijlocul fix cumpărat pe factură.

601: „Pe ecranul Mijloace fixe nu există buton de adăugare a unui mijloc fix (la achiziții).” Decizia lui Costin (varianta sigură, a):
„linia «imobilizare» pe factura primită (Facturi primite → activul intră în registru din documentul lui, la validarea notei)”. Deci nu un
formular nou, ci documentul de achiziție: linia facturii primite pe un cont de imobilizare amortizabilă (20x / 21x) cere datele fișei
mijlocului fix (codul din catalog și durata în plaja lui, data punerii în funcțiune, metoda de amortizare); la validarea facturii,
activul se scrie în registru legat de nota facturii (`mf_note`, „intrare”) și devine activ numai când nota e validată (triggerul
`trg_mf_nota_status`, ca la plusul de inventar și leasing — 519). Valoarea lui = baza liniei în lei (cursul facturii).

TEMEI (textul din `anaf_surse/omfp_1802_2014.html`). OMFP 1802/2014 pct.226 alin.(1): „O imobilizare corporală recunoscută ca activ
trebuie evaluată inițial la costul său determinat potrivit regulilor de evaluare din prezentele reglementări, în funcție de modalitatea
de intrare în entitate.”; pct.8 pct.6: „costul de achiziție al bunurilor cuprinde prețul de cumpărare, taxele de import și alte taxe (cu
excepția acelora pe care persoana juridică le poate recupera de la autoritățile fiscale), cheltuielile de transport [...]” — aici prețul
de cumpărare = baza liniei (TVA-ul deductibil e recuperabil); cheltuielile conexe de pe alte documente nu sunt pe linia asta. Durata
normală de funcționare se alege în plaja Catalogului HG 2139/2004 (anexa, cap.I pct.4), ca la plusul de inventar
(`uc_tenants._verifica_catalog`, 521); metoda — CF art.28 (`inventariere.pregateste_mf_plus` refuză metoda nepermisă pe categorie).
Terenurile (211) nu se amortizează și imobilizările în curs (231) n-au încă fișă: nu intră aici.

Nu scrie SQL: citirile și scrierile trec prin depozite (`repo_operatiuni`, `repo_mijloace_fixe`, `mf_note`)."""
from datetime import date as _date
from decimal import ROUND_HALF_UP, Decimal

#: Grupele de conturi ale imobilizărilor AMORTIZABILE din planul de conturi (OMFP 1802/2014): 203 dezvoltare, 205 concesiuni / licențe,
#: 208 alte imobilizări necorporale; 212 construcții, 213 instalații / mijloace de transport, 214 mobilier și aparatură de birou
GRUPE_AMORTIZABILE = ("203", "205", "208", "212", "213", "214")
#: metodele de amortizare ale fișei (CF art.28), în ordinea formularului
METODE = ("liniara", "degresiva", "accelerata")
CAMPURI = ("cod_catalog", "dnf_luni", "data_pif", "metoda")


def e_imobilizare(cont):
    """Contul e al unei imobilizări amortizabile (linia aduce un mijloc fix în registru)."""
    return str(cont or "").strip()[:3] in GRUPE_AMORTIZABILE


def camp(manuala, i, c):
    """Id-ul câmpului pe ecran: `pr-mf<i>-<c>` (factura din XML, liniile de la 0) / `pm-mf<i+1>-<c>` (factura de mână, liniile de la 1)."""
    return "%s-mf%d-%s" % ("pm" if manuala else "pr", i + 1 if manuala else i, c)


def cere(f, corp, cont_factura):
    """[(index linie, date fișă)] — liniile facturii pe un cont de imobilizare, cu datele fișei cerute; altfel refuzul, cu TOATE câmpurile
    lipsă / greșite deodată, fiecare lângă linia lui. Nu scrie nimic (se cheamă înaintea oricărei scrieri)."""
    from core import erori as _erori, mf_registru as _mfr
    from core.common import cate as _cate
    manuala = bool(f.get("manuala"))
    conturi = list(corp.get("conturi") or [])
    date = list(corp.get("imobilizari") or [])
    er = _erori.ErorileFormularului("Factura primită nu s-a validat")
    out = []
    catalog = None
    for i, linie in enumerate(f.get("linii") or []):
        cont = (str(conturi[i] or "").strip() if i < len(conturi) else "") or str(cont_factura or "").strip()
        if not e_imobilizare(cont):
            continue
        d = (date[i] if i < len(date) else None) or {}
        cod = str(d.get("cod_catalog") or "").strip().rstrip(".")
        corporala = cont.startswith("21")
        c = None
        if corporala:
            catalog = catalog if catalog is not None else _mfr.catalog()
            c = catalog.get(cod)
            if not cod:
                er.camp(camp(manuala, i, "cod_catalog"), "Scrie codul din Catalogul HG 2139/2004 al mijlocului fix: durata se alege în plaja lui.")
            elif not c:
                er.camp(camp(manuala, i, "cod_catalog"), "Codul %s nu e în Catalogul HG 2139/2004." % cod)
        try:
            dnf = int(str(d.get("dnf_luni") or "").strip())
        except ValueError:
            dnf = 0
        if dnf <= 0:
            er.camp(camp(manuala, i, "dnf_luni"), "Scrie durata normală de funcționare, în luni.")
        elif c and not (c["ani_min"] * 12 <= dnf <= c["ani_max"] * 12):
            er.camp(camp(manuala, i, "dnf_luni"), "Durata se alege în plaja catalogului pentru codul %s (%s): între %d și %s." % (
                cod, c["denumire"], c["ani_min"] * 12, _cate(c["ani_max"] * 12, "lună", "luni")))
        pif = None
        try:
            pif = _date.fromisoformat(str(d.get("data_pif") or "").strip()[:10])
        except ValueError:
            er.camp(camp(manuala, i, "data_pif"), "Alege data punerii în funcțiune.")
        metoda = str(d.get("metoda") or "").strip()
        if metoda not in METODE:
            er.camp(camp(manuala, i, "metoda"), "Alege metoda de amortizare.")
        out.append((i, {"cont_imobilizare": cont, "denumire": str(linie.get("descriere") or "").strip()[:200] or "Mijloc fix",
                        "cod_catalog": cod or None, "dnf_luni": dnf, "data_pif": pif, "metoda": metoda}))
    er.refuza()
    return out


def inscrie(cur, schema, nota_id, factura_id, cereri):
    """Scrie activele liniilor în registru, inactive, legate de nota facturii (`mf_note`, „intrare”): devin active la validarea ei.
    Valoarea = baza liniei în lei (valoarea netă de pe factură, altfel cantitate × preț, înmulțită cu cursul facturii). -> [{id, cod,
    denumire, valoare}]."""
    from core import inventariere as _iv, mf_note as _mfn, repo_mijloace_fixe as _rmf, repo_operatiuni as _ro, sume_lei as _sl
    from core.uc_tenants import _numar_inventar, cont_amortizare_pentru
    linii = _ro.linii_factura(cur, schema, factura_id)
    curs = _sl.curs_factura(_ro.moneda_si_cursul_facturii(cur, schema, factura_id))
    out = []
    for i, c in cereri:
        _lid, cant, pret, neta = linii[i]
        baza = Decimal(str(neta)) if neta is not None else Decimal(str(cant or 0)) * Decimal(str(pret or 0))
        valoare = (baza * curs).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        reg = _iv.pregateste_mf_plus(dict(c, valoare=valoare, cont_amortizare=cont_amortizare_pentru(c["cont_imobilizare"])))
        cod = _numar_inventar(cur, schema, None)
        mid = _rmf.adauga_cu_reevaluare(cur, schema, cod, reg["denumire"], reg["cont_imobilizare"], reg["cont_amortizare"], reg["valoare"],
                                        reg["rezidual"], reg["dnf_luni"], reg["data_pif"], reg["metoda"], False)[0]
        if c["cod_catalog"]:
            _rmf.seteaza_cod_catalog_schema(cur, schema, mid, c["cod_catalog"])
        _rmf.in_asteptarea_validarii(cur, schema, mid)
        _mfn.leaga(cur, schema, mid, nota_id, "intrare")
        out.append({"id": mid, "cod": cod, "denumire": reg["denumire"], "valoare": str(valoare)})
    return out


#: refuzul când factura are o linie de imobilizare, dar nota ei nu s-a putut scrie: activul intră în registru DIN notă
FARA_NOTA = ("Mijlocul fix intră în registru din nota facturii, iar nota n-a putut fi scrisă: %s Corectează și validează din nou; "
             "nimic nu s-a salvat.")

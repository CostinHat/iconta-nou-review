# -*- coding: utf-8 -*-
"""Registrul mijloacelor fixe: amortizarea ÎNREGISTRATĂ în contabilitate, separat de calculul teoretic (decizia Costin 08.10.2026, W2,
verbatim în DECIZII).

„Registrul mijloacelor fixe arată «amortizat 4.200» pentru MF-001, dar 2813 are 2.400 (lipsește amortizarea ianuarie–septembrie 2026).
Decizie: registrul afișează amortizarea înregistrată în contabilitate, iar separat diferența față de calculul teoretic, cu lunile
neînregistrate. Închiderea lunii e blocată dacă amortizarea lunii nu e înregistrată. Registrul mai afișează durata, codul din catalog și
planul lunar de amortizare.”

CE E „ÎNREGISTRAT”: notele contabile nu poartă mijlocul fix pe linie, ci CONTUL de amortizare (2813 …). Deci:
  * soldul creditor al contului de amortizare (soldul inițial din planul de conturi + notele VALIDATE până azi) e cifra contabilă;
  * pe mijloc fix se atribuie numai când contul are UN SINGUR mijloc fix activ — altfel cifra e a contului, și se spune;
  * o lună e „înregistrată” pe un cont dacă are o notă validată care creditează contul (sau sinteticul lui) în luna aceea.
TEORETIC = `d406_active.amortizat_la_data` / `amortizare_luna` — același calcul care generează nota lunii (metoda reală, CF art.28).
CATALOGUL = HG 2139/2004 (anaf_surse/hg_2139_2004_catalog_clasificare_durate_mijloace_fixe.txt): codul de clasificare și plaja
duratei normale, în ani.
"""
import io
import os
import re
from decimal import Decimal

from core.common import cate as _cate

_CATALOG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "anaf_surse",
                        "hg_2139_2004_catalog_clasificare_durate_mijloace_fixe.txt")
_RAND = re.compile(r"^(\d+(?:\.\d+)+)\.\s+(.*?)[\s;:,.]*\s(\d+)\s*-\s*(\d+)\s*$")
TEMEI_CATALOG = "HG 2139/2004"


def catalog():
    """{cod: {denumire, ani_min, ani_max}} — numai codurile cu plajă de durată (grupele fără plajă nu se aleg). Fără cache de proces:
    citirea fișierului versionat costă ~3 ms (măsurat), iar un cache ar fi încă o stare de proces de declarat (P6)."""
    out = {}
    for linie in io.open(_CATALOG, encoding="utf-8"):
        if linie.strip() == "DICȚIONAR":   # anexa (corespondența cu HG 964/1998) nu e catalogul: se oprește aici
            break
        m = _RAND.match(linie.strip())
        if m:
            out[m.group(1)] = {"denumire": m.group(2).strip(" -"), "ani_min": int(m.group(3)), "ani_max": int(m.group(4))}
    return out


def verifica_cod(cod, dnf_luni):
    """(None, avertisment|None) dacă codul e în catalog; (refuz, None) altfel. Avertismentul: durata în afara plajei."""
    c = catalog().get(str(cod or "").strip().rstrip("."))
    if not c:
        return ("Codul %r nu e în Catalogul privind clasificarea și duratele normale de funcționare (%s) — scrie codul de "
                "clasificare, de exemplu 2.1.17.2.1." % (cod, TEMEI_CATALOG)), None
    if dnf_luni and not (c["ani_min"] * 12 <= int(dnf_luni) <= c["ani_max"] * 12):
        return None, ("Durata de %s e în afara plajei catalogului pentru codul %s (%d–%s)." %
                      (_cate(dnf_luni, "lună", "luni"), cod, c["ani_min"], _cate(c["ani_max"], "an", "ani")))
    return None, None


def _mf_dict(r):
    (mid, cod, den, ci, ca, val, rez, dnf, pif, met, activ, reev, dcd) = r[:13]
    # [359, A.1] `toate` poartă la sfârșit amortizarea preluată și data preluării (după `cod_catalog`)
    prel, dprel = (r[14], r[15]) if len(r) > 15 else (None, None)
    return {"id": mid, "cod": cod, "denumire": den, "cont_imobilizare": ci, "cont_amortizare": ca or "2813",
            "valoare": Decimal(str(val or 0)), "rezidual": Decimal(str(rez or 0)), "dnf_luni": dnf, "data_pif": pif,
            "metoda": met, "activ": bool(activ), "reevaluari": reev, "destinatie_cd": bool(dcd),   # ruta veche: bool (ecranul C&D)
            "amortizare_preluata": prel, "data_preluare": dprel}


def sold_creditor_cont(cur, cont, pana_la):
    """Soldul creditor al contului: soldul inițial din `solduri_initiale` (aceeași sursă ca balanța — `documente_api.balanta`; pe F2,
    2813 are acolo 2.200, iar în `plan_conturi` 0) + notele VALIDATE până la data dată (amortizarea „înregistrată” = notă validată)."""
    initial = sold_initial_cont(cur, cont)
    cur.execute("SELECT COALESCE(SUM(CASE WHEN l.cont_credit = %s OR l.cont_credit LIKE %s THEN l.suma ELSE 0 END), 0) "
                "- COALESCE(SUM(CASE WHEN l.cont_debit = %s OR l.cont_debit LIKE %s THEN l.suma ELSE 0 END), 0) "
                "FROM inregistrari_linii l JOIN inregistrari i ON i.id = l.inregistrare_id "
                "WHERE i.status = 'validata' AND i.data <= %s", (cont, cont + ".%", cont, cont + ".%", pana_la))
    r = cur.fetchone()
    return initial + Decimal(str((list(r.values())[0] if isinstance(r, dict) else r[0]) or 0))


def luni_inregistrate(cur, cont):
    """{(an, luna)} în care o notă VALIDATĂ creditează contul de amortizare (sau un analitic al lui)."""
    cur.execute("SELECT DISTINCT EXTRACT(YEAR FROM i.data)::int AS an, EXTRACT(MONTH FROM i.data)::int AS luna FROM inregistrari i "
                "JOIN inregistrari_linii l ON l.inregistrare_id = i.id WHERE i.status = 'validata' "
                "AND (l.cont_credit = %s OR l.cont_credit LIKE %s)", (cont, cont + ".%"))
    return {tuple(x.values()) if isinstance(x, dict) else tuple(x) for x in cur.fetchall()}


def luni_in_ciorna(cur, cont):
    """[deficiența 312] {(an, luna)} în care o notă CIORNĂ (generată, nevalidată) creditează contul de amortizare: închiderea spune
    „generată, de validat”, nu „neînregistrată”, iar „Generează amortizarea restantă” n-o mai oferă pentru ele."""
    cur.execute("SELECT DISTINCT EXTRACT(YEAR FROM i.data)::int AS an, EXTRACT(MONTH FROM i.data)::int AS luna FROM inregistrari i "
                "JOIN inregistrari_linii l ON l.inregistrare_id = i.id WHERE i.status = 'ciorna' "
                "AND (l.cont_credit = %s OR l.cont_credit LIKE %s)", (cont, cont + ".%"))
    return {tuple(x.values()) if isinstance(x, dict) else tuple(x) for x in cur.fetchall()}


def _luni(de_la, pana_la):
    an, luna = de_la
    while (an, luna) <= pana_la:
        yield an, luna
        luna += 1
        if luna > 12:
            an, luna = an + 1, 1


def sold_initial_cont(cur, cont):
    """Soldul creditor inițial al contului de amortizare, din `solduri_initiale` (amortizarea cumulată la preluare)."""
    cur.execute("SELECT COALESCE(SUM(sold_creditor), 0) - COALESCE(SUM(sold_debitor), 0) FROM solduri_initiale "
                "WHERE cont = %s OR cont LIKE %s", (cont, cont + ".%"))
    r = cur.fetchone()
    return Decimal(str((list(r.values())[0] if isinstance(r, dict) else r[0]) or 0))


def luni_acoperite_de_soldul_initial(mfs, sold_initial):
    """{(an, luna)} acoperite de soldul inițial al contului: amortizarea cumulată la preluare stinge lunile CELE MAI VECHI ale
    planului (toate mijloacele de pe cont, însumate pe lună), în ordine, cât încape. Pe F2: 2.200 / 200 = 11 luni (02–12.2025).
    Fără asta, lunile dinaintea preluării ar apărea „neînregistrate” deși amortizarea lor e chiar în soldul preluat."""
    from core import d406_active as _a
    pe_luna = {}
    for m in mfs:
        if not (m["activ"] and m["data_pif"] and m["dnf_luni"]):
            continue
        _k = m["data_pif"].month + int(m["dnf_luni"])
        for an, luna in _luni((m["data_pif"].year, m["data_pif"].month), (m["data_pif"].year + (_k - 1) // 12, (_k - 1) % 12 + 1)):
            try:
                rata = Decimal(str(_a.amortizare_luna(m, an, luna)))
            except ValueError:   # metodă nepermisă / date invalide: rândul registrului o arată (`eroare`), aici nu se ghicește o rată
                break
            if rata > 0:
                pe_luna[(an, luna)] = pe_luna.get((an, luna), Decimal(0)) + rata
    acoperite, cumul = set(), Decimal(0)
    for k in sorted(pe_luna):
        if cumul + pe_luna[k] > sold_initial + Decimal("0.01"):
            break
        cumul += pe_luna[k]
        acoperite.add(k)
    return acoperite


def plan_lunar(mf, inregistrate, azi, acoperite=frozenset()):
    """[(an, luna, rata, stare)] de la luna PIF până la sfârșitul duratei; stare: sold_initial / inregistrata / neinregistrata /
    in_curs / viitoare."""
    from core import d406_active as _a
    pif = mf["data_pif"]
    if not pif or not mf["dnf_luni"]:
        return []
    _k = pif.month + int(mf["dnf_luni"])          # luna PIF + durata (amortizarea începe în luna următoare PIF)
    final = (pif.year + (_k - 1) // 12, (_k - 1) % 12 + 1)
    out = []
    for an, luna in _luni((pif.year, pif.month), final):
        rata = Decimal(str(_a.amortizare_luna(mf, an, luna)))
        if rata <= 0:
            continue
        stare = ("viitoare" if (an, luna) > (azi.year, azi.month) else "in_curs" if (an, luna) == (azi.year, azi.month)
                 else "inregistrata" if (an, luna) in inregistrate else "sold_initial" if (an, luna) in acoperite
                 else "neinregistrata")
        out.append((an, luna, rata, stare))
    return out


def amortizare_lunii_neinregistrata(cur, rows, an, luna):
    """[W2] [{cont, rata}] — conturile de amortizare cu rată teoretică > 0 în (an, luna) a unor active a căror amortizare a lunii nu e
    trecută PE ACTIV într-o notă validată (lotul 13, 522: „Amortizarea înregistrată se ține pe fiecare activ” — înainte, o lună era
    „înregistrată” pe cont dacă orice notă validată credita contul, deci luna lipsă a unui activ nou se ascundea sub nota celorlalte),
    în afara lunilor acoperite de soldul preluat; plus {cont, rata: None, eroare} pentru mijlocul a cărui rată nu se poate calcula
    (metodă nepermisă). Baza blocajului închiderii lunii. `cur` are `search_path` pe firmă (rândurile sunt ale lui `toate`)."""
    import datetime as _dt
    from core import d406_active as _a, mf_note as _mfn
    pe_cont, mfs, necalculabile = {}, {}, []
    sfarsit = _dt.date(int(an) + (int(luna) == 12), int(luna) % 12 + 1, 1) - _dt.timedelta(days=1)
    pa = _mfn.pe_activ(cur, None, sfarsit)
    for m in (_mf_dict(r) for r in rows):
        if not (m["activ"] and m["data_pif"] and m["dnf_luni"]):
            continue
        mfs.setdefault(m["cont_amortizare"], []).append(m)
        try:
            rata = Decimal(str(_a.amortizare_luna(m, an, luna)))
        except ValueError as e:   # nu se ghicește o rată: închiderea se oprește pe ea, cu motivul
            necalculabile.append({"cont": m["cont_amortizare"], "rata": None, "eroare": str(e)})
            continue
        if rata > 0 and (an, luna) not in pa.get(m["id"], {}).get("luni", set()):
            pe_cont.setdefault(m["cont_amortizare"], Decimal(0))
            pe_cont[m["cont_amortizare"]] += rata
    return necalculabile + [{"cont": c, "rata": str(v)} for c, v in sorted(pe_cont.items())
                            if (an, luna) not in luni_acoperite_de_soldul_initial(mfs[c], sold_initial_cont(cur, c) - preluat_pe_cont(mfs[c]))]


def preluat_pe_cont(mfs):
    """[359, A.1] Amortizarea preluată din registrul vechi a mijloacelor contului: e în soldul inițial, dar lunile ei nu mai sunt ale iConta
    (`d406_active._preluare` le dă rata 0), deci nu acoperă lunile celorlalte mijloace ale contului."""
    from core import d406_active as _a
    return sum((pr[1] for pr in (_a._preluare(m) for m in mfs) if pr is not None), Decimal(0))


def luni_anterioare_neinregistrate(cur, rows, an, luna):
    """[deficiența 215, retestul Costin 09.10: „Închidere lună: lunile anterioare cu amortizare neînregistrată nu apar ca semnal”]
    [{cont, luni: [(an, luna)…], total}] — lunile DINAINTEA lunii (an, luna), de la prima lună de amortizare a registrului, în care
    rata unui cont de amortizare nu e înregistrată (aceeași regulă ca blocajul lunii: `amortizare_lunii_neinregistrata`)."""
    pifuri = [m["data_pif"] for m in (_mf_dict(r) for r in rows) if m["activ"] and m["data_pif"] and m["dnf_luni"]]
    if not pifuri:
        return []
    p = min(pifuri)
    p = p if hasattr(p, "year") else __import__("datetime").date.fromisoformat(str(p)[:10])
    a, l = (p.year + 1, 1) if p.month == 12 else (p.year, p.month + 1)   # amortizarea începe în luna de după punerea în funcțiune
    pe_cont = {}
    while (a, l) < (an, luna):
        for x in amortizare_lunii_neinregistrata(cur, rows, a, l):
            if x.get("rata") is None:
                continue
            d = pe_cont.setdefault(x["cont"], {"cont": x["cont"], "luni": [], "total": Decimal(0), "rate": {}})
            d["luni"].append((a, l))
            d["total"] += Decimal(str(x["rata"]))
            d["rate"][(a, l)] = Decimal(str(x["rata"]))   # [312] rata pe lună: lunile deja generate se scad din total
        a, l = (a + 1, 1) if l == 12 else (a, l + 1)
    return [pe_cont[c] for c in sorted(pe_cont)]


def luni_ca_interval(luni):
    """[(2026, 5), (2026, 6), (2026, 7), (2026, 9)] -> „05–07/2026, 09/2026” (lunile consecutive se strâng, ca pe ecranul Mijloace fixe)."""
    out, i = [], 0
    while i < len(luni):
        j = i
        while j + 1 < len(luni) and (luni[j + 1][0] * 12 + luni[j + 1][1]) == (luni[j][0] * 12 + luni[j][1]) + 1:
            j += 1
        (a1, l1), (a2, l2) = luni[i], luni[j]
        out.append("%02d/%d" % (l1, a1) if i == j else ("%02d–%02d/%d" % (l1, l2, a1) if a1 == a2 else "%02d/%d–%02d/%d" % (l1, a1, l2, a2)))
        i = j + 1
    return ", ".join(out)


def registru(cur, rows, azi=None):
    """Rândurile registrului (din `repo_mijloace_fixe.toate`) cu amortizarea teoretică, cea înregistrată PE ACTIV, diferența, lunile
    neînregistrate, durata, codul din catalog, planul lunar și starea (activ / casat / intrare sau casare în așteptarea validării).

    [lotul 13, deficiența 522, comanda Costin 13.1] „Coloana «Înregistrat» se citește pe cont (2813), nu pe activ. Cu MF-001 «casat»,
    întreaga amortizare a lui (4.000) apare la MF-PLUS […] Amortizarea înregistrată se ține pe fiecare activ.” Înregistrat = partea
    activului din soldul preluat (amortizarea preluată din registrul vechi sau ratele lui din lunile acoperite de sold) + rândurile LUI pe
    contul de amortizare din notele validate (`mf_note.pe_activ`). Ce stă pe cont fără activ (notă manuală) se arată separat, pe cont."""
    from core import d406_active as _a, inchidere_luna as _il, mf_note as _mfn
    from core.common import azi_ro
    from core import eticheta_nota as _et
    azi = azi or azi_ro()   # ziua României, ca `ultima_zi_incheiata` și închiderea lunii
    pana = _il.ultima_zi_incheiata(azi)   # [Retest 2 pct.5] calculul și soldul înregistrat: până la ultima lună încheiată
    mfs = [_mf_dict(r) for r in rows]
    cod_cat = {r[0]: (r[13] if len(r) > 13 else None) for r in rows}
    cat = catalog()
    pe_cont = {}
    for m in mfs:
        if m["activ"]:
            pe_cont.setdefault(m["cont_amortizare"], []).append(m["id"])
    sold = {c: sold_creditor_cont(cur, c, pana) for c in pe_cont}
    acoperite = {c: luni_acoperite_de_soldul_initial([m for m in mfs if m["activ"] and m["cont_amortizare"] == c],
                                                     sold_initial_cont(cur, c)) for c in pe_cont}
    pa = _mfn.pe_activ(cur, None, pana)
    asteapta = _mfn.in_asteptare(cur, None)
    out = []
    for m in mfs:
        e = {"amortizat_teoretic": None, "ramas": None, "eroare": None, "inregistrat": None, "inregistrat_pe_cont": None,
             "diferenta": None, "luni_neinregistrate": [], "plan_lunar": [], "cod_catalog": cod_cat.get(m["id"]),
             "catalog": cat.get(str(cod_cat.get(m["id"]) or "").rstrip(".")), "durata_luni": m["dnf_luni"]}
        st = asteapta.get(m["id"], {})
        if "intrare" in st:   # [519] adus de o ciornă: intră în registru la validarea ei
            e["stare"], e["nota_asteptare"] = "intrare_in_asteptare", _et.nota(cur, None, st["intrare"][0])
        elif "iesire" in st:  # [519] casarea e ciornă: activul rămâne activ până la validarea ei
            e["stare"], e["nota_asteptare"] = "casare_in_asteptare", _et.nota(cur, None, st["iesire"][0])
        else:
            e["stare"] = "activ" if m["activ"] else "casat"
        if m["activ"]:
            try:
                t = _a.amortizat_la_data(m, pana)
                e["amortizat_teoretic"], e["ramas"] = str(t["amortizat"]), str(t["ramas"])
                c = m["cont_amortizare"]
                pm = pa.get(m["id"], {"inregistrat": Decimal(0), "luni": set(), "luni_ciorna": set()})
                plan = plan_lunar(m, pm["luni"], azi, acoperite[c])
                e["plan_lunar"] = [{"an": a, "luna": l, "rata": str(r), "stare": ("in_ciorna" if s == "neinregistrata" and (a, l) in pm["luni_ciorna"]
                                                                                   else s)} for a, l, r, s in plan]
                e["luni_neinregistrate"] = ["%02d/%d" % (l, a) for a, l, r, s in plan if s == "neinregistrata" and (a, l) not in pm["luni_ciorna"]]
                e["luni_in_ciorna"] = ["%02d/%d" % (l, a) for a, l, r, s in plan if s == "neinregistrata" and (a, l) in pm["luni_ciorna"]]
                pr = m.get("amortizare_preluata")
                din_sold = Decimal(str(pr)) if pr is not None else sum((r for a, l, r, s in plan if s == "sold_initial"), Decimal(0))
                inreg = din_sold + pm["inregistrat"]
                e["inregistrat"] = str(inreg)
                e["diferenta"] = str(Decimal(str(t["amortizat"])) - inreg)
                e["inregistrat_pe_cont"] = {"cont": c, "sold": str(sold[c]), "mijloace": len(pe_cont[c])}
            except (ValueError, KeyError) as ex:
                e["eroare"] = str(ex)
        out.append(dict(m, valoare=str(m["valoare"]), rezidual=str(m["rezidual"]),
                        metoda_eticheta=_a.eticheta_metoda(m.get("metoda")),   # [Retest 2 pct.2]
                        data_pif=str(m["data_pif"]) if m["data_pif"] else None, reevaluari=None,
                        amortizat=e["amortizat_teoretic"], **e))
    # [522] ce stă pe contul de amortizare fără activ (o notă manuală): se spune pe cont, nu se pune pe un activ
    for c in pe_cont:
        nealocat = sold[c] - sum((Decimal(x["inregistrat"]) for x in out if x["activ"] and x["cont_amortizare"] == c and x["inregistrat"]),
                                 Decimal(0))
        for x in out:
            if x["activ"] and x["cont_amortizare"] == c and x["inregistrat_pe_cont"]:
                x["inregistrat_pe_cont"]["nealocat"] = str(nealocat)
    return out


def inregistrat_pe_activ(cur, schema, rows, mijloc_fix_id, la_data):
    """[lotul 13, 518 / 516] Amortizarea ÎNREGISTRATĂ a activului la `la_data`: partea lui din soldul preluat + rândurile lui validate
    (aceeași regulă ca registrul). `cur` cu `search_path` pe firmă; `rows` = `repo_mijloace_fixe.toate`."""
    from core import mf_note as _mfn
    mfs = [_mf_dict(r) for r in rows]
    m = next(x for x in mfs if x["id"] == int(mijloc_fix_id))
    c = m["cont_amortizare"]
    acoperite = luni_acoperite_de_soldul_initial([x for x in mfs if x["activ"] and x["cont_amortizare"] == c], sold_initial_cont(cur, c))
    pr = m.get("amortizare_preluata")
    if pr is not None:
        din_sold = Decimal(str(pr))
    else:
        from core import d406_active as _a
        din_sold = sum((Decimal(str(_a.amortizare_luna(m, a, l))) for a, l in acoperite
                        if (a, l) > (m["data_pif"].year, m["data_pif"].month)), Decimal(0))
    return din_sold + _mfn.pe_activ(cur, None, la_data).get(m["id"], {}).get("inregistrat", Decimal(0))

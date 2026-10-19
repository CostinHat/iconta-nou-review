"""
core/mijloace_fixe_import_api.py — import mijloace fixe (stratul 6 migrare) per firma.

Citeste un registru de mijloace fixe (.xlsx/.csv) cu: cod, denumire, valoare intrare,
valoare reziduala, durata (luni), data PIF, metoda, conturi; optional valoarea ramasa (neamortizata).
Importa in tabelul existent `mijloace_fixe` (DELETE + INSERT per firma).

Verificari informative (nu blocante):
- rezidual <= valoare (altfel eroare de date)
- valoare >= 5000 lei (plafon 2026 OUG 8/2026); sub plafon = avertisment
  (mijloacele existente la 31.12.2025 raman amortizabile pe durata ramasa - regula tranzitorie)
Amortizarea cumulata = cea calculata de MOTOR (d406_active.amortizat_la_data) din valoare, data PIF,
durata si metoda — NU valoare minus coloana „ramas" din fisier.

[Lot 19 defect 6, 03.10.2026] REZIDUAL NU E „RAMAS". Coloana „ramas / neamortizat" (valoarea contabila
neta la data exportului) se citea in `rezidual`, iar motorul trateaza `rezidual` ca valoare NEAMORTIZABILA
(amortizabil = valoare - rezidual) — deci un activ preluat la jumatatea duratei nu se mai amortiza in partea
ramasa, iar un fisier fara coloana primea rezidual = valoare (zero amortizare, pe toata durata). Temei:
OMFP 1802/2014 pct.139 alin.(2): „Amortizarea valorii activelor imobilizate cu durate limitate de utilizare
economica reprezinta alocarea sistematica a valorii amortizabile a unui activ pe intreaga durata de utilizare
economica. Valoarea amortizabila este reprezentata de cost sau de alta valoare care substituie costul".
Acum: `rezidual` vine DOAR dintr-o coloana numita „rezidual/reziduala" (lipsa = 0); coloana „ramas" e o
VERIFICARE — daca difera de valoarea ramasa calculata de motor la data importului cu mai mult de o rata
lunara, randul primeste avertisment (nu blocheaza: amortizarea se calculeaza din PIF, durata, metoda).

"""
# [E2b, 15.09.2026] Tranzactia e a APELANTULUI: `db.get_conn` comite la iesirea din bloc, iar un
# `commit` aici ar taia tranzactia lui in doua (P4). Depozitul primeste conexiunea si scrie; nu
# deschide, nu comite.
from __future__ import annotations
import re as _re
import datetime

from core import obiecte_inventar as _oi
from core.pdf_util import bani as _bani, data_ro as _data_ro   # DS cap.4: sumele și datele din text, canonic

# PRAGUL NU MAI E SCRIS AICI (01.09.2026, R108). Era `PLAFON_MF_2026 = 5000.0` — un literal FARA
# DATA, deci avertismentul iesea gresit pentru bunurile intrate inainte de 01.01.2026, cand pragul
# era 2.500. Se cere acum de la singura poarta, `obiecte_inventar.prag_mf(la_data)`, care citeste
# registrul.


from core.numere import numar as _numar  # sursa unica (15.07.2026, vezi core/numere.py)
from core.migrare_api import respinge  # [P8/C] respingerea e o afirmatie, cu regula din nomenclator


def _intreg(v):
    return int(round(_numar(v)))




#: metodele de amortizare ale Codului fiscal (CF art.28): liniară, degresivă, accelerată, superaccelerată (alin.8^1, OUG 8/2026)
METODE = ("liniara", "degresiva", "accelerata", "superaccelerata")


def _normalizeaza_metoda(v):
    """Metoda din celulă -> una din METODE; celula goală -> "" (se semnalează: liniară implicit); altceva -> None (rândul se respinge).
    [361, comanda Costin 8.2 pct.4: „nimic nu se înlocuiește pe tăcute”] până azi o metodă necunoscută („inventata”) devenea liniară."""
    t = _re.sub(r"[\s._-]+", "", str(v or "").lower())   # colapseaza separatorii: "super accelerata" -> "superaccelerata"
    if not t:
        return ""
    if "superaccel" in t:          # INAINTE de "acceler": "superaccelerata" contine "acceler"
        return "superaccelerata"   # CF art.28 alin.8^1 (OUG 8/2026)
    if "degres" in t:
        return "degresiva"
    if "acceler" in t:
        return "accelerata"
    if "linia" in t:
        return "liniara"
    return None


def e_teren(cont_imob):
    """Contul 2111 „Terenuri” (sau sinteticul 211 fără analitic): terenul nu se amortizează (CF art.28 alin.(3) lit.a)), deci durata 0 e
    corectă. [362] Amenajările de terenuri (2112) se amortizează (2811)."""
    c = str(cont_imob or "").strip().split(".")[0]
    return c in ("211", "2111")


def cont_amortizare_asteptat(cont_imob):
    """Contul de amortizare care corespunde contului de imobilizare, după planul OMFP 1802/2014: 28 + cifrele 2–3 ale contului (205 ->
    2805, 2131 -> 2813, 212 -> 2812, 2112 -> 2811); None pentru teren sau un cont care nu e de imobilizări amortizabile."""
    c = str(cont_imob or "").strip().split(".")[0]
    if len(c) < 3 or not c.isdigit() or c[0] != "2" or c[:2] in ("23", "26", "27", "28", "29") or e_teren(c):
        return None
    return "28" + c[1:3]


# [14.10.2026, comanda Costin „Importul din SAGA”, verbatim în DECIZII] Fișierul trece prin `core.import_tabel`. Antetele SAGA
# vin din manualul SAGA C, ecranul Imobilizări (`anaf_surse/saga_manual_topic34_imobilizari.txt`): „Nr.inv.”, „Denumire”,
# „Nr.document”, „Gestiune”, „Cod clasă”, „Data intrare”, „Valoare intrare”, „Valoare inventar”, „Dur.luni”, „Tip amortizare”,
# „Val. ramasa”, „Dur. ramasă”, „Amort. lunara”, „Amort. inreg.”, „Necorp.”, „Cont”, „Cont amortizare”, „Cont cheltuiala”.
# Până azi, pe un astfel de export, valoarea de intrare se lua din „Data intrare” (prima coloană care conținea „intrare”), iar
# contul de imobilizare („Cont”) nu se recunoștea deloc.
from core import import_tabel as _it

CAMPURI = {
    "cod": ("nr inv", "nr inventar", "numar inventar", "numar de inventar", "cod inventar", "cod", "inventar"),
    "denumire": ("denumire mijloc fix", "denumire", "mijloc fix", "nume"),
    "rezidual": ("valoare reziduala", "rezidual*"),
    "ramas": ("val ramasa", "valoare ramasa", "valoare neamortizata", "ramas", "ramasa", "neamortizat*"),
    "amortizat": ("amort inreg", "amortizare inregistrata", "amortizare cumulata", "amortizat"),
    "valoare": ("valoare intrare", "valoare de intrare", "valoare achizitie", "valoare de achizitie", "cost achizitie",
                "valoare"),
    "valoare_inventar": ("valoare inventar",),
    "durata": ("dur luni", "durata luni", "durata normala", "durata*", "luni", "dnf"),
    "pif": ("data pif", "data punerii in functiune", "data intrare", "pif", "punere in functiune", "data"),
    "metoda": ("tip amortizare", "metoda amortizare", "metoda de amortizare", "metoda*"),
    "cont_imob": ("cont imobilizare", "cont imob", "=cont"),
    "cont_amort": ("cont amortizare", "cont amort"),
    "cd": ("cercetare*", "c d", "destinat cd", "destinatie cd"),
}


def extrage(continut, nume_fisier="", data_preluare=None):
    """Lista de dicturi cu câmpurile mijlocului fix, cu `stare` (ok / semnalat / respins) și `motive`, din ACEEAȘI verificare pe care o
    aplică salvarea. [359] `data_preluare` = data soldurilor de deschidere (`bilant_api.data_soldurilor`): amortizarea cumulată din fișier
    („amortizare cumulată” / „amortizare înregistrată”, sau valoarea minus „valoare rămasă”) se ia LA ACEA DATĂ și se compară cu cea
    calculată din PIF, durată și metodă la aceeași dată (fără ea: azi)."""
    brut = _it.citeste(continut, nume_fisier)
    if not brut or all(_it.rand_gol(r) for r in brut):
        return []
    try:
        antet, start = _it.gaseste_antet(brut, CAMPURI, obligatorii=("denumire",), nume_fisier=nume_fisier)
    except _it.FisierNecitit as e:
        if isinstance(e, _it.ColoaneAmbigue):
            raise
        raise ValueError("nu se găsește coloana denumire mijloc fix - fișier nerecunoscut")
    col = lambda camp, exclus=(): _it.coloana(antet, CAMPURI[camp], exclus=exclus, camp=camp)
    i_den = col("denumire")
    i_cod = col("cod", (i_den,))
    # rezidual si ramas se identifica INTAI, ca „valoare reziduala" / „valoare ramasa" sa nu fie luate drept
    # valoarea de intrare cand stau inaintea ei in antet
    i_rez = col("rezidual")
    i_dur = col("durata")
    i_ram = col("ramas", (i_rez, i_dur) + tuple(j for j, h in enumerate(antet) if h.split()[:1] in (["dur"], ["durata"])))
    i_amz = col("amortizat")
    i_vinv = col("valoare_inventar")
    i_pif = col("pif")
    i_val = col("valoare", (i_rez, i_ram, i_vinv, i_pif))
    i_met = col("metoda")
    i_camo = col("cont_amort")
    i_cimo = col("cont_imob", (i_camo,))
    i_cd = col("cd")   # [lot 19 d11]
    la = data_preluare or datetime.date.today()

    out = []
    for idx, r in enumerate(brut[start:], start=1):
        nr = start + idx

        def cel(i):
            return _it.celula(r, i)
        den = cel(i_den)
        if not den:
            if any(str(x or "").strip() for x in r):   # [pct.4] un rând cu date nu dispare: se arată, respins, cu motivul
                out.append({"rand_fisier": nr, "cod": cel(i_cod), "denumire": "", "valoare": _numar(cel(i_val)), "rezidual": 0.0,
                            "dnf_luni": _intreg(cel(i_dur)), "data_pif": _it.data(_it.valoare(r, i_pif)) if i_pif >= 0 else None,
                            "data_pif_brut": str(_it.valoare(r, i_pif) or "") if i_pif >= 0 else "",
                            "metoda": "", "metoda_brut": cel(i_met), "cont_imobilizare": cel(i_cimo), "cont_amortizare": cel(i_camo),
                            "amortizat_preluat": None, "amortizat_calculat": None, "destinatie_cd": False, "semnale_extra": []})
            continue
        valoare = _numar(cel(i_val))
        rezidual = _numar(cel(i_rez)) if i_rez >= 0 else 0.0   # lipsa coloanei = 0, NU valoare (defect 6)
        durata = _intreg(cel(i_dur))
        # durata in ani -> luni daca pare ani (< 60 si fisierul zice "ani")
        if 0 < durata <= 50 and any(w.startswith("an") for w in (antet[i_dur].split() if i_dur >= 0 else [])):
            durata *= 12
        _pif_iso = _it.data(_it.valoare(r, i_pif)) if i_pif >= 0 else None
        try:
            _pif = datetime.date.fromisoformat(_pif_iso) if _pif_iso else None
        except ValueError:
            _pif = None
        metoda = _normalizeaza_metoda(cel(i_met))
        semnale = []
        _prag = float(_oi.prag_mf(_pif))
        _cand = _data_ro(_pif) if _pif else "dată lipsă"
        if 0 < valoare < _prag:
            if _oi.prag_mf_cunoscut(_pif):
                semnale.append("sub plafonul de mijloc fix de %s, la data intrării %s" % (_bani(_prag, "lei"), _cand))
            else:
                # Necunoscutul nu se rotunjeste la „stiu ca nu": registrul n-are prag pentru data aia
                semnale.append("sub cel mai vechi plafon cunoscut (%s) — registrul n-are prag verificat pentru %s" % (_bani(_prag, "lei"), _cand))
        if metoda == "" and not e_teren(cel(i_cimo)):
            semnale.append("fără metodă de amortizare: se amortizează liniar (metoda de bază a CF art.28)")
        if not cel(i_cimo):
            semnale.append("cont de imobilizare lipsă - categorie neclasificată (CF art.28 alin.5 lit.c): doar liniar/degresiv; "
                           "accelerat/superaccelerat vor fi refuzate la D406 până se completează contul")
        dcd = _da_nu(cel(i_cd)) if i_cd >= 0 else False
        if dcd is None:
            semnale.append("coloana C&D are valoarea %r — se acceptă da/nu; activul intră fără destinația C&D" % cel(i_cd))
            dcd = False
        # [comanda Costin 8.2 pct.4: „nimic nu se înlocuiește pe tăcute”] codul de inventar lipsă primește unul generat — spus pe rând
        if not cel(i_cod):
            semnale.append("fără cod de inventar în fișier — primește codul MF%03d; îl poți schimba în registrul mijloacelor fixe" % idx)
        # [359] amortizarea cumulată PRELUATĂ, la data preluării: coloana ei, altfel valoarea minus valoarea rămasă din fișier
        preluat, din_ce = None, ""
        if i_amz >= 0 and str(cel(i_amz)).strip() != "":
            preluat = _numar(cel(i_amz))
        elif i_ram >= 0 and str(cel(i_ram)).strip() != "":
            preluat = valoare - _numar(cel(i_ram))
            # cifra scrisă de contabil e valoarea rămasă: mesajul pornește de la ea, nu de la diferența calculată
            din_ce = " = valoarea de intrare %s − valoarea rămasă din fișier %s" % (_bani(valoare, "lei"), _bani(_numar(cel(i_ram)), "lei"))
        calculat, _ram = _la_zi(valoare, rezidual, durata, _pif, metoda or "liniara", cel(i_cimo), dcd, la)
        if e_teren(cel(i_cimo)) and durata <= 0:
            calculat = 0.0
        if preluat is not None and calculat is not None and durata > 0 and abs(preluat - calculat) > (valoare - rezidual) / durata + 1:
            semnale.append("amortizarea preluată (%s%s) diferă de cea calculată la %s din PIF, durată și metodă (%s): verifică data PIF, "
                           "durata și metoda — după preluare amortizarea continuă din calcul" % (
                               _bani(preluat, "lei"), din_ce, _data_ro(la), _bani(calculat, "lei")))
        if i_vinv >= 0 and cel(i_vinv) != "" and abs(_numar(cel(i_vinv)) - valoare) > 0.01:
            semnale.append(
                "valoarea de inventar din fișier (%s) diferă de valoarea de intrare (%s) — în aplicația veche au fost modernizări sau "
                "reevaluări, care nu se preiau: amortizarea continuă din valoarea de intrare. Dacă activul a fost modernizat sau reevaluat, "
                "valoarea și durata din fișier trebuie aduse la zi înainte de import" % (_bani(_numar(cel(i_vinv)), "lei"), _bani(valoare, "lei")))
        out.append({
            "rand_fisier": nr,
            "cod": cel(i_cod) or f"MF{idx:03d}",
            "denumire": den,
            "valoare": valoare,
            "rezidual": rezidual,
            "amortizat_preluat": preluat,     # [359] din registrul vechi, la data preluării
            "amortizat_calculat": calculat,   # din motor, la aceeași dată (None daca motorul nu poate calcula randul)
            "data_preluare": la.isoformat(),
            "dnf_luni": durata,
            "data_pif": _pif_iso,
            "data_pif_brut": str(_it.valoare(r, i_pif) or "") if i_pif >= 0 else "",
            "metoda": metoda or "liniara" if metoda is not None else "",
            "metoda_brut": cel(i_met),
            "cont_imobilizare": cel(i_cimo),   # NU se completeaza tacit cu 2131 (categoria permisiva); gol -> lit.c
            "cont_amortizare": cel(i_camo) or (cont_amortizare_asteptat(cel(i_cimo)) or ""),
            "destinatie_cd": dcd,               # CF art.20 alin.(1) lit.b): accelerata si pt aparatura C&D
            "semnale_extra": semnale,
        })
    eticheteaza(out, la)
    return out


def eticheteaza(randuri, azi=None):
    """[comanda Costin 8.2 pct.4] `stare` ∈ ok / semnalat / respins și `motive`, din ACEEAȘI verificare pe care o aplică salvarea."""
    er = verifica_randuri(randuri, azi)
    for r in randuri:
        resp = [e["mesaj"] for e in er if e.get("rand") == r["rand_fisier"]]
        obs = list(r.get("semnale_extra") or [])
        r["stare"] = "respins" if resp else ("semnalat" if obs else "ok")
        r["motive"] = resp or obs
    return randuri


def _da_nu(v):
    """„da”/„nu” dintr-o celulă de import (da/nu, x, 1/0, true/false); gol = nu; altceva = None (avertisment)."""
    s = str(v or "").strip().lower()
    if s in ("", "nu", "0", "false", "n", "-"):
        return False
    if s in ("da", "x", "1", "true", "d"):
        return True
    return None


def _la_zi(valoare, rezidual, durata, pif, metoda, cont_imob, destinatie_cd=False, la=None):
    """(amortizat, ramas) la data `la` (implicit azi), din motorul unic — sau (None, None) cand randul nu se poate calcula
    (durata/valoare lipsa, metoda nepermisa pe categorie); motivul e in respingerile randului."""
    from core import d406_active
    try:
        r = d406_active.amortizat_la_data({"valoare": valoare, "rezidual": rezidual, "dnf_luni": durata,
                                           "data_pif": pif, "metoda": metoda, "cont_imobilizare": cont_imob,
                                           "destinatie_cd": destinatie_cd},
                                          la or datetime.date.today())
    except ValueError:
        return None, None
    return float(r["amortizat"]), float(r["ramas"])


def rezumat(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('mijloace_fixe')")
        if cur.fetchone()[0] is None:
            return {"are_mijloace": False, "randuri": 0, "total_valoare": 0, "total_rezidual": 0}
        cur.execute("SELECT count(*), COALESCE(sum(valoare),0), COALESCE(sum(rezidual),0) FROM mijloace_fixe")
        n, tv, tr = cur.fetchone()
    return {"are_mijloace": n > 0, "randuri": n,
            "total_valoare": float(tv), "total_rezidual": float(tr)}


def verifica_randuri(randuri, azi=None):
    """PURĂ: respingerile [{rand, motiv, mesaj}] — rândurile care NU intră. [comanda Costin 8.2] 361: PIF în viitor și metoda inexistentă se
    resping (o metodă necunoscută devenea tăcut liniară); 362: contul de imobilizare e din clasa 2, iar cel de amortizare îi corespunde
    (205 -> 2805, 2131 -> 2813); terenul (2111) nu se amortizează, deci durata 0 e corectă acolo; 363: valoarea de intrare negativă se
    numește ca atare, cu suma în format românesc."""
    azi = azi or datetime.date.today()
    er, coduri = [], {}
    for i, r in enumerate(randuri or [], start=2):
        i = _it.nr_rand(r, i)
        cod = str(r.get("cod") or "").strip()
        den = str(r.get("denumire") or "").strip()
        eticheta = den or cod or "rândul %s" % i
        val = float(r.get("valoare") or 0)
        rez = float(r.get("rezidual") or 0)
        dur = int(r.get("dnf_luni") or r.get("durata") or 0)   # [Q3] cheia reala e dnf_luni
        cimo = str(r.get("cont_imobilizare") or "").strip()
        camo = str(r.get("cont_amortizare") or "").strip()
        teren = e_teren(cimo)
        if not den:
            er.append(respinge("mijloc fix", i, "denumire_lipsa", "%s: rândul n-are denumirea mijlocului fix" % eticheta))
        if not cod:
            er.append(respinge("mijloc fix", i, "cod_lipsa", "%s: fără cod de inventar" % eticheta))
        elif cod in coduri:
            er.append(respinge("mijloc fix", i, "cod_duplicat",
                               "codul de inventar %s apare de două ori (rândurile %s și %s)" % (cod, coduri[cod], i)))
        else:
            coduri[cod] = i
        if val < 0:
            er.append(respinge("mijloc fix", i, "valoare_lipsa", "%s: valoarea de intrare %s e negativă" % (eticheta, _bani(val, "lei"))))
        elif val == 0:
            er.append(respinge("mijloc fix", i, "valoare_lipsa", "%s: valoarea de intrare lipsește (0)" % eticheta))
        elif rez > val + 0.01:
            er.append(respinge("mijloc fix", i, "rezidual_peste_intrare",
                               "%s: valoarea reziduală (%s) depășește valoarea de intrare (%s)" % (eticheta, _bani(rez, "lei"), _bani(val, "lei"))))
        if dur <= 0 and not teren:
            er.append(respinge("mijloc fix", i, "durata_lipsa",
                               "%s: durata în luni lipsește sau nu e pozitivă (%s) - fără ea nu se calculează amortizarea" % (eticheta, dur)))
        pif = r.get("data_pif")
        if not pif and str(r.get("data_pif_brut") or "").strip():
            er.append(respinge("mijloc fix", i, "data_invalida", "%s: data PIF %r nu se înțelege" % (eticheta, r.get("data_pif_brut"))))
        elif pif:
            try:
                _p = datetime.date.fromisoformat(str(pif)[:10])
                if _p > azi:
                    er.append(respinge("mijloc fix", i, "data_viitor", "%s: data PIF %s e în viitor" % (eticheta, _data_ro(_p))))
            except ValueError:
                er.append(respinge("mijloc fix", i, "data_invalida", "%s: data PIF %r nu se înțelege" % (eticheta, pif)))
        # metoda scrisă în fișier (`metoda_brut`) sau cea trimisă la salvare: una necunoscută respinge rândul; celula goală e semnal (liniară)
        metoda_scrisa = str(r.get("metoda_brut") or r.get("metoda") or "").strip()
        if metoda_scrisa and _normalizeaza_metoda(metoda_scrisa) is None:
            er.append(respinge("mijloc fix", i, "metoda_necunoscuta",
                               "%s: metoda de amortizare «%s» nu există — CF art.28: liniară, degresivă, accelerată, superaccelerată"
                               % (eticheta, metoda_scrisa)))
        if cimo:
            if not (cimo[:1] == "2" and cimo.split(".")[0].isdigit()):
                er.append(respinge("mijloc fix", i, "cont_imobilizare_invalid",
                                   "%s: contul %s nu e de imobilizări (clasa 2)" % (eticheta, cimo)))
            else:
                asteptat = cont_amortizare_asteptat(cimo)
                if asteptat and camo and not camo.split(".")[0].startswith(asteptat):
                    er.append(respinge("mijloc fix", i, "cont_amortizare_necorespunzator",
                                       "%s: amortizarea contului %s se ține pe %s, nu pe %s" % (eticheta, cimo, asteptat, camo)))
        prel = r.get("amortizat_preluat")
        if prel is not None and val > 0 and float(prel) > val - rez + 0.01:
            er.append(respinge("mijloc fix", i, "amortizare_peste_valoare",
                               "%s: amortizarea preluată (%s) depășește valoarea amortizabilă (%s)"
                               % (eticheta, _bani(float(prel), "lei"), _bani(val - rez, "lei"))))
        if dur > 0 and val > 0 and rez <= val + 0.01 and not teren and not any(e.get("rand") == i for e in er):
            # [C24, 14.10.2026] amortizarea se calculează AICI, pe server, din ce se scrie — nu din câmpul previzualizării. Un rând pe care
            # motorul nu-l poate calcula (ex. metoda accelerată pe un cont neclasificat) se refuză numit, cu motivul motorului.
            motiv = _motiv_necalculabil(r, dur)
            if motiv:
                er.append(respinge("mijloc fix", i, "amortizare_necalculabila", "%s: amortizarea nu se poate calcula — %s" % (eticheta, motiv)))
    return er


def _motiv_necalculabil(r, dur):
    """Textul motorului de amortizare când rândul nu se poate calcula; `""` când se poate."""
    from core import d406_active
    pif = r.get("data_pif")
    try:
        pif = datetime.date.fromisoformat(str(pif)[:10]) if pif else None
    except ValueError:
        return "data punerii în funcțiune %r nu se înțelege" % (pif,)
    try:
        d406_active.amortizat_la_data({"valoare": float(r.get("valoare") or 0), "rezidual": float(r.get("rezidual") or 0),
                                       "dnf_luni": dur, "data_pif": pif, "cod": r.get("cod"),
                                       "metoda": r.get("metoda") or "liniara",
                                       "cont_imobilizare": r.get("cont_imobilizare") or "",
                                       "destinatie_cd": bool(r.get("destinatie_cd"))}, datetime.date.today())
    except ValueError as e:
        return str(e)
    return ""


def importa(conn, randuri):
    """DELETE + INSERT per firma. Intoarce {importati, respinse}: rândurile bune se scriu, cele respinse se întorc numite
    (C24). Ridica ValueError numai daca NICIUN rand nu poate intra (vezi verifica_randuri)."""
    # [probare invalid, 03.09.2026 — aceeasi clasa ca importul de istoric] UN IMPORT GOL
    # STERGEA TOT, IN TACERE. Lista vida trecea de verificare (n-are ce respinge), ajungea la
    # `DELETE FROM mijloace_fixe` de mai jos, si raspundea ca un import reusit cu zero randuri. Un fisier gol,
    # unul cu numai antet (`extrage` intoarce [] pe el), sau un apel de API cu lista goala — toate
    # ajungeau acolo. *Un import care nu aduce nimic n-are voie sa stearga ce era acolo.*
    if not randuri:
        raise ValueError("nu ai trimis niciun rând. Importul ar fi șters registrul mijloacelor "
                         "fixe al firmei — cel pe care stă amortizarea — și n-ar fi pus nimic "
                         "în loc. Dacă chiar vrei să golești registrul, e altă operațiune.")
    er = verifica_randuri(randuri)
    # [C24, decizia Costin 14.10.2026, verbatim în DECIZII: „fără blocare la salvare; rândul problemă se arată, restul se
    # salvează”] Rândurile respinse NU intră și se întorc numite (`respinse`); celelalte se salvează. Numai un import în care
    # NICIUN rând nu poate intra se refuză întreg — altfel ar șterge registrul și n-ar pune nimic în loc.
    respinse_idx = {x["rand"] for x in er}
    bune = [r for i, r in enumerate(randuri, start=2) if _it.nr_rand(r, i) not in respinse_idx]
    if not bune:
        raise ValueError("Niciun rând nu poate intra: %s. Mijloacele fixe intră în amortizare și în D406 SAF-T; registrul "
                         "existent a rămas neatins."
                         % "; ".join("rand %s: %s" % (x["rand"], x["mesaj"]) for x in er[:6]))
    with conn.cursor() as cur:
        cur.execute("DELETE FROM mijloace_fixe")
        n = 0
        for r in bune:
            cur.execute("""
                INSERT INTO mijloace_fixe
                  (cod, denumire, cont_imobilizare, cont_amortizare, valoare, rezidual,
                   dnf_luni, data_pif, metoda, activ, destinatie_cd, amortizare_preluata, data_preluare)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,true,%s,%s,%s)
            """, (r["cod"], r["denumire"], r.get("cont_imobilizare") or "",   # fara default 2131; gol = neclasificat -> lit.c la calc_asset
                  r.get("cont_amortizare") or cont_amortizare_asteptat(r.get("cont_imobilizare")) or "",
                  r.get("valoare", 0), r.get("rezidual", 0), r.get("dnf_luni", 0),
                  r.get("data_pif"), r.get("metoda") or "liniara", bool(r.get("destinatie_cd")),
                  r.get("amortizat_preluat"), r.get("data_preluare")))
            n += 1
    return {"importati": n, "respinse": er}


def reconciliere_balanta(randuri, solduri):
    """[359, comanda Costin 8.2] Totalurile registrului pe conturile de imobilizări (valoarea de intrare) și de amortizare (amortizarea
    preluată), față de balanța de deschidere (`solduri_initiale`: {cont: (debit, credit)}). Un cont cu diferență se numește; fără balanță de
    deschidere, nu se poate confrunta (spus, nu presupus 0). -> [{cont, fel, registru, balanta, diferenta}] (numai conturile atinse)."""
    from decimal import Decimal as _D
    pe_cont = {}
    for r in randuri or []:
        if r.get("stare") == "respins":
            continue
        ci = str(r.get("cont_imobilizare") or "").strip().split(".")[0]
        ca = str(r.get("cont_amortizare") or "").strip().split(".")[0]
        if ci:
            pe_cont.setdefault((ci, "imobilizare"), _D(0))
            pe_cont[(ci, "imobilizare")] += _D(str(r.get("valoare") or 0))
        if ca and r.get("amortizat_preluat") is not None:
            pe_cont.setdefault((ca, "amortizare"), _D(0))
            pe_cont[(ca, "amortizare")] += _D(str(r.get("amortizat_preluat") or 0))
    out = []
    for (cont, fel), reg in sorted(pe_cont.items()):
        bal = None
        if solduri:
            d = sum((_D(str(v[0])) - _D(str(v[1])) for c, v in solduri.items() if str(c).split(".")[0].startswith(cont)), _D(0))
            bal = d if fel == "imobilizare" else -d
        out.append({"cont": cont, "fel": fel, "registru": float(reg), "balanta": None if bal is None else float(bal),
                    "diferenta": None if bal is None else float(reg - bal)})
    return out

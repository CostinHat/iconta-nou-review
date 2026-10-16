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


def _data(v):
    if v is None or str(v).strip() == "":
        return None
    if isinstance(v, datetime.datetime):
        return v.date().isoformat()
    if isinstance(v, datetime.date):
        return v.isoformat()
    t = str(v).strip()
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%m/%d/%Y"):
        try:
            return datetime.datetime.strptime(t, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _normalizeaza_metoda(v):
    t = _re.sub(r"[\s._-]+", "", str(v or "").lower())   # colapseaza separatorii: "super accelerata" -> "superaccelerata"
    if "superaccel" in t:          # INAINTE de "acceler": "superaccelerata" contine "acceler"
        return "superaccelerata"   # CF art.28 alin.8^1 (OUG 8/2026)
    if "degres" in t:
        return "degresiva"
    if "acceler" in t:
        return "accelerata"
    return "liniara"


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


def extrage(continut, nume_fisier=""):
    """Intoarce lista de dicturi cu campurile mijlocului fix + verificari."""
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

    out = []
    for idx, r in enumerate(brut[start:], start=1):
        nr = start + idx
        def cel(i):
            return _it.celula(r, i)

        den = cel(i_den)
        if not den:
            continue
        valoare = _numar(cel(i_val))
        rezidual = _numar(cel(i_rez)) if i_rez >= 0 else 0.0   # lipsa coloanei = 0, NU valoare (defect 6)
        durata = _intreg(cel(i_dur))
        # durata in ani -> luni daca pare ani (< 60 si fisierul zice "ani")
        if 0 < durata <= 50 and any(w.startswith("an") for w in (antet[i_dur].split() if i_dur >= 0 else [])):
            durata *= 12

        avertismente = []
        if rezidual > valoare + 0.01:
            avertismente.append("valoarea reziduală depășește valoarea de intrare")
        # `_data` intoarce un SIR ISO, nu un `date` — prima forma a trecut sirul direct la
        # `prag_mf` si a produs `TypeError: '>=' not supported between str and date`. Prins de
        # `test_mijloace_fixe_import_categorie`, pe fixturi reale.
        _pif_iso = _data(_it.valoare(r, i_pif)) if i_pif >= 0 else None
        try:
            _pif = datetime.date.fromisoformat(_pif_iso) if _pif_iso else None
        except ValueError:
            _pif = None
        _prag = float(_oi.prag_mf(_pif))
        _cand = _data_ro(_pif) if _pif else "dată lipsă"
        if 0 < valoare < _prag:
            if _oi.prag_mf_cunoscut(_pif):
                avertismente.append("sub plafonul de mijloc fix de %s, la data intrării %s"
                                    % (_bani(_prag, "lei"), _cand))
            else:
                # Necunoscutul nu se rotunjeste la „stiu ca nu": registrul n-are prag pentru data
                # aia, deci se spune ca pragul e MOSTENIT, nu verificat la sursa.
                avertismente.append("sub cel mai vechi plafon cunoscut (%s) — registrul n-are "
                                    "prag verificat pentru %s" % (_bani(_prag, "lei"), _cand))
        if durata <= 0:
            avertismente.append("durată lipsă")
        if not cel(i_cimo):
            avertismente.append("cont de imobilizare lipsă - categorie neclasificată "
                                "(CF art.28 alin.5 lit.c): doar liniar/degresiv; "
                                "accelerat/superaccelerat vor fi refuzate la D406 până se completează contul")

        dcd = _da_nu(cel(i_cd)) if i_cd >= 0 else False
        if dcd is None:
            avertismente.append("coloana C&D are valoarea %r — se acceptă da/nu; activul intră fără destinația C&D" % cel(i_cd))
            dcd = False
        amortizat, ramas = _la_zi(valoare, rezidual, durata, _pif, _normalizeaza_metoda(cel(i_met)), cel(i_cimo), dcd)
        if i_ram >= 0 and cel(i_ram) != "" and ramas is not None:
            ramas_fisier = _numar(cel(i_ram))
            rata = (valoare - rezidual) / durata
            if abs(ramas_fisier - ramas) > rata + 1:
                avertismente.append(
                    "valoarea rămasă din fișier (%s) diferă de cea calculată la %s din data PIF, durată și "
                    "metodă (%s) — amortizarea continuă din calcul, nu din coloana rămas; verifică cele trei"
                    % (_bani(ramas_fisier, "lei"), _data_ro(datetime.date.today()), _bani(ramas, "lei")))
        if i_amz >= 0 and cel(i_amz) != "" and amortizat is not None and durata > 0:
            amz_fisier = _numar(cel(i_amz))
            if abs(amz_fisier - amortizat) > (valoare - rezidual) / durata + 1:
                avertismente.append(
                    "amortizarea înregistrată din fișier (%s) diferă de cea calculată la %s din data PIF, durată și metodă "
                    "(%s) — amortizarea continuă din calcul; verifică data, durata și metoda" %
                    (_bani(amz_fisier, "lei"), _data_ro(datetime.date.today()), _bani(amortizat, "lei")))
        if i_vinv >= 0 and cel(i_vinv) != "" and abs(_numar(cel(i_vinv)) - valoare) > 0.01:
            avertismente.append(
                "valoarea de inventar din fișier (%s) diferă de valoarea de intrare (%s) — în aplicația veche au fost "
                "modernizări sau reevaluări, care nu se preiau: amortizarea continuă din valoarea de intrare. Dacă activul a fost modernizat sau reevaluat, valoarea și durata din fișier trebuie aduse la zi înainte de import"
                % (_bani(_numar(cel(i_vinv)), "lei"), _bani(valoare, "lei")))

        out.append({
            "rand_fisier": nr,
            "cod": cel(i_cod) or f"MF{idx:03d}",
            "denumire": den,
            "valoare": valoare,
            "rezidual": rezidual,
            "amortizat": amortizat,           # la zi, din motor (None daca motorul nu poate calcula randul)
            "ramas": ramas,
            "dnf_luni": durata,
            "data_pif": _pif_iso,
            "metoda": _normalizeaza_metoda(cel(i_met)),
            "cont_imobilizare": cel(i_cimo),   # NU se completeaza tacit cu 2131 (categoria permisiva); gol -> lit.c
            "cont_amortizare": cel(i_camo) or "2813",
            "destinatie_cd": dcd,               # CF art.20 alin.(1) lit.b): accelerata si pt aparatura C&D
            "avertismente": avertismente,
            "ok": len(avertismente) == 0,
        })
    return out


def _da_nu(v):
    """„da”/„nu” dintr-o celulă de import (da/nu, x, 1/0, true/false); gol = nu; altceva = None (avertisment)."""
    s = str(v or "").strip().lower()
    if s in ("", "nu", "0", "false", "n", "-"):
        return False
    if s in ("da", "x", "1", "true", "d"):
        return True
    return None


def _la_zi(valoare, rezidual, durata, pif, metoda, cont_imob, destinatie_cd=False):
    """(amortizat, ramas) la data de azi, din motorul unic — sau (None, None) cand randul nu se poate calcula
    (durata/valoare lipsa, metoda nepermisa pe categorie); motivul e deja in avertismentele randului."""
    from core import d406_active
    try:
        r = d406_active.amortizat_la_data({"valoare": valoare, "rezidual": rezidual, "dnf_luni": durata,
                                           "data_pif": pif, "metoda": metoda, "cont_imobilizare": cont_imob,
                                           "destinatie_cd": destinatie_cd},
                                          datetime.date.today())
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


def verifica_randuri(randuri):
    """PURA: [{rand, motiv, mesaj}]. Nicio validare nu exista pana la 15.07.2026:
    durata 0 (amortizarea nu se poate calcula), valoare ramasa > valoare de intrare
    (imposibil), cod de inventar duplicat - toate intrau, iar migrarea zicea "gata"."""
    er, coduri = [], {}
    for i, r in enumerate(randuri or [], start=2):
        i = _it.nr_rand(r, i)
        cod = str(r.get("cod") or "").strip()
        den = str(r.get("denumire") or cod or "?").strip()
        val = float(r.get("valoare") or 0)
        rez = float(r.get("rezidual") or 0)
        dur = int(r.get("dnf_luni") or r.get("durata") or 0)   # [Q3] cheia reala e dnf_luni (extrage:136); "durata" nu exista niciodata -> dadea 0 pe fiecare rand
        if not cod:
            er.append(respinge("mijloc fix", i, "cod_lipsa", "%s: fără cod de inventar" % den))
        elif cod in coduri:
            er.append(respinge("mijloc fix", i, "cod_duplicat",
                               "codul de inventar %s apare de două ori (rândurile %s și %s)"
                               % (cod, coduri[cod], i)))
        else:
            coduri[cod] = i
        if dur <= 0:
            er.append(respinge("mijloc fix", i, "durata_lipsa",
                               "%s: durata în luni lipsește sau nu e pozitivă (%s) - fără ea nu se calculează amortizarea" % (den, dur)))
        if val <= 0:
            er.append(respinge("mijloc fix", i, "valoare_lipsa",
                               "%s: valoare de intrare %s" % (den, val)))
        elif rez > val + 0.01:
            er.append(respinge("mijloc fix", i, "rezidual_peste_intrare",
                               "%s: valoarea reziduală (%s) depășește valoarea de intrare (%s)"
                               % (den, _bani(rez, "lei"), _bani(val, "lei"))))
        elif dur > 0:
            # [C24, 14.10.2026] amortizarea se calculează AICI, pe server, din ce se scrie — nu din câmpul `amortizat` al
            # previzualizării. Un rând pe care motorul nu-l poate calcula (ex. metoda accelerată pe un cont neclasificat) se
            # refuză numit, cu motivul motorului; până azi trecea de verificare și răsturna toată salvarea cu un 422 de model.
            motiv = _motiv_necalculabil(r, dur)
            if motiv:
                er.append(respinge("mijloc fix", i, "amortizare_necalculabila",
                                   "%s: amortizarea nu se poate calcula — %s" % (den, motiv)))
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
                   dnf_luni, data_pif, metoda, activ, destinatie_cd)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,true,%s)
            """, (r["cod"], r["denumire"], r.get("cont_imobilizare") or "",   # fara default 2131; gol = neclasificat -> lit.c la calc_asset
                  r.get("cont_amortizare", "2813"), r.get("valoare", 0),
                  r.get("rezidual", 0), r.get("dnf_luni", 0),
                  r.get("data_pif"), r.get("metoda", "liniara"), bool(r.get("destinatie_cd"))))
            n += 1
    return {"importati": n, "respinse": er}

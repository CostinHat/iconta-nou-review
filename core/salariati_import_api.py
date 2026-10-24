"""
core/salariati_import_api.py — import salariati (stratul 4 migrare) per firma.

Citeste un export din vechea aplicatie (.xlsx/.csv) si mapeaza flexibil coloanele
(nume/prenume/CNP/salariu/functie/data angajare) indiferent de ordine sau denumire exacta.
Importa in tabelul existent `salariati` din schema tenantului (NU il recreeaza).
Valideaza CNP (cheie de control oficiala 279146358279 + structura data + judet).

"""
# [E2b, 15.09.2026] Tranzactia e a APELANTULUI: `db.get_conn` comite la iesirea din bloc, iar un
# `commit` aici ar taia tranzactia lui in doua (P4). Depozitul primeste conexiunea si scrie; nu
# deschide, nu comite.
from __future__ import annotations



def valideaza_cnp(cnp):
    """[347] Sursa unică e `core.identitate.valideaza_cnp` (motivul în cuvinte); numele rămâne pentru apelanții de aici."""
    from core.identitate import valideaza_cnp as _v
    return _v(cnp)


def _da_nu(v):
    """„da”/„nu” (și 1/0, true/false, x) -> bool; gol sau altceva -> None (necunoscut, nu ghicit)."""
    t = str(v or "").strip().lower()
    return True if t in ("da", "1", "true", "x", "yes") else (False if t in ("nu", "0", "false", "no") else None)


from core.numere import numar as _numar  # sursa unica (15.07.2026, vezi core/numere.py)
from core.pdf_util import data_ro as _data_ro   # DS cap.4: data din text, canonic
from core.migrare_api import respinge, semnaleaza  # [P8/C] respingerea e o afirmatie, cu regula din nomenclator
from core.common import cate as _cate




def _split_nume(intreg):
    """Daca avem un singur camp 'nume complet', desparte in nume + prenume."""
    parti = str(intreg or "").strip().split()
    if len(parti) >= 2:
        return parti[0], " ".join(parti[1:])
    return (parti[0] if parti else ""), ""


# [14.10.2026, comanda Costin „Importul din SAGA”, verbatim în DECIZII] Fișierul trece prin `core.import_tabel`. Antetele SAGA
# vin din manualul SAGA C, ecranul Salariați (`anaf_surse/saga_manual_topic25_salariati.txt`): „Nume”, „Prenume”, „Data
# angajării”, „Funcție baza”, „Norma pe zi” (ORE: 8 … 0), „Ore pe lună” (NU ore pe zi), „Salariu brut”, „Salariu orar”, „CNP”,
# „Județ” (al adresei), „Casa de sănătate”, „Cont card”. Până azi, pe un astfel de export: „Funcție baza” nu se potrivea cu
# „funcție de bază” (fiecare salariat refuzat), „Data angajării” nu se potrivea cu „angajare” (dată pierdută), „Ore pe lună”
# intra ca ore pe zi, iar „Norma pe zi” = 4 devenea normă ÎNTREAGĂ (orice valoare fără „part” era întreagă).
from core import import_tabel as _it

CAMPURI = {
    "nume": ("nume salariat", "nume", "nume si prenume", "nume complet"),
    "prenume": ("prenume",),
    "cnp": ("cnp", "cod numeric personal", "cod numeric"),
    "data": ("data angajarii", "data angajare", "data angaj*", "angaj*", "data contract", "contract din"),
    "norma": ("norma pe zi", "tip norma", "norma*"),
    "ore_luna": ("ore pe luna", "ore lunar*", "ore luna"),
    "ore": ("ore pe zi", "ore zi", "ore"),
    "brut": ("salariu brut", "brut", "salariu de baza", "salariu de incadrare", "salariu"),
    "intretinere": ("persoane in intretinere", "intretinere", "persoane"),
    "casa": ("casa de sanatate", "casa sanatate", "judet casa", "casa", "judet"),
    "cor": ("cod cor", "cor", "cod ocupatie", "ocupatie"),
    "iban": ("iban", "cont iban", "cont bancar", "cont card"),
    "fbaza": ("functie de baza", "functia de baza", "functie baza", "functia baza"),
    # [348, comanda Costin 8.2] denumirea funcției scrisă în fișier („Funcție”) — numai prin egalitate, ca să nu prindă „Funcție baza”
    "functie": ("=functie", "=functia", "denumire functie", "denumirea functiei", "=post"),
    "scut": ("scutit contributie minima", "scutit*", "contributie minima"),
}
#: [lotul 11] numele câmpului în refuzul coloanelor ambigue (`import_tabel.coloana`), în limba contabilului — nu cheia internă
#: (garda: core/test_lot11_import_etichete_camp.py)
ETICHETE_CAMP = {
    "nume": "numele salariatului",
    "prenume": "prenumele",
    "cnp": "CNP-ul",
    "data": "data angajării",
    "norma": "norma de lucru",
    "ore_luna": "orele pe lună",
    "ore": "orele pe zi",
    "brut": "salariul brut",
    "intretinere": "persoanele în întreținere",
    "casa": "casa de sănătate",
    "cor": "codul COR",
    "iban": "IBAN-ul",
    "fbaza": "funcția de bază",
    "functie": "denumirea funcției",
    "scut": "scutirea de contribuția minimă",
}

# Casa de sănătate scrisă cu numele județului („CAS Cluj”, „Casa de Asigurări de Sănătate Bistrița-Năsăud”) -> codul județului.
# Lista județelor e cea oficială (codurile din JUDETE_CASA); se compară fără diacritice, liniuțe și prefixele caselor.
_JUDETE_NUME = {
    "alba": "AB", "arad": "AR", "arges": "AG", "bacau": "BC", "bihor": "BH", "bistrita nasaud": "BN", "botosani": "BT",
    "brasov": "BV", "braila": "BR", "buzau": "BZ", "caras severin": "CS", "calarasi": "CL", "cluj": "CJ", "constanta": "CT",
    "covasna": "CV", "dambovita": "DB", "dolj": "DJ", "galati": "GL", "giurgiu": "GR", "gorj": "GJ", "harghita": "HR",
    "hunedoara": "HD", "ialomita": "IL", "iasi": "IS", "ilfov": "IF", "maramures": "MM", "mehedinti": "MH", "mures": "MS",
    "neamt": "NT", "olt": "OT", "prahova": "PH", "satu mare": "SM", "salaj": "SJ", "sibiu": "SB", "suceava": "SV",
    "teleorman": "TR", "timis": "TM", "tulcea": "TL", "vaslui": "VS", "valcea": "VL", "vrancea": "VN", "bucuresti": "B",
    "municipiul bucuresti": "B",
}
_PREFIXE_CASA = ("casa de asigurari de sanatate a judetului", "casa de asigurari de sanatate", "casa de sanatate",
                 "cas a judetului", "cjas", "cas", "casmb", "judetul", "jud", "municipiul")


def cod_judet_casa(v):
    """Codul județului din valoarea coloanei („CJ”, „cj”, „Cluj”, „CAS Cluj”, „CASMB” -> „B”). Necunoscut -> textul, verbatim
    (verificarea îl refuză numit: `judet_invalid`), nu ghicit."""
    t = str(v or "").strip()
    if not t:
        return ""
    if t.upper() in JUDETE_CASA:
        return t.upper()
    n = _it.norm(t)
    if n == "casmb":
        return "B"
    for p in _PREFIXE_CASA:
        if n.startswith(p + " "):
            n = n[len(p) + 1:]
            break
    return _JUDETE_NUME.get(n, t)


def _norma(v):
    """`(tip_norma, ore_zi, ore_luna_zero)` din coloana normei.

    Text: „întreagă” / „parțială” (ca până azi). NUMĂR (SAGA „Norma pe zi” = ore): 8 -> întreagă, 8 ore; 1–7 -> parțială, cu
    atâtea ore; 0 -> contract fără normă zilnică (SAGA: „Ore pe lună”) — aplicația nu-l preia automat, rândul se refuză numit."""
    t = str(v or "").strip()
    if not t:
        return "", 0.0, False
    try:
        n = float(t.replace(",", "."))
    except ValueError:
        tl = t.lower()
        return ("partiala" if ("part" in tl or "parțial" in tl) else "intreaga"), 0.0, False
    if n == 0:
        return "", 0.0, True
    if n >= 8:
        return "intreaga", n, False
    return "partiala", n, False


def extrage(continut, nume_fisier=""):
    """
    Intoarce [{nume, prenume, cnp, data_angajare, tip_norma, ore_zi, salariu_brut,
               persoane_intretinere, judet_casa, cor, iban, functie_baza, scutit_contrib_minim, cnp_valid, cnp_motiv}].
    """
    brut = _it.citeste(continut, nume_fisier)
    if not brut or all(_it.rand_gol(r) for r in brut):
        return []
    try:
        antet, start = _it.gaseste_antet(brut, CAMPURI, obligatorii=("cnp",), nume_fisier=nume_fisier)
    except _it.ColoaneAmbigue:
        raise
    except _it.FisierNecitit:
        antet, start = _it.gaseste_antet(brut, CAMPURI, obligatorii=("nume",), nume_fisier=nume_fisier)
    col = lambda camp, exclus=(): _it.coloana(antet, CAMPURI[camp], exclus=exclus, camp=ETICHETE_CAMP[camp])
    i_nume = col("nume")
    i_pren = col("prenume", (i_nume,))
    i_cnp = col("cnp")
    i_data = col("data")
    i_norma = col("norma")
    i_ore_luna = col("ore_luna")
    i_ore = col("ore", (i_ore_luna, i_norma))
    i_brut = col("brut")
    i_intr = col("intretinere")
    i_jud = col("casa")
    i_cor = col("cor")
    i_iban = col("iban")   # [iban_import] contul in care se plateste salariul (SEPA)
    # [decizia Costin 07.10, pct.4] cele două DA/NU cerute explicit: coloana lipsă sau celula goală -> None (rândul se refuză)
    i_fbaza = col("fbaza")
    i_scut = col("scut")
    i_functie = col("functie", exclus=(i_fbaza, i_cor))
    if i_nume < 0 and i_cnp < 0:
        raise ValueError("nu se găsește coloana nume/CNP salariat - fișier nerecunoscut")

    out = []
    for nr, r in enumerate(brut[start:], start=start + 1):
        cel = lambda i: _it.celula(r, i)
        cnp = cel(i_cnp)
        nume_v = cel(i_nume)
        pren_v = cel(i_pren)
        # daca prenume lipseste dar numele pare complet, desparte
        if not pren_v and i_pren < 0 and " " in nume_v:
            nume_v, pren_v = _split_nume(nume_v)

        # [comanda Costin 8.2 pct.4: „orice rând citit e afișat sau semnalat cu motiv”] se sare numai rândul complet gol; un rând cu
        # date dar fără nume și CNP se arată, respins (CNP-ul lipsă), nu dispare
        if _it.rand_gol(r):
            continue

        valid, motiv = valideaza_cnp(cnp)
        # [Q11] fara default tacit (DS cap.17): coloana norma lipsa / celula goala -> tip_norma
        # necunoscut (""), NU "intreaga" fabricata. Doar o valoare PREZENTA se interpreteaza. [420] Lipsa devine mai jos o PROPUNERE
        # vizibilă, editabilă și marcată „de verificat” — nu un implicit tăcut.
        tip_norma, ore_norma, ore_luna = _norma(cel(i_norma)) if i_norma >= 0 else ("", 0.0, False)
        ore = _numar(cel(i_ore)) if i_ore >= 0 else 0.0
        if ore <= 0:
            ore = ore_norma
        # [decizii 07.10 pct.4, aceeași clasă] 8 ore = norma întreagă (dedus din normă); la normă PARȚIALĂ orele nu se ghicesc
        # (până azi „4” din oficiu) — lipsa se refuză numit (`ore_lipsa`)
        if ore <= 0 and tip_norma == "intreaga":
            ore = 8

        # [decizia Costin 14.10.2026 pct.3–4, verbatim în DECIZII] persoanele în întreținere și scutirea de contribuția minimă LIPSĂ
        # din fișier (coloana absentă — exportul SAGA nu le are — sau celula goală) nu mai refuză rândul: intră cu 0 / „nescutit” și
        # salariatul e MARCAT („de verificat”), vizibil în statul de plată până la confirmare (`salariati.de_verificat`).
        de_verificat = []
        # [lotul 10, deficiența 420, comanda Costin 10.1, verbatim în DECIZII „Comanda 10.1”] „rândurile fără normă de lucru și funcție
        # de bază sunt respinse întregi […] Câmpurile lipsă se completează pe ecran, înainte de import, cu propunere editabilă (normă
        # întreagă, funcție de bază Da), la fel cum sunt tratate deja COR, scutirea și persoanele în întreținere (intră marcate „de
        # verificat”).” Norma lipsă (coloana absentă / celula goală; NU „0 = ore pe lună”, care rămâne refuzată) -> propusă întreagă, 8
        # ore — sau parțială cu orele din fișier, când fișierul are ore pe zi sub 8; funcția de bază lipsă -> propusă „Da”. Amândouă
        # marcate „de verificat” până le confirmă contabilul (pe ecranul importului sau în Stat de plată).
        if not tip_norma and not ore_luna:
            tip_norma = "partiala" if 0 < ore < 8 else "intreaga"
            if tip_norma == "intreaga" and ore <= 0:      # orele din fișier peste 8 rămân, refuzate numit (`ore_invalide`)
                ore = 8
            de_verificat.append("tip_norma")
        fbaza = _da_nu(cel(i_fbaza)) if i_fbaza >= 0 else None
        if fbaza is None:
            fbaza = True
            de_verificat.append("functie_baza")
        persoane = int(_numar(cel(i_intr))) if (i_intr >= 0 and cel(i_intr)) else None
        if persoane is None:
            de_verificat.append("persoane_intretinere")
        scutit = _da_nu(cel(i_scut)) if i_scut >= 0 else None
        if scutit is None:
            de_verificat.append("scutit_contrib_minim")
        elif scutit:
            # [lotul 12, C133] fișierul spune „scutit”, dar nu și motivul (D112 `motivExc`, OPANAF 605/2026 anexa 2, pct.12): salariatul intră
            # scutit și marcat de verificat — motivul îl alege contabilul în Stat de plată („De verificat”), nu se presupune
            de_verificat.append("motiv_exceptare")
        out.append({
            "rand_fisier": nr,
            "nume": nume_v,
            "prenume": pren_v,
            "cnp": cnp,
            "data_angajare": _it.data(_it.valoare(r, i_data)) if i_data >= 0 else None,
            "tip_norma": tip_norma,
            "norma_ore_luna": ore_luna,
            "ore_zi": ore,
            "salariu_brut": _numar(cel(i_brut)),
            "persoane_intretinere": persoane or 0,
            "judet_casa": cod_judet_casa(cel(i_jud)),
            "cor": cel(i_cor),
            # [348] funcția așa cum e scrisă în fișier: se AFIȘEAZĂ la previzualizare (codul COR rămâne cel care se salvează)
            "functie": cel(i_functie) if i_functie >= 0 else "",
            # [iban_import] normalizat (fara spatii, majuscule); gol -> "" (necunoscut, NU fabricat)
            "iban": cel(i_iban).replace(" ", "").upper(),
            "functie_baza": fbaza,                         # [420] lipsă -> propus „Da”, marcat de verificat
            "scutit_contrib_minim": bool(scutit),          # lipsă -> „nescutit”, marcat de verificat
            "de_verificat": de_verificat,
            "cnp_valid": valid,
            "cnp_motiv": motiv,
        })
    return out


def rezumat(conn):
    """{are_salariati, randuri, de_verificat} pentru firma curenta (tabel existent salariati). [lotul 10, deficiența 423 b] „starea «gata»
    nu spune câți salariați rămân «de verificat»” — `de_verificat` = câți salariați au încă un câmp importat neconfirmat."""
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('salariati')")
        if cur.fetchone()[0] is None:
            return {"are_salariati": False, "randuri": 0, "de_verificat": 0}
        cur.execute("SELECT count(*), count(*) FILTER (WHERE cardinality(de_verificat) > 0) FROM salariati")
        n, dv = cur.fetchone()
    return {"are_salariati": n > 0, "randuri": n, "de_verificat": dv}


JUDETE_CASA = ("AB","AR","AG","BC","BH","BN","BT","BV","BR","BZ","CS","CL","CJ","CT",
               "CV","DB","DJ","GL","GR","GJ","HR","HD","IL","IS","IF","MM","MH","MS",
               "NT","OT","PH","SM","SJ","SB","SV","TR","TM","TL","VS","VL","VN","B")


def verifica_randuri(randuri, azi=None):
    """PURA: [{rand, motiv, mesaj}] - ce nu poate intra in evidenta.

    Pana la 15.07.2026 importa() verifica DOAR cnp_valid; restul intra oricum. Dovedit
    prin migrare reala: brut 1500 la norma intreaga (sub minimul de 4325 -> firma ar fi
    platit CAS/CASS pe 4125 fara sa stie, art.146(5^6)), angajare in 2027, 15 ore/zi,
    judet 'ZZ' inexistent, COR '999999' - toate au intrat, iar migrarea a zis "gata".
    """
    import datetime as _dt
    azi = azi or _dt.date.today()
    er = []
    vazut = {}

    for i, r in enumerate(randuri or [], start=2):   # antetul e randul 1
        i = _it.nr_rand(r, i)
        nume = ("%s %s" % (r.get("nume") or "", r.get("prenume") or "")).strip() or "?"
        # [14.10.2026] cifra de control se RECALCULEAZĂ aici: `cnp_valid` venea din cererea ecranului, iar un client putea
        # trimite `cnp_valid: true` pentru un CNP greșit. Verdictul e al serverului, nu al previzualizării.
        _cnp_ok, _cnp_motiv = valideaza_cnp(r.get("cnp"))
        if not _cnp_ok:
            er.append(respinge("salariat", i, "cnp_invalid",
                            "%s: CNP invalid (%s)" % (nume, _cnp_motiv)))
            continue
        # [C, lotul 9 — clasa lui 385: dublura din fișier] același CNP pe două rânduri: salvarea (actualizarea pe CNP) îl
        # înlocuia pe tăcute pe primul cu al doilea — „nimic nu se înlocuiește pe tăcute” (regula importurilor, comanda 8.2 pct.4)
        _cnp = str(r.get("cnp") or "").strip()
        if _cnp in vazut:
            er.append(respinge("salariat", i, "identificator_dublat",
                               "%s: CNP-ul %s apare și pe rândul %s — un salariat se trece o singură dată" % (nume, _cnp, vazut[_cnp])))
            continue
        vazut[_cnp] = i
        d = r.get("data_angajare")
        if d:
            try:
                dd = d if isinstance(d, _dt.date) else _dt.date.fromisoformat(str(d)[:10])
                if dd > azi:
                    er.append(respinge("salariat", i, "data_viitor",
                                    "%s: data angajării (%s) e în viitor" % (nume, _data_ro(dd))))
            except ValueError:
                er.append(respinge("salariat", i, "data_invalida",
                                "%s: data angajării nu se înțelege (%r)" % (nume, d)))
        if r.get("norma_ore_luna"):
            er.append(respinge("salariat", i, "norma_ore_luna",
                            "%s: norma pe zi e 0 (contract cu ore pe lună) - treci în fișier orele pe zi ale normei" % nume))
        elif not str(r.get("tip_norma") or "").strip():
            er.append(respinge("salariat", i, "norma_lipsa",
                            "%s: norma de lucru lipsește (întreagă/parțială) - necesară pentru D112" % nume))
        elif r.get("tip_norma") == "partiala" and not (r.get("ore_zi") or 0):
            er.append(respinge("salariat", i, "ore_lipsa",
                            "%s: orele pe zi ale normei parțiale lipsesc - baza D112 la normă parțială" % nume))
        # [decizia Costin 07.10, pct.4] aceeași regulă ca pe ecran: cele două DA/NU se cer explicit, cu câmpul numit
        if r.get("functie_baza") is None:
            er.append(respinge("salariat", i, "functie_baza_lipsa",
                            "%s: funcția de bază (Da/Nu) lipsește - coloana «Funcție de bază»; decide deducerea personală" % nume))
        # [PIVOT, decizia Costin 14.10.2026 pct.4] scutirea lipsă NU mai refuză rândul (era decizia 07.10 pct.4): se importă
        # „nescutit” și se marchează de verificat (`extrage` / `importa`).
        # [salariu_import] salariul de baza e OBLIGATORIU si > 0 (ca la creare, salariati_api #8):
        # intra in D112 si pe fluturas. Lipsa lui (coloana absenta / celula goala -> parser 0.0) NU se
        # accepta tacit (DS cap.17, fara default fabricat): firma ar plati CAS/CASS pe podeaua sub-minim
        # (art.146(5^6)/168(6^1)) fara sa stie, iar statul ar arata brut 0 / cost pozitiv - incoerent.
        _brut = r.get("salariu_brut")
        try:
            _brut_ok = _brut is not None and float(_brut) > 0
        except (TypeError, ValueError):
            _brut_ok = False
        if not _brut_ok:
            er.append(respinge("salariat", i, "salariu_lipsa",
                            "%s: salariul de bază lipsește sau nu e mai mare ca 0 - intră în D112 și pe fluturaș, trebuie să fie cel real" % nume))
        ore = r.get("ore_zi")
        if ore and not (1 <= float(ore) <= 8):   # 0/None = necunoscut (acoperit de norma_lipsa); doar valoarea PREZENTA gresita
            er.append(respinge("salariat", i, "ore_invalide",
                            "%s: ore/zi = %s (norma legală e de maximum 8)" % (nume, ore)))
        j = str(r.get("judet_casa") or "").strip().upper()
        if j and j not in JUDETE_CASA:
            er.append(respinge("salariat", i, "judet_invalid", "%s: județul '%s' nu există" % (nume, j)))
        # [iban_import] IBAN e OPTIONAL la import (gol -> salariatul e exclus din SEPA si raportat, nu platit
        # tacit - vezi plata_salarii), dar o valoare PREZENTA trebuie sa fie valida mod-97: un IBAN gresit
        # trimite banii altcuiva. DS cap.6 (validare preventiva cu mesaj explicativ).
        ib = str(r.get("iban") or "").strip()
        if ib:
            from core.salariati_api import iban_valid   # import local: salariati_api importa din acest modul (circular la nivel de modul)
            if not iban_valid(ib):
                er.append(respinge("salariat", i, "iban_invalid",
                                "%s: IBAN-ul (%s) e invalid — verifică-l, altfel salariatul nu intră în fișierul de plată SEPA" % (nume, ib)))
    return er


def semnale_randuri(randuri):
    """PURĂ: semnalele [{rand, motiv, mesaj}] — rândurile care INTRĂ cu ceva de știut (comanda Costin 8.2 pct.4: „nimic nu se
    înlocuiește pe tăcute”). [348] codul COR lipsă (funcția din fișier se arată, dar nu se transformă în cod); [decizia 14.10 pct.3–4]
    persoanele în întreținere și scutirea lipsă intră cu 0 / „nescutit” și salariatul e marcat de verificat — acum spus și pe rând."""
    out = []
    for i, r in enumerate(randuri or [], start=2):
        i = _it.nr_rand(r, i)
        nume = ("%s %s" % (r.get("nume") or "", r.get("prenume") or "")).strip() or "?"
        if not str(r.get("cor") or "").strip():
            f = str(r.get("functie") or "").strip()
            out.append(semnaleaza("salariat", i, "cor_lipsa",
                                  "%s: codul COR lipsește%s — salariatul intră fără cod; îl alegi în fișa lui"
                                  % (nume, " (funcția din fișier: «%s»)" % f if f else "")))
        dv = r.get("de_verificat") or []
        # [lotul 11, 420] pe un salariat existent, câmpul lipsă păstrează valoarea din fișa lui (`din_fise`) — spusă ca atare, nu ca propunere
        din = r.get("din_fisa") or []
        if "persoane_intretinere" in dv:
            out.append(semnaleaza("salariat", i, "persoane_lipsa",
                                  ("%s: persoanele în întreținere lipsesc din fișier — rămân cele din fișa existentă (%d) și salariatul e "
                                   "marcat de verificat" % (nume, int(r.get("persoane_intretinere") or 0))) if "persoane_intretinere" in din
                                  else "%s: persoanele în întreținere lipsesc din fișier — intră cu 0 și salariatul e marcat de verificat" % nume))
        if "scutit_contrib_minim" in dv:
            out.append(semnaleaza("salariat", i, "scutire_lipsa",
                                  ("%s: scutirea de contribuția minimă lipsește din fișier — rămâne cea din fișa existentă („%s”) și "
                                   "salariatul e marcat de verificat" % (nume, "scutit" if r.get("scutit_contrib_minim") else "nescutit"))
                                  if "scutit_contrib_minim" in din else
                                  "%s: scutirea de contribuția minimă lipsește din fișier — intră „nescutit” și salariatul e marcat de "
                                  "verificat" % nume))
        if "motiv_exceptare" in dv:   # [C133]
            out.append(semnaleaza("salariat", i, "motiv_scutire_lipsa",
                                  "%s: e scutit de contribuția minimă, dar fișierul nu spune motivul scutirii (D112 îl declară) — salariatul "
                                  "e marcat de verificat; motivul îl alegi în Stat de plată, la „De verificat”" % nume))
        # [420] propunerile editabile: ce se propune și că se poate schimba pe rând, înainte de salvare
        if "tip_norma" in dv:
            norma = ("normă întreagă (8 ore)" if r.get("tip_norma") == "intreaga"
                     else "normă parțială, %s pe zi" % _cate(r.get("ore_zi"), "oră", "ore"))
            out.append(semnaleaza("salariat", i, "norma_propusa",
                                  ("%s: norma de lucru lipsește din fișier — rămâne cea din fișa existentă, %s; schimb-o pe rând dacă nu e "
                                   "așa (intră marcată de verificat)" % (nume, norma)) if "tip_norma" in din else
                                  "%s: norma de lucru lipsește din fișier — propusă %s; schimb-o pe rând dacă nu e așa (intră marcată de "
                                  "verificat)" % (nume, norma if r.get("tip_norma") == "intreaga" else norma + " (din fișier)")))
        if "functie_baza" in dv:
            out.append(semnaleaza("salariat", i, "functie_baza_propusa",
                                  ("%s: funcția de bază lipsește din fișier — rămâne cea din fișa existentă („%s”); schimb-o pe rând dacă "
                                   "nu e așa (intră marcată de verificat)" % (nume, "Da" if r.get("functie_baza") else "Nu"))
                                  if "functie_baza" in din else
                                  "%s: funcția de bază lipsește din fișier — propusă „Da”; schimb-o pe rând dacă nu e așa (intră marcată "
                                  "de verificat)" % nume))
    return out


def eticheteaza(randuri):
    """[comanda Costin 8.2 pct.4] Starea fiecărui rând, din ACEEAȘI verificare pe care o aplică salvarea (`verifica_randuri`) plus
    semnalele: `stare` ∈ ok / semnalat / respins, `motive` = textele."""
    er, sem = verifica_randuri(randuri), semnale_randuri(randuri)
    for i, r in enumerate(randuri, start=2):
        n = _it.nr_rand(r, i)
        resp = [e["mesaj"] for e in er if e.get("rand") == n]
        obs = [e["mesaj"] for e in sem if e.get("rand") == n]
        r["stare"] = "respins" if resp else ("semnalat" if obs else "ok")
        r["motive"] = resp or obs
    return randuri


def din_fise(conn, randuri):
    """[lotul 11, deficiența 420 — retestul Costin 21.10.2026, verbatim în DECIZII „Comanda 11.1” pct.12: „norma și funcția de bază lipsă
    din fișier se pun tăcut. Trebuie editabile în previzualizare și marcate «de verificat», ca celelalte.”]

    Pe un salariat care EXISTĂ deja (același CNP), un câmp lipsă din fișier nu primește propunerea fixă (normă întreagă, „Da”, 0,
    „nescutit”): salvarea păstrează valoarea din fișă (upsert-ul din `importa`), deci previzualizarea trebuie să arate EXACT acea valoare,
    editabilă și marcată de verificat. Altfel ecranul propunea „întreagă” și salvarea păstra „parțială, 4 ore” — sau, ca pe F6 (norma și
    funcția de bază puse tăcut la importul din 19.10), totul arăta propus, iar după salvare marcajul dispărea.
    Scrie pe rând valoarea din fișă și `din_fisa` = câmpurile luate de acolo. Un salariat nou rămâne cu propunerea. Întoarce `randuri`."""
    cnp = sorted({str(r.get("cnp") or "").strip() for r in randuri or [] if r.get("de_verificat")} - {""})
    if not cnp:
        return randuri
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('salariati')")
        if cur.fetchone()[0] is None:
            return randuri
        cur.execute("SELECT cnp, part_time, ore_zi, functie_baza, persoane_intretinere, scutit_contrib_minim FROM salariati "
                    "WHERE cnp = ANY(%s)", (cnp,))
        fise = {str(x[0]).strip(): x[1:] for x in cur.fetchall()}
    for r in randuri:
        f = fise.get(str(r.get("cnp") or "").strip())
        if not f:
            continue
        part, ore, fbaza, pers, scut = f
        dv, din = r.get("de_verificat") or [], []
        if "tip_norma" in dv and part is not None:
            r["tip_norma"] = "partiala" if part else "intreaga"
            r["ore_zi"] = float(ore) if ore is not None else (0.0 if part else 8.0)
            din.append("tip_norma")
        if "functie_baza" in dv and fbaza is not None:
            r["functie_baza"] = bool(fbaza)
            din.append("functie_baza")
        if "persoane_intretinere" in dv and pers is not None:
            r["persoane_intretinere"] = int(pers)
            din.append("persoane_intretinere")
        if "scutit_contrib_minim" in dv and scut is not None:
            r["scutit_contrib_minim"] = bool(scut)
            din.append("scutit_contrib_minim")
        r["din_fisa"] = din
    return randuri


def existent(conn, cnp_uri):
    """[lotul 10, deficiența 426 — clasa] Salariații firmei pe care fișierul îi ACTUALIZEAZĂ (același CNP) și ce se sprijină pe fișele lor:
    {total (salariații firmei), randuri (câți din fișier există deja), nume: [„Nume Prenume”], state_plata: {numar, ultima}} — statele
    de plată deja emise pentru ei (calculate pe fișele vechi)."""
    cnp_uri = sorted({str(c or "").strip() for c in cnp_uri or []} - {""})
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('salariati')")
        if cur.fetchone()[0] is None:
            return {"total": 0, "randuri": 0, "nume": [], "state_plata": {"numar": 0, "ultima": None}}
        cur.execute("SELECT count(*) FROM salariati")
        total = cur.fetchone()[0]
        cur.execute("SELECT id, trim(coalesce(nume,'') || ' ' || coalesce(prenume,'')) FROM salariati WHERE cnp = ANY(%s) "
                    "ORDER BY nume, prenume", (cnp_uri,))
        gasiti = cur.fetchall()
        cur.execute("SELECT count(*), max(luna) FROM state_plata WHERE salariat_id = ANY(%s)", ([g[0] for g in gasiti],))
        ns, ultima = cur.fetchone()
    return {"total": int(total), "randuri": len(gasiti), "nume": [g[1] for g in gasiti],
            "state_plata": {"numar": int(ns or 0), "ultima": ultima.isoformat() if ultima else None}}


def text_inlocuire(vechi, nou):
    """[426] „spune că există deja […], arată [ce e] vechi și nou […]; dacă există [date dependente], spune” — textul comun avertismentului
    din previzualizare și refuzului de la salvare. Câmpurile numite sunt exact cele pe care le rescrie `importa` (upsert-ul pe CNP
    + `salariu_istoric.seteaza` la data angajării)."""
    nume = ", ".join(vechi["nume"][:5]) + (" și încă %d" % (len(vechi["nume"]) - 5) if len(vechi["nume"]) > 5 else "")
    unul = vechi["randuri"] == 1
    cine = ("salariatul din fișier există deja" if nou["randuri"] == 1
            else "din cei %d din fișier, %s" % (nou["randuri"], "unul există deja" if unul else "%d există deja" % vechi["randuri"]))
    t = ("Firma are deja %s; %s după CNP: %s. Salvarea %s cu datele din fișier — numele, data angajării, codul COR, casa de sănătate, "
         "norma, persoanele în întreținere, scutirea, funcția de bază și salariul de bază de la data angajării (un câmp lipsă din fișier și "
         "IBAN-ul gol nu șterg ce era)." % (_cate(vechi["total"], "salariat", "salariați"), cine, nume,
                                           "îi actualizează fișa" if unul else "le actualizează fișele"))
    sp = vechi.get("state_plata") or {}
    if sp.get("numar"):
        luna_sp = "%s/%s" % (sp["ultima"][5:7], sp["ultima"][:4])
        t += (" Pentru %s %s pe %s."   # participiul acordat cu numeralul, în aceeași ramură cu el (`cate`)
              % ("acest salariat" if unul else "acești salariați",
                 "este deja emis un stat de plată (pe %s), calculat" % luna_sp if sp["numar"] == 1
                 else "sunt deja emise %s (ultimul pe %s), calculate" % (_cate(sp["numar"], "stat de plată", "state de plată"), luna_sp),
                 "fișa veche" if unul else "fișele vechi"))
    return t


def importa(conn, randuri, inlocuieste=False):
    """
    Insereaza salariatii in tabelul existent. UPSERT pe CNP (daca exista, actualizeaza).
    Ridica ValueError daca vreun rand nu poate intra (vezi verifica_randuri).
    Refuzul e PRIMA POARTA: nimic nu se scrie dintr-un import cu randuri invalide.
    Intoarce {importati, respinse, actualizati}. NU exista skip: importa ridica la primul CNP invalid (prima poarta).
    [lotul 10, deficiența 426 — clasa] fișele salariaților existenți (același CNP) se actualizează NUMAI cu `inlocuieste=True`
    (confirmarea de pe ecran); fără ea -> `migrare_api.InlocuireNeconfirmata` (409), cu cine se actualizează și ce.
    """
    # [lotul 6] Aceeasi clasa ca la articole: o cerere fara randuri nu e un import de zero.
    if not randuri:
        raise ValueError("nu ai trimis niciun rând. Un import fără rânduri n-are ce adăuga în "
                         "evidența salariaților; dacă voiai altceva, e altă operațiune.")
    er = verifica_randuri(randuri)
    # [decizia Costin 14.10.2026 pct.2, verbatim în DECIZII] „rândurile bune se salvează, cele refuzate se arată numite, cu motivul
    # în cuvinte” — numai un import fără niciun rând bun se refuză întreg.
    respinse_idx = {e["rand"] for e in er}
    bune = [r for i, r in enumerate(randuri, start=2) if _it.nr_rand(r, i) not in respinse_idx]
    if not bune:
        det = "; ".join("rand %s: %s" % (e["rand"], e["mesaj"]) for e in er[:6])
        if len(er) > 6:
            det += " (și încă %d)" % (len(er) - 6)
        # [lotul 6] Se numara RANDURILE distincte, nu erorile: un singur rand cu doua probleme
        # spunea „2 rânduri nu pot intra", iar omul cauta al doilea. A DOUA instanta a defectului
        # reparat in lotul 1 pe istoricul de declaratii — acolo, cu aceleasi cuvinte.
        _n = len({e["rand"] for e in er})
        _cine = ("Un rând nu poate intra" if _n == 1 else _cate(_n, "rând", "rânduri") + " nu pot intra")
        raise ValueError("%s în evidență: %s. Salariații intră în D112 și REGES - datele trebuie "
                         "să fie cele reale; niciun salariat n-a fost scris." % (_cine, det))
    vechi = existent(conn, [r.get("cnp") for r in bune])
    from core import migrare_api as _mig
    _mig.cere_confirmarea_inlocuirii(vechi["randuri"] > 0, inlocuieste, text_inlocuire(vechi, {"randuri": len(bune)}), vechi,
                                     {"randuri": len(bune)}, vechi["state_plata"])   # [426] poarta comună a clasei
    importati = noi = 0
    with conn.cursor() as cur:
        # asiguram constrangerea unica pe cnp pentru upsert (idempotent)
        cur.execute("""
            DO $$ BEGIN
              IF NOT EXISTS (
                SELECT 1 FROM pg_constraint c
                JOIN pg_namespace n ON n.oid = c.connamespace
                WHERE c.conname = 'salariati_cnp_uniq' AND n.nspname = current_schema()
              ) THEN
                ALTER TABLE salariati ADD CONSTRAINT salariati_cnp_uniq UNIQUE (cnp);
              END IF;
            END $$;
        """)
        for r in bune:
            # rândurile respinse au rămas pe dinafară (`respinse`, întoarse numite) — aici numai rândurile bune
            part_time = (r.get("tip_norma") == "partiala")   # norma e cerută mai sus (norma_lipsa): fără „intreaga” implicit
            # upsert-ok: re-import salariat pe CNP (cheie naturala) - actualizeaza fisa existenta NUMAI dupa confirmarea inlocuirii
            # (poarta [426] de mai sus, `inlocuieste=True`); campurile absente / propunerile nu strica fisa, IBAN pazit separat
            cur.execute("""
                INSERT INTO salariati
                  (cnp, nume, prenume, data_angajare, part_time, ore_zi,
                   persoane_intretinere, judet_casa, cor, iban, functie_baza, scutit_contrib_minim, de_verificat)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (cnp) DO UPDATE SET
                  -- [14.10.2026] un câmp ABSENT din fișierul de acum (marcat în EXCLUDED.de_verificat) nu șterge valoarea existentă.
                  -- [lotul 11, 420 — retestul Costin 21.10.2026 pe F6: „norma și funcția de bază lipsă din fișier se pun tăcut”] și
                  -- RĂMÂNE MARCAT „de verificat”: fișa nu deosebește o valoare confirmată de una pusă tăcut de un import mai vechi (F6:
                  -- norma și funcția de bază puse la 19.10, înainte de 420), deci intersecția cu marcajul vechi le ascundea pe acestea.
                  -- Marcajul = câmpurile absente din fișierul de acum, neschimbate pe ecran (EXCLUDED.de_verificat); un câmp prezent
                  -- în fișier (sau ales pe ecran) iese din marcaj.
                  scutit_contrib_minim=CASE WHEN 'scutit_contrib_minim' = ANY(EXCLUDED.de_verificat)
                                            THEN salariati.scutit_contrib_minim ELSE EXCLUDED.scutit_contrib_minim END,
                  -- [lotul 10, 420] aceeași regulă pentru propunerile de normă și funcție de bază: o propunere nu strică fișa existentă
                  functie_baza=CASE WHEN 'functie_baza' = ANY(EXCLUDED.de_verificat)
                                    THEN salariati.functie_baza ELSE EXCLUDED.functie_baza END,
                  -- [14.10.2026 pct.4] persoanele și scutirea confirmate rămân confirmate la reimport (intersecția cu marcajul vechi);
                  -- [lotul 11, 420] norma și funcția de bază propuse rămân marcate (F6: puse tăcut de un import vechi, fără marcaj)
                  -- [lotul 12, C133] motivul scutirii rămâne de verificat cât timp fișa nu-l are; scutirea pusă pe „nescutit” îl golește
                  de_verificat=ARRAY(SELECT x FROM unnest(EXCLUDED.de_verificat) AS x
                                     WHERE x IN ('tip_norma', 'functie_baza') OR x = ANY(salariati.de_verificat)
                                        OR (x = 'motiv_exceptare' AND salariati.motiv_exceptare IS NULL)),
                  motiv_exceptare=CASE WHEN (CASE WHEN 'scutit_contrib_minim' = ANY(EXCLUDED.de_verificat)
                                                  THEN salariati.scutit_contrib_minim ELSE EXCLUDED.scutit_contrib_minim END)
                                       THEN salariati.motiv_exceptare END,
                  nume=EXCLUDED.nume, prenume=EXCLUDED.prenume,
                  data_angajare=EXCLUDED.data_angajare,
                  part_time=CASE WHEN 'tip_norma' = ANY(EXCLUDED.de_verificat) THEN salariati.part_time ELSE EXCLUDED.part_time END,
                  ore_zi=CASE WHEN 'tip_norma' = ANY(EXCLUDED.de_verificat) THEN salariati.ore_zi ELSE EXCLUDED.ore_zi END,
                  persoane_intretinere=CASE WHEN 'persoane_intretinere' = ANY(EXCLUDED.de_verificat)
                                            THEN salariati.persoane_intretinere ELSE EXCLUDED.persoane_intretinere END,
                  judet_casa=EXCLUDED.judet_casa, cor=EXCLUDED.cor,
                  -- [iban_import] la re-import fara coloana IBAN (EXCLUDED.iban NULL) NU sterge IBAN-ul deja
                  -- introdus manual pe ecran: pastreaza valoarea existenta (COALESCE), nu o goleste tacit.
                  iban=COALESCE(EXCLUDED.iban, salariati.iban)
                RETURNING id, (xmax = 0)
            """, (r["cnp"], r["nume"], r["prenume"], r.get("data_angajare"),
                  part_time, r.get("ore_zi"),   # validat mai sus (norma + orele normei parțiale): fără „8” implicit
                  r.get("persoane_intretinere", 0),
                  r.get("judet_casa", ""), r.get("cor", ""),
                  (r.get("iban") or "").strip() or None,   # gol -> NULL (necunoscut), nu "" fabricat
                  r.get("functie_baza"), bool(r.get("scutit_contrib_minim")),   # [decizii 07.10 pct.4; PIVOT 14.10 pct.4]
                  _de_verificat(r)))
            # [PASUL 2b] salariul de baza pe salariu_istoric (sursa unica); reparat si activ (coloana retrasa PASUL 1)
            _sid, _nou = cur.fetchone()   # [447] xmax = 0: rândul a fost INSERAT (salariat nou), altfel fișa a fost actualizată
            noi += 1 if _nou else 0
            from core import salariu_istoric as _si
            from datetime import date as _dm
            _si.seteaza(cur, _sid, r.get("salariu_brut", 0), r.get("data_angajare") or _dm.today().isoformat())
            importati += 1
    # [lotul 11, 447: „mesajul după import: «0 noi, 3 fișe actualizate», nu «3 importați» plus «3 actualizate»”] `importati` cuprinde și
    # fișele actualizate; ecranul spune `noi` și `actualizate` (numărate la scriere), fiecare o singură dată
    return {"importati": importati, "noi": noi, "actualizate": importati - noi, "respinse": er,
            "actualizati": vechi if vechi["randuri"] else None}


#: Câmpurile care pot intra „de verificat” (sursa unică: importul le marchează, salvarea din Stat de plată le confirmă —
#: `salariati_api.actualizeaza_salariat`). [lotul 10, 420] + norma și funcția de bază propuse la import.
DE_VERIFICAT = ("persoane_intretinere", "scutit_contrib_minim", "tip_norma", "functie_baza", "motiv_exceptare")   # [C133] + motivul scutirii


def _de_verificat(r):
    """Marcajul rândului: câmpurile venite fără valoare. Numai valorile cunoscute; o scutire `None` (cerere fără ea) = marcată."""
    m = [x for x in (r.get("de_verificat") or []) if x in DE_VERIFICAT]
    if r.get("scutit_contrib_minim") is None and "scutit_contrib_minim" not in m:
        m.append("scutit_contrib_minim")
    return m

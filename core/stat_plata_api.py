# stat_plata_api.py - Stat de plata lunar + fluturas PDF.
from core.common import Perioada  # [D1, lotul 07.10] d112.pull/genereaza(conn, schema, perioada)
from datetime import date
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from core.pdf_fonturi import init_fonturi, font
from core import pontaj as _pontaj
from core import perioada as _per
from core import salarizare
from core import scadente as _scad
from core import beneficii_api as _ben
from core import common as _common

def stat_plata(conn, schema, an, luna):
    """Calcul salarii pentru toti salariatii activi, la data de referinta (an, luna)."""
    ref = date(an, luna, 1)
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT id, nume, prenume, cnp, persoane_intretinere, part_time, ore_zi,
                   tichet_masa_valoare, iban, cor, data_angajare, data_incetare,
                   data_nastere, copii_scolarizati, declaratie_copii, functie_baza
            FROM {schema}.salariati
            WHERE (data_incetare IS NULL OR data_incetare >= %s)
              AND (data_angajare IS NULL OR data_angajare < (%s::date + INTERVAL '1 month'))
            ORDER BY nume, prenume
        """, (date(an, luna, 1), date(an, luna, 1)))
        randuri = cur.fetchall()
    # CM-uri pe luna
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT salariat_id, COALESCE(SUM(zile),0), COALESCE(SUM(net),0), COALESCE(SUM(brut_ang+brut_fnuass),0)
            FROM {schema}.concedii_medicale WHERE an = %s AND luna = %s GROUP BY salariat_id
        """, (an, luna))
        cm = {r[0]: {"zile": int(r[1]), "net": float(r[2]), "brut": float(r[3])} for r in cur.fetchall()}
    # [lot 19 pct.4c] suspendările (CFP / suspendare) ale fiecărui salariat — afișate și editate din rândul statului
    with conn.cursor() as cur:
        cur.execute(f"SELECT salariat_id, data_inceput, data_sfarsit, tip, temei FROM {schema}.suspendari_contract "
                    f"ORDER BY salariat_id, data_inceput")
        susp_toate = {}
        for _sid, _a, _b, _tip, _tm in cur.fetchall():
            susp_toate.setdefault(_sid, []).append({"data_inceput": _a.isoformat(), "data_sfarsit": _b.isoformat(),
                                                    "tip": _tip, "temei": _tm or ""})
    # [F133 Faza 2a] tichete de vacanta acordate in luna (one-off, din beneficii_lunare)
    vac_luna = _ben.lista_luna(conn, schema, an, luna, "vacanta")
    cult_luna = _ben.lista_luna(conn, schema, an, luna, "cultural")  # [tichete culturale]
    cresa_luna = _ben.lista_luna(conn, schema, an, luna, "cresa")  # [tichete de cresa]
    plafon_vac_an = 6 * float(_common.cota("salariu_minim", ref)[0])  # 6 salarii minime/an
    # [F133 Faza 2b1] tichete cadou acordate in luna: NEIMPOZABIL (nu atinge calcul_salariu/D112).
    # total/salariat (SUM evenimente) + flag taxabil (>300 sau eveniment nelegal -> semnal, tratare la 2b2).
    cadou_luna = _ben.lista_luna(conn, schema, an, luna, "cadou")
    cadou_det = _ben.cadou_detalii_luna(conn, schema, an, luna)
    stat = []
    import calendar as _cal
    from core import salariu_istoric as _si  # salariul contractual DATE-AWARE (sursa unica: salariu_istoric)
    _ultima_luna = date(an, luna, _cal.monthrange(an, luna)[1])
    # [#1/#3] pontajul lunii confirmat? o singura interogare (nu per-salariat).
    _pontaj_confirmat = _per.e_confirmat(conn, schema, an, luna, "pontaj")["confirmat"]
    _cs_sal = conn.cursor()
    for (sid, nume, prenume, cnp, pers, part_time, ore_zi, tichet_val, iban, cor, data_ang, data_inc,
         data_nastere, copii_scolarizati, declaratie_copii, functie_baza) in randuri:
        brut = _si.salariu_la(_cs_sal, schema, sid, _ultima_luna)  # salariul contractual din istoric
        # [lot 19 pct.4c] prezența în contract în lună: angajare/încetare, CFP/suspendare, schimbare de salariu.
        # Codul muncii art.159 alin.(1) + art.49 alin.(2); brutul cuvenit = Σ salariul zilei / zile lucrătoare.
        _susp = _si.suspendari_luna(_cs_sal, schema, sid, an, luna)
        _za = len(_si.zile_active(an, luna, data_ang, data_inc, _susp))
        _brut_cuv = float(_si.brut_cuvenit(_cs_sal, schema, sid, an, luna, data_ang, data_inc, _susp))
        _zlm, _zll = _si.zile_la_minim(_cs_sal, schema, sid, an, luna, data_ang, data_inc, _susp)
        _fac_prorata = (_zlm / _zll) if _zll else 0.0  # lit.a): zile ACTIVE si LA MINIM
        c_cm = cm.get(sid)
        # zile lucratoare FARA sarbatori (OUG 158/2005 art.10) - numitorul proratarii CM
        zile_luna = _scad.zile_lucratoare_luna(an, luna)
        cm_zile = c_cm["zile"] if (c_cm and c_cm["zile"] > 0) else 0
        # [D2 02.08] tichete de masa pe zile EFECTIV lucrate (HG 1045/2018 art.10(3)): zile lucratoare
        # - CM (evidenta) - CO/delegatie/absente/invoire (pontaj). Reversarea decuplarii 20.07 (DECIZII 02.08).
        # [D2/cap.23 + #1/#3] tichetele cer pontaj CONFIRMAT. NU mai blocheaza TOT statul (deadlock: statul
        # murea la HTTP 423 -> ecranul cu butonul Pontaj devenea inaccesibil -> pontajul nu se mai putea confirma).
        # Per-salariat: cand pontajul lunii nu e confirmat, randul se calculeaza cu tichete=0 + flag
        # pontaj_neconfirmat (tichetele raman blocate pana la confirmarea pontajului). HG 1045/2018 art.10(3).
        _pontaj_neconf = float(tichet_val or 0) > 0 and not _pontaj_confirmat
        _tichet_val = 0.0 if _pontaj_neconf else float(tichet_val or 0)
        _fara_tichet = _pontaj.zile_fara_tichet(conn, schema, sid, an, luna) if _tichet_val > 0 else 0
        # [lot 19 pct.4c] tichetele pe zilele ACTIVE ale contractului (nu pe toată luna): HG 1045/2018 art.10(3)
        tichet_zile = max(_za - cm_zile - _fara_tichet, 0)
        # CM pe zile din contract: brutul cuvenit (prezența) minus zilele de CM la salariul mediu zilnic al prezenței.
        # Lună întreagă fără schimbare: _brut_cuv = brut și _za = zile_luna -> exact formula de dinainte.
        if cm_zile > 0:
            brut_lucrat = (_brut_cuv * max(_za - cm_zile, 0) / _za) if _za else 0.0
        else:
            brut_lucrat = _brut_cuv
        vac = vac_luna.get(sid, 0)  # [F133 Faza 2a] tichete vacanta acordate in luna
        cult = cult_luna.get(sid, 0)  # [tichete culturale] acordate in luna (lunar + ocazional)
        cresa = cresa_luna.get(sid, 0)  # [tichete de cresa] acordate in luna
        # [D3 02.08] exces vacanta peste plafonul anual (6 sm) -> venit salarial in brut (cumulat an)
        _cum_c3 = float(_ben.total_an(conn, schema, sid, an, "vacanta", pana_luna=luna) or 0)
        _cum_a3 = float(_ben.total_an(conn, schema, sid, an, "vacanta", pana_luna=luna - 1) or 0) if luna > 1 else 0.0
        _exces_v3 = _ben.exces_vacanta_luna(_cum_c3, _cum_a3, plafon_vac_an)
        calc = salarizare.calcul_salariu(brut_lucrat, persoane=pers or 0, la_data=ref,
                                         functie_baza=bool(functie_baza),   # [3c] CF art.77(1): deducere NUMAI la functia de baza
                                         norma_intreaga=not part_time,
                                         venit_brut_total=float(brut or 0),
                                         data_angajare=data_ang,
                                         data_incetare=data_inc,
                                         facilitate_prorata=_fac_prorata,
                                         tichet_valoare=_tichet_val, tichet_zile=tichet_zile,
                                         tichet_vacanta=max(float(vac or 0) - _exces_v3, 0.0),
                                         tichet_vacanta_exces=_exces_v3,
                                         tichet_cultural=float(cult or 0),
                                         tichet_cresa=float(cresa or 0),
                                         sub_26=salarizare.sub_26_la(data_nastere, ref),   # [deducere suplimentara]
                                         copii_scoala=(int(copii_scolarizati or 0) if declaratie_copii else 0),
                                         declaratie_copii=bool(declaratie_copii),
                                         suspendari=_susp)
        # semnal la depasirea plafonului anual de vacanta (6 sal.minime) - cumulat pana la luna curenta
        vac_an = _ben.total_an(conn, schema, sid, an, "vacanta", pana_luna=luna) if vac else 0
        cadou = cadou_luna.get(sid, 0)  # [F133 Faza 2b1] total cadou (neimpozabil in 2b1)
        cadou_taxabil = any(d["taxabil"] for d in cadou_det.get(sid, []))  # >300 sau nelegal
        stat.append({
            "id": sid,
            "nume": f"{nume or ''} {prenume or ''}".strip(),
            # [front_e] campuri de identitate/contract pt corectie din UI (backend le accepta deja via SalariatEdit)
            "nume_ed": nume, "prenume_ed": prenume, "cnp": cnp,
            "tip_norma": ("partiala" if part_time else "intreaga"),
            "data_angajare": data_ang.isoformat() if data_ang else None, "ore_zi": ore_zi,
            "brut": float(calc["brut"]), "cas": float(calc["cas"]),
            # [lot 19 pct.4c] transparența proratării: salariul din contract și zilele lucrătoare active din lună
            "brut_contractual": float(brut or 0), "zile_active": _za,
            "suspendari": susp_toate.get(sid, []),
            "cass": float(calc["cass"]), "impozit": float(calc["impozit"]),
            "deducere": float(calc["deducere"]["total"]),
            # [deducere_desfacuta 22.08.2026] componentele, ca fluturasul sa poata NUMI
            # fiecare rand. `deducere` ramane TOTALUL: d112 raporteaza totalul, nu se atinge.
            "deducere_baza": float(calc["deducere"]["baza"]),
            "deducere_tineri": float(calc["deducere"]["tineri"]),
            "deducere_copii": float(calc["deducere"]["copii"]),
            "net": float(calc["net"]), "cam": float(calc["cam"]),
            "cas_suprataxa": float(calc.get("cas_suprataxa", 0)),
            "cass_suprataxa": float(calc.get("cass_suprataxa", 0)),
            "tichete_nominal": float(calc.get("tichete_nominal", 0)),
            "tichete_zile": tichet_zile if _tichet_val > 0 else 0,
            "pontaj_neconfirmat": bool(_pontaj_neconf),  # [#1/#3] tichete blocate pana la confirmarea pontajului
            "tichet_masa_valoare": float(tichet_val or 0),  # valoarea configurata (chiar daca blocata luna asta)
            "tichete_vacanta": float(calc.get("tichete_vacanta", 0)),
            "vacanta_peste_plafon": bool(vac and vac_an > plafon_vac_an),
            "cadou": float(cadou or 0),  # [F133 Faza 2b1] neimpozabil, primit pe card
            "tichete_cultural": float(calc.get("tichete_cultural", 0)),  # [tichete culturale] impozit only, pe card
            "tichete_cresa": float(calc.get("tichete_cresa", 0)),  # [tichete de cresa] impozit only, pe card
            "cadou_taxabil": bool(cadou_taxabil),  # semnal: >300 sau eveniment nelegal (2b2)
            "iban": (iban or "").strip(),  # [F134] cont beneficiar pt plata pe card ('' = lipsa -> semnal)
            "cor": (cor or "").strip(),  # [F137] cod ocupatie COR ('' = lipsa -> semnal, necesar REGES)
            "data_incetare": (str(data_inc) if data_inc else ""),  # PASUL 1: data incetarii contractului (gol = activ)
            "cass_tichete": float(calc.get("cass_tichete", 0)),
            "impozit_tichete": float(calc.get("impozit_tichete", 0)),
            # [F133] pt afisaj transparent: impozit salariu (fara tichete), retinerea pe tichete,
            # valoarea totala a tichetelor si totalul disponibil (cash net + tichete pe card separat).
            "impozit_salariu": float(calc["impozit"]) - float(calc.get("impozit_tichete", 0)),
            "retinut_tichete": float(calc.get("cass_tichete", 0)) + float(calc.get("impozit_tichete", 0)),
            "valoare_tichete": float(calc.get("tichete_nominal", 0)) + float(calc.get("tichete_vacanta", 0)) + float(cadou or 0) + float(calc.get("tichete_cultural", 0)) + float(calc.get("tichete_cresa", 0)),
            "total_disponibil": float(calc["net"]) + float(calc.get("tichete_nominal", 0)) + float(calc.get("tichete_vacanta", 0)) + float(cadou or 0) + float(calc.get("tichete_cultural", 0)) + float(calc.get("tichete_cresa", 0)),
            "cost": float(calc["cost_angajator"]),
            "cm_zile": cm_zile,
            "cm_brut": c_cm["brut"] if c_cm else 0,
            # [salariu_edit] baza contractuala (salariu_istoric) lipsa/0 -> statul e incoerent
            # (net 0 dar apare cost din suprataxa sub-minim); se SEMNALEAZA, nu se afiseaza tacit (MEMORY §13).
            "baza_lipsa": float(brut or 0) <= 0,
            "salariu_baza": float(brut or 0),  # [salariu_edit] baza contractuala (istoric), pt pre-completarea editarii
            # [stat_emis 21.08.2026] doua campuri pe care fluturasul si le recalcula singur, cu alte
            # intrari. Acum le ia de aici: statul e sursa unica a cifrelor de pe fluturas.
            "facilitate": float(calc.get("facilitate", 0)),
            "cm_net": float(c_cm["net"]) if c_cm else 0.0,
            # baza CAM a salariatului, exact ca D112 (`_d112_genereaza`: bazac = brut realizat + exces + cadou -
            # facilitate, fiecare la leu) - cheie interna, consumata de `_imparte_cam` mai jos
            "_bazac": max(int(_leu(brut_lucrat)) + int(_leu(calc.get("tichete_vacanta_exces", 0)))
                          + int(_leu(calc.get("tichete_cadou", 0))) - int(_leu(calc.get("facilitate", 0))), 0),
        })
    _cs_sal.close()
    _imparte_cam(stat, ref)
    return stat


def _leu(x):
    from decimal import Decimal as _D
    from core.numere import leu_aritmetic
    return leu_aritmetic(_D(str(x)))


def _imparte_cam(stat, ref):
    """CAM-ul de pe cartele = CAM-ul DECLARAT, impartit pe salariati (comanda Costin 06.10.2026 pct.11: „CAM 259,77 pe
    cartele vs 260 în notă”; costul angajatorului de pe fluturas iese din aceleasi sume ca D112).

    D112 nu are CAM pe salariat: il declara o data, pe TOTAL (cod 480 = ROUND(Σ bazac x 2,25%), aritmetic). Cartela il
    arata pe salariat, deci il IMPARTE: fiecare primeste partea intreaga din bazac x cota, iar leii ramasi pana la total
    merg, cate unul, la cele mai mari fractiuni (metoda resturilor celor mai mari; egalitate -> ordinea statului).
    INTERPRETARE CU TEMEI (DECIZII 06.10.2026 pct.11): legea nu imparte CAM-ul pe salariat; alternativa respinsa - CAM cu
    bani pe salariat si o linie de rotunjire separata - lasa suma cartelelor diferita de D112 si de nota."""
    from decimal import Decimal as _D
    from core.numere import leu_aritmetic
    cota = _D(str(_common.cota("cam", ref)[0]))
    brute = [_D(r["_bazac"]) * cota for r in stat]
    total = int(leu_aritmetic(sum(brute, _D(0))))
    parti = [int(x) for x in brute]   # partea intreaga (valori >= 0)
    rest = total - sum(parti)
    ordine = sorted(range(len(stat)), key=lambda i: (-(brute[i] - parti[i]), i))
    for i in ordine[:max(rest, 0)]:
        parti[i] += 1
    for r, cam in zip(stat, parti):
        r["cost"] = round(r["cost"] - r["cam"] + cam, 2)
        r["cam"] = float(cam)
        del r["_bazac"]

def stat_final(conn, schema, an, luna):
    """Statul de plată AȘA CUM SE PLĂTEȘTE ȘI SE TIPĂREȘTE: `stat_plata` + indemnizația de concediu medical cu reținerile
    DECLARATE (comanda Costin 06.10.2026, pct.2: „421 se soldează la ban și în lunile cu concediu medical”).

    D112 reține O DATĂ pe salariat, din salariu și din indemnizație împreună: impozitul se calculează pe baza lunară combinată.
    Certificatul (`concedii_medicale`) ține reținerile indemnizației calculate SEPARAT, iar diferența de rotunjire ajungea pe
    fluturaș (măsurat: 275 lei net pe certificat, 274 lei din sumele declarate). Aici reținerile indemnizației = totalul
    DECLARAT al salariatului (`d112.genereaza` -> `RezultatD112.asigurati`) − reținerile din salariu (rândul statului), iar
    netul indemnizației = brutul ei declarat (pe certificat, la leu ca în D112) − ele. `stat_plata` rămâne neajustat fiindcă
    îl citește chiar `d112.pull` (altfel ar fi circular); `core/d112.py` nu se atinge (condiția D1, decizia Costin 04.10).

    Dacă D112 nu se poate genera (profil incomplet), rândul păstrează valorile certificatului și o spune: `cm_retineri_sursa`."""
    from decimal import Decimal as _D
    from core.numere import leu_aritmetic
    stat = stat_plata(conn, schema, an, luna)
    cu_cm = [r for r in stat if r.get("cm_zile")]
    if not cu_cm:
        return stat
    for r in cu_cm:
        r["cm_retineri_sursa"] = "certificat"
    try:
        from core import d112 as _d112
        _prof, sal = _d112.pull(conn, schema, Perioada(an=an, luna=luna))
        _xml, res = _d112.genereaza(conn, schema, Perioada(an=an, luna=luna))
    except Exception:   # noqa: BLE001 — D112 negenerabil: rămân valorile certificatului, marcate
        return stat
    if len(sal) != len(res.asigurati):
        return stat
    decl = {}
    for s_, a in zip(sal, res.asigurati):
        if ("%s %s" % (s_.get("nume") or "", s_.get("prenume") or "")).strip() == a.nume:
            decl[s_["id"]] = a
    with conn.cursor() as cur:
        cur.execute("SELECT salariat_id, brut_ang, brut_fnuass FROM concedii_medicale WHERE an=%s AND luna=%s", (an, luna))
        brut_cm = {}
        for sid, ba, bf in cur.fetchall():
            brut_cm[sid] = brut_cm.get(sid, _D(0)) + leu_aritmetic(_D(str(ba or 0))) + leu_aritmetic(_D(str(bf or 0)))
    for r in cu_cm:
        a = decl.get(r["id"])
        if a is None:
            continue
        ret_sal = _D(str(r["cas"])) + _D(str(r["cass"])) + _D(str(r.get("cass_tichete") or 0)) + _D(str(r["impozit"]))
        ret_cm = _D(a.cas + a.cass + a.impozit) - ret_sal
        r["cm_retineri"] = float(ret_cm)
        r["cm_brut_declarat"] = float(brut_cm.get(r["id"], 0))
        r["cm_net"] = float(brut_cm.get(r["id"], _D(0)) - ret_cm)
        r["cm_retineri_sursa"] = "D112"
    return stat


def net_de_plata(conn, schema, an, luna):
    """Σ netul care se plateste pe luna: al fluturasului fiecarui salariat (exemplarul emis, daca luna e emisa pentru el;
    altfel randul statului de acum - aceeasi regula ca `rand_fluturas`). Contrapartida contului 421 dupa nota statului."""
    from core import stat_plata_emis as _spe
    from decimal import Decimal as _D
    emise = _spe.citeste(conn, schema, an, luna)
    total = _D(0)
    for r in stat_final(conn, schema, an, luna):
        ex = _spe.ultimul(emise, int(r["id"]))
        total += _D(str((ex["date"] if ex else r).get("net") or 0))
    return total


def net_cm_de_plata(conn, schema, an, luna):
    """Σ netul indemnizatiilor de concediu medical de pe fluturasi (exemplarul emis, altfel statul de acum) — contrapartida
    contului 423 dupa nota statului (comanda Costin 06.10.2026, pct.2)."""
    from core import stat_plata_emis as _spe
    from decimal import Decimal as _D
    emise = _spe.citeste(conn, schema, an, luna)
    total = _D(0)
    for r in stat_final(conn, schema, an, luna):
        ex = _spe.ultimul(emise, int(r["id"]))
        total += _D(str((ex["date"] if ex else r).get("cm_net") or 0))
    return total


def exemplar_curent(conn, schema, salariat_id, an, luna):
    """Exemplarul EMIS cel mai recent al salariatului, sau None daca luna nu e emisa. Separat de
    `rand_fluturas` fiindca fluturasul are nevoie si de METADATELE actului (al catelea exemplar, pe
    care il inlocuieste), nu doar de cifre."""
    from core import stat_plata_emis as _spe
    ex = _spe.citeste(conn, schema, an, luna, salariat_id=salariat_id)
    return max(ex, key=lambda x: x["exemplar"]) if ex else None


def rand_fluturas(conn, schema, salariat_id, an, luna):
    """Rândul din care se TIPĂREȘTE fluturașul — sursa unică a cifrelor lui.

    Dacă luna e EMISĂ, întoarce exemplarul înghețat (documentul care a ajuns la om); altfel, rândul
    statului de acum. Fluturașul nu mai calculează nimic: până la 21.08.2026 își refăcea singur tot
    calculul, cu alte intrări, și ieșea DIFERIT pe 14 din 192 de perechi reale — dădea pe hârtie
    tichete pe care statul le blocase (pontaj neconfirmat, HG 1045/2018 art.10(3)) și ignora plafonul
    anual de vacanță. Două calcule ale aceluiași lucru nu rămân egale."""
    # Fara masca pe coloane lipsa: prima forma inghitea eroarea si cadea pe recalcul, dar lasa
    # tranzactia OTRAVITA (InFailedSqlTransaction la urmatoarea interogare) si ascundea o migrare
    # neaplicata. Un tenant nemigrat e o eroare de instalare, nu o stare de functionare.
    _ex = exemplar_curent(conn, schema, salariat_id, an, luna)
    if _ex:
        return _ex["date"]
    return next((r for r in stat_final(conn, schema, an, luna)
                 if int(r.get("id") or 0) == salariat_id), None)



def randuri_deducere(r):
    """Randurile de deducere de pe fluturas, fiecare sub NUMELE lui. [deducere_desfacuta 22.08.2026]

    Pana la 22.08.2026 exista un singur rand, ("Deducere personala", total) — iar totalul include si
    deducerile SUPLIMENTARE: tineri sub 26 de ani si copii scolarizati. Pe un tanar la salariul minim
    din iulie 2026 randul arata 1.513,75 lei sub numele unei deduceri care e 865,00. Nu e o lipsa, e o
    ETICHETA FALSA pe o hartie care ajunge la salariat — masurat: 3 din 5 cazuri obisnuite si 2 din 24
    de salariati reali activi la 01.07.2026.

    TEMEI: CF art.77 alin.(2) deducerea personala de baza; alin.(4^1) suplimentara pentru tineri sub
    26 de ani; alin.(4^2) suplimentara pentru copii scolarizati. Trei deduceri distincte in lege, deci
    trei randuri distincte pe hartie.

    Suplimentarele apar doar cand sunt ACORDATE. Absenta lor, aratata cu motiv, e interdictia 64 —
    masurata separat, alt prag; aici se repara strict eticheta care minte.

    Exemplarele inghetate scrise inainte de data asta n-au componentele: atunci randul isi spune pe
    nume ('...si suplimentare'), nu pretinde ca e doar cea personala.
    """
    def _ded_lei(k):
        return float(r.get(k) or 0)

    total = _ded_lei("deducere")
    if not any(k in r for k in ("deducere_baza", "deducere_tineri", "deducere_copii")):
        return [("Deducere personala si suplimentare (total)", total)]
    randuri = [("Deducere personala", _ded_lei("deducere_baza"))]
    if _ded_lei("deducere_tineri"):
        randuri.append(("Deducere suplimentara, tineri sub 26 de ani", _ded_lei("deducere_tineri")))
    if _ded_lei("deducere_copii"):
        randuri.append(("Deducere suplimentara, copii scolarizati", _ded_lei("deducere_copii")))
    return randuri

# Randurile compozitiei se disting prin FEL, nu prin eticheta. Un gard care ar intreba
# `eticheta == "SALARIU NET"` ar pazi un sir AFISABIL - se poate rescrie fara ca nimic sa cada
# (METODA §23). `fel` decide ingrosarea, si pe hartie, si pe ecran.
FEL_LINIE = "linie"          # rand obisnuit, cu suma
FEL_TOTAL = "total"          # rand ingrosat: SALARIU NET, TOTAL DISPONIBIL
FEL_MENTIUNE = "mentiune"    # rand in tabel FARA suma (zilele de CM)
FEL_NOTA = "nota"            # nota de sub tabel: ce plateste ANGAJATORUL, nu salariatul

# Campurile statului pe care compozitia le DUCE la om - pe hartie si pe ecran. Nu e o lista de
# bunavointa: `core/test_compozitie_fluturas.py` pune in fiecare o valoare-martor unica si cere
# s-o REGASEASCA in iesire. Un camp scos din compozitie si uitat aici pica testul.
CAMPURI_COMPUSE = ("brut", "facilitate", "cas", "cass", "deducere_baza", "deducere_tineri",
                   "deducere_copii", "impozit_salariu", "net", "cm_zile", "cm_net", "cm_brut",
                   "cass_tichete", "impozit_tichete", "tichete_nominal", "tichete_vacanta",
                   "cadou", "tichete_cultural", "tichete_cresa", "valoare_tichete",
                   "total_disponibil", "cost", "cam", "cas_suprataxa", "cass_suprataxa")

# Ce trimite ruta si compozitia NU arata, cu motivul scris. Fara randul asta, absenta ar arata
# identic cu o scapare - iar conditia de inchidere a lui R97 cere ori reparatie, ori motiv scris.
CAMPURI_NEAFISATE_MOTIVATE = {
    "retinut_tichete": ("suma exacta a doua randuri deja aratate - CASS tichete + impozit tichete. "
                        "Un subtotal asezat langa chiar componentele lui nu adauga nimic pe un "
                        "fluturas; ce lipsea era compozitia, nu inca o suma."),
}


def compozitie_fluturas(r):
    """Compozitia netului, ca lista de randuri - O SINGURA sursa pentru hartie SI pentru ecran.

    DE CE EXISTA (30.08.2026, lista 5 a verdictului 1d). Componentele netului se compuneau inauntrul
    lui `fluturas_pdf`, deci se vedeau numai daca omul descarca PDF-ul; pe ecran statul arata cifra
    fara compozitie - 12 campuri trimise de ruta si nerandate de nimeni (clasa R97). Reparatia se
    putea face a doua oara in JS, si atunci ar fi existat DOUA liste ale aceluiasi lucru: exact
    clasa pe care `rand_fluturas` o descrie in docstring - *doua calcule ale aceluiasi lucru nu
    raman egale*.

    O DIVERGENTA GASITA LA SCRIERE, si reparata aici prin constructie: `fluturas_pdf` calcula
    `val_tichete = nominal + vacanta + cadou`, iar ruta trimitea `total_disponibil` cu inca doi
    termeni - tichetele CULTURALE si cele de CRESA. Deci hartia si ecranul aratau totaluri
    DIFERITE pentru acelasi salariat, ori de cate ori avea tichete culturale sau de cresa. Mai
    mult, gardul `if are_masa or are_vac or are_cadou` sarea intreaga sectiune de tichete pentru
    un salariat care are NUMAI tichete culturale sau de cresa. Acum totalul se ia din campul
    statului, nu se recalculeaza.

    EXEMPLARELE INGHETATE de dinaintea unui camp nu-l au. Ca la `randuri_deducere`: cand campul
    lipseste din rand, se cade pe suma componentelor - un exemplar vechi nu are voie sa arate 0
    acolo unde arata o suma inainte.

    Intoarce [{"eticheta", "valoare", "fel"}]; `valoare` e None pe randurile fara suma.
    """
    def _n(k):
        return float(r.get(k) or 0)

    linii = [
        ("Salariu brut", _n("brut"), FEL_LINIE),
        ("Facilitate salariu minim (netaxabilă)", _n("facilitate"), FEL_LINIE),
        ("CAS (25%)", -_n("cas"), FEL_LINIE),
        ("CASS (10%)", -_n("cass"), FEL_LINIE),
        *[(e, v, FEL_LINIE) for e, v in randuri_deducere(r)],
        ("Impozit pe venit", -_n("impozit_salariu"), FEL_LINIE),
        ("SALARIU NET", _n("net"), FEL_TOTAL),
    ]
    cm_zile = int(_n("cm_zile"))
    if cm_zile:
        linii.insert(1, ("Zile de concediu medical: %d" % cm_zile, None, FEL_MENTIUNE))
        linii.insert(len(linii) - 1, ("Indemnizație CM (netă)", _n("cm_net"), FEL_LINIE))
    # [F133] tichete: doar TAXA (CASS+impozit) se retine din salariul CASH -> reduce NET-ul, deci
    # ramane INAINTE de SALARIU NET (coloana reconciliaza la net). Valoarea tichetelor se primeste
    # PE CARD SEPARAT (nu cash) -> se arata DUPA net, plus totalul disponibil.
    are_masa, are_vac, are_cadou = _n("tichete_nominal") > 0, _n("tichete_vacanta") > 0, _n("cadou") > 0
    are_cult, are_cresa = _n("tichete_cultural") > 0, _n("tichete_cresa") > 0
    if are_masa or are_vac or are_cadou or are_cult or are_cresa:
        # retinerea (CASS+impozit) apare DOAR pt masa/vacanta (taxabile); cadoul e neimpozabil (2b1),
        # iar culturalele si cresa poarta doar impozit, deja inclus in `impozit_tichete`.
        if are_masa or are_vac:
            i = len(linii) - 1  # inaintea SALARIU NET
            linii.insert(i, ("  CASS tichete (10%) — reținut din salariu", -_n("cass_tichete"), FEL_LINIE)); i += 1
            linii.insert(i, ("  Impozit tichete (10%) — reținut din salariu", -_n("impozit_tichete"), FEL_LINIE))
        if are_masa:
            linii.append(("Tichete de masă (%d zile × %g lei, pe card)"
                          % (int(_n("tichete_zile")), _n("tichet_masa_valoare")),
                          _n("tichete_nominal"), FEL_LINIE))
        if are_vac:
            linii.append(("Tichete de vacanță (pe card separat)", _n("tichete_vacanta"), FEL_LINIE))
        if are_cadou:
            linii.append(("Tichete cadou (neimpozabile, pe card separat)", _n("cadou"), FEL_LINIE))
        if are_cult:
            linii.append(("Tichete culturale (pe card separat)", _n("tichete_cultural"), FEL_LINIE))
        if are_cresa:
            linii.append(("Tichete de creșă (pe card separat)", _n("tichete_cresa"), FEL_LINIE))
        # Campul statului, nu o recalculare - vezi divergenta din docstring. Exemplarele inghetate
        # de dinaintea campului cad pe suma componentelor, ca sa nu arate 0.
        val_tichete = (float(r["valoare_tichete"]) if r.get("valoare_tichete") is not None
                       else _n("tichete_nominal") + _n("tichete_vacanta") + _n("cadou")
                       + _n("tichete_cultural") + _n("tichete_cresa"))
        total_disp = (float(r["total_disponibil"]) if r.get("total_disponibil") is not None
                      else _n("net") + val_tichete)
        linii.append(("Total tichete (pe card)", val_tichete, FEL_LINIE))
        linii.append(("TOTAL DISPONIBIL (net + tichete)", total_disp, FEL_TOTAL))

    # Ce plateste ANGAJATORUL. Sub tabel pe hartie, sub compozitie pe ecran - nu se scade din net,
    # si de-aia nu sta in coloana care reconciliaza la net.
    linii.append(("CAM — contribuția asiguratorie pentru muncă (2,25%), plătită de angajator",
                  _n("cam"), FEL_NOTA))
    _supra = _n("cas_suprataxa") + _n("cass_suprataxa")
    if _supra > 0:
        linii.append(("Suprataxă part-time (CAS + CASS pe podeaua salariului minim), plătită de angajator",
                      _supra, FEL_NOTA))
    if _n("cm_brut"):
        linii.append(("Indemnizație de concediu medical, brută (suportată de angajator și de FNUASS)",
                      _n("cm_brut"), FEL_NOTA))
    linii.append(("Cost total angajator", _n("cost"), FEL_NOTA))

    return [{"eticheta": e, "valoare": v, "fel": f} for e, v, f in linii]


def fluturas_pdf(conn, schema, salariat_id, an, luna, nume_firma=""):
    """Design System cap.7: reportlab Table, nu drawString manual. Sume in format romanesc.

    RANDOR, nu calculator: toate cifrele vin din `rand_fluturas`. Vezi acolo de ce."""
    from reportlab.lib.pagesizes import A4 as _A4
    from reportlab.lib.units import mm as _mm
    from reportlab.lib import colors as _colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.enums import TA_RIGHT
    from core.pdf_util import bani as _bani

    r = rand_fluturas(conn, schema, salariat_id, an, luna)
    if not r:
        return None
    _ex = exemplar_curent(conn, schema, salariat_id, an, luna)

    with conn.cursor() as _cur:
        _cur.execute(f"SELECT culoare_factura, font_factura FROM {schema}.firma_profil WHERE id = 1")
        _prof = _cur.fetchone()
    _cul_profil, _font_profil = (_prof if _prof else (None, None))
    init_fonturi()
    fr, fb = font(_font_profil or "sans")
    try:
        ac = _colors.HexColor(_cul_profil or "#1d4ed8")
    except Exception:
        ac = _colors.HexColor("#1d4ed8")

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=_A4,
        leftMargin=18 * _mm, rightMargin=18 * _mm,
        topMargin=16 * _mm, bottomMargin=16 * _mm,
        title="Fluturaș %02d/%d%s" % (luna, an, (" — " + nume_firma) if nume_firma else ""), author="iConta",   # [05.10.2026]
    )
    stil = getSampleStyleSheet()
    st_titlu = ParagraphStyle("titlu", parent=stil["Normal"], fontName=fb, fontSize=14, textColor=ac, leading=17)
    st_meta = ParagraphStyle("meta", parent=stil["Normal"], fontName=fr, fontSize=10, textColor=_colors.HexColor("#555555"))
    st_lbl = ParagraphStyle("lbl", parent=stil["Normal"], fontName=fr, fontSize=10)
    st_val = ParagraphStyle("val", parent=stil["Normal"], fontName=fr, fontSize=10, alignment=TA_RIGHT)
    st_lbl_b = ParagraphStyle("lblb", parent=st_lbl, fontName=fb, fontSize=11)
    st_val_b = ParagraphStyle("valb", parent=st_val, fontName=fb, fontSize=11)

    el = [
        Paragraph(f"Fluturas de salariu — {luna:02d}/{an}", st_titlu),
        Paragraph(nume_firma, st_meta),
        Paragraph(f"Salariat: {r.get('nume') or ''}", st_meta),
    ]
    # Un al doilea exemplar care arata IDENTIC cu primul nu e o corectie, e un al doilea original.
    # Omul are deja un fluturas acasa; hartia trebuie sa-i spuna care dintre cele doua tine.
    if _ex and int(_ex.get("exemplar") or 1) > 1:
        from core.pdf_util import data_ro as _data_ro  # sursa canonica (DS cap.4), nu strftime local
        _cand = _data_ro(_ex.get("emis_la"))
        _cand = (" din " + _cand) if _cand else ""
        el.append(Paragraph(
            "CORECȚIE — exemplarul %d, care înlocuiește exemplarul %d%s. Suma corectă e cea de mai jos."
            % (int(_ex["exemplar"]), int(_ex["exemplar"]) - 1, _cand),
            ParagraphStyle("cor", parent=st_meta, fontName=fb,
                           textColor=_colors.HexColor("#b91c1c"))))
    el.append(Spacer(1, 10))

    # [lista 5, 30.08.2026] Randurile NU se mai compun aici: vin din `compozitie_fluturas`, aceeasi
    # sursa pe care o trimite ruta catre ecran. Vezi acolo de ce.
    comp = compozitie_fluturas(r)
    rows = []
    for c in comp:
        if c["fel"] == FEL_NOTA:
            continue  # notele angajatorului se tiparesc SUB tabel, ca pana acum
        bold = c["fel"] == FEL_TOTAL
        lbl_st = st_lbl_b if bold else st_lbl
        val_st = st_val_b if bold else st_val
        val_txt = _bani(c["valoare"], "lei") if c["valoare"] is not None else ""
        rows.append([Paragraph(c["eticheta"], lbl_st), Paragraph(val_txt, val_st)])

    tabel = Table(rows, colWidths=[100 * _mm, 40 * _mm])
    n_last = len(rows) - 1
    tabel.setStyle(TableStyle([
        ("LINEABOVE", (0, n_last), (-1, n_last), 1, ac),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    el.append(tabel)
    el.append(Spacer(1, 8))
    _st_nota = ParagraphStyle("cost", parent=stil["Normal"], fontName=fr, fontSize=9,
                              textColor=_colors.HexColor("#555555"))
    for c in comp:
        if c["fel"] != FEL_NOTA:
            continue
        el.append(Paragraph("%s: %s" % (c["eticheta"], _bani(c["valoare"], "lei")), _st_nota))
    doc.build(el)
    return buf.getvalue()

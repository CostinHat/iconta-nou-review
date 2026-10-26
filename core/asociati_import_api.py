"""
core/asociati_import_api.py — import asociati (stratul 5 migrare) per firma.

Citeste un export (.xlsx/.csv) cu nume, CNP/CUI, cota %. Mapeaza flexibil coloanele.
Importa in tabelul existent `asociati` (DELETE + INSERT per firma); [lotul 10, 426] peste o structura existenta, fara data de
cesiune, numai confirmat (`inlocuieste`).
Valideaza CNP daca are 13 cifre (cheie 279146358279); CUI-ul persoanei juridice: cifra de control [Q4] si, din comanda Costin 8.2
[367], existenta la ANAF si numele din fisier fata de cel de la ANAF.
Coerenta: suma cotelor trebuie sa dea 100% (refuz, `cote_nu_dau_suta`).

"""
# [E2b, 15.09.2026] Tranzactia e a APELANTULUI: `db.get_conn` comite la iesirea din bloc, iar un
# `commit` aici ar taia tranzactia lui in doua (P4). Depozitul primeste conexiunea si scrie; nu
# deschide, nu comite.
from __future__ import annotations
from core.identitate import valideaza_cui as _valideaza_cui  # [Q4] CUI juridic validat ca CUI, nu ca CNP



def valideaza_cnp(cnp):
    """[347] Sursa unică e `core.identitate.valideaza_cnp` (motivul în cuvinte); numele rămâne pentru apelanții de aici."""
    from core.identitate import valideaza_cnp as _v
    return _v(cnp)


# [14.10.2026, comanda Costin „Importul din SAGA”, verbatim în DECIZII] Citirea fișierului și potrivirea coloanelor trec prin
# `core.import_tabel` (sursa unică: format, codare Windows-1250 recunoscută sau refuzată, antet sub titluri, coloane pe cuvinte
# întregi, ambiguitate refuzată numit) — nu mai e o copie a lui `_gaseste_col` aici.
from core import import_tabel as _it

CAMPURI = {
    "nume": ("nume asociat", "denumire asociat", "=nume", "nume*", "asociat*", "denumire*"),
    "cod": ("cnp cui", "cnp", "cui", "cif", "cod fiscal", "=cod"),
    "cota": ("cota*", "procent*", "participare", "%"),
}
#: [lotul 11] numele câmpului în refuzul coloanelor ambigue (`import_tabel.coloana`), în limba contabilului — nu cheia internă
#: (garda: core/test_lot11_import_etichete_camp.py)
ETICHETE_CAMP = {
    "nume": "numele asociatului",
    "cod": "CNP-ul / CUI-ul asociatului",
    "cota": "cota de participare",
}


from core.numere import numar as _numar  # sursa unica (15.07.2026); "%" tratat acolo
from core.migrare_api import respinge, semnaleaza  # [P8/C] respingerea e o afirmatie, cu regula din nomenclator
from core.pdf_util import data_ro as _data_ro   # DS cap.4: data din text, canonic
from core.common import cate as _cate
from core import chei_unice as _chei   # [lotul 10, C73] cheia naturală dublată -> refuz numit, nu 500
from core import cui_forma as _forma_cui   # [lotul 11, decizia Costin 10.3 pct.4] codul (CUI / CNP) în forma păstrată


def extrage(continut, nume_fisier=""):
    """Intoarce [{nume, cnp, cota, tip, cnp_valid, cnp_motiv}]."""
    randuri = _it.citeste(continut, nume_fisier)
    if not randuri or all(_it.rand_gol(r) for r in randuri):
        return []
    try:
        antet, start = _it.gaseste_antet(randuri, CAMPURI, obligatorii=("nume",), nume_fisier=nume_fisier)
    except _it.FisierNecitit as e:
        if isinstance(e, _it.ColoaneAmbigue):
            raise
        try:
            antet, start = _it.gaseste_antet(randuri, CAMPURI, obligatorii=("cod",), nume_fisier=nume_fisier)
        except _it.FisierNecitit:
            raise ValueError("nu se găsește coloana nume/cod asociat - fișier nerecunoscut")
    col = lambda camp, exclus=(): _it.coloana(antet, CAMPURI[camp], exclus=exclus, camp=ETICHETE_CAMP[camp])
    i_cod = col("cod")
    i_nume = col("nume", (i_cod,))
    i_cota = col("cota", (i_cod, i_nume))
    if i_nume < 0 and i_cod < 0:
        raise ValueError("nu se găsește coloana nume/cod asociat - fișier nerecunoscut")
    randuri = randuri[start - 1:]
    out = []
    for nr, r in enumerate(randuri[1:], start=start + 1):
        def cel(i):
            return _it.celula(r, i)
        nume_v = cel(i_nume)
        # [lotul 11, clasa „normalizare locală a CUI”] forma unică `cui_forma.stocare`: „RO” scos numai din fața unui cod din cifre (CUI-ul
        # unui asociat persoană juridică); înainte `.replace("RO", "")` îl scotea de oriunde („FRRO123456789” -> „FR123456789”)
        cod = _forma_cui.stocare(cel(i_cod)) or ""
        cota = _numar(cel(i_cota))
        # [364, comanda Costin 8.2] rândul fără nume NU mai dispare în tăcere (7 rânduri -> „6 asociați”, totalul cotelor fără el): se
        # citește și se respinge numit (`verifica_randuri`). Numai rândul complet gol se sare.
        if not (nume_v or cod or cel(i_cota)):
            continue
        # persoana fizica daca pare CNP de 13 cifre; juridica daca are alt cod; [365] fara cod — tipul NU se ghiceste („juridică” din oficiu)
        este_cnp = len(cod) == 13 and cod.isdigit()
        if este_cnp:
            valid, motiv = valideaza_cnp(cod)
            tip = "fizica"
        elif cod:
            valid, motiv = _valideaza_cui(cod)
            tip = "juridica"
        else:
            valid, motiv, tip = False, "fără CNP / CUI", ""
        out.append({"nume": nume_v, "cnp": cod, "cota": cota,
                    "tip": tip, "cnp_valid": valid, "cnp_motiv": motiv, "rand_fisier": nr})
    return out


def coerenta_cote(randuri, respinse=()):
    """{total, coincide} — suma cotelor vs 100%, pe rândurile care INTRĂ: [384, retestul 19.10.2026: „«total cote ✓ 100%» adună și
    rândurile respinse; intră un singur asociat, cu 30%”] rândurile cu `rand_fisier` în `respinse` (respinse pe rând: CNP invalid, fără
    nume, dublură…) nu intră, deci nici cota lor nu se adună."""
    respinse = {str(x) for x in respinse}
    total = round(sum((r.get("cota") or 0) for r in randuri if str(r.get("rand_fisier")) not in respinse), 2)  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
    return {"total": total, "coincide": abs(total - 100.0) < 0.01}


def rezumat(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('asociati')")
        if cur.fetchone()[0] is None:
            return {"are_asociati": False, "randuri": 0, "total_cota": 0}
        cur.execute("SELECT count(*), COALESCE(sum(cota),0) FROM asociati")
        n, tc = cur.fetchone()
    return {"are_asociati": n > 0, "randuri": n, "total_cota": float(tc)}


def _cifre(cod):
    return "".join(ch for ch in str(cod or "") if ch.isdigit())


def _nume_comparabil(nume):
    """[367] Numele pentru comparația cu ANAF: fără diacritice, fără majuscule și fără punctuație/spații — „S.R.L.” = „SRL”,
    „Ţ” = „Ț” = „T”. Forma juridică NU se scoate: „Firma” și „Firma SRL” rămân diferite (alt nume, de corectat în fișier)."""
    import unicodedata
    t = unicodedata.normalize("NFKD", str(nume or "")).casefold()
    return "".join(ch for ch in t if ch.isalnum() and not unicodedata.combining(ch))


def verificare_anaf(randuri):
    """[367, comanda Costin 8.2] CUI-urile asociaților persoane juridice (cele care trec cifra de control), întrebate la ANAF:
    {cui: {gasit, denumire}}; None dacă serviciul ANAF nu răspunde (rândurile intră cu semnalul `anaf_neverificat`, nu cu un refuz
    fals și nici cu o eroare internă)."""
    from core import anaf_api
    cui_uri = []
    for r in randuri or []:
        cod = str(r.get("cnp") or "").strip()
        if cod and not (len(cod) == 13 and cod.isdigit()) and _valideaza_cui(cod)[0]:
            cui_uri.append(_cifre(cod))
    cui_uri = list(dict.fromkeys(cui_uri))
    if not cui_uri:
        return {}
    try:
        rez = anaf_api.valideaza_cui(cui_uri)
    except Exception:  # noqa: BLE001 — orice cădere a serviciului străin are același răspuns: neverificat, spus pe rând
        return None
    out = {c: {"gasit": False, "denumire": ""} for c in cui_uri}
    for x in rez:
        c = _cifre(x.get("cui"))
        if c in out:
            out[c] = {"gasit": bool(x.get("gasit", True)), "denumire": x.get("denumire") or ""}
    return out


def verifica_randuri(randuri, anaf=None):
    """PURA: [{rand, motiv, mesaj}]. CNP/CUI valid + cotele insumeaza exact 100%.

    coerenta_cote() exista de la inceput, dar importa() n-o chema: cotele de 115% au
    intrat, iar migrarea a marcat stratul "gata" verde. D205 nu se poate genera cu ele
    (dovedit 15.07.2026, prin migrare reala).

    [364–367, comanda Costin 8.2] Si: rândul fără nume, rândul fără CNP/CUI (asociatul n-ar putea apărea în D205), același CNP/CUI pe
    două rânduri, cota negativă sau peste 100; iar cu `anaf` (rezultatul `verificare_anaf`): CUI-ul pe care ANAF nu-l găsește și
    numele din fișier diferit de cel de la ANAF.
    """
    er = []
    vazut = {}
    for i, r in enumerate(randuri or [], start=2):   # antetul e randul 1
        i = _it.nr_rand(r, i)
        nume = str(r.get("nume") or "").strip()
        cod = str(r.get("cnp") or "").strip()
        eticheta = nume or ("asociatul cu %s" % cod if cod else "asociatul")
        if not nume:
            er.append(respinge("asociat", i, "denumire_lipsa",
                               "rândul n-are numele asociatului — fără nume nu poate intra în structura firmei"))
        # [Q4] ramifica fizic/juridic ca extrage(): CUI de juridica se valideaza ca CUI (cifra de
        # control), NU ca CNP de 13 cifre. Altfel asociatul-firma acceptat la preview era respins aici.
        if cod:
            este_cnp = len(cod) == 13 and cod.isdigit()
            ok, motiv = valideaza_cnp(cod) if este_cnp else _valideaza_cui(cod)
            if not ok:
                er.append(respinge(
                    "asociat", i, "cnp_invalid" if este_cnp else "cui_invalid",
                    "%s: %s invalid (%s)" % (eticheta, "CNP" if este_cnp else "CUI", motiv)))
            elif not este_cnp and anaf:
                a = anaf.get(_cifre(cod))
                if a is not None and not a["gasit"]:
                    er.append(respinge("asociat", i, "cui_negasit_anaf",
                                       "%s: CUI-ul %s nu e găsit la ANAF — verifică-l în fișier" % (eticheta, cod)))
                elif a is not None and nume and _nume_comparabil(a["denumire"]) != _nume_comparabil(nume):
                    er.append(respinge("asociat", i, "nume_diferit_anaf",
                                       "%s: la ANAF, CUI-ul %s este al firmei «%s» — corectează numele sau CUI-ul în fișier"
                                       % (eticheta, cod, a["denumire"])))
            cheie = _cifre(cod) or cod
            if cheie in vazut:
                er.append(respinge("asociat", i, "identificator_dublat",
                                   "%s: %s %s apare și pe rândul %s — un asociat se trece o singură dată, cu cota lui totală"
                                   % (eticheta, "CNP-ul" if len(cod) == 13 and cod.isdigit() else "CUI-ul", cod, vazut[cheie])))
            else:
                vazut[cheie] = i
        else:
            er.append(respinge("asociat", i, "identificator_lipsa",
                               "%s: lipsește CNP-ul sau CUI-ul — fără el asociatul nu poate apărea în D205" % eticheta))
        try:
            cota = float(r.get("cota") or 0)
        except (TypeError, ValueError):
            cota = None
        if cota is None or cota < 0 or cota > 100:
            er.append(respinge("asociat", i, "cota_invalida",
                               "%s: cota %s%% nu e o cotă de participare (între 0 și 100)"
                               % (eticheta, ("%g" % cota).replace(".", ",") if cota is not None else r.get("cota"))))
    # [384] cotele se adună numai pe rândurile care intră (cele fără respingere pe rând)
    c = coerenta_cote(randuri or [], {e.get("rand") for e in er})
    if (randuri or []) and not c["coincide"]:
        # randul "-": afirmatia e despre SETUL de asociati, nu despre un rand anume - iar asta se
        # scrie, nu se ascunde alegand arbitrar primul rand.
        # [366] domeniul se scrie în cuvinte („toți asociații”), nu „-”: ecranul îl arată lângă mesaj (era „rând undefined”)
        er.append(respinge("asociati (toti)", "toți asociații", "cote_nu_dau_suta",
                           "cotele asociaților care intră însumează %s%%, nu 100%%" % ("%g" % c["total"]).replace(".", ",")))
    return er


def semnale_randuri(randuri, anaf=None):
    """PURĂ: [367] cu ANAF căzut (`anaf` None), asociații persoane juridice intră cu observația că CUI-ul nu s-a putut confrunta."""
    if anaf is not None:
        return []
    out = []
    for i, r in enumerate(randuri or [], start=2):
        cod = str(r.get("cnp") or "").strip()
        if cod and not (len(cod) == 13 and cod.isdigit()) and _valideaza_cui(cod)[0]:
            out.append(semnaleaza("asociat", _it.nr_rand(r, i), "anaf_neverificat",
                                  "%s: serviciul ANAF nu a răspuns — CUI-ul %s și numele nu s-au putut confrunta cu ANAF"
                                  % (str(r.get("nume") or "asociatul").strip(), cod)))
    return out


def eticheteaza(randuri, anaf=None):
    """[comanda Costin 8.2 pct.4] Starea fiecărui rând (ok / semnalat / respins) din ACEEAȘI verificare ca salvarea."""
    er, sem = verifica_randuri(randuri, anaf), semnale_randuri(randuri, anaf)
    for i, r in enumerate(randuri, start=2):
        n = _it.nr_rand(r, i)
        resp = [e["mesaj"] for e in er if e.get("rand") == n]
        obs = [e["mesaj"] for e in sem if e.get("rand") == n]
        r["stare"] = "respins" if resp else ("semnalat" if obs else "ok")
        r["motive"] = resp or obs
    return randuri


def arhiveaza_pentru_cesiune(conn, data_cesiune):
    """[lot 19 pct.4e; scoasă în funcție comună la lotul 10, deficiența 431] Structura CURENTĂ intră în `asociati_istoric`, valabilă
    până în ziua dinaintea cesiunii (Legea 31/1990 art.67 alin.(6): „Dividendele care se cuvin după data transmiterii acțiunilor
    aparțin cesionarului, în afară de cazul în care părțile au convenit altfel.”). Chemată de import (`importa`) și de cesiunea din
    Date firmă (`asociati_api.cesiune`) — o singură logică. Întoarce câte rânduri a arhivat; ValueError numit la refuz.

    GARANȚIA „istoric fără goluri” (pentru D205 / nota de dividende): fiecare structură arhivată e valabilă de la ziua de după
    precedenta până la `valabil_pana_la` ei, iar cea curentă de la ziua de după ultima. De aceea: (a) o cesiune vine după ultima
    înregistrată; (b) [lotul 10, 431] o cesiune cere o structură curentă (altfel intervalul de dinaintea ei ar rămâne fără
    asociați); (c) data cesiunii nu e în viitor."""
    import datetime as _dt
    try:
        dc = _dt.date.fromisoformat(str(data_cesiune)[:10])
    except ValueError:
        raise ValueError("data cesiunii %r nu e o dată (AAAA-LL-ZZ)." % data_cesiune)
    if dc > _dt.date.today():
        raise ValueError("data cesiunii (%s) e în viitor: o transmitere se înregistrează după ce a avut loc." % _data_ro(dc))
    pana = dc - _dt.timedelta(days=1)
    arhivati = 0
    with conn.cursor() as cur:
        cur.execute("SELECT max(valabil_pana_la) FROM asociati_istoric")
        ultima = cur.fetchone()[0]
        if ultima is not None and pana <= ultima:
            raise ValueError("data cesiunii (%s) trebuie să fie după ultima cesiune înregistrată (structura "
                             "anterioară e valabilă până la %s)." % (_data_ro(dc), _data_ro(ultima)))
        cur.execute("SELECT nume, cnp, cota FROM asociati WHERE cota > 0")
        vechi = cur.fetchall()
        if not vechi:
            raise ValueError("firma n-are înregistrată structura asociaților de dinaintea cesiunii — fără ea, perioada de "
                             "până la %s ar rămâne fără asociați (dividendele de atunci n-ar avea cui se împărți). "
                             "Înregistrează întâi structura de dinainte (ca o corectură, fără dată de cesiune), apoi cesiunea."
                             % _data_ro(pana))
        # [lotul 10, C73] data e verificată mai sus (după ultima cesiune); o violare a lui `asociati_istoric_uniq` aici vine de la o
        # cesiune înregistrată între timp de altă salvare, pe aceeași dată -> refuz numit, nu 500
        with _chei.refuza_dublura(cur, ("asociati_istoric_uniq",), lambda cur, e: _chei.CheieDublata(
                "În timp ce salvai, altă salvare a înregistrat deja o cesiune cu structura valabilă până la %s. Cesiunea ta nu s-a "
                "scris: reîncarcă pagina și verifică istoricul asociaților." % _data_ro(pana), valoare=_chei.valoarea(e))):
            for nume, cnp, cota in vechi:
                cur.execute("INSERT INTO asociati_istoric (cnp, nume, cota, valabil_pana_la) VALUES (%s,%s,%s,%s)",
                            (cnp or "", nume, cota, pana))
                arhivati += 1
    return arhivati


def _refuz_asociat_scris_intre_timp(cur, e):
    """[lotul 10, C73] Refuzul numit al CNP-ului / CUI-ului de asociat scris între timp de altă salvare."""
    return _chei.CheieDublata("În timp ce salvai, altă salvare a scris deja asociatul cu CNP-ul / CUI-ul %s. Din structura ta nu s-a "
                              "scris nimic: reîncarcă pagina, verifică asociații firmei și salvează din nou dacă e cazul."
                              % _chei.valoarea(e), valoare=_chei.valoarea(e))


def _procent(cota):
    """„60%”, „33,5%” — cota de participare cum o citește contabilul (fără zecimale inutile)."""
    return "%s%%" % ("%g" % float(cota or 0)).replace(".", ",")


def existent(conn):
    """[lotul 10, deficiența 426 — clasa] Structura asociaților deja salvată și ce se sprijină pe ea: {randuri, structura: [{nume, cnp,
    cota}], note_dividende: [{nota_id, eticheta, data, suma}]}. Notele de dividende care depind de structura de acum = distribuirile
    (credit 457; interimarele 463 = 456) de după ultima cesiune înregistrată (`asociati_istoric`): D205 și nota de dividende le împart
    după structura valabilă la data lor (`dividende_curs.structura_la`), deci după cea de acum — o corectură le schimbă împărțirea."""
    from core import eticheta_nota as _et
    with conn.cursor() as cur:
        cur.execute("SELECT nume, cnp, cota FROM asociati ORDER BY cota DESC, nume")
        structura = [{"nume": n, "cnp": c or "", "cota": float(q or 0)} for n, c, q in cur.fetchall()]
        cur.execute("SELECT max(valabil_pana_la) FROM asociati_istoric")
        ultima = cur.fetchone()[0]
        cur.execute("SELECT i.id, i.data, SUM(l.suma) FROM inregistrari i JOIN inregistrari_linii l ON l.inregistrare_id = i.id "
                    "WHERE (l.cont_credit LIKE '457%%' OR (l.cont_credit LIKE '456%%' AND l.cont_debit LIKE '463%%')) "
                    "AND (%s::date IS NULL OR i.data > %s::date) GROUP BY i.id, i.data ORDER BY i.data, i.id", (ultima, ultima))
        note = cur.fetchall()
        etichete = dict(_et.note(cur, "", [r[0] for r in note]))
    return {"randuri": len(structura), "structura": structura,
            "note_dividende": [{"nota_id": i, "eticheta": etichete.get(i) or "", "data": d.isoformat(), "suma": float(sm)}
                               for i, d, sm in note]}


def text_inlocuire(vechi, nou):
    """[426] „spune că există deja […], arată [ce e] vechi și nou […]; dacă există [date dependente], spune” — textul comun
    avertismentului din previzualizare și refuzului de la salvare: structura de acum și cea din fișier, cu cotele, și notele de dividende
    care se împart după structura de acum, numite. `nou` = rândurile care intră (`migrare_api.randuri_care_intra`)."""
    from core.pdf_util import bani as _bani
    from core.migrare_api import text_fisier_nou as _tfn

    def _str(lst):
        return ", ".join("%s %s" % (str(a.get("nume") or "").strip() or "—", _procent(a.get("cota"))) for a in lst) or "niciun asociat"
    t = ("Firma are deja %s: %s. Fișierul nou: %s. Fără dată de cesiune, salvarea e o corectură: structura de acum se înlocuiește "
         "și nu rămâne în istoric." % (_cate(vechi["randuri"], "asociat", "asociați"), _str(vechi["structura"]),
                                       _tfn(_str(nou), len(nou or []), getattr(nou, "citite", None))))   # [lotul 13, 583]
    note = vechi.get("note_dividende") or []
    if note:
        # [lotul 10] numeralul acordat prin `cate` (gardul `test_plural_dupa_numar`): „3 note de dividende se împart”, „20 de note …”
        t += (" %s după structura de acum: %s — D205 %s va împărți după cotele noi, iar înregistrarea din Registrul jurnal rămâne "
              "neschimbată." % (
                  "Nota de dividende se împarte" if len(note) == 1 else _cate(len(note), "notă de dividende", "note de dividende")
                  + " se împart",
                  "; ".join("nota %s (%s lei)" % (n["eticheta"], _bani(n["suma"])) for n in note[:6])
                  + (" și încă %d" % (len(note) - 6) if len(note) > 6 else ""), "o" if len(note) == 1 else "le"))
    t += (" Dacă asociații s-au schimbat printr-o cesiune, scrie data cesiunii: structura de acum rămâne în istoric pentru dividendele "
          "distribuite înainte.")
    return t


def importa(conn, randuri, data_cesiune=None, anaf=None, inlocuieste=False):
    """DELETE + INSERT per firma. Intoarce {importati, arhivati, inlocuit}.
    Ridica ValueError daca randurile nu pot intra (vezi verifica_randuri).
    [lotul 10, deficiența 426 — clasa] o structură existentă se înlocuiește FĂRĂ dată de cesiune (corectură) NUMAI cu `inlocuieste=True`
    (confirmarea de pe ecran); fără ea -> `migrare_api.InlocuireNeconfirmata` (409), cu structura veche și nouă și notele de dividende
    care depind de ea. Cu dată de cesiune structura veche nu se pierde (intră în istoric, `arhiveaza_pentru_cesiune`) — nu se cere.

    [lot 19 pct.4e, 02.10.2026] `data_cesiune` (opțional): data de la care NOUA structură e valabilă (transmiterea
    părților sociale). Structura curentă se ARHIVEAZĂ în `asociati_istoric`, valabilă până în ziua dinainte — ca D205 să
    împartă dividendele distribuite înainte după vechile cote: Legea 31/1990 art.67 alin.(6) „Dividendele care se cuvin
    după data transmiterii acțiunilor aparțin cesionarului”. Fără dată = corectură a structurii curente (ca înainte)."""
    # [probare invalid, 03.09.2026 — aceeasi clasa ca importul de istoric] UN IMPORT GOL
    # STERGEA TOT, IN TACERE. Lista vida trecea de verificare (n-are ce respinge), ajungea la
    # `DELETE FROM asociati` de mai jos, si raspundea ca un import reusit cu zero randuri. Un fisier gol,
    # unul cu numai antet (`extrage` intoarce [] pe el), sau un apel de API cu lista goala — toate
    # ajungeau acolo. *Un import care nu aduce nimic n-are voie sa stearga ce era acolo.*
    if not randuri:
        raise ValueError("nu ai trimis niciun rând. Importul ar fi șters lista de asociați a "
                         "firmei, cu cotele lor de participare, și n-ar fi pus nimic în loc. "
                         "Dacă chiar vrei să golești lista, e altă operațiune.")
    er = verifica_randuri(randuri, anaf)
    if er:
        raise ValueError("%s: %s. Asociații și cotele lor intră în D205 "
                         "(dividende) - cotele trebuie să dea exact 100%%."
                         % (_cate(len(er), "problemă", "probleme"), "; ".join(x["mesaj"] for x in er[:6])))
    vechi = existent(conn)
    from core import migrare_api as _mig
    # [426] poarta comună a clasei: corectura peste o structură existentă cere confirmarea, ÎNAINTEA oricărei scrieri
    _mig.cere_confirmarea_inlocuirii(vechi["randuri"] > 0 and not data_cesiune, inlocuieste, text_inlocuire(vechi, randuri), vechi,
                                     {"randuri": len(randuri)}, vechi["note_dividende"])
    arhivati = arhiveaza_pentru_cesiune(conn, data_cesiune) if data_cesiune else 0
    with conn.cursor() as cur:
        cur.execute("DELETE FROM asociati")
        n = 0
        # [lotul 10, C73] `verifica_randuri` a refuzat deja identificatorul dublat din rânduri; o violare a lui `asociati_cnp_uniq`
        # aici vine de la o altă salvare a structurii, terminată în timpul acesteia -> refuz numit, nu 500
        with _chei.refuza_dublura(cur, ("asociati_cnp_uniq",), _refuz_asociat_scris_intre_timp):
            for r in randuri:
                cur.execute(
                    "INSERT INTO asociati (nume, cnp, cota) VALUES (%s,%s,%s)",
                    (r["nume"], r.get("cnp", ""), r.get("cota", 0)))
                n += 1
    return {"importati": n, "arhivati": arhivati,
            "inlocuit": {"randuri": vechi["randuri"]} if vechi["randuri"] and not data_cesiune else None}

"""
core/asociati_import_api.py — import asociati (stratul 5 migrare) per firma.

Citeste un export (.xlsx/.csv) cu nume, CNP/CUI, cota %. Mapeaza flexibil coloanele.
Importa in tabelul existent `asociati` (DELETE + INSERT per firma).
Valideaza CNP daca are 13 cifre (cheie 279146358279); CUI persoana juridica acceptat fara validare.
Coerenta: suma cotelor ar trebui sa dea 100% (informativ, nu blocant).

"""
# [E2b, 15.09.2026] Tranzactia e a APELANTULUI: `db.get_conn` comite la iesirea din bloc, iar un
# `commit` aici ar taia tranzactia lui in doua (P4). Depozitul primeste conexiunea si scrie; nu
# deschide, nu comite.
from __future__ import annotations
import datetime
from core.identitate import valideaza_cui as _valideaza_cui  # [Q4] CUI juridic validat ca CUI, nu ca CNP

_CHEIE = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]


def valideaza_cnp(cnp):
    """(valid, motiv). Doar pentru coduri de 13 cifre (persoana fizica)."""
    cnp = str(cnp or "").strip()
    if len(cnp) != 13 or not cnp.isdigit():
        return False, "nu e CNP 13 cifre"
    if cnp[0] not in "123456789":
        return False, "prima cifra"
    s = int(cnp[0]); aa = int(cnp[1:3]); ll = int(cnp[3:5]); zz = int(cnp[5:7])
    sec = {1: 1900, 2: 1900, 3: 1800, 4: 1800, 5: 2000, 6: 2000,
           7: 2000, 8: 2000, 9: 1900}.get(s, 1900)
    an = sec + aa
    if not (1 <= ll <= 12):
        return False, "lună invalidă"
    try:
        datetime.date(an, ll, zz)
    except ValueError:
        return False, "dată invalidă"
    jj = int(cnp[7:9])
    if not (1 <= jj <= 52):
        return False, "județ invalid"
    suma = sum(int(cnp[i]) * _CHEIE[i] for i in range(12))
    ctrl = suma % 11
    ctrl = 1 if ctrl == 10 else ctrl
    if ctrl != int(cnp[12]):
        return False, "cifra de control"
    return True, "ok"


# [14.10.2026, comanda Costin „Importul din SAGA”, verbatim în DECIZII] Citirea fișierului și potrivirea coloanelor trec prin
# `core.import_tabel` (sursa unică: format, codare Windows-1250 recunoscută sau refuzată, antet sub titluri, coloane pe cuvinte
# întregi, ambiguitate refuzată numit) — nu mai e o copie a lui `_gaseste_col` aici.
from core import import_tabel as _it

CAMPURI = {
    "nume": ("nume asociat", "denumire asociat", "=nume", "nume*", "asociat*", "denumire*"),
    "cod": ("cnp cui", "cnp", "cui", "cif", "cod fiscal", "=cod"),
    "cota": ("cota*", "procent*", "participare", "%"),
}


from core.numere import numar as _numar  # sursa unica (15.07.2026); "%" tratat acolo
from core.migrare_api import respinge  # [P8/C] respingerea e o afirmatie, cu regula din nomenclator
from core.pdf_util import data_ro as _data_ro   # DS cap.4: data din text, canonic
from core.common import cate as _cate


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
    col = lambda camp, exclus=(): _it.coloana(antet, CAMPURI[camp], exclus=exclus, camp=camp)
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
        cod = cel(i_cod).upper().replace("RO", "").replace(" ", "")
        cota = _numar(cel(i_cota))
        if not nume_v:
            continue
        # persoana fizica daca pare CNP de 13 cifre, altfel juridica
        este_cnp = len(cod) == 13 and cod.isdigit()
        if este_cnp:
            valid, motiv = valideaza_cnp(cod)
            tip = "fizica"
        else:
            valid, motiv = True, "CUI"   # juridica, nu validam CNP
            tip = "juridica"
        out.append({"nume": nume_v, "cnp": cod, "cota": cota,
                    "tip": tip, "cnp_valid": valid, "cnp_motiv": motiv, "rand_fisier": nr})
    return out


def coerenta_cote(randuri):
    """{total, coincide} — suma cotelor vs 100%."""
    total = round(sum(r.get("cota", 0) for r in randuri), 2)  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
    return {"total": total, "coincide": abs(total - 100.0) < 0.01}


def rezumat(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('asociati')")
        if cur.fetchone()[0] is None:
            return {"are_asociati": False, "randuri": 0, "total_cota": 0}
        cur.execute("SELECT count(*), COALESCE(sum(cota),0) FROM asociati")
        n, tc = cur.fetchone()
    return {"are_asociati": n > 0, "randuri": n, "total_cota": float(tc)}


def verifica_randuri(randuri):
    """PURA: [{rand, motiv, mesaj}]. CNP/CUI valid + cotele insumeaza exact 100%.

    coerenta_cote() exista de la inceput, dar importa() n-o chema: cotele de 115% au
    intrat, iar migrarea a marcat stratul "gata" verde. D205 nu se poate genera cu ele
    (dovedit 15.07.2026, prin migrare reala).
    """
    er = []
    for i, r in enumerate(randuri or [], start=2):   # antetul e randul 1
        i = _it.nr_rand(r, i)
        nume = str(r.get("nume") or "?").strip()
        cod = str(r.get("cnp") or "").strip()
        # [Q4] ramifica fizic/juridic ca extrage(): CUI de juridica se valideaza ca CUI (cifra de
        # control), NU ca CNP de 13 cifre. Altfel asociatul-firma acceptat la preview era respins aici.
        if cod:
            este_cnp = len(cod) == 13 and cod.isdigit()
            ok, motiv = valideaza_cnp(cod) if este_cnp else _valideaza_cui(cod)
            if not ok:
                er.append(respinge(
                    "asociat", i, "cnp_invalid" if este_cnp else "cui_invalid",
                    "%s: %s invalid (%s)" % (nume, "CNP" if este_cnp else "CUI", motiv)))
    c = coerenta_cote(randuri or [])
    if (randuri or []) and not c["coincide"]:
        # randul "-": afirmatia e despre SETUL de asociati, nu despre un rand anume - iar asta se
        # scrie, nu se ascunde alegand arbitrar primul rand.
        er.append(respinge("asociati (toti)", "-", "cote_nu_dau_suta",
                           "cotele asociaților însumează %s%%, nu 100%%" % c["total"]))
    return er


def importa(conn, randuri, data_cesiune=None):
    """DELETE + INSERT per firma. Intoarce {importati, arhivati}.
    Ridica ValueError daca randurile nu pot intra (vezi verifica_randuri).

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
    er = verifica_randuri(randuri)
    if er:
        raise ValueError("%s: %s. Asociații și cotele lor intră în D205 "
                         "(dividende) - cotele trebuie să dea exact 100%%."
                         % (_cate(len(er), "problemă", "probleme"), "; ".join(x["mesaj"] for x in er[:6])))
    arhivati = 0
    if data_cesiune:
        import datetime as _dt
        try:
            dc = _dt.date.fromisoformat(str(data_cesiune)[:10])
        except ValueError:
            raise ValueError("data cesiunii %r nu e o dată (AAAA-LL-ZZ)." % data_cesiune)
        if dc > _dt.date.today():
            raise ValueError("data cesiunii (%s) e în viitor: o transmitere se înregistrează după ce a avut loc." % _data_ro(dc))
        pana = dc - _dt.timedelta(days=1)
        with conn.cursor() as cur:
            cur.execute("SELECT max(valabil_pana_la) FROM asociati_istoric")
            ultima = cur.fetchone()[0]
            if ultima is not None and pana <= ultima:
                raise ValueError("data cesiunii (%s) trebuie să fie după ultima cesiune înregistrată (structura "
                                 "anterioară e valabilă până la %s)." % (_data_ro(dc), _data_ro(ultima)))
            cur.execute("SELECT nume, cnp, cota FROM asociati WHERE cota > 0")
            for nume, cnp, cota in cur.fetchall():
                cur.execute("INSERT INTO asociati_istoric (cnp, nume, cota, valabil_pana_la) VALUES (%s,%s,%s,%s)",
                            (cnp or "", nume, cota, pana))
                arhivati += 1
    with conn.cursor() as cur:
        cur.execute("DELETE FROM asociati")
        n = 0
        for r in randuri:
            cur.execute(
                "INSERT INTO asociati (nume, cnp, cota) VALUES (%s,%s,%s)",
                (r["nume"], r.get("cnp", ""), r.get("cota", 0)))
            n += 1
    return {"importati": n, "arhivati": arhivati}

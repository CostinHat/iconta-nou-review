# -*- coding: utf-8 -*-
"""REPOSITORY — compensarea creanțelor și datoriilor reciproce cu același partener (lotul 10, deficiența 428).

Deciziile Costin 20.10.2026 (verbatim în DECIZII „Lotul 10: deciziile lui Costin la întrebările din lot”): „Construiesc acum” — tabelă de
compensări (factura emisă ↔ factura primită, suma, data) și ecran; fiecare compensare stinge cele două facturi și mută TVA-ul prin același
punct ca banca și casa. Comanda 10.1 (deficiența 428): „fiecare încasare (bancă, casă, compensare) legată de factură mută automat partea
încasată în 4427”.

TEMEIUL (citit verbatim din `anaf_surse/`):
  * Codul civil art.1616 (`cod_civil_287_2009_art_1616_1623_compensare.txt`): „Datoriile reciproce se sting prin compensaţie până la
    concurenţa celei mai mici dintre ele.” Art.1617 alin.(1): „Compensaţia operează de plin drept de îndată ce există două datorii certe,
    lichide şi exigibile, oricare ar fi izvorul lor, şi care au ca obiect o sumă de bani [...] de aceeaşi natură.”
  * HG 685/1999, anexa 2, art.5 (`hg_685_1999_norme_compensare_creante_datorii.txt`): „Data efectuarii stingerii datoriilor si a creantelor
    este cea a ordinului de compensare”; art.11: „Ordinul de compensare [...] reprezinta document justificativ de inregistrare in
    contabilitate a stingerii creantelor si a datoriilor care au facut obiectul compensarii. Ordinul de compensare se anexeaza la nota
    contabila.”; art.11: „Ordinele de compensare au regim special, sunt numerotate din tipografie” — numărul îl scrie contabilul, de pe
    ordin; aplicația nu-l inventează.
  * OMFP 1802/2014 pct.56 alin.(3) (`omfp_1802_2014_reglementari_consolidat.txt`): „Eventualele compensări între creanțe și datorii față
    de aceeași entitate efectuate cu respectarea prevederilor legale pot fi înregistrate numai după contabilizarea creanțelor și
    veniturilor, respectiv a datoriilor și cheltuielilor corespunzătoare.” Nota: 401 „Furnizori” = 4111 „Clienți”, cu partenerul pe rând.
  * HG 1/2016 pct.26 alin.(7) (`hg_1_2016_norme_cod_fiscal.txt`): „În sensul art. 282 alin. (3) din Codul fiscal, prin încasarea
    contravalorii livrării de bunuri sau a prestării de servicii se înțelege orice modalitate [...], precum plata în bani, plata în natură,
    compensarea”; alin.(9): „În cazul compensării datoriilor aferente unor facturi [...] se consideră că furnizorul/prestatorul a încasat,
    respectiv beneficiarul a plătit contravaloarea bunurilor/serviciilor, la data la care se sting total sau parțial datoriile”.
  * CF art.282 alin.(3), (8): exigibilitatea la încasare; „fiecare încasare totală sau parțială se consideră că include și taxa aferentă”
    — partea compensată mută TVA-ul prin `tva_incasare.linii_la_incasare` (4428 = 4427 pe emisă, 4426 = 4428 pe primită, fiecare după
    regimul ei la data ei).

UN RÂND `compensari` = o pereche (o factură emisă stinsă cu o factură primită, aceeași sumă), cu NOTA EI (o notă pe pereche, ca la bancă:
o notă pe factură alocată) — altfel, pe o notă cu două facturi emise, liniile 4111 și 4428 = 4427 nu s-ar mai putea împărți pe facturi.
Nota NU poartă `factura_id` (o notă are o singură cheie, compensarea stinge două facturi): legătura e rândul `compensari`, iar cititorii
plăților unei facturi o citesc prin `legaturi()` / `nota_de_compensare()` — sursa unică a lui „notele care sting factura”.

FIECARE FUNCȚIE PRIMEȘTE CURSORUL / CONEXIUNEA APELANTULUI. Nu deschide conexiuni, nu comite.
"""
import re
from decimal import Decimal, ROUND_HALF_UP

from psycopg2.extras import RealDictCursor

from core import cui_forma as _forma_cui

_BAN = Decimal("0.01")

#: nota compensării — OMFP 1802/2014 pct.56 alin.(3): datoria față de furnizor (401) stinsă cu creanța asupra clientului (4111)
LINIE_COMPENSARE = ("401", "4111")

COD_DATE = "COMPENSARE_DATE"
COD_STARE = "COMPENSARE_STARE"

#: regula care oprește o factură de la compensare (`afirmatie["regula"]` în `facturi_deschise`) — sursa unică, citită și de teste.
#: [lotul 11, decizia Costin din 10.3, verbatim în DECIZII „Comanda 10.3”: „Compensarea în valută rămâne refuzată, cu motiv.”] Motivul:
#: stingerea unei creanțe / datorii în valută la data ordinului cere și diferența de curs față de cursul din evidență — OMFP 1802/2014
#: pct.322 alin.(1): „Diferențele de curs valutar care apar cu ocazia decontării creanțelor și datoriilor în valută la cursuri diferite față
#: de cele la care au fost înregistrate inițial pe parcursul lunii sau față de cele la care sunt înregistrate în contabilitate trebuie
#: recunoscute în luna în care apar, ca venituri sau cheltuieli din diferențe de curs valutar.” Aplicația n-o calculează la compensare,
#: deci nu scrie o notă fără ea. Același refuz pe toate drumurile: propunerea (`facturi_deschise`, factura „nu intră”, cu motivul pe
#: ecran), verificarea cererii (`verifica`, API-ul și butonul) și deci ordinul (generat numai din perechile verificate).
REGULA_VALUTA = "compensarea se face în lei (diferența de curs la data ordinului nu e tratată de aplicație)"
TEMEI_VALUTA = "OMFP 1802/2014 pct.322 alin.(1)"
REGULA_CONTARE = "OMFP 1802/2014 pct.56 alin.(3)"
REGULA_PARTENER = "datoriile reciproce se compensează cu același partener, identificat prin codul fiscal"


class RefuzCompensare(Exception):
    """Refuz declarat, cu motivul ca date (`cod`, `mesaj`, `detalii`): `COMPENSARE_DATE` (cererea nu e bună) / `COMPENSARE_STARE`
    (facturile nu sunt în starea care permite compensarea). `detalii` = ce a oprit cererea (factura, restul, data), ca date — ca la
    `contare_facturi.RefuzContare`: cine distinge refuzurile căutând un șir în mesaj ar păzi formularea, nu comportamentul."""

    def __init__(self, cod, mesaj, detalii=None):
        super().__init__(mesaj)
        self.cod, self.mesaj, self.detalii = cod, mesaj, detalii or {}


# ══════════════════════════════════════════════════════════════════ LEGĂTURA NOTĂ — FACTURĂ (sursa unică)
def legaturi(p=""):
    """Tabelul derivat (inregistrare_id, factura_id): notele care sting o factură — cheia notei (`inregistrari.factura_id`: banca, casa,
    chitanța, contarea) și compensările (`compensari`: nota unei compensări stinge AMBELE facturi). `p` = prefixul de schemă ("" pe
    search_path, `"tenant_x".` / `tenant_x.`). UNION: o notă legată de o factură pe ambele căi se numără o dată."""
    return ("(SELECT id AS inregistrare_id, factura_id FROM {p}inregistrari WHERE factura_id IS NOT NULL "
            "UNION SELECT inregistrare_id, factura_emisa_id FROM {p}compensari WHERE inregistrare_id IS NOT NULL "
            "UNION SELECT inregistrare_id, factura_primita_id FROM {p}compensari WHERE inregistrare_id IS NOT NULL)").format(p=p)


def nota_de_compensare(alias_i, expr_factura, p=""):
    """Condiția SQL „nota `alias_i` e compensarea care stinge factura `expr_factura`” — pentru cititorii care leagă nota de factură prin
    `i.factura_id = f.id` și adaugă compensarea cu OR."""
    return ("EXISTS (SELECT 1 FROM {p}compensari cz WHERE cz.inregistrare_id = {i}.id "
            "AND {f} IN (cz.factura_emisa_id, cz.factura_primita_id))").format(p=p, i=alias_i, f=expr_factura)


def nota_stinge_factura(alias_i, expr_factura, p=""):
    """[lotul 12, C153] Condiția SQL unică „nota `alias_i` stinge factura `expr_factura`”: nota legată de factură (`factura_id`), nota unei
    chitanțe de dinainte de 278 (fără `factura_id`, cu chitanța neanulată a facturii — nota validată nu se mai modifică, `regula_nota`) și
    compensarea (`nota_de_compensare`, 428). Până azi o aveau întreagă numai reconcilierea (`reconciliere_api.facturi_deschise`) și
    Registrul jurnal; rapoartele comerciale (fișa partenerului, durata medie de încasare) n-o vedeau pe a doua, deci o factură încasată cu
    chitanță veche apărea nedecontată."""
    return ("({i}.factura_id = {f} OR ({i}.factura_id IS NULL AND EXISTS (SELECT 1 FROM {p}chitante cc WHERE cc.inregistrare_id = {i}.id "
            "AND cc.factura_id = {f} AND NOT cc.anulata)) OR {cz})").format(i=alias_i, f=expr_factura, p=p,
                                                                          cz=nota_de_compensare(alias_i, expr_factura, p))


def cui_partener(cui):
    """CUI-ul partenerului în forma păstrată (`cui_forma.stocare`: fără spații, fără „RO” în fața cifrelor; codul de TVA al unui
    partener din alt stat rămâne cu prefixul lui) — același partener pe factura emisă și pe cea primită; "" fără cod. [lotul 11,
    decizia Costin 10.3 pct.4, clasa „normalizare locală a CUI”] Înainte: o a doua normalizare, scrisă aici, paralelă cu `stocare`."""
    return _forma_cui.stocare(cui) or ""


# ══════════════════════════════════════════════════════════════════ FACTURILE COMPENSABILE
def _detalii(cur, schema, ids):
    cur.execute(f"SELECT id, directie, COALESCE(tip, 'factura') AS tip, serie, numar, data_emitere, COALESCE(moneda, 'RON') AS moneda, "
                f"tert_nume, tert_cui, COALESCE(total_lei, total) AS total_lei FROM {schema}.facturi WHERE id = ANY(%s)", (list(ids),))
    return {r["id"]: dict(r) for r in cur.fetchall()}


def facturi_deschise(conn, schema):
    """Facturile emise neîncasate și primite neplătite, cu restul lor (soldul reconcilierii, `reconciliere_api.facturi_deschise` — același
    pe care îl alocă banca și casa; numără și compensările), partenerul, contarea și ce le oprește de la compensare (`afirmatie`: o
    afirmație tipată `neconformitate` — factura, regula și motivul —, decizia Costin 21.08.2026; None = compensabilă). Proformele /
    avizele nu sunt creanțe sau datorii (nu se listează)."""
    from core import afirmatii as _af, contare_facturi as _cf, pdf_util as _pu, reconciliere_api as _rec, tva_incasare as _tvi
    deschise = {f["id"]: f for f in _rec.facturi_deschise(conn, schema)}
    if not deschise:
        return []
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        det = _detalii(cur, schema, deschise)
        contare = _cf.stare_contare(cur, schema, list(deschise))
        out = []
        for fid, f in sorted(deschise.items(), key=lambda kv: (kv[1]["data_emitere"], kv[0])):
            d = det[fid]
            if d["tip"] != "factura":
                continue
            motiv = regula = None
            if d["moneda"] != "RON":
                motiv = ("în %s: compensarea în valută nu se face în aplicație — stingerea cere și diferența de curs la data ordinului "
                         "(%s), pe care aplicația n-o calculează; înregistreaz-o din Registrul jurnal, cu diferența pe 665 / 765"
                         % (d["moneda"], TEMEI_VALUTA))
                regula = REGULA_VALUTA
            elif not contare.get(fid):
                motiv = ("nu e contabilizată: compensarea se înregistrează numai după contabilizarea creanței, respectiv a datoriei "
                         "(OMFP 1802/2014 pct.56 alin.(3))")
                regula = REGULA_CONTARE
            elif not cui_partener(d["tert_cui"]):
                motiv = "factura n-are codul fiscal al partenerului"
                regula = REGULA_PARTENER
            document = _pu.serie_nr(d["serie"], d["numar"])   # [lotul 11, 443] afișare: „F6 nr. 1”, nu „F61” (nu e identificator)
            out.append({"id": fid, "directie": d["directie"], "document": document,
                        "data": str(d["data_emitere"])[:10], "partener": d["tert_nume"], "cui": cui_partener(d["tert_cui"]),
                        "total": str(Decimal(str(d["total_lei"] or 0)).quantize(_BAN, rounding=ROUND_HALF_UP)),
                        "rest": str(Decimal(str(f["sold"])).quantize(_BAN, rounding=ROUND_HALF_UP)), "moneda": d["moneda"],
                        "data_contare": (contare[fid] or {}).get("data") if contare.get(fid) else None,
                        "tva_la_incasare": _tvi.regim(cur, schema, fid) == _tvi.REGIM_INCASARE,
                        "afirmatie": _af.afirmatie("neconformitate", "compensare", motiv, unde="factura %s" % document,
                                                   regula=regula) if motiv else None})
    return out


def perechi_propuse(emise, primite):
    """Perechile propuse ale unui partener: emisele și primitele, fiecare în ordinea datei, se sting una pe alta cu cât rămâne din cea
    mai mică (Codul civil art.1616: „până la concurenţa celei mai mici dintre ele”). Pur; `rest` în lei, ca text sau Decimal."""
    re_ = [[f["id"], Decimal(str(f["rest"]))] for f in emise]
    rp = [[f["id"], Decimal(str(f["rest"]))] for f in primite]
    out, i, j = [], 0, 0
    while i < len(re_) and j < len(rp):
        s = min(re_[i][1], rp[j][1])
        if s > 0:
            out.append({"factura_emisa_id": re_[i][0], "factura_primita_id": rp[j][0], "suma": str(s.quantize(_BAN, rounding=ROUND_HALF_UP))})
        re_[i][1] -= s
        rp[j][1] -= s
        if re_[i][1] <= 0:
            i += 1
        if rp[j][1] <= 0:
            j += 1
    return out


def propunere(conn, schema):
    """Partenerii cu facturi emise neîncasate ȘI primite neplătite, cu facturile lor și perechile propuse (numai din facturile
    compensabile — fără `afirmatie`). {parteneri: [{cui, partener, emise, primite, perechi, total}]}."""
    pe = {}
    for f in facturi_deschise(conn, schema):
        if not f["cui"]:
            continue
        p = pe.setdefault(f["cui"], {"cui": f["cui"], "partener": f["partener"], "emise": [], "primite": []})
        p["emise" if f["directie"] == "emisa" else "primite"].append(f)
    out = []
    for p in sorted(pe.values(), key=lambda x: (x["partener"] or "", x["cui"])):
        if not (p["emise"] and p["primite"]):
            continue
        p["perechi"] = perechi_propuse([f for f in p["emise"] if not f["afirmatie"]], [f for f in p["primite"] if not f["afirmatie"]])
        p["total"] = str(sum((Decimal(x["suma"]) for x in p["perechi"]), Decimal(0)).quantize(_BAN, rounding=ROUND_HALF_UP))
        out.append(p)
    return {"parteneri": out}


# ══════════════════════════════════════════════════════════════════ VERIFICAREA ȘI SCRIEREA
#: [lotul 13, deficiența 655] suma cererii, în forma canonică a ecranului („1210.50”, câmpul numeric comun) sau cu virgulă la zecimale
#: („1210,50”): cel mult două zecimale. Un text cu punct de mii („1.210” = o mie două sute zece) nu e o sumă în lei și bani — înainte
#: `Decimal("1.210")` era 1,21 și trecea de verificarea zecimalelor (1,210 == 1,21); acum se refuză numit, nu se citește greșit tăcut.
_RE_SUMA = re.compile(r"^\d+(?:[.,]\d{1,2})?$")


def _suma(v):
    t = str(v).replace(" ", "")
    if not _RE_SUMA.match(t):
        raise RefuzCompensare(COD_DATE, "Suma de compensat se scrie în lei și bani, cu cel mult două zecimale (ex. 1210,50).")
    s = Decimal(t.replace(",", "."))
    if s <= 0 or s != s.quantize(_BAN, rounding=ROUND_HALF_UP):
        raise RefuzCompensare(COD_DATE, "Suma de compensat trebuie să fie mai mare decât zero, în lei și bani (cel mult două zecimale).")
    return s


def verifica(conn, schema, data, perechi):
    """Perechile cererii, verificate pe facturile de azi: fiecare pereche = o emisă și o primită compensabile ale ACELUIAȘI partener (toate
    perechile, al aceluiași), suma > 0 și, cumulat pe factură, cel mult restul ei (Codul civil art.1616), data ordinului nu înaintea
    facturilor și nici a contării lor (OMFP 1802/2014 pct.56 alin.(3)). Întoarce [{emisa, primita, suma}] (facturile ca în
    `facturi_deschise`) sau ridică `RefuzCompensare` cu motivul."""
    if not perechi:
        raise RefuzCompensare(COD_DATE, "Alege cel puțin o pereche de facturi de compensat.")
    deschise = {f["id"]: f for f in facturi_deschise(conn, schema)}
    ramas, out, partener = {}, [], None
    for p in perechi:
        try:
            ide, idp = int(p.get("factura_emisa_id")), int(p.get("factura_primita_id"))
        except (TypeError, ValueError, AttributeError):
            raise RefuzCompensare(COD_DATE, "Fiecare pereche are o factură emisă și una primită.")
        s = _suma(p.get("suma"))
        e, f = deschise.get(ide), deschise.get(idp)
        if not e or e["directie"] != "emisa":
            raise RefuzCompensare(COD_STARE, "Factura emisă aleasă nu mai are nimic de încasat (sau nu e o factură emisă).")
        if not f or f["directie"] != "primita":
            raise RefuzCompensare(COD_STARE, "Factura primită aleasă nu mai are nimic de plătit (sau nu e o factură primită).")
        for x in (e, f):
            if x["afirmatie"]:
                raise RefuzCompensare(COD_STARE, "Factura %s nu se poate compensa: %s." % (x["document"], x["afirmatie"]["motiv"]),
                                      {"factura": x["id"], "regula": x["afirmatie"]["regula"]})
        if e["cui"] != f["cui"]:
            raise RefuzCompensare(COD_STARE, "Facturile %s și %s au parteneri diferiți: se compensează numai datoriile reciproce cu "
                                             "același partener (Codul civil art.1616)." % (e["document"], f["document"]),
                                  {"facturi": [e["id"], f["id"]], "parteneri": [e["cui"], f["cui"]]})
        if partener and e["cui"] != partener:
            raise RefuzCompensare(COD_DATE, "Un ordin de compensare privește un singur partener: generează câte unul pentru fiecare.")
        partener = e["cui"]
        for x in (e, f):
            if str(data) < x["data"]:
                raise RefuzCompensare(COD_DATE, "Data ordinului (%s) e înaintea facturii %s (%s): datoria nu exista încă." % (
                    _ro(data), x["document"], _ro(x["data"])), {"factura": x["id"], "data_factura": x["data"]})
            if x["data_contare"] and str(data) < str(x["data_contare"])[:10]:
                raise RefuzCompensare(COD_DATE, "Data ordinului (%s) e înaintea contării facturii %s (%s): compensarea se înregistrează "
                                                "numai după contabilizare (OMFP 1802/2014 pct.56 alin.(3))." % (
                                                    _ro(data), x["document"], _ro(x["data_contare"])),
                                      {"factura": x["id"], "data_contare": str(x["data_contare"])[:10]})
            rest = ramas.setdefault(x["id"], Decimal(x["rest"]))   # o singură valoare: în text și în `detalii`
            if s > rest:
                raise RefuzCompensare(COD_DATE, "Pe factura %s rămân %s lei de %s; nu se pot compensa %s lei." % (
                    x["document"], _bani(rest), "încasat" if x["directie"] == "emisa" else "plătit", _bani(s)),
                    {"factura": x["id"], "ramas": rest, "suma": s})
        for x in (e, f):
            ramas[x["id"]] -= s
        out.append({"emisa": e, "primita": f, "suma": s})
    return out


def _ro(d):
    from core import pdf_util as _pu
    return _pu.data_ro(str(d)[:10])


def _bani(v):
    from core import pdf_util as _pu
    return _pu.bani(v)


def document(numar, data):
    """„Ordin de compensare nr <număr> din <zz.ll.aaaa>” — documentul justificativ al notei (HG 685/1999 anexa 2 art.11)."""
    from core import jurnal_api as _j
    return _j.eticheta_document("Ordin de compensare", numar, data)


def scrie(cur, schema, data, document_ref, pereche):
    """O pereche: nota ciornă (R36) cu documentul ordinului — 401 = 4111 pe suma compensată, cu partenerul pe rând —, rândul
    `compensari` legat de ea și liniile TVA la încasare ale AMBELOR facturi, prin punctul unic (`tva_incasare.linii_la_incasare`, ca banca
    și casa): partea încasată a celei emise 4428 = 4427 (CF art.282 alin.(3), (8)), partea plătită a celei primite 4426 = 4428 (CF art.297
    alin.(2)-(3)), fiecare după regimul ei la data ei. Întoarce (id-ul notei, liniile ei)."""
    from core import repo_contabilitate as _rc, tva_incasare as _tvi
    e, f, s = pereche["emisa"], pereche["primita"], pereche["suma"]
    descr = ("Compensare %s (emisă) cu %s (primită) — %s" % (e["document"], f["document"], e["partener"] or e["cui"]))[:200]
    iid = _rc.nota_operatiune_ciorna(cur, schema, data, descr, document_ref=document_ref)
    iid = iid["id"] if isinstance(iid, dict) else iid[0]
    linii = [LINIE_COMPENSARE + (s,)]
    _rc.adauga_linie_partener(cur, schema, iid, LINIE_COMPENSARE[0], LINIE_COMPENSARE[1], s, e["cui"], e["partener"])
    cur.execute(f"INSERT INTO {schema}.compensari (data, factura_emisa_id, factura_primita_id, suma, inregistrare_id, document_ref) "
                f"VALUES (%s,%s,%s,%s,%s,%s)", (data, e["id"], f["id"], s, iid, document_ref))
    for fid in (e["id"], f["id"]):
        for d, c, v in _tvi.linii_la_incasare(cur, schema, fid, s):
            _rc.adauga_linie(cur, schema, iid, d, c, v)
            linii.append((d, c, v))
    return iid, linii


def ale_facturii(cur, schema, factura_id):
    """Compensările în care intră factura: [(id, data, document_ref)]."""
    p = ("%s." % schema) if schema else ""   # schema goală = search_path pus de `db.get_conn(schema)` (ștergerea facturii)
    cur.execute(f"SELECT id, data, document_ref FROM {p}compensari WHERE %s IN (factura_emisa_id, factura_primita_id) ORDER BY id",
                (int(factura_id),))
    return [tuple(r.values()) if isinstance(r, dict) else tuple(r) for r in cur.fetchall()]

# -*- coding: utf-8 -*-
"""core/rectificativa.py — [lotul 11, deficiența C77] DECLARAȚIA DEJA DEPUSĂ PE PERIOADĂ: inițială sau rectificativă.

CE ERA GREȘIT. Generatoarele scriau `d_rec="0"` constant (D101, D112, D205, D301, D390) sau luau `d_rec` numai din bifa
formularului (D216, D395, D397, … — cu `0` implicit). A doua depunere pe aceeași perioadă — coada îi dă `nr_depunere` = MAX + 1
(`coada_api.marcheaza_depusa`) — pleca la ANAF marcată „inițială”, iar ecranul nu spunea nimic.

TEMEIUL GENERAL, CPF art.105 alin.(1)-(3), textul (anaf_surse/legea_207_2015_consolidat.txt):
  „(1) Declarația de impunere poate fi corectată de către contribuabil/plătitor, pe perioada termenului de prescripție a dreptului
   de a stabili creanțe fiscale. […] (2) Declarația informativă poate fi corectată de către contribuabil/plătitor indiferent de
   perioada la care se referă. (3) Declarațiile prevăzute la alin. (1) și (2) pot fi corectate prin depunerea unei declarații
   rectificative.”
  „(4) În cazul taxei pe valoarea adăugată, corectarea erorilor din deconturile de taxă se realizează potrivit prevederilor Codului
   fiscal.” (D300 — nu are rectificativă; vezi `TEMEI_PE_TIP`.)
Forma rectificativei e a fiecărui formular (`TEMEI_PE_TIP`, citat din instrucțiunile / structura lui).

CUM ȘTIE APLICAȚIA CĂ O DECLARAȚIE E DEJA DEPUSĂ: `public.declaratii_depuse` — orice rând pe (firmă, an, luna, tip), oricare ar fi
sursa: `iconta` (depusă prin coadă), `extern` („depusă în afara iConta.eu”, cu data de pe recipisă), `contabil_anterior` (marcată la
preluare, data necunoscută), `migrare` / importul istoric. `luna` e luna perioadei: luna, ultima lună a trimestrului (trim × 3) sau 12
la anuale (`coada_api.perioada_din_payload`, același calcul).

UNDE SE PUNE `d_rec`: în GENERATOR (care știe forma formularului), la generare — XML-ul intră în coadă gata făcut. La depunere,
`coada_api.marcheaza_depusa` refuză declarația generată înaintea unei depuneri apărute între timp pe aceeași perioadă
(`refuz_la_depunere`): ar pleca a doua oară ca inițială.
"""
from __future__ import annotations

import re
from collections import namedtuple

from core.erori import RefuzGenerare   # modul fără importuri: nu face ciclu

#: Starea rectificativei pentru o generare: `d_rec` 0/1, `mentiune` (textul de pe ecran, sau None la inițială), `nr` = nr_depunere
#: al depunerii curente pe care s-a sprijinit generarea (None = nicio depunere), `dep` = depunerea curentă (dict) sau None.
Stare = namedtuple("Stare", "d_rec mentiune nr dep")

#: Temeiul formei rectificativei, pe formular (textul citat; sursa în paranteză).
TEMEI_PE_TIP = {
    "d101": ("OPANAF 206/2025 anexa nr.2 cap.I pct.3: „În cazul în care plătitorul corectează declaraţia depusă, declaraţia "
             "rectificativă se întocmeşte pe acelaşi model de formular, înscriind \"X\" în spaţiul special prevăzut în acest scop.” "
             "(structura D101: „d_rec =(0,1,2) 0-initiala, 1-rectificativa”)"),
    "d112": ("OPANAF 605/2026 anexa nr.2 pct.2.3: „Declaraţia rectificativă se întocmeşte pe acelaşi model de formular ca şi "
             "declaraţia care se corectează, bifându-se cu X căsuţa aflată pe prima pagină a formularului.” pct.2.4: „Declaraţia "
             "rectificativă se completează integral, înscriindu-se toate datele şi informaţiile prevăzute de formular, inclusiv cele "
             "care nu diferă faţă de declaraţia iniţială.” (structura D112: „d_rec=1 pt. tip_rec>0 sau null”)"),
    "d205": ("OPANAF 179/2022 anexa nr.3 (instrucțiunile formularului 205) pct.I.5.2: „Declaraţia rectificativă se întocmeşte pe "
             "tipuri de venit şi va cuprinde numai poziţiile corectate, declarate eronat în declaraţia iniţială, sau poziţiile care, în "
             "mod eronat, nu au fost cuprinse în declaraţia iniţială.” pct.I.5.3 lit.a): „se vor înscrie datele de identificare ale "
             "beneficiarului de venit din declaraţia iniţială, iar la col. 7 - 10 se va înscrie cifra \"0\" (zero)”"),
    "d301": ("OPANAF 592/2016 anexa nr.2 cap.III: „Declaraţia depusă iniţial se rectifică prin depunerea unei noi declaraţii, pe "
             "acelaşi format, bifând căsuţa corespunzătoare de pe formular.”"),
    "d390": ("OPANAF 705/2020 anexa nr.2 cap.I: „Declaraţia depusă iniţial se rectifică prin depunerea unei noi declaraţii, pe acelaşi "
             "format, bifând căsuţa corespunzătoare de pe formular. În declaraţia rectificativă se rectifică tranzacţii declarate în "
             "orice perioadă de raportare anterioară şi se completează toate rubricile formularului cu datele valabile la momentul "
             "declarării, indiferent dacă acestea au mai fost declarate.”"),
    "d406": ("OPANAF 1783/2021 anexa nr.3 pct.18: „Prima Declaraţie informativă D406 validată, depusă pentru o lună sau un trimestru "
             "de către un contribuabil/plătitor este considerată declaraţie iniţială. Declaraţiile ulterioare depuse pentru aceeaşi "
             "perioadă (lună/trimestru) sunt automat considerate declaraţii rectificative.” pct.21: „Declaraţiile rectificative […] "
             "trebuie să cuprindă toate informaţiile din declaraţia iniţială, plus cele asupra cărora s-au efectuat corecţii.”"),
    "d394": ("OPANAF 2194/2025 anexa nr.2 pct.3: „În cazul în care, după depunerea declaraţiei, persoana impozabilă constată existenţa "
             "unor omisiuni/erori în datele declarate, aceasta trebuie să depună o nouă declaraţie corect completată […], declaraţie "
             "care înlocuieşte declaraţia informativă depusă iniţial.”"),
    "d100": ("OPANAF 587/2016 anexa nr.4 (instrucțiunile formularului 100): „Corectarea obligațiilor declarate eronat în formular se "
             "face prin depunerea formularului 710 «Declarație rectificativă», cod 14.13.01.00/r, conform procedurii legale în vigoare.”"
             " Anexa nr.5 cap.I: „Declarația rectificativă se utilizează pentru corectarea impozitelor și taxelor […] declarate în "
             "formularul 100”"),
    "d300": ("CPF art.105 alin.(4): „În cazul taxei pe valoarea adăugată, corectarea erorilor din deconturile de taxă se realizează "
             "potrivit prevederilor Codului fiscal.”; OPANAF 174/2026 anexa nr.2: „Nu se admit întocmirea şi depunerea de deconturi "
             "rectificative pentru corectarea datelor din deconturile anterioare.”"),
    "d216": ("Structura XML D216 v1.0.0 (static.anaf.ro, structuraXML_D216_v1.0.0_30082024.pdf) rândul 1.1: „index_corectie — "
             "Indexul de depunere al declaratiei initiale care se coreteaza — IF d_rec eq. 1 THEN index MUST EXISTS”; DUK D216 v0: "
             "„index_corectie>0 daca si numai daca este d216 rectificativa”"),
    "d395": "DUK D395 v1: `d_rec` admite numai 0 (probat 21.10.2026) — formularul n-are rectificativă (`NU_ADMIT_RECTIFICATIVA`).",
    "d397": "DUK D397 v0: atributul `d_rec` (0 inițială / 1 rectificativă); CPF art.105 alin.(2)-(3) (declarație informativă).",
}

#: Formularele la care ANAF nu are bifă de rectificativă în XML: a doua depunere pe perioadă ÎNLOCUIEȘTE declarația (D394) sau e
#: considerată automat rectificativă (D406). Ecranul o spune; XML-ul nu are ce marca.
FARA_MARCAJ_IN_XML = ("d394", "d406")

_RE_ROOT = re.compile(r"<(?!\?)(?!!)([A-Za-z_][\w:.-]*)([^>]*)>", re.S)
_RE_DREC = re.compile(r'\bd_rec\s*=\s*"(\d+)"')


def luna_cheie(luna=None, trim=None):
    """Luna sub care `declaratii_depuse` ține perioada: luna, trim × 3, sau 12 la anuale (ca `coada_api.perioada_din_payload`)."""
    if luna:
        return int(luna)
    if trim:
        return int(trim) * 3
    return 12


def _rand(r, chei):
    return dict(r) if isinstance(r, dict) else dict(zip(chei, r))


def depuneri(cur, schema, tip, an, luna=None, trim=None):
    """Toate depunerile înregistrate pe (firma schemei, tip, an, perioadă), în ordinea `nr_depunere`: [{nr_depunere, data_depunere,
    sursa, xml, recipisa, spv_index}]. `spv_index` = indexul SPV scris la „Confirmă depunerea” (coada; aceeași clipă `now()` ca
    rândul depunerii, `coada_api.marcheaza_depusa`)."""
    chei = ("nr_depunere", "data_depunere", "sursa", "xml", "recipisa", "spv_index")
    cur.execute(
        "SELECT d.nr_depunere, d.data_depunere, d.sursa, d.xml, d.recipisa, "
        "(SELECT c.spv_index FROM public.declaratii_coada c WHERE c.tenant_id = d.tenant_id AND c.tip = d.tip AND c.stare = 'depusa' "
        " AND c.depus_la = d.data_depunere ORDER BY c.id DESC LIMIT 1) "
        "FROM public.declaratii_depuse d JOIN public.tenants t ON t.id = d.tenant_id "
        "WHERE t.schema_name = %s AND d.tip = %s AND d.an = %s AND d.luna = %s ORDER BY d.nr_depunere",
        (str(schema).strip('"'), str(tip).lower(), int(an), luna_cheie(luna, trim)))
    return [_rand(r, chei) for r in cur.fetchall()]


def depunere_curenta_tenant(cur, tenant_id, tip, an, luna):
    """Depunerea curentă (nr_depunere maxim) pe (tenant_id, tip, an, luna) — {nr_depunere, data_depunere, sursa} sau None."""
    chei = ("nr_depunere", "data_depunere", "sursa")
    cur.execute("SELECT nr_depunere, data_depunere, sursa FROM public.declaratii_depuse_curente "
                "WHERE tenant_id = %s AND tip = %s AND an = %s AND luna = %s", (tenant_id, str(tip).lower(), int(an), int(luna)))
    r = cur.fetchone()
    return _rand(r, chei) if r else None


def _data(dep):
    from zoneinfo import ZoneInfo
    from core.pdf_util import data_ro
    d = dep.get("data_depunere")
    if d is not None and getattr(d, "tzinfo", None):
        d = d.astimezone(ZoneInfo("Europe/Bucharest"))
    return data_ro(d)


def index_depunere(dep):
    """Indexul de depunere ANAF al unei depuneri, dacă e cunoscut: indexul SPV scris la confirmare, altfel recipisa marcării
    „depusă în afara iConta.eu” — numai dacă e un număr. None altfel (nu se inventează)."""
    for v in ((dep or {}).get("spv_index"), (dep or {}).get("recipisa")):
        s = str(v or "").strip()
        if s.isdigit() and int(s) > 0:
            return s
    return None


def descriere_depunere(dep):
    """„declarația depusă …” — cine și când, din sursa depunerii (fără dată inventată la `contabil_anterior`)."""
    sursa = (dep or {}).get("sursa")
    if sursa == "contabil_anterior":
        return "declarația depusă de contabilul anterior (data nu e cunoscută în iConta.eu)"
    if sursa == "extern":
        rec = str(dep.get("recipisa") or "").strip()
        return "declarația depusă în afara iConta.eu pe %s%s" % (_data(dep), (", recipisa %s" % rec) if rec else "")
    if sursa == "iconta":
        idx = index_depunere(dep)
        return "declarația depusă prin iConta.eu pe %s%s" % (_data(dep), (", index %s" % idx) if idx else "")
    return "declarația depusă pe %s (preluată din istoricul firmei)" % _data(dep)


def mentiune(tip, dep):
    """Textul de pe ecran pentru o declarație generată peste o depunere existentă."""
    if dep is None:
        return None
    t = str(tip).lower()
    if t == "d394":
        return "Rectificativă: înlocuiește %s." % descriere_depunere(dep)
    return "Rectificativă la %s." % descriere_depunere(dep)


def stabileste(conn, schema, tip, an, luna=None, trim=None, bifata=False):
    """`Stare` pentru o generare: rectificativă dacă pe perioadă e înregistrată o depunere (oricare sursă) SAU dacă contabilul a bifat
    „rectificativă” în formular (știe de o depunere pe care iConta.eu n-o are). Fără conexiune/schemă (calcul pur) -> inițială."""
    deps = []
    if conn is not None and schema:
        with conn.cursor() as cur:
            deps = depuneri(cur, schema, tip, an, luna, trim)
    dep = deps[-1] if deps else None
    if dep is not None:
        return Stare(1, mentiune(tip, dep), dep["nr_depunere"], dict(dep, toate=deps))
    if bifata:
        return Stare(1, "Rectificativă (bifată în formular): iConta.eu nu are nicio depunere înregistrată pe perioadă.", None, None)
    return Stare(0, None, None, None)


def bifata(manual):
    """Bifa „rectificativă” din formularul manual (`manual["d_rec"]`), ca număr 0/1."""
    try:
        return int(str((manual or {}).get("d_rec") or 0).strip() or 0) == 1
    except ValueError:
        return False


def marcaj_xml(tip, xml):
    """Ce spune XML-ul despre el însuși: True = rectificativă (`d_rec` ≠ 0 pe elementul rădăcină), False = inițială, None = formularul
    nu are marcaj în XML (D100, D300, D394, D406) sau XML-ul lipsește."""
    if not xml or str(tip).lower() in FARA_MARCAJ_IN_XML:
        return None
    m = _RE_ROOT.search(str(xml))
    if not m:
        return None
    d = _RE_DREC.search(m.group(2))
    if not d:
        return None
    return int(d.group(1)) != 0


def refuz_la_depunere(cur, tenant_id, tip, an, luna, payload):
    """[C77] La „Confirmă depunerea”: declarația a fost generată înaintea unei depuneri apărute ÎNTRE TIMP pe aceeași perioadă (o
    marcare „depusă în afara iConta.eu”, o altă depunere) -> refuz: ar pleca a doua oară ca inițială. Generatorul își scrie în
    rezultat (`randuri.depunere_anterioara_nr`) depunerea pe care s-a sprijinit; o declarație fără cheia aceasta (din coada de dinainte,
    sau un formular care nu o scrie) se judecă după marcajul din XML. {ok, cod, mesaj} sau None."""
    if an is None or luna is None:
        return None
    dep = depunere_curenta_tenant(cur, tenant_id, tip, an, luna)
    if dep is None:
        return None
    p = payload or {}
    rand = p.get("randuri") if isinstance(p.get("randuri"), dict) else {}
    if "depunere_anterioara_nr" in rand:
        if rand.get("depunere_anterioara_nr") == dep["nr_depunere"]:
            return _refuz_d394_neconfirmata(tip, an, luna, dep, p)
    elif marcaj_xml(tip, p.get("xml")) is not False:
        return _refuz_d394_neconfirmata(tip, an, luna, dep, p)
    return {"ok": False, "cod": "RECTIFICATIVA_NECESARA",
            "mesaj": ("Pe %s %s e înregistrată %s, după ce declarația aceasta a fost generată: plecată acum, ar ajunge la ANAF a doua "
                      "oară ca inițială. Generează-o din nou: iese rectificativă." % (
                          str(tip).upper(), "%02d/%d" % (int(luna), int(an)),
                          descriere_depunere(dep)))}


# ============================================================
#  [lotul 12, C19 — comanda Costin 12.3 pct.6, verbatim în DECIZII] „rectificativa D394 pentru o perioadă deja depusă se generează doar
#  la cererea contabilului, cu diferențele față de cea depusă arătate înainte; niciodată automat.”
#  D394 n-are marcaj de rectificativă în XML (`FARA_MARCAJ_IN_XML`; D394Validator v5: rădăcina fără `d_rec`) — a doua declarație pe
#  perioadă o ÎNLOCUIEȘTE pe prima (OPANAF 2194/2025 anexa nr.2 pct.3, `TEMEI_PE_TIP["d394"]`). Ce le deosebește e numai conținutul, deci
#  contabilul îl vede înainte (`d394.diferente`, față de XML-ul depus păstrat în `declaratii_depuse.xml`) și cere rectificativa pentru
#  EXACT acel conținut: confirmarea e amprenta XML-ului văzut (`date_extra.rectificativa_confirmata` în cerere, păstrată în coadă).
# ============================================================
class RefuzRectificativa(RefuzGenerare):
    """Refuzul generării D394 peste o depunere: codul și datele diferențelor în `detaliu()` (ecranul le desenează), fraza în `mesaj`
    (coada, reluarea declarației care aștepta notele, notificarea)."""
    TIP = "rectificativa D394"

    def __init__(self, cod, mesaj, **campuri):
        super().__init__(mesaj)
        self.cod, self.campuri = cod, campuri

    def detaliu(self):
        return dict(super().detaliu(), cod=self.cod, **self.campuri)


def confirmarea(cerere):
    """Amprenta pe care contabilul a confirmat-o în cerere (`date_extra.rectificativa_confirmata`), sau „” fără confirmare."""
    extra = cerere.get("date_extra") if isinstance(cerere, dict) else None
    return str(extra.get("rectificativa_confirmata") or "") if isinstance(extra, dict) else ""


def poarta_d394(conn, schema, body, xml, res):
    """D394 pe o perioadă cu declarația depusă: trece numai cu confirmarea contabilului pentru EXACT acest XML. Altfel refuz:
      RECTIFICATIVA_FARA_DIFERENTE — XML-ul nou e identic cu cel depus: nimic de rectificat, nu se generează nimic (oricum ar fi cerut);
      RECTIFICATIVA_DE_CONFIRMAT  — diferențele (fără XML depus păstrat: tot conținutul, cu „necunoscut” pe partea depusă) și amprenta
                                    de confirmat; cu o confirmare veche (datele s-au schimbat după ce le-a văzut) -> `schimbata`.
    Fără depunere pe perioadă -> None (inițiala trece neschimbată)."""
    from core import coada_api as _coada, d394 as _d394
    an, luna = int(getattr(res, "an", None) or body["an"]), int(getattr(res, "luna", None) or body["luna"])
    with conn.cursor() as cur:
        deps = depuneri(cur, schema, "d394", an, luna)
    if not deps:
        return None
    dep = deps[-1]
    per, descriere = "%02d/%d" % (luna, an), descriere_depunere(dep)
    dif = _d394.diferente(dep.get("xml"), xml)
    pastrat = dif is not None
    campuri = {"perioada": per, "depunere": descriere, "depunere_nr": dep["nr_depunere"], "xml_depus_pastrat": pastrat}
    if pastrat and not dif:
        raise RefuzRectificativa(
            "RECTIFICATIVA_FARA_DIFERENTE",
            "D394 pe %s: declarația generată acum din datele firmei e identică cu %s. Nu e nimic de rectificat, deci nu se generează "
            "nicio declarație." % (per, descriere), diferente=[], amprenta=None, schimbata=False, **campuri)
    amprenta, cerut = _coada.amprenta_xml(xml), confirmarea(body)
    if cerut == amprenta:
        return None
    raise RefuzRectificativa(
        "RECTIFICATIVA_DE_CONFIRMAT",
        "D394 pe %s e deja depusă (%s). %sO rectificativă o înlocuiește integral (OPANAF 2194/2025 anexa nr.2 pct.3) și se generează numai "
        "la cererea ta, din Declarații, după ce vezi diferențele față de cea depusă." % (
            per, descriere, "Datele perioadei s-au schimbat după ce ai văzut diferențele; uită-te din nou la ele. " if cerut else ""),
        diferente=dif if pastrat else _d394.continut(xml), amprenta=amprenta, schimbata=bool(cerut), **campuri)


def d394_confirmata(payload):
    """Declarația D394 din coadă poartă confirmarea contabilului pentru exact XML-ul ei (cererea păstrată în `_cerere`)."""
    from core import coada_api as _coada
    p = payload or {}
    return bool(p.get("xml")) and confirmarea(p.get("_cerere")) == _coada.amprenta_xml(p.get("xml"))


def _refuz_d394_neconfirmata(tip, an, luna, dep, payload):
    """[lotul 12, C19, comanda Costin 12.3 pct.6] „rectificativa D394 pentru o perioadă deja depusă se generează doar la cererea
    contabilului, cu diferențele față de cea depusă arătate înainte; niciodată automat.” La „Confirmă depunerea”: o D394 peste o depunere
    pleacă numai cu confirmarea contabilului pentru exact XML-ul ei (`d394_confirmata`). Prinde declarațiile intrate în coadă
    înainte de reparație (generate fără diferențe arătate) — nu se rescriu, se generează din nou din Declarații. None la celelalte."""
    if str(tip).lower() != "d394":
        return None
    if d394_confirmata(payload):
        return None
    per = "%02d/%d" % (int(luna), int(an))
    return {"ok": False, "cod": "RECTIFICATIVA_NECONFIRMATA",
            "mesaj": ("D394 pe %s e deja depusă (%s), iar declarația aceasta o înlocuiește fără ca diferențele față de ea să-ți fi fost "
                      "arătate. O declarație rectificativă se depune numai la cererea ta: Declarații → D394 → %s → „Continuă”, uită-te la diferențe, "
                      "apoi „Generează declarația rectificativă” și trimite-o în coadă în locul acesteia." % (per, descriere_depunere(dep), per))}


def aplica(res, st):
    """Scrie `Stare` pe rezultatul generatorului: `d_rec` (pentru build_xml), `rectificativa` (textul de pe ecran) și
    `depunere_anterioara_nr` (ajunge în `randuri`, pentru `refuz_la_depunere`). Câmpurile există pe dataclass-ul rezultatului."""
    res.d_rec = st.d_rec
    res.rectificativa = st.mentiune
    res.depunere_anterioara_nr = st.nr
    return res


# ============================================================
#  FORMULARELE CU BIFA ÎN `manual` — prin dispecer (`declaratii_api.genereaza`)
# ============================================================
#: Formularele al căror generator ia `d_rec` din `manual["d_rec"]` (bifa „rectificativă” din formular, 0 implicit). Dispecerul
#: (`pe_cerere`) o pune pe 1 când perioada are o depunere înregistrată — bifa contabilului rămâne (știe de depuneri pe care iConta.eu
#: nu le are). Valoarea = câmpul din `manual` în care formularul cere indexul de depunere al inițialei, dacă îl cere (completat din
#: depunerea înregistrată, când indexul e cunoscut). D216 / D395 / D397 își fac singure calculul (`stabileste`), nu sunt aici.
DREC_DIN_MANUAL = {
    "d104": None, "d106": None, "d107": None, "d108": None, "d110": None, "d114": None, "d119": None, "d120": None, "d130": None,
    "d177": "index", "d200": None, "d201": None, "d204": None, "d207": None, "d213": "index_init", "d221": None,
    "d223": None, "d307": None, "d311": None, "d318": None, "d393": None, "d401": None, "d402": None, "d403": None,
    "d407": None, "d600": None,
}

#: Formularele al căror validator NU admite rectificativa: `d_rec` are intervalul [0, 0] (probat pe DUK 21.10.2026, același XML valid cu
#: `d_rec="0"`, respins cu `d_rec="1"`: „eroare atribut: d_rec: valoarea '1' nu se incadreaza in intervalul cerut”). O a doua declarație
#: pe perioadă n-are cum pleca altfel decât „inițială” — exact defectul C77 —, deci nu se generează: refuz numit.
NU_ADMIT_RECTIFICATIVA = {
    "d214": "DUK D214 v0 (probat 21.10.2026): d_rec admite numai 0",
    "d395": "DUK D395 v1 (probat 21.10.2026): d_rec admite numai 0",
    "d398": "DUK D398 (probat 21.10.2026): d_rec admite numai 0",
}


def refuz_fara_rectificativa(tip, an, luna, st):
    """`RefuzGenerare` pentru un formular din `NU_ADMIT_RECTIFICATIVA` cerut peste o depunere înregistrată (sau bifat rectificativ)."""
    t = str(tip).lower()
    ce = descriere_depunere(st.dep) if st.dep is not None else "rectificativa bifată în formular"
    return RefuzGenerare(
        "%s pe %02d/%d: %s. Validatorul ANAF al formularului %s nu admite declarație rectificativă (atributul d_rec primește numai 0), "
        "deci o a doua declarație pe aceeași perioadă ar pleca tot ca inițială; iConta.eu nu o generează." % (
            t.upper(), int(luna_cheie(luna)), int(an), ce[0].upper() + ce[1:], t.upper()))


#: Generatoarele care decid singure (`stabileste` / `aplica`) — d_rec din depunerile înregistrate.
DECID_SINGURE = ("d100", "d101", "d101g", "d112", "d205", "d216", "d301", "d390", "d394", "d395", "d397", "d406")

#: Formularele cu marcaj de rectificativă pe care nici dispecerul, nici generatorul nu-l pot pune singuri — cu motivul.
DREC_NEACOPERITE = {
    "d212": ("D212: rectificativa bifează capitolul corectat (rectif1 / rectif2 — DUK D212 v9), alegere a contabilului; d_rec=1 "
             "fără capitol e respinsă"),
    "d220": "D220: rectificativa se exprimă prin d_rec1 / d_rec2 (tipul rectificării, DUK D220 v1), alegere a contabilului",
    "d300": "D300: decontul nu are rectificativă (CPF art.105 alin.(4)); patch-ul (refuz la generare) e cerut în raport",
    "d208": "D208: validatorul are `d_rec` (DUK D208 v6), generatorul nu-l emite; de completat (fișier în afara lotului)",
}


def pe_cerere(conn, schema, tip, body):
    """[C77] Pentru dispecer: la formularele din `DREC_DIN_MANUAL`, `manual["d_rec"]` = 1 dacă perioada cererii are o depunere
    înregistrată (și indexul inițialei în câmpul cerut de formular, dacă e cunoscut și necompletat). -> (body, Stare | None)."""
    t = str(tip).lower()
    if (t not in DREC_DIN_MANUAL and t not in NU_ADMIT_RECTIFICATIVA) or not isinstance(body, dict) or not body.get("an"):
        return body, None
    manual = dict(body.get("manual") or {})
    st = stabileste(conn, schema, t, int(body["an"]), body.get("luna"), body.get("trim"), bifata=bifata(manual))
    if t in NU_ADMIT_RECTIFICATIVA:
        if st.d_rec:
            raise refuz_fara_rectificativa(t, body["an"], body.get("luna") or (int(body["trim"]) * 3 if body.get("trim") else 12), st)
        return body, None
    if st.dep is None:
        return body, st
    manual["d_rec"] = 1
    camp = DREC_DIN_MANUAL[t]
    if camp and not str(manual.get(camp) or "").strip():
        idx = index_depunere((st.dep.get("toate") or [st.dep])[0])
        if idx:
            manual[camp] = idx
    return {**body, "manual": manual}, st


def pe_rezultat(res, st):
    """[C77] Mențiunea de pe ecran pe rezultatul unui formular din `DREC_DIN_MANUAL` (care n-are câmpul lui): `rectificativa`."""
    if st is not None and st.d_rec and res is not None and not isinstance(res, list) and getattr(res, "rectificativa", None) is None:
        try:
            res.rectificativa = st.mentiune
        except AttributeError:
            pass
    return res

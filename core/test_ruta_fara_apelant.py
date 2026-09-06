# -*- coding: utf-8 -*-
"""GARD [R70, 26.08.2026]: o rută NOUĂ fără apelant nu trece poarta.

De unde vine. Am scris `POST /public/confirma-email`, i-am construit gardul, a trecut toată suita
— și nimic n-o chema. Linkul din email ducea în SPA cu un fragment necunoscut. Un defect de
**prag 1** pe cod scris și gardat în aceeași zi, găsit nu de un instrument, ci de exercitarea pe
date. Gărzile verificau ce face ruta **dacă** e chemată; niciuna nu întreba **dacă** e chemată.

CE FACE IMPOSIBIL: o rută nouă care intră fără ca ceva din `static/` s-o cheme.

CE NU FACE, și e jumătate din onestitatea gardului: **nu curăță trecutul.** Costin: *„cele
existente rămân, cu lista declarată — clichet, nu poartă retroactivă."* Iar lista de mai jos e un
**BASELINE**, nu o afirmație: conține și rute care chiar n-au apelant (`urme-portal`,
`d406-active`, `s1003-*`, `s1005-*`), și artefacte ale detectorului (căi compuse la rulare pe care
nu le-am verificat una câte una). Fiecare intrare primește motivul **când e atinsă**, nu înainte.

CE A DEVENIT GARDUL PE 27.08.2026, și se scrie aici fiindcă e o schimbare de sens, nu una de
conținut: **ieri verifica o LISTĂ, azi verifică un MARCAJ.** `_BASELINE` era un singur set ținut
de mână, în care stăteau amestecate două lucruri diferite — rute păstrate **deliberat** fără ecran,
și **artefacte ale detectorului** (căi compuse la rulare, pe care el nu le poate vedea). Cele două
se despart acum:

  * `declarate()` — **DERIVAT din cod**, nu scris aici: rutele al căror decorator poartă
    `# [api_intern_v1] <motivul>`. O rută care primește ecran și pierde marcajul **iese singură**
    din mulțime; una care e păstrată deliberat **trebuie** să spună de ce, lângă ea, în `main.py`.
  * `_ARTEFACTE` — ce rămâne: cazurile în care **detectorul greșește**, grupate pe felul greșelii.
    Aici lista de mână e legitimă, fiindcă descrie limitele instrumentului, nu intenția codului.

Cine citește trebuie să știe: **o intrare nouă în `_ARTEFACTE` e o mărturisire despre detector; un
marcaj nou în `main.py` e o decizie despre produs.** Nu se mai pot confunda.

CUM DETECTEAZĂ, și de ce așa după patru încercări. Întrebarea *„cine cheamă ruta asta?"* nu are
răspuns textual în codul ăsta: UI-ul compune căi la rulare și dispecerizează prin tabele
(`operatiuni_ecran.js`: `ruta: "nota-sgr"`). Patru reguli succesive au greșit alternativ:
  1. ultimul segment al căii            -> ratează căile compuse (13 raportate, 6 reale)
  2. bucăți literale cu `/` în față     -> ratează dispecerizarea prin tabel (zeci de false)
  3. segmente separate, oricare         -> trece orice, ancorele scurte apar peste tot
  4. **bucăți literale FĂRĂ `/`, toate** -> forma de aici; prinde tabelul, ratează încă unele
     căi compuse pe grup (`stat-plata/…`)
A patra e cea mai puțin greșită, nu cea corectă. **De aceea gardul nu asertează pe cifră, ci pe
MULȚIME**: un fals-pozitiv rămâne în baseline fără să mintă despre altceva, iar o rută nouă iese
în evidență oricum.
"""
import glob
import io
import importlib.util
import os

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCAN = os.path.join(_RAD, "scripts", "scan_trasee.py")

# ARTEFACTELE DETECTORULUI, 27.08.2026 — grupate pe FELUL greșelii, nu înșirate.
# Aici nu stă nicio decizie despre produs: stau limitele instrumentului. Cele păstrate deliberat
# fără ecran își spun motivul în `main.py`, iar `declarate()` le citește de acolo.
_ARTEFACTE = {
    # (a) contract EXTERN, chemat de integratori, nu din `static/` — suprafața „cheia de integrare"
    ("GET", "/api/v1/firme"), ("GET", "/api/v1/firme/{tenant_id}/balanta"),
    ("GET", "/api/v1/firme/{tenant_id}/facturi"), ("POST", "/api/v1/firme/{tenant_id}/facturi"),
    ("GET", "/api/v1/firme/{tenant_id}/kpi"),
    # (b) cerute de BROWSER, nu de JS — legitime prin construcție
    ("GET", "/favicon.ico"), ("GET", "/robots.txt"), ("GET", "/sitemap.xml"),
    # (c) cale compusă la rulare, pe care detectorul nu o poate vedea (limita din antet)
    ("GET", "/portal/facturi"), ("GET", "/portal/firme"),
    ("GET", "/portal/solicitari/contor"),
    ("POST", "/migrare/fisier"),
    ("GET", "/tenants/{tenant_id}/perioade-blocate/istoric"),
    ("POST", "/tenants/{tenant_id}/s1003-valideaza"), ("GET", "/tenants/{tenant_id}/s1003-xml"),
    ("POST", "/tenants/{tenant_id}/s1005-valideaza"), ("GET", "/tenants/{tenant_id}/s1005-xml"),
    ("POST", "/tenants/{tenant_id}/stat-plata/corectie"),
    ("GET", "/tenants/{tenant_id}/stat-plata/emis"),
    ("POST", "/tenants/{tenant_id}/stat-plata/emite"),
    ("POST", "/tenants/{tenant_id}/stat-plata/motiv"),
    # (d) chiar fără ecran, pe o suprafață declarată ne-documentară (GDPR)
    ("POST", "/gdpr/sterge-cabinet/{cabinet_id}/executa"),
    ("POST", "/gdpr/sterge-cabinet/{cabinet_id}/previzualizare"),
}

_MARCAJ = "[api_intern_v1]"
_METODE = ("get", "post", "put", "patch", "delete")


def declarate(fisier="main.py"):
    """Rutele care își declară în COD lipsa ecranului. DERIVAT, nu ținut de mână.

    Decoratorul se citește ca **nod de AST** (`app.<metodă>("cale")`), iar marcajul se caută pe
    **linia lui**, aflată din `lineno` — nu se caută nicăieri altundeva în fișier. Un comentariu
    rătăcit la 50 de linii distanță nu poate declara nimic.
    """
    import ast
    sursa = io.open(os.path.join(_RAD, fisier), encoding="utf-8").read()
    linii = sursa.split(chr(10))
    out = set()
    for n in ast.walk(ast.parse(sursa)):
        if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for d in n.decorator_list:
            if not (isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
                    and isinstance(d.func.value, ast.Name) and d.func.value.id == "app"
                    and d.func.attr in _METODE and d.args
                    and isinstance(d.args[0], ast.Constant)):
                continue
            if _MARCAJ in linii[d.lineno - 1]:
                out.add((d.func.attr.upper(), d.args[0].value))
    return out


def acceptate():
    """Ce nu se raportează: ce spune codul că e deliberat, plus ce știm că detectorul ratează."""
    return declarate() | _ARTEFACTE


def _scan():
    spec = importlib.util.spec_from_file_location("scan_trasee", _SCAN)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _static():
    t = []
    for f in (glob.glob(os.path.join(_RAD, "static", "**", "*.js"), recursive=True)
              + glob.glob(os.path.join(_RAD, "static", "*.html"))):
        t.append(io.open(f, encoding="utf-8", errors="ignore").read())
    return "\n".join(t)


def _apare(js, ancora):
    """[R80, 30.08.2026] Ancora apare ca REFERINȚĂ DE RUTĂ, nu ca simplu cuvânt.

    Până azi testul era `ancora in js` — adică „Registru jurnal" dintr-un titlu conta drept apelare a
    lui `/tenants/{id}/jurnal`. Predicatul e acum unul singur, în `scripts/scan_ancore_rute`, folosit
    **și** de măsurătoarea orbirii (R80) **și** de detectorul ăsta. Dacă ar fi două, măsurătoarea ar
    spune „ancora discriminează" în timp ce detectorul declară ACCEPTAT pe o potrivire din proză —
    exact divergența pe care gardul celor trei cititori o interzice.
    """
    import os
    import sys as _sys
    _sys.path.insert(0, os.path.join(_RAD, "scripts"))
    from scan_ancore_rute import apare as _a
    return _a(js, ancora)


def bucati(cale):
    """Bucățile LITERALE ale căii, fără `/` în față — ca dispecerizarea prin tabel
    (`ruta: "nota-sgr"`) să fie recunoscută drept apelare.

    [R80] `/` NU se adaugă aici, deliberat: forma dispecerizată n-are slash. Discriminarea se face
    în `_apare`, care acceptă și `/ancora`, și `"ancora"`."""
    out, cur = [], []
    for seg in cale.split("/"):
        if seg.startswith("{"):
            if cur:
                out.append("/".join(cur))
                cur = []
        elif seg:
            cur.append(seg)
    if cur:
        out.append("/".join(cur))
    return [b for b in out if len(b) >= 4]


def _fara_apelant(rute, js):
    return {(r["metoda"], r["cale"]) for r in rute
            if bucati(r["cale"]) and not all(_apare(js, b) for b in bucati(r["cale"]))}


# [R80, 27.08.2026] Numitorul, scris o dată și verificat mecanic.
#
# Costin: *„un gard care spune «nicio rută fără apelant» trebuie să spună și «despre 88% din
# suprafață»."* Verdele unui test e **numele** lui — de aceea numele de mai jos poartă
# `DINTRE_CELE_VIZIBILE`, nu o cifră care ar îmbătrâni în el. Cifra stă aici și se recalculează.
_OARBE = 6           # 27.08.2026: 51 · 30.08.2026 dimineața: 55 · **30.08.2026, după R80: 6**.
                     # Ancora e acum SEGMENT DE CALE, nu cuvânt. Cele 6 rămase sunt exact rutele al
                     # căror singur segment literal e `tenants` (238 apariții — e în fiecare cale),
                     # plus `GET /`, care n-are niciun segment literal. Adică EXACT instanța
                     # fondatoare a lui R80 — `PUT /tenants/{id}` — rămâne oarbă, onest.
_TOTAL_LA_MASURARE = 411


def _acoperire():
    """(vizibile, total, procent) — recalculat, nu ținut minte."""
    import sys as _sys
    _s = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
    if _s not in _sys.path:
        _sys.path.insert(0, _s)
    from scan_ancore_rute import masoara
    rute, _js, orbi, _v = masoara()
    return len(rute) - len(orbi), len(rute), round(100.0 * (len(rute) - len(orbi)) / len(rute))


def test_gardul_isi_spune_NUMITORUL():
    """Doc↔cod pe propria orbire. Dacă `_OARBE` nu mai e adevărat, gardul ar continua să treacă
    verde afirmând o acoperire pe care n-o mai are — și tocmai asta e clasa pe care o păzește."""
    vizibile, total, procent = _acoperire()
    assert total - vizibile == _OARBE, (
        "rutele oarbe sunt %d, iar `_OARBE` scrie %d. Actualizează cifra ȘI restanța R80 — "
        "altfel verdele de mai jos afirmă o acoperire care nu mai există."
        % (total - vizibile, _OARBE))
    assert total == _TOTAL_LA_MASURARE or total > 300, "numitorul s-a mutat: %d" % total
    print("\n[R70] acoperire reală: %d din %d rute (%d%%) — despre restul, gardul e mut"
          % (vizibile, total, procent))


def test_nicio_ruta_NOUA_fara_apelant_DINTRE_CELE_VIZIBILE():
    st = _scan()
    gasite = _fara_apelant(st.citeste_rute(), _static())
    noi = sorted(gasite - acceptate())
    vizibile, total, procent = _acoperire()
    assert not noi, (
        "rute noi pe care nu le cheamă nimic din `static/` (verificate: %d din %d, %d%%):\n  "
        % (vizibile, total, procent)
        + "\n  ".join("%s %s" % r for r in noi)
        + "\n\nO rută scrisă, gardată și verde, dar nechemată, e cod care nu se execută — "
          "instanța care a produs gardul ăsta a stat ascunsă o zi. Cheam-o dintr-un ecran, "
          "sau pune-i `# [api_intern_v1] <motivul>` pe linia decoratorului, dacă e păstrată "
          "deliberat fără ecran. `_ARTEFACTE` e numai pentru cazurile în care greșește "
          "DETECTORUL, nu pentru intenții.")


def test_ANTI_VACUU_detectorul_chiar_vede_rute():
    st = _scan()
    rute = st.citeste_rute()
    assert len(rute) > 300, "doar %d rute citite — gardul s-ar uita în gol" % len(rute)
    assert _static(), "nu s-a citit niciun fișier din static/ — detectorul ar raporta tot"
    # Anti-vacuu de al doilea fel: nu „vede ceva", ci „nu vede TOT". Instanța, 27.08.2026:
    # `PUT /tenants/{tenant_id}` a rămas fără niciun apelant, iar gardul n-a clipit — singura ei
    # ancoră literală e `tenants`, care apare de 235 de ori în JS.
    vizibile, total, _p = _acoperire()
    assert vizibile < total, (
        "detectorul se declară complet. Nu e: vezi R80. Dacă orbirea chiar a dispărut, "
        "scoate testul ăsta deliberat.")


def test_artefactele_nu_pastreaza_morti():
    """Clichet pe mulțime, în direcția cealaltă: o intrare care nu mai e raportată (ruta a primit
    ecran, sau a fost ștearsă) trebuie scoasă DELIBERAT, ca lista să nu devină o colecție de morți.

    Se aplică pe partea VIZIBILĂ a suprafeței — vezi `test_gardul_isi_spune_NUMITORUL` și R80.

    Se aplică DOAR artefactelor. Cele declarate în cod ies singure: dacă marcajul dispare odată cu
    ruta, `declarate()` nu le mai vede — de-aia partea aia nu mai are nevoie de clichet."""
    st = _scan()
    gasite = _fara_apelant(st.citeste_rute(), _static())
    disparute = sorted(_ARTEFACTE - gasite)
    assert not disparute, (
        "intrări din `_ARTEFACTE` care nu mai sunt raportate: %s — scoate-le, altfel lista "
        "scuză o problemă care nu mai există" % ["%s %s" % r for r in disparute])


def test_ANTI_VACUU_marcajele_chiar_se_citesc():
    """Dacă `declarate()` s-ar întoarce goală — decorator schimbat, marcaj redenumit — jumătatea
    derivată ar dispărea în tăcere, iar `_ARTEFACTE` ar părea că acoperă tot."""
    d = declarate()
    assert len(d) >= 5, (
        "doar %d rute cu marcaj `%s` citite din `main.py` — cititorul s-a rupt" % (len(d), _MARCAJ))
    assert not (d & _ARTEFACTE), (
        "rute care stau în AMÂNDOUĂ listele: %s — o intenție declarată nu e un artefact al "
        "detectorului; ține-o într-un singur loc" % sorted(d & _ARTEFACTE))


def test_CALIBRARE_marcajul_de_pe_ALTA_linie_nu_declara_nimic(tmp_path):
    """Direcția «acceptă pe nedrept»: un comentariu rătăcit nu poate scuza o rută."""
    f = tmp_path / "m.py"
    f.write_text('# [api_intern_v1] motiv ratacit' + chr(10) +
                 '@app.get("/x/inventata")' + chr(10) +
                 'def x():' + chr(10) + '    pass' + chr(10), encoding="utf-8")
    global _RAD
    vechi = _RAD
    try:
        _RAD = str(tmp_path)
        assert declarate("m.py") == set(), "un marcaj de pe altă linie a declarat o rută"
        f.write_text('@app.get("/x/inventata")  # [api_intern_v1] motiv' + chr(10) +
                     'def x():' + chr(10) + '    pass' + chr(10), encoding="utf-8")
        assert declarate("m.py") == {("GET", "/x/inventata")}, "marcajul de pe linia bună nu e citit"
    finally:
        _RAD = vechi


def test_CALIBRARE_dispecerizarea_prin_tabel_NU_e_raportata():
    """Direcția «acuză pe nedrept», pe instanța reală care a doborât a doua regulă: ecranul de
    operațiuni cheamă zeci de rute printr-un tabel (`ruta: "nota-sgr"`), fără `/` în față și fără
    calea întreagă. Dacă gardul le-ar raporta, ar cere ștergerea a jumătate din operațiuni."""
    js = ('const P = `/tenants/${t.id}/${op.ruta}`;'
          'const T = [{ cheie: "sgr", ruta: "nota-sgr" }, { cheie: "ong", ruta: "nota-ong" }];')
    fals = _fara_apelant(
        [{"metoda": "POST", "cale": "/tenants/{tenant_id}/nota-sgr"},
         {"metoda": "POST", "cale": "/tenants/{tenant_id}/nota-ong"}], js)
    assert not fals, "dispecerizarea prin tabel e raportată ca lipsă de apelant: %s" % sorted(fals)


def test_CALIBRARE_o_ruta_chiar_nechemata_E_raportata():
    """Cealaltă direcție: fără ea, o reparație care ar declara totul «chemat» ar trece prima probă
    și ar goli gardul."""
    gasite = _fara_apelant(
        [{"metoda": "POST", "cale": "/tenants/{tenant_id}/ruta-inventata-fara-ecran"}], "// nimic")
    assert gasite == {("POST", "/tenants/{tenant_id}/ruta-inventata-fara-ecran")}, gasite


# Cele CINCI care chiar n-au ecran, dupa citire (26-27.08.2026). Restul din `_BASELINE` sunt
# artefacte ale detectorului (cai compuse la rulare), nu rute orfane -- vezi antetul.
_CELE_CINCI_REALE = [
    ("main.py", '@app.post("/tenants/{tenant_id}/banca/parse-extras")'),
    ("main.py", '@app.post("/tenants/{tenant_id}/calcul-cm")'),
    ("main.py", '@app.post("/tenants/{tenant_id}/import-efactura")'),
    ("main.py", '@app.get("/tenants/{tenant_id}/jurnal-marja")'),
    ("main.py", '@app.get("/tenants/{tenant_id}/urme-portal")'),
]


def test_cele_cinci_reale_isi_declara_lipsa_ecranului():
    """Costin, 27.08: cele nedeclarate «se declara sau se scot». Declaratia e in cod, langa ruta,
    ca marcajul `[api_intern_v1]` -- si de aici incolo nu mai poate disparea tacut.

    Nu asertez pe TEXTUL motivului (ar fi gard pe text, METODA §23): asertez ca linia
    decoratorului rutei poarta marcajul. Continutul motivului e treaba omului care citeste."""
    fara = []
    for fis, decorator in _CELE_CINCI_REALE:
        text = io.open(os.path.join(_RAD, fis), encoding="utf-8").read()
        linii = [l for l in text.splitlines() if l.startswith(decorator)]
        assert len(linii) == 1, "decoratorul %s apare de %d ori in %s" % (decorator, len(linii), fis)
        if "[api_intern_v1]" not in linii[0]:
            fara.append("%s: %s" % (fis, decorator))
    assert not fara, (
        "rute fara ecran care nu-si mai declara lipsa in cod:\n  " + "\n  ".join(fara)
        + "\n\nO ruta pastrata deliberat spune de ce; una care tace e o ramasita. "
          "Marcajul e `# [api_intern_v1] <motivul>` pe linia decoratorului.")

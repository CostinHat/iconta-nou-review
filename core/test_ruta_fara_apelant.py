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

# BASELINE la 26.08.2026 — vezi antetul: e o fotografie, nu o listă de vinovați.
_BASELINE = {
    ("GET", "/api/v1/firme"), ("GET", "/api/v1/firme/{tenant_id}/balanta"),
    ("GET", "/api/v1/firme/{tenant_id}/facturi"), ("POST", "/api/v1/firme/{tenant_id}/facturi"),
    ("GET", "/api/v1/firme/{tenant_id}/kpi"),
    ("GET", "/favicon.ico"), ("GET", "/robots.txt"), ("GET", "/sitemap.xml"),
    ("POST", "/gdpr/sterge-cabinet/{cabinet_id}/executa"),
    ("POST", "/gdpr/sterge-cabinet/{cabinet_id}/previzualizare"),
    ("POST", "/migrare/fisier"),
    ("GET", "/portal/facturi"), ("GET", "/portal/firme"),
    ("GET", "/portal/solicitari/contor"),
    ("GET", "/public/plata/{ref}"), ("POST", "/public/plata/{ref}/confirma"),
    ("POST", "/tenants/{tenant_id}/banca/parse-extras"),
    ("POST", "/tenants/{tenant_id}/calcul-cm"),
    ("GET", "/tenants/{tenant_id}/d406-active"), ("GET", "/tenants/{tenant_id}/d406-stocuri"),
    ("POST", "/tenants/{tenant_id}/import-efactura"),
    ("GET", "/tenants/{tenant_id}/jurnal-marja"),
    ("GET", "/tenants/{tenant_id}/perioade-blocate/istoric"),
    ("POST", "/tenants/{tenant_id}/s1003-valideaza"), ("GET", "/tenants/{tenant_id}/s1003-xml"),
    ("POST", "/tenants/{tenant_id}/s1005-valideaza"), ("GET", "/tenants/{tenant_id}/s1005-xml"),
    ("POST", "/tenants/{tenant_id}/stat-plata/corectie"),
    ("GET", "/tenants/{tenant_id}/stat-plata/emis"),
    ("POST", "/tenants/{tenant_id}/stat-plata/emite"),
    ("POST", "/tenants/{tenant_id}/stat-plata/motiv"),
    ("GET", "/tenants/{tenant_id}/urme-portal"),
}


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


def bucati(cale):
    """Bucățile LITERALE ale căii, fără `/` în față — ca dispecerizarea prin tabel
    (`ruta: "nota-sgr"`) să fie recunoscută drept apelare."""
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
            if bucati(r["cale"]) and not all(b in js for b in bucati(r["cale"]))}


def test_nicio_ruta_NOUA_fara_apelant():
    st = _scan()
    gasite = _fara_apelant(st.citeste_rute(), _static())
    noi = sorted(gasite - _BASELINE)
    assert not noi, (
        "rute noi pe care nu le cheamă nimic din `static/`:\n  "
        + "\n  ".join("%s %s" % r for r in noi)
        + "\n\nO rută scrisă, gardată și verde, dar nechemată, e cod care nu se execută — "
          "instanța care a produs gardul ăsta a stat ascunsă o zi. Cheam-o dintr-un ecran, "
          "sau adaug-o în `_BASELINE` cu motivul, dacă e intenționat internă.")


def test_ANTI_VACUU_detectorul_chiar_vede_rute():
    st = _scan()
    rute = st.citeste_rute()
    assert len(rute) > 300, "doar %d rute citite — gardul s-ar uita în gol" % len(rute)
    assert _static(), "nu s-a citit niciun fișier din static/ — detectorul ar raporta tot"


def test_baseline_nu_creste_tacut():
    """Clichet pe mulțime, nu pe cifră: o intrare care dispare din baseline (ruta a primit ecran,
    sau a fost ștearsă) trebuie scoasă DELIBERAT, ca lista să nu devină o colecție de morți."""
    st = _scan()
    gasite = _fara_apelant(st.citeste_rute(), _static())
    disparute = sorted(_BASELINE - gasite)
    assert not disparute, (
        "intrări din `_BASELINE` care nu mai sunt fără apelant: %s — scoate-le din listă"
        % ["%s %s" % r for r in disparute])


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

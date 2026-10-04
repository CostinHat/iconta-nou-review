# -*- coding: utf-8 -*-
"""GARD — interfața urmează serverul (decizia Costin 04.10.2026: „orice acțiune refuzată rolului nu se afișează
(derivat din gărzile rutelor)”). Instrumentul: `scripts/scan_drepturi_ui.py`.

CE FACE IMPOSIBIL
  1. un apel JS la o rută RESTRÂNSĂ fără ca fișierul să declare elementul care îl face (`data-actiune` /
     `data-actiune-camp` / `permis(...)`) — butonul ar apărea asistentului și abia la clic ar primi refuzul;
  2. o declarație care nu mai e o rută (o greșeală de tastare n-ar ascunde nimic, tăcut);
  3. un apel JS pe o METODĂ pe care ruta n-o are — clasa găsită pe drum: „Răspunsuri REGES” chema `GET` pe o rută
     `POST` și primea 405 la fiecare apăsare, din ziua în care a apărut (`e5dad122`, 05.07.2026);
  4. o cale dinamică nouă, nelegabilă static, trecută neobservată — se pinează, cu motivul;
  5. dispariția porții din pagină (modulul, apelul la pornire, regula CSS).

CE NU VEDE (declarat): leagă apelul de FIȘIER, nu de elementul exact. Că marcajul stă pe butonul care face
apelul o probează proba din browser (`frontend_test/proba_asistent_drepturi.py`), nu acest gard.
"""
import io
import os
import re
import sys

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))
import scan_drepturi_ui as S  # noqa: E402


@pytest.fixture(scope="module")
def m():
    return S.masoara()


def test_ANTI_VACUU(m):
    assert len(m["legate"]) >= 150, "instrumentul leagă doar %d apeluri — s-a stricat?" % len(m["legate"])
    assert len(S.apeluri()) >= 400


def test_orice_apel_la_o_ruta_restransa_are_elementul_declarat(m):
    lipsa = ["%s:%d %s" % (r[0], r[1], r[2]) for r in m["lipsa"]]
    assert not lipsa, ("apeluri la rute restrânse fără `data-actiune` în fișier (%d):\n  %s\nMarchează elementul "
                       "care face apelul cu data-actiune=\"METODĂ /cale\" (șablonul din main.py)."
                       % (len(lipsa), "\n  ".join(lipsa)))


def test_declaratiile_sunt_rute_reale():
    """Imposibilul 2: orice „METODĂ /cale” declarată (atribut, `dataset`, `permis`, ambele ramuri ale unui ternar)
    e o rută reală — o greșeală de tastare n-ar ascunde nimic, tăcut."""
    reale = {"%s %s" % k for k in S.garzi_din_main()}
    import glob
    rele = []
    for f in glob.glob(os.path.join(RAD, "static", "js", "**", "*.js"), recursive=True):
        for a in S.declarate_in(io.open(f, encoding="utf-8").read()):
            if a.endswith("/"):
                continue
            if a not in reale:
                rele.append((os.path.relpath(f, RAD), a))
    assert not rele, rele


def test_operatiunile_speciale_merg_pe_rute_reale_cu_drept():
    """Calea dinamică din `operatiuni_ecran.js`: `POST /tenants/{tenant_id}/<ruta>`, acțiunea derivată din
    registru (`actiuneOp`). Fiecare `ruta:` trebuie să fie o rută reală, pe `cere_drept`."""
    src = io.open(os.path.join(RAD, "static", "js", "ecrane", "operatiuni_ecran.js"), encoding="utf-8").read()
    # Că butoanele poartă `data-actiune="${actiuneOp(o)}"` se probează pe pagina RANDATĂ (proba din browser), nu
    # căutând șirul în sursă (clichetul 50: o gardă asertează pe structură).
    rute = re.findall(r'\bruta:\s*"([\w-]+)"', src)
    assert len(rute) >= 30, rute
    g = S.garzi_din_main()
    rele = [r for r in rute if (g.get(("POST", "/tenants/{tenant_id}/" + r)) or ("",))[0] != "drept"]
    assert not rele, "operațiuni fără rută pe `cere_drept`: %s" % rele


# Căile pe care instrumentul nu le poate lega static — fiecare cu motivul. Cheia: (fișier, METODĂ, cale normalizată).
_DINAMICE = {
    ("static/js/ecrane/admin_activitate.js", "POST", "/admin/cabinete/{}/{}"):
        "acțiunea de cabinet a SUPERADMINULUI (suspendă/reactivează), pe desktopul lui — nu e o rută de cabinet",
    ("static/js/ecrane/cabinet.js", "GET", "/asistenti/echipa/jurnal{}"):
        "CITIRE (jurnalul echipei, cu interogarea lipită de cale) pe desktopul administratorului",
    ("static/js/ecrane/firme.js", "GET", "/public/verifica-cui/"):
        "rută PUBLICĂ (verificarea CUI la ANAF), fără gardă de rol",
    ("static/js/ecrane/firme.js", "POST", "/tenants/{}/{}"):
        "validarea bilanțului: `${tip()}-valideaza` (S1003/S1005); butonul #bl-val declară AMBELE rute",
    ("static/js/ecrane/firme.js", "GET", "/tenants/{}/{}"):
        "XML-ul bilanțului: `${tip()}-xml` — CITIRE",
    ("static/js/ecrane/operatiuni_ecran.js", "POST", "/tenants/{}/{}"):
        "operațiunile speciale: `${opCurenta.ruta}` — verificat de testul operațiunilor de mai sus",
    ("static/js/ecrane/portal.js", "DELETE", "/portal/acces-cont/acces/"):
        "PORTALUL clientului (rută de client, cu id concatenat)",
    ("static/js/ecrane/portal.js", "DELETE", "/portal/bon/"):
        "PORTALUL clientului (rută de client, cu id concatenat)",
    ("static/js/ecrane/setari.js", "GET", "/spv/stare"):
        "CITIRE a stării conectorului SPV (ruta nu stă pe decoratorii `app.*` din main.py)",
    ("static/js/ecrane/setari.js", "GET", "/spv/autorizare"):
        "CITIRE: începutul autorizării OAuth SPV (ruta nu stă pe decoratorii `app.*` din main.py)",
}


def test_caile_nelegabile_sunt_pinate_cu_motiv(m):
    gasite = {(r[0], r[2], r[3]) for r in m["nerezolvate"]}
    noi = sorted(gasite - set(_DINAMICE))
    vechi = sorted(set(_DINAMICE) - gasite)
    assert not noi, "căi noi pe care instrumentul nu le leagă — legă-le sau pinează-le cu motiv: %s" % noi
    assert not vechi, "pinuri care nu mai există — scoate-le: %s" % vechi
    for k, motiv in _DINAMICE.items():
        assert len(motiv) > 40, "pin fără motiv: %s" % (k,)


def test_bilantul_declara_ambele_rute():
    src = io.open(os.path.join(RAD, "static", "js", "ecrane", "firme.js"), encoding="utf-8").read()
    d = S.declarate_in(src)
    assert {"POST /tenants/{tenant_id}/s1003-valideaza", "POST /tenants/{tenant_id}/s1005-valideaza"} <= d


def test_niciun_apel_pe_o_metoda_pe_care_ruta_n_o_are(m):
    """Imposibilul 3 (clasa reges-poll): calea există, dar pe ALTĂ metodă -> 405 la fiecare apăsare."""
    g = S.garzi_din_main()
    rx = [(mm, S._regex_cale(c)) for (mm, c) in g]
    rele = []
    for rel, ln, met, cale in m["nerezolvate"]:
        alte = sorted({mm for mm, r in rx if r.match(cale) and mm != met})
        if alte:
            rele.append("%s:%d %s %s (ruta există doar pe %s)" % (rel, ln, met, cale, alte))
    assert not rele, rele


def test_poarta_e_montata():
    js = lambda *p: io.open(os.path.join(RAD, "static", "js", *p), encoding="utf-8").read()
    app = js("app.js")
    imp = re.search(r'import\s*\{\s*incarcaDrepturi\s*,\s*pornestePoarta\s*\}\s*from\s*"\./drepturi\.js(?:\?v=\w+)?"', app)
    assert imp, "app.js nu mai importă poarta drepturilor"
    incarca = re.search(r"await incarcaDrepturi\(\);\s*pornestePoarta\(\);", app)
    desktop = re.search(r"creeazaNavigator\(radacina, desktopAsistent\)", app)
    assert incarca and desktop and incarca.start() < desktop.start(), \
        "drepturile trebuie luate ÎNAINTE de desktop (altfel butonul interzis apare o clipă)"
    dj = js("drepturi.js")
    assert re.search(r'api\.get\("/eu/drepturi"\)', dj), "poarta nu mai citește lista de la server"
    assert re.search(r'classList\.add\("drept-refuzat"\)', dj) and re.search(r'querySelectorAll\("\[data-actiune-camp\]"\)', dj)
    css = io.open(os.path.join(RAD, "static", "stil.css"), encoding="utf-8").read()
    assert re.search(r"\.drept-refuzat\s*\{\s*display:\s*none\s*!important", css), "regula CSS a porții lipsește"


def test_CALIBRARE_instrumentul_vede_lipsa_si_ramurile():
    """Modul propriu de eșec: potrivirea pe SUBȘIR („POST /tenants” găsit în „POST /tenants/{tenant_id}/…”),
    și ramura a doua a unui ternar pierdută la prima ghilimea."""
    assert S.declarate_in('data-actiune="POST /tenants/{tenant_id}/facturi"') == {"POST /tenants/{tenant_id}/facturi"}
    assert "POST /tenants" not in S.declarate_in('data-actiune="POST /tenants/{tenant_id}/facturi"')
    d = S.declarate_in('<b data-actiune="${c ? "POST /a" : "DELETE /b"}">x</b>')
    assert d == {"POST /a", "DELETE /b"}
    assert S.declarate_in('if (!permis(x ? "DELETE /p" : "POST /p")) b.remove();') == {"DELETE /p", "POST /p"}


# ── a doua treaptă: marcajul pe ELEMENTUL legat de handler (unde legătura se poate dovedi) ────────────
# Clichet pe apelurile a căror legare nu se poate dovedi static (handler în altă funcție, selector calculat, element
# construit cu createElement). Numărul nu are voie să crească; când scade, se coboară aici.
_CLICHET_NELEGATE_PE_ELEMENT = 36


def test_marcajul_sta_pe_elementul_legat():
    """Mutația care a cerut treapta asta: marcajul scos de pe „Adaugă firma” (din formular), rămas pe „+ Adaugă
    firmă” (din listă) — treapta pe fișier rămânea verde. Aici, butonul al cărui handler face apelul îl declară."""
    r = S.masoara_pe_element()
    assert not r["gresite"], "elemente legate de un apel restrâns fără acțiunea lui (%d):\n  %s" % (
        len(r["gresite"]), "\n  ".join("%s:%d %s  pe  %s" % x for x in r["gresite"]))
    n = len(r["nelegate"])
    assert n <= _CLICHET_NELEGATE_PE_ELEMENT, "apeluri nelegabile pe element în creștere: %d > %d" % (
        n, _CLICHET_NELEGATE_PE_ELEMENT)
    assert n == _CLICHET_NELEGATE_PE_ELEMENT, "clichetul e depășit în bine — coboară-l la %d" % n


def test_CALIBRARE_legarea_pe_element():
    """Modurile proprii de eșec, prinse la construcție: (a) `\\b` lega `.dec-recl` de `dec-recl-suma`; (b) o funcție
    chemată din alt loc se lega de handlerul de deasupra ei."""
    t = ('<span class="x dec-recl-suma">1</span><select class="dec-recl" data-actiune="PUT /a"></select>\n'
         'z.querySelectorAll(".dec-recl").forEach((s) => s.addEventListener("change", async () => {\n'
         '  await api.put(`/a`, {});\n}));\n')
    assert S.element_al_apelului(t, t.index("api.put")).startswith('<select class="dec-recl"')
    t2 = ('<button id="b">x</button>\nq.querySelector("#b").addEventListener("click", () => f());\n'
          'return 1;\n}\nasync function alta() {\n  if (x) {\n    await api.post(`/c`, {});\n  }\n}\n')
    assert S.element_al_apelului(t2, t2.index("api.post")) is None, "apel din ALTĂ funcție legat de handlerul de deasupra"


def test_butoanele_de_intrare_in_formular_isi_declara_actiunea():
    """Clasa găsită pe producție (04.10.2026): Ana, fără niciun drept, vedea „+ Notă nouă” — butonul nu cheamă nicio
    rută (deschide editorul), deci treptele de mai sus nu-l văd, iar salvarea ascunsă lăsa un formular fără ieșire.
    Orice buton de intrare („+ …”, „Adaugă…”, „Emite…”) poartă acțiunea formularului sau motivul pentru care nu e una."""
    rele = S.butoane_creare_nemarcate()
    assert not rele, "butoane de intrare fără data-actiune / data-fara-actiune (%d): %s" % (len(rele), rele)
    # anti-vacuu: instrumentul vede butoanele marcate (altfel lista goală ar fi adevărată despre o lume pe care n-o vede)
    import glob
    marcate = sum(len(S._BUTON_CREARE.findall(io.open(f, encoding="utf-8").read()))
                  for f in glob.glob(os.path.join(RAD, "static", "js", "**", "*.js"), recursive=True))
    assert marcate >= 50, "instrumentul vede doar %d butoane de intrare — s-a stricat?" % marcate

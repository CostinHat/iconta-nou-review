# -*- coding: utf-8 -*-
"""scripts/calibreaza_16_7.py — calibrarea rândurilor a (bara de sus: „✕”) și b (acțiunea principală o singură dată) ale verificatorului de design, în ambele direcții, pe ecrane
reale pe 8019 (comanda 16.7, pct.4). Intrarea unică; iese cu 1 la orice abatere de la harta de mai jos și dacă luna reală nu e 11/2026 (facturile din 31.10.2026).
Nu e rulare a porții. Capturile și JSON-urile: ~/calibrare_16_7_capturi/ (în afara depozitului); în depozit intră numai .txt:
docs/dovezi/16_7/calibrare/{calibrare_a.txt, calibrare_b.txt, regresie.txt, jurnal_pytest.log}.
Regulile comune cu matricea (`ruleaza_pe_server`): refuz cu 1 dacă `git status --porcelain --untracked-files=no -- scripts core` nu e gol sau lipsește
~/ghid_incoming/8019_liber_16_7.txt; lacătul testelor; 8019 oprit, baza restaurată, 8019 pornit din worktree (indexul), lucru, apoi oprit și restaurat din nou
(inclusiv la eroare, SIGTERM sau SIGHUP)."""
import contextlib
import datetime
import hashlib
import io
import json
import os
import signal
import subprocess
import sys
import tempfile

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))
import lacat_test as LT  # noqa: E402
import matrice_16_7 as M  # noqa: E402
import verificator_design as VD  # noqa: E402

DOVEZI = os.path.join(RAD, "docs", "dovezi", "16_7")
CALIB = os.path.join(DOVEZI, "calibrare")
CAPTURI = os.path.expanduser("~/calibrare_16_7_capturi")
LIBER = os.path.expanduser("~/ghid_incoming/8019_liber_16_7.txt")
FISIERE_VERIFICATOR = ("scripts/verificator_design.py", "scripts/verificator_design_masuri.js")
REZ = ("1920x1080", "1366x768")
JURNAL_COMUN = os.path.expanduser("~/iconta_nou/.lot_jurnal.log")


def git(*a):
    return subprocess.run(["git", *a], cwd=RAD, capture_output=True, text=True, check=True).stdout


def sha256(cale):
    return hashlib.sha256(open(os.path.join(RAD, cale), "rb").read()).hexdigest()


def linie_sha():
    return "sha=%s " % git("rev-parse", "HEAD").strip() + " ".join("%s=%s" % (f, sha256(f)) for f in FISIERE_VERIFICATOR)


def restaureaza():
    subprocess.run(["sh", "scripts/baza_test.sh", "restaureaza"], cwd=RAD, capture_output=True, text=True)


def ruleaza_pe_server(nume, corp, scrie_sha=None):
    """Regulile comune ale calibrării și ale matricei; -> codul de ieșire."""
    murdar = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no", "--", "scripts", "core"], cwd=RAD, capture_output=True, text=True).stdout.strip()
    if murdar:
        print("[%s] REFUZ: scripts/ sau core/ au modificări necomise:\n%s" % (nume, murdar), file=sys.stderr)
        return 1
    if not os.path.exists(LIBER):
        print("[%s] REFUZ: lipsește %s (8019 neeliberat de arhitect)" % (nume, LIBER), file=sys.stderr)
        return 1
    if LT.ia(os.getpid(), nume):
        return 1
    os.environ["LACAT_TEST_PID"] = str(os.getpid())   # opreste/restaureaza lansate de aici nu sunt refuzate de lacăt

    def iesire(semnal, _cadru):
        raise SystemExit(128 + semnal)
    for s in (signal.SIGTERM, signal.SIGHUP):
        signal.signal(s, iesire)
    try:
        VD.opreste()
        restaureaza()
        if VD.porneste() != 0:
            print("[%s] 8019 n-a pornit" % nume, file=sys.stderr)
            return 1
        stare = json.load(open(VD.STARE))
        if stare["sha"] != git("rev-parse", "HEAD").strip():
            print("[%s] REFUZ: serverul 8019 rulează %s, nu HEAD" % (nume, stare["sha"][:8]), file=sys.stderr)
            return 1
        if scrie_sha:
            os.makedirs(os.path.dirname(scrie_sha), exist_ok=True)
            open(scrie_sha, "w", encoding="utf-8").write(linie_sha() + "\n")
        return corp()
    finally:
        VD.opreste()
        restaureaza()


# ── harta ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
_F = "const F=[...document.querySelectorAll('.fereastra')].pop();"
_X40 = ("F.querySelectorAll('.fereastra-antet .nav-x').forEach(x=>{x.style.boxSizing='border-box';x.style.padding='0';x.style.flex='none';"
             "x.style.width='40px';x.style.height='40px';x.style.minWidth='40px';x.style.minHeight='40px';});")
_REVERSE = "F.querySelector('.fereastra-antet').style.flexDirection='row-reverse';"
_CLONA = "const x=F.querySelector('.fereastra-antet .nav-x');x.parentNode.appendChild(x.cloneNode(true));"
_ADAUGA_X = ("const a=F.querySelector('.fereastra-antet');const x=document.createElement('button');x.className='nav-x';x.textContent='✕';"
                  "x.style.cssText='box-sizing:border-box;padding:0;flex:none;width:40px;height:40px;min-width:40px;min-height:40px;';a.appendChild(x);")


def _buton_in_continut(text):
    return ("const c=F.querySelector('.fereastra-corp');const b=document.createElement('button');b.textContent='%s';c.appendChild(b);" % text)


def _buton_in_details_si_tabel(text):
    return ("const c=F.querySelector('.fereastra-corp');const d=document.createElement('details');d.open=true;"
                 "d.innerHTML='<summary>detalii</summary><button>%s</button>';c.appendChild(d);"
                 "const t=document.createElement('table');t.innerHTML='<tbody><tr><td><button>%s</button></td></tr></tbody>';c.appendChild(t);" % (text, text))


def motive_x(js):
    return [m for m in js["pica"]["a"] if M.e_motiv_x(m)]


def dubluri(js):
    return [m for m in js["pica"]["b"] if m.startswith("acțiunea principală „") and "apare și în conținut" in m]


#: id | ecran | interventie | verificare(js) -> (ok, obținut)
def _a1(js):
    mx = motive_x(js)
    return any(m.startswith("lipsește „✕”") for m in mx) and js["pica"]["a"] != [], "; ".join(mx) or "niciun motiv ✕"


def _a3(js):
    mx = motive_x(js)
    return js["fapte"]["a"].get("x") == 1 and mx == ["„✕” nu e de 40 × 40 (34 × 34)"], "x=%s; %s" % (js["fapte"]["a"].get("x"), "; ".join(mx) or "niciun motiv ✕")


def _a4(js):
    return not motive_x(js), "; ".join(motive_x(js)) or "niciun motiv ✕"


def _a5(js):
    mx = motive_x(js)
    return len(mx) == 1 and mx[0].startswith("„✕” nu e în dreapta sus"), "; ".join(mx) or "niciun motiv ✕"


def _a6(js):
    mx = motive_x(js)
    return len(mx) == 1 and mx[0].startswith("2 butoane „✕”"), "; ".join(mx) or "niciun motiv ✕"


def _a7(js):
    return not js["pica"]["a"], "; ".join(js["pica"]["a"]) or "rândul a TRECE"


def _b_pica(text):
    def f(js):
        d = dubluri(js)
        return bool(js["pica"]["b"]) and any("„%s”" % text in m for m in d), "; ".join(d) or "fără motiv de dublare"
    return f


def _b_trece(js):
    return not js["pica"]["b"] and js["fapte"]["b"].get("actiune_dubla") == 0, "; ".join(js["pica"]["b"]) or "rândul b TRECE"


def _b_fara_dublare(js):
    return not dubluri(js) and js["fapte"]["b"].get("actiune_dubla") == 0, "; ".join(dubluri(js)) or "fără motiv de dublare"


HARTA_A = [
    ("a.1", "Registru jurnal F1", None, _a1),
    ("a.2", "Stat de plată F5", None, _a1),
    ("a.3", M.FEREASTRA_MICA, None, _a3),
    ("a.4", M.FEREASTRA_MICA, _X40, _a4),
    ("a.5", M.FEREASTRA_MICA, _X40 + _REVERSE, _a5),
    ("a.6", M.FEREASTRA_MICA, _X40 + _CLONA, _a6),
    ("a.7", "Registru jurnal F1", _ADAUGA_X, _a7),
]
HARTA_B = [
    ("b.1", "Stocuri F1", None, _b_pica("+ NIR nou")),
    ("b.2", "Raport Z F1", None, _b_pica("Generează notă")),
    ("b.3", "Registru jurnal F1", None, _b_pica("+ Notă nouă")),
    ("b.4", "Stat de plată F5", None, _b_pica("Contabilizează statul")),
    ("b.5", "Cartea mare F1", _buton_in_continut("Descarcă PDF"), _b_pica("Descarcă PDF")),
    ("b.6", "Cartea mare F1", None, _b_trece),
    ("b.7", "Închidere lună F1", None, _b_trece),
    ("b.8", "Cartea mare F1", _buton_in_details_si_tabel("Descarcă PDF"), _b_fara_dublare),
    ("b.9", "Firme", None, _b_fara_dublare),
]
MARTORI = ["Registru jurnal F1", "Stat de plată F5", "Stocuri F1", "Raport Z F1", "Cartea mare F1", "Închidere lună F1", "Firme", "Sinteza zilei",
           "Panou Admin — Raportări", "Control fiscal", "Emite factură F1", "Bancă F1"]


def deschide(nume, rez, interventie=None, masuri_alt=None):
    """-> js (măsurătorile) sau None; JSON-ul vechi se șterge întâi. Intervenția (corp JS) se învelește într-o funcție cu `F` = ultima fereastră de lucru."""
    if interventie:
        interventie = "(() => {" + _F + interventie + "})()"
    cale = os.path.join(CAPTURI, "%s_%s.json" % (VD.slug(nume), rez))
    if os.path.exists(cale):
        os.remove(cale)
    with contextlib.redirect_stdout(io.StringIO()):
        cod = VD.ecran(nume, rez, CAPTURI, interventie=interventie, masuri_alt=masuri_alt, director_png=CAPTURI)
    if cod != 0 or not os.path.exists(cale):
        return None
    return json.load(open(cale, encoding="utf-8"))


def harta(harta_, titlu, antet):
    linii, abateri = [antet, titlu], 0
    for id_, ecran, interventie, verifica in harta_:
        for rez in REZ:
            js = deschide(ecran, rez, interventie)
            if js is None:
                ok, obtinut = False, "ecranul nu s-a deschis"
            elif js.get("eroare_deschidere"):
                ok, obtinut = False, "eroare la deschidere: %s" % js["eroare_deschidere"]
            else:
                ok, obtinut = verifica(js)
            abateri += not ok
            linii.append("%s | %s | %s | %s | %s" % (id_, ecran, rez, "ATINS" if ok else "RATAT", obtinut))
            print(linii[-1], flush=True)
    return linii, abateri


def masuri_baza():
    baza = git("merge-base", "HEAD", "main").strip()
    cale = os.path.join(tempfile.gettempdir(), "masuri_baza_16_7.js")
    open(cale, "w", encoding="utf-8").write(git("show", "%s:scripts/verificator_design_masuri.js" % baza))
    return baza, cale


def regresie(antet):
    baza, cale = masuri_baza()
    linii, k = [antet, "regresie: %d ecrane martor × 2 rezoluții; măsurătorile de la baza %s (masuri_alt) față de cele noi, pe aceeași pagină" % (len(MARTORI), baza[:8])], 0
    for nume in MARTORI:
        for rez in REZ:
            js = deschide(nume, rez, masuri_alt=cale)
            if js is None or "masuri_alt" not in js:
                linii.append("%s | %s | NEDESCHIS" % (nume, rez))
                k += 1
                continue
            vechi, nou = js["masuri_alt"]["pica"], js["pica"]
            dif = []
            for r in "cdefgh":
                if vechi[r] != nou[r]:
                    dif.append("rândul %s: vechi %s, nou %s" % (r, vechi[r], nou[r]))
            asteptat_a = [m for m in vechi["a"] if not m.startswith(("lipsește „←”", "„←” nu e vizibil de 40 × 40")) and m != "„✕” în bara de sus"]
            if [m for m in nou["a"] if not M.e_motiv_x(m)] != asteptat_a:
                dif.append("rândul a: vechi %s, nou %s" % (vechi["a"], nou["a"]))
            if [m for m in nou["b"] if m not in dubluri(js)] != vechi["b"]:
                dif.append("rândul b: vechi %s, nou %s" % (vechi["b"], nou["b"]))
            k += bool(dif)
            linii.append("%s | %s | %s" % (nume, rez, "; ".join(dif) or "la fel (rândurile c–h identice; a și b după regula nouă)"))
            print(linii[-1], flush=True)
    linii.append("k (diferențe) = %d" % k)
    return linii, k


def randuri_16_7():
    try:
        return sum(1 for ln in open(JURNAL_COMUN, encoding="utf-8") if ln.startswith("16.7\t"))
    except OSError:
        return 0


def test_pur(antet):
    """Testul nou în subproces pytest, cu LOT_JURNAL propriu: roșu pe verificatorul de la bază (rădăcină temporară = copia lui scripts/ de pe HEAD, cele două fișiere
    suprascrise din bază, plus core/catalog_ecrane.json), verde pe cel nou. Rândurile lot=16.7 din jurnalul comun, înainte și după fiecare."""
    baza = git("merge-base", "HEAD", "main").strip()
    env = dict(os.environ, LOT_JURNAL=os.path.join(CALIB, "jurnal_pytest.log"))
    cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", os.path.join(RAD, "core", "test_verificator_design_16_7.py")]
    linii, abateri = [antet], 0
    with tempfile.TemporaryDirectory(prefix="calib_16_7_") as tmp:
        subprocess.run(["cp", "-r", os.path.join(RAD, "scripts"), os.path.join(tmp, "scripts")], check=True)
        os.makedirs(os.path.join(tmp, "core"))
        subprocess.run(["cp", os.path.join(RAD, "core", "catalog_ecrane.json"), os.path.join(tmp, "core")], check=True)
        for f in FISIERE_VERIFICATOR:
            open(os.path.join(tmp, f), "w", encoding="utf-8").write(git("show", "%s:%s" % (baza, f)))
        for nume, rad, vrem in (("roșu pe verificatorul de la bază", tmp, "rosu"), ("verde pe verificatorul nou", RAD, "verde")):
            inainte = randuri_16_7()
            p = subprocess.run(cmd, cwd=RAD, capture_output=True, text=True, env=dict(env, VERIFICATOR_RAD_16_7=rad))
            dupa = randuri_16_7()
            ies = p.stdout + p.stderr
            if vrem == "rosu":
                ok = p.returncode != 0 and "AssertionError" in ies and "FileNotFoundError" not in ies and "ImportError" not in ies and "ModuleNotFoundError" not in ies
            else:
                ok = p.returncode == 0
            abateri += not ok
            linii.append("testul nou, %s: %s (cod %d; %s); rânduri lot=16.7 în jurnalul comun înainte %d, după %d, diferență %d" % (
                nume, "ATINS" if ok else "RATAT", p.returncode, (ies.strip().splitlines() or [""])[-1][:140], inainte, dupa, dupa - inainte))
            print(linii[-1], flush=True)
            abateri += dupa != inainte
    return linii, abateri


def corp():
    antet = linie_sha()
    os.makedirs(CALIB, exist_ok=True)
    os.makedirs(CAPTURI, exist_ok=True)
    total = 0
    linii, ab = harta(HARTA_A, "calibrare a (bara de sus: „✕”), fiecare caz la 1920x1080 și 1366x768", antet)
    open(os.path.join(CALIB, "calibrare_a.txt"), "w", encoding="utf-8").write("\n".join(linii) + "\n")
    total += ab
    linii, ab = harta(HARTA_B, "calibrare b (acțiunea principală o singură dată)", antet)
    total += ab
    linii_t, ab_t = test_pur(antet)
    open(os.path.join(CALIB, "calibrare_b.txt"), "w", encoding="utf-8").write("\n".join(linii + ["", "testul nou (core/test_verificator_design_16_7.py):"] + linii_t[1:]) + "\n")
    total += ab_t
    linii, k = regresie(antet)
    open(os.path.join(CALIB, "regresie.txt"), "w", encoding="utf-8").write("\n".join(linii) + "\n")
    print("[calibreaza_16_7] abateri de la harta: %d; regresie k=%d" % (total, k))
    return 1 if total else 0


def main():
    azi = datetime.date.today()
    if (azi.year, azi.month) != (2026, 11):
        print("[calibreaza_16_7] luna reală nu e 11/2026 (%s): OPRIT — gata: 16.7 nepublicat, luna reala nu e 11/2026" % azi, file=sys.stderr)
        return 1
    return ruleaza_pe_server("calibreaza_16_7.py", corp)


if __name__ == "__main__":
    sys.exit(main())

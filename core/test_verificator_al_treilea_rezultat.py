# -*- coding: utf-8 -*-
"""GARD [31.08.2026, cerut de Costin]: verificatorul de neconformități nu mai afirmă absența când
n-a putut verifica.

DE UNDE VINE, cu instanța ei. `verificator_neconformitati.sh` tipărea
*„FAIL NC-07 JWT_SECRET lipsește din proces!"* când `sudo` nu e disponibil neinteractiv. **Secretul
era acolo**; ce lipsea era dreptul de a te uita. *Un blocaj care afirmă absența când de fapt n-a
putut verifica e blocaj fără temei* — aceeași clasă cu „un necunoscut nu se rotunjește la «știu că
nu»" (interdicția 32/10, R39). Normă: `CONFORMITATE.md` 77.

**Reparația e un al treilea rezultat, nu mai multe drepturi.** Setul de sudoers rămâne îngust: un
verificator care are nevoie de drepturi în plus ca să spună adevărul cere să fie crezut pe încredere.

MĂSURAT ÎNAINTE DE REPARAȚIE (31.08), pe scriptul real, nu pe presupuneri — **o formă VIE, trei
LATENTE**, iar una dintre cele latente greșește în direcția OPUSĂ (METODA §22):

  VIE      NC-07 · `sudo` indisponibil            → raporta absența secretului
  LATENTĂ  interogarea care nu rulează            → șir gol ≠ „0" → FAIL
  LATENTĂ  fișierul care lipsește                 → `grep` eșuează → FAIL
  LATENTĂ  globul care nu potrivește nimic        → `wc -l` dă 0 → **PASS** pe mulțime goală
  Plus     ancora ștearsă de o rescriere legitimă → FAIL pe vecie, despre un obiect inexistent
  Plus     `EXIT=0` peste `FAIL: 3`               → rezumatul spunea roșu, codul de ieșire verde

CE FACE IMPOSIBIL: ca oricare dintre cele șase să se întoarcă — fiecare are testul ei, iar fiecare
test are **direcția inversă** lângă el (o neconformitate reală trebuie să rămână FAIL, altfel
„repararea" ar fi doar amuțirea verificatorului).

CE NU FACE, declarat:
  - **nu verifică dacă NC-urile în sine sunt bine alese** — asta e o judecată din 09.07.2026;
  - **nu execută verificările reale** (ar cere baza, procesul viu și sudo). Se sursează funcțiile
    și se exercită **clasificarea**, care e exact partea care mințea;
  - **nu apără codul de ieșire împotriva unui apelant care-l ignoră** — azi scriptul se rulează cu
    mâna și nu-l consumă nimic programatic (măsurat: zero apelanți în `.py`/`.sh`).
"""
import os
import re
import subprocess

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: Implicit = scriptul din repo. `VERIF_NC_SCRIPT` e un SEAM de probă: proba prin mutație copiază
#: scriptul, îi scoate câte o apărare, și cere ca testul corespunzător să devină roșu. În poartă
#: variabila nu e setată niciodată — `test_seamul_de_proba_nu_e_activ_in_poarta` o cere explicit,
#: ca seam-ul să nu poată deveni o cale prin care gardul păzește alt fișier decât cel livrat.
_SCRIPT = os.environ.get("VERIF_NC_SCRIPT") or os.path.join(_RAD, "verificator_neconformitati.sh")

#: Cele cinci funcții pe care le exercită gardul. Dacă una dispare din script, testele de mai jos
#: ar trece pe o listă goală de rânduri — deci absența lor e eșec, nu tăcere (anti-vacuu).
FUNCTII = {"pass", "esec", "neverif", "psqlv", "db0", "marker", "fara_tipar", "env_proces"}

_RE_RAND = re.compile(r"^(PASS|FAIL|NEVERIF|INFO)\s+(\S+)\s+(.*)$")
#: Codul dintre paranteze drepte de pe un rand NEVERIF. E STABIL si se probeaza; motivul de dupa
#: el e pentru om si se poate rescrie fara sa cada nimic.
_RE_COD = re.compile(r"\[([a-z-]+)\]")
CODURI = {"interogare-neexecutata", "fisier-ilizibil", "ancora-moarta", "glob-gol",
          "proces-negasit", "sudo-indisponibil", "proc-necitibil"}


def _ruleaza(corp, mediu=None):
    """Sursează scriptul (doar funcțiile) și rulează `corp`. Întoarce (rânduri, cod).

    `rânduri` sunt STRUCTURI — `[{verdict, nc, restul}]` —, nu text: comparațiile de mai jos se fac
    pe câmpuri, nu pe subșiruri (METODA §23 / clichetul 50).
    """
    env = dict(os.environ, VERIF_NC_DOAR_FUNCTII="1")
    env.update(mediu or {})
    scr = 'set +e\nsource "%s"\n%s\n' % (_SCRIPT, corp)
    r = subprocess.run(["bash", "-c", scr], capture_output=True, text=True, timeout=120, env=env)
    randuri = []
    for linie in r.stdout.splitlines():
        m = _RE_RAND.match(linie.strip())
        if m:
            c = _RE_COD.search(m.group(3))
            randuri.append({"verdict": m.group(1), "nc": m.group(2), "restul": m.group(3),
                            "cod": c.group(1) if c else None})
    return randuri, r.returncode


def _verdicte(corp, mediu=None):
    return [x["verdict"] for x in _ruleaza(corp, mediu)[0]]


def _cu_cod(corp, mediu=None):
    """[(verdict, cod)] — perechea pe care se face aserțiunea. Un verdict fără codul lui nu
    deosebește două ramuri care ajung la aceeași concluzie din motive diferite, iar o mutație care
    scoate una dintre ele rămâne verde. S-a întâmplat: 2 din 7 la prima probă prin mutație."""
    return [(x["verdict"], x["cod"]) for x in _ruleaza(corp, mediu)[0]]


def _fals_rad(tmp_path, fisiere):
    """Construiește o rădăcină sintetică. `fisiere` = {cale relativă: conținut}."""
    for cale, continut in fisiere.items():
        f = tmp_path / cale
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(continut, encoding="utf-8")
    return str(tmp_path)


# ── ANTI-VACUU: scriptul chiar se sursează și chiar definește funcțiile ────────────────────────

def test_seamul_de_proba_nu_e_activ_in_poarta():
    """Seam-ul care permite proba prin mutație e și o cale prin care gardul ar putea păzi ALT
    fișier decât cel livrat. În poartă nu are voie să fie setat: dacă e, gardul e verde despre o
    copie, iar scriptul real n-a fost atins de nimeni."""
    assert _SCRIPT == os.path.join(_RAD, "verificator_neconformitati.sh"), (
        "VERIF_NC_SCRIPT e setat (%r) — gardul păzește o copie, nu scriptul din repo" % _SCRIPT)


def test_ANTI_VACUU_scriptul_se_surseaza_si_defineste_functiile():
    """Fără asta, fiecare test de mai jos ar rula pe zero rânduri și ar trece — forma de orbire
    prin construcție cea mai ieftină: redenumești o funcție, gardul tace."""
    assert os.path.exists(_SCRIPT), "verificatorul a dispărut: %s" % _SCRIPT
    r = subprocess.run(["bash", "-c", 'source "%s"; declare -F | awk "{print \\$3}"' % _SCRIPT],
                       capture_output=True, text=True, timeout=60,
                       env=dict(os.environ, VERIF_NC_DOAR_FUNCTII="1"))
    definite = set(r.stdout.split())
    assert definite >= FUNCTII, (
        "[anti-vacuu] funcții lipsă din verificator: %s — testele de clasificare ar trece pe nimic"
        % sorted(FUNCTII - definite))


def test_ANTI_VACUU_sursarea_NU_ruleaza_verificarile():
    """Dacă sursarea ar executa corpul, fiecare test ar atinge baza și procesul viu — iar gardul ar
    deveni el însuși un efect secundar."""
    randuri, _ = _ruleaza("true")
    assert randuri == [], "sursarea a produs rânduri de verdict: %s" % randuri[:3]


# ── FIȘIERUL CARE LIPSEȘTE ─────────────────────────────────────────────────────────────────────

def test_fisier_ILIZIBIL_da_NEVERIF_nu_FAIL(tmp_path):
    """Markerul e pus DELIBERAT într-un alt fișier din rădăcină: fără precondiția de citire,
    execuția ar cădea pe ramura „ancora s-a mutat" și ar da FAIL. Așa, cele două ramuri se
    deosebesc — altfel testul ar trece și cu precondiția scoasă, iar mutația ar rămâne verde.
    *S-a întâmplat: prima probă prin mutație a dat 5 roșii din 7, iar asta era una dintre cele
    două care n-au căzut.*"""
    rad = _fals_rad(tmp_path, {"altul.py": "are m_oarecare\n"})
    v = _cu_cod('RAD=%s; marker "NC-X" "d" "m_oarecare" "%s/nu_exista.py"' % (rad, rad))
    assert v == [("NEVERIF", "fisier-ilizibil")], (
        "un fișier care nu se poate citi a fost raportat ca %s — verificatorul afirmă "
        "neconformitate despre un fișier pe care nu l-a deschis" % v)


# ── ANCORA: prezentă / moartă / mutată — trei stări, nu două ───────────────────────────────────

def test_ancora_PREZENTA_da_PASS(tmp_path):
    rad = _fals_rad(tmp_path, {"t.py": "are marker_xyz aici\n"})
    assert _verdicte('RAD=%s; marker "NC-X" "d" "marker_xyz" "%s/t.py"' % (rad, rad)) == ["PASS"]


def test_ancora_MOARTA_da_NEVERIF(tmp_path):
    """Instanța reală: `fix_serie_contare_v1` a fost scos de commitul `55a57f6`, o rescriere
    legitimă a contării. Verificarea nu mai are obiect — nu codul și-a pierdut conformitatea."""
    rad = _fals_rad(tmp_path, {"t.py": "fara nimic\n"})
    v = _cu_cod('RAD=%s; marker "NC-X" "d" "marker_disparut" "%s/t.py"' % (rad, rad))
    assert v == [("NEVERIF", "ancora-moarta")], (
        "o ancoră care nu mai există nicăieri a fost raportată ca %s — verificatorul ar acuza pe "
        "vecie un cod care n-a greșit" % v)


def test_CALIBRARE_ancora_MUTATA_ramane_FAIL(tmp_path):
    """Direcția inversă, obligatorie: „reparația" nu are voie să amuțească verificatorul. Dacă
    markerul există în ALT fișier, verificarea chiar a eșuat."""
    rad = _fals_rad(tmp_path, {"t.py": "fara\n", "alt.py": "are marker_mutat\n"})
    v = _verdicte('RAD=%s; marker "NC-X" "d" "marker_mutat" "%s/t.py"' % (rad, rad))
    assert v == ["FAIL"], "o ancoră mutată în alt fișier a fost raportată ca %s, nu FAIL" % v


def test_cautarea_de_ancora_NU_intra_in_git(tmp_path):
    """REGRESIE PE UN BUG PROPRIU, făcut chiar scriind garda asta. Prima formă folosea
    `grep -rq -- "$m" "$RAD" --include=...`; `--` oprește parsarea opțiunilor, deci `--include`
    devenea NUME DE FIȘIER, iar căutarea intra în `.git` și potrivea în packfile-uri. Rezultatul:
    „ancora s-a mutat" despre un marker care nu mai există nicăieri. *Prins măsurând, nu citind.*"""
    rad = _fals_rad(tmp_path, {"t.py": "fara\n", ".git/objects/pack/x.py": "marker_ingropat\n"})
    v = _cu_cod('RAD=%s; marker "NC-X" "d" "marker_ingropat" "%s/t.py"' % (rad, rad))
    assert v == [("NEVERIF", "ancora-moarta")], (
        "căutarea de ancoră a intrat în `.git` și a raportat %s — un marker din istoria git nu e "
        "cod viu" % v)


# ── INTEROGAREA CARE NU RULEAZĂ ────────────────────────────────────────────────────────────────

def test_interogarea_care_NU_RULEAZA_da_NEVERIF_nu_FAIL():
    v = _cu_cod('psqlv() { return 1; }; db0 "NC-X" "d" "SELECT 1"')
    assert v == [("NEVERIF", "interogare-neexecutata")], (
        "o interogare care n-a rulat a fost raportată ca %s — forma veche întorcea șir gol, iar "
        "un șir gol nu e «0», deci ieșea FAIL despre date pe care nu le-a citit nimeni" % v)


def test_CALIBRARE_interogarea_care_RULEAZA_pastreaza_PASS_si_FAIL():
    assert _verdicte('psqlv() { printf 0; }; db0 "NC-X" "d" "S"') == ["PASS"]
    assert _verdicte('psqlv() { printf 3; }; db0 "NC-X" "d" "S"') == ["FAIL"], (
        "un rezultat nenul nu mai produce FAIL — reparația ar fi amuțit verificatorul")


# ── GLOBUL GOL: direcția OPUSĂ, cea care raporta PASS ──────────────────────────────────────────

def test_glob_GOL_da_NEVERIF_nu_PASS(tmp_path):
    """Cea mai rea dintre cele patru, fiindcă greșea în direcția liniștitoare: `grep | wc -l` pe
    zero fișiere dă 0, iar 0 însemna «zero apariții, conform». Un zero pe mulțime goală arată
    identic cu un zero real (METODA §22)."""
    gol = tmp_path / "gol"
    gol.mkdir()
    v = _cu_cod('E=%s; fara_tipar "NC-X" "d" "alert(" ".bak"' % gol)
    assert v == [("NEVERIF", "glob-gol")], (
        "un director fără niciun .js a fost raportat ca %s — verificatorul ar declara conformitate "
        "despre o mulțime pe care n-a scanat-o" % v)


def test_CALIBRARE_glob_cu_fisiere_pastreaza_PASS_si_FAIL(tmp_path):
    d = tmp_path / "ecrane"
    d.mkdir()
    (d / "a.js").write_text("nimic interzis\n", encoding="utf-8")
    assert _verdicte('E=%s; fara_tipar "NC-X" "d" "alert(" ".bak"' % d) == ["PASS"]
    (d / "b.js").write_text("alert(1)\n", encoding="utf-8")
    assert _verdicte('E=%s; fara_tipar "NC-X" "d" "alert(" ".bak"' % d) == ["FAIL"], (
        "o apariție reală nu mai produce FAIL")


# ── MEDIUL PROCESULUI VIU: instanța care a deschis clasa ───────────────────────────────────────

def test_proces_NEGASIT_da_NEVERIF():
    v = _cu_cod('pgrep() { return 1; }; env_proces "NC-07" "JWT_SECRET"')
    assert v == [("NEVERIF", "proces-negasit")], (
        "fără procesul viu, verificatorul a raportat %s despre mediul lui" % v)


def test_sudo_INDISPONIBIL_da_NEVERIF_nu_FAIL():
    """INSTANȚA CARE A DESCHIS CLASA, în forma ei exactă: procesul există, secretul e acolo, dar
    `sudo` nu răspunde neinteractiv."""
    v = _cu_cod('pgrep() { echo 1234; }; sudo() { return 1; }; env_proces "NC-07" "JWT_SECRET"')
    assert v == [("NEVERIF", "sudo-indisponibil")], (
        "cu `sudo` indisponibil, verificatorul a raportat %s — exact propoziția pentru care există "
        "gardul ăsta: «JWT_SECRET lipsește din proces», despre un secret care era acolo" % v)


def test_proc_NECITIBIL_da_NEVERIF_nu_FAIL():
    """RAMURA PORTANTĂ pentru verdict, și are nevoie de test propriu. `sudo` răspunde la `true`,
    deci verificarea de drepturi trece — dar citirea lui `/proc/<pid>/environ` eșuează oricum
    (proces dispărut între timp, namespace, hardening). Fără al treilea rezultat aici, `mediu`
    rămâne gol, `grep` nu găsește nimic, și iese **FAIL** — exact minciuna originală, pe alt drum.

    *Testul ăsta există fiindcă proba prin mutație a arătat că ramura de dinainte (mesajul
    „sudo indisponibil") o acoperea: scoteam apărarea portantă și gardul rămânea verde.*"""
    fals = ('pgrep() { echo 1234; }; '
            'sudo() { if [ "$2" = "true" ]; then return 0; fi; return 1; }; ')
    v = _cu_cod(fals + 'env_proces "NC-07" "JWT_SECRET"')
    assert v == [("NEVERIF", "proc-necitibil")], (
        "citirea eșuată a mediului procesului a fost raportată ca %s — verificatorul afirmă că "
        "secretul lipsește dintr-un mediu pe care nu l-a putut citi" % v)


def test_CALIBRARE_cu_sudo_disponibil_secretul_lipsa_ramane_FAIL():
    """Direcția inversă: dacă chiar se poate citi și chiar lipsește, e FAIL. Altfel gardul ar fi
    transformat o neconformitate reală de securitate într-un «n-am putut verifica»."""
    fals = ('pgrep() { echo 1234; }; '
            'sudo() { if [ "$2" = "true" ] || [ "$1" = "-n" -a "$2" = "true" ]; then return 0; fi; '
            'printf "ALTCEVA=1\\n"; return 0; }; ')
    assert _verdicte(fals + 'env_proces "NC-07" "JWT_SECRET"') == ["FAIL"]
    fals_ok = ('pgrep() { echo 1234; }; '
               'sudo() { if [ "$2" = "true" ]; then return 0; fi; printf "JWT_SECRET=x\\n"; }; ')
    assert _verdicte(fals_ok + 'env_proces "NC-07" "JWT_SECRET"') == ["PASS"]


# ── CODUL DE IEȘIRE NU MAI CONTRAZICE REZUMATUL ────────────────────────────────────────────────

def test_codul_de_iesire_e_ACELASI_lucru_cu_rezumatul():
    """A treia față a bolii: scriptul tipărea `FAIL: 3` și ieșea cu **0**. Se rulează întreg, pe
    starea reală (oricare ar fi ea), și se cere ca cifrele din rezumat și codul de ieșire să spună
    același lucru: 1 dacă există FAIL · 2 dacă nu, dar există NEVERIF · 0 altfel."""
    r = subprocess.run(["bash", _SCRIPT], capture_output=True, text=True, timeout=300, cwd=_RAD)
    m = re.search(r"^PASS:\s*(\d+)\s+FAIL:\s*(\d+)\s+NEVERIF:\s*(\d+)\s*$", r.stdout, re.M)
    assert m, "rezumatul nu mai poartă cele trei cifre — nu se poate confrunta cu codul de ieșire"
    p, f, n = (int(x) for x in m.groups())
    assert p + f + n > 10, "[anti-vacuu] doar %d verificări rulate — scriptul s-a golit" % (p + f + n)
    asteptat = 1 if f else (2 if n else 0)
    assert r.returncode == asteptat, (
        "rezumatul spune PASS %d / FAIL %d / NEVERIF %d, dar codul de ieșire e %d, nu %d — o rulare "
        "oarbă sau roșie nu are voie să arate verde pentru cine citește doar codul"
        % (p, f, n, r.returncode, asteptat))


def test_NC02_isi_pastreaza_verificarea_COMPORTAMENTALA():
    """Temeiul unei RETRAGERI, gardat — altfel se erodează în tăcere.

    Ancora pe marker a lui NC-02 (`fix_serie_contare_v1`) a fost **retrasă** pe 31.08, la cererea lui
    Costin. Motivul: markerul fusese scos de commitul `55a57f6`, o rescriere legitimă a contării —
    verificarea își pierduse obiectul, nu codul conformitatea. *Retragerea e justificată de un singur
    fapt: ce voia să apere e deja apărat de verificarea **comportamentală** de deasupra ei, care se
    uită la DATE (`descrieri contare fara MD-MD`), nu la un șir din cod.*

    Dacă dispare și aceea, NC-02 rămâne complet neverificat, iar motivul scris în script devine fals
    — fără ca nimic să se aprindă. De-aia se cere aici: NC-02 trebuie să producă cel puțin un rând.
    Un `NEVERIF` e acceptat (interogarea poate să nu ruleze); **absența** nu.
    """
    r = subprocess.run(["bash", _SCRIPT], capture_output=True, text=True, timeout=300, cwd=_RAD)
    randuri = [_RE_RAND.match(x.strip()) for x in r.stdout.splitlines()]
    nc02 = [m.group(1) for m in randuri if m and m.group(2) == "NC-02"]
    assert nc02, (
        "NC-02 nu mai produce niciun rând. Ancora pe marker a fost retrasă tocmai fiindcă "
        "verificarea comportamentală o acoperă — dacă a dispărut și ea, retragerea a rămas fără "
        "temei, iar NC-02 nu mai e verificat de nimeni.")
    assert set(nc02) <= {"PASS", "FAIL", "NEVERIF"}, "verdict necunoscut pe NC-02: %s" % nc02


def test_ancora_RETRASA_nu_se_intoarce_pe_furis():
    """Direcția inversă a retragerii: cineva „repară" NC-02 punând la loc o verificare pe marker.
    Ar arăta ca o îmbunătățire și ar reintroduce exact clasa — o ancoră pe PREZENȚA unei reparații,
    care moare la prima rescriere legitimă. Se cere ca NC-02 să nu aibă mai mult de un rând: cel
    comportamental. Dacă chiar trebuie re-ancorat, decizia se ia explicit și testul se schimbă odată
    cu ea — ceea ce e chiar scopul."""
    r = subprocess.run(["bash", _SCRIPT], capture_output=True, text=True, timeout=300, cwd=_RAD)
    randuri = [_RE_RAND.match(x.strip()) for x in r.stdout.splitlines()]
    nc02 = [m.group(3) for m in randuri if m and m.group(2) == "NC-02"]
    assert len(nc02) == 1, (
        "NC-02 are %d rânduri, nu unul: %s — ancora pe marker a fost retrasă prin decizie "
        "(31.08.2026, motivul e scris în script). O verificare nouă pe NC-02 se adaugă prin decizie, "
        "nu pe furiș." % (len(nc02), nc02))


def test_rezumatul_SPUNE_cand_rularea_nu_e_completa():
    """Un NEVERIF care nu se vede în rezumat e la fel de bun ca unul care nu există: cine citește
    doar ultimele rânduri ar pleca crezând că s-a verificat tot."""
    r = subprocess.run(["bash", _SCRIPT], capture_output=True, text=True, timeout=300, cwd=_RAD)
    linii = [x.strip() for x in r.stdout.splitlines()]
    n_randuri = len([x for x in linii if _RE_RAND.match(x)
                     and _RE_RAND.match(x).group(1) == "NEVERIF"])
    avertisment = [x for x in linii if x.startswith("ATENTIE:")]
    if n_randuri:
        assert avertisment, (
            "%d rânduri NEVERIF, dar rezumatul nu avertizează — rularea incompletă trece drept "
            "completă" % n_randuri)
    else:
        assert not avertisment, "avertisment de rulare incompletă fără niciun NEVERIF"

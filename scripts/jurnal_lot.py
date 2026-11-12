# -*- coding: utf-8 -*-
"""scripts/jurnal_lot.py — jurnalul lotului, scris de scripturi (comanda 16.1, pct.2). Fișier: <rădăcina depozitului principal>/.lot_jurnal.log (ignorat de git;
LOT_JURNAL îl mută în teste). Un rând = un eveniment, câmpuri separate prin TAB:
    lot, faza, eveniment (inceput|sfarsit), ora ISO, sha, rezultat, id-ul rulării, pid, detalii
O fază cu început fără sfârșit, al cărei proces nu mai trăiește, e marcată „intrerupt” de următorul script care scrie în jurnal (niciodată absentă sau verde).
Fazele obligatorii (aceeași listă la publica_lot.sh): pornire, hook, verificator, verificator_poarta, pytest, plasa_e2e, publicare.
  inceput <lot> <faza> [detalii]            scrie începutul, tipărește id-ul rulării
  sfarsit <lot> <faza> <id> <rezultat> [detalii]
  pornire <lot> [fișier-praguri] [--ora-reala <ISO>]   scrie începutul și sfârșitul fazei „pornire”, cu hash-ul pragurilor și al scripturilor porții; fixează lotul curent.
                                            Cu --ora-reala (lotul care introduce jurnalul): rândurile poartă ora dată și „reconstituit” în detalii
  pornire-coada <lot> <praguri> [<cheie> [<comandă>]]   lansarea din coadă: rândul „pornire” cu marcaj de proveniență (coada=1 marca=<hash>), unul singur pe lot
  rezumat <lot>                             duratele pe fază (copia din raport)
  lucru <lot>                               scrie fazele timpului de lucru ale lui Code (derivate din marcajele jurnalului; idempotent; 17.5-A)
  lot-curent                                tipărește lotul (LOT, ramura lucru/lotNN-M, fișierul lot_curent din depozit)"""
import datetime
import fcntl
import hashlib
import os
import re
import subprocess
import sys
import time

AICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AICI)
import poarta_lib as L  # noqa: E402

FAZE_OBLIGATORII = ("pornire", "hook", "verificator", "poarta_verificator", "poarta_pytest", "poarta_plasa", "publicare")
#: scripturile porții a căror schimbare e vizibilă arhitectului prin hash în jurnal (pct.1a)
SCRIPTURI_POARTA = ("scripts/poarta_lot.sh", "scripts/publica_lot.sh", "scripts/baza_test.sh", "scripts/poarta_nucleu.txt", "scripts/plasa_16_2.manifest",
                    "scripts/poarta_clasifica.py", "scripts/poarta_lib.py", "conftest.py")


def _git(*a, cwd=None):
    return subprocess.run(["git", *a], cwd=cwd or os.getcwd(), capture_output=True, text=True).stdout.strip()


def comun(cwd=None):
    return _git("rev-parse", "--path-format=absolute", "--git-common-dir", cwd=cwd)


def cale_jurnal():
    if os.environ.get("LOT_JURNAL"):
        return os.environ["LOT_JURNAL"]
    return os.path.join(os.path.dirname(comun()), ".lot_jurnal.log")


def lot_curent():
    if os.environ.get("LOT"):
        return os.environ["LOT"]
    m = re.search(r"lot(\d+)-(\d+)", _git("symbolic-ref", "--short", "HEAD"))
    try:
        fisier = open(os.path.join(comun(), "lot_curent.txt"), encoding="utf-8").read().strip()
    except OSError:
        fisier = ""
    if m:
        din_ramura = "%s.%s" % m.groups()
        # un lot de corecție (16.1-C2) trăiește pe ramura lotului de bază (lucru/lot16-1): fișierul îl numește
        return fisier if fisier.startswith(din_ramura + "-") else din_ramura
    return fisier or "?"


def _sha():
    return _git("rev-parse", "HEAD")[:12] or "-"


def _viu(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except (OSError, ValueError):
        return False


def _citeste(cale):
    try:
        return [ln.rstrip("\n").split("\t") for ln in open(cale, encoding="utf-8") if ln.strip()]
    except OSError:
        return []


def _scrie(cale, campuri):
    os.makedirs(os.path.dirname(cale) or ".", exist_ok=True)
    with open(cale, "a", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.write("\t".join(str(c).replace("\t", " ").replace("\n", " ") for c in campuri) + "\n")


#: ora impusă rândurilor scrise de `pornire --ora-reala` (None = ora ceasului)
_ORA_IMPUSA = None


def _acum():
    return _ORA_IMPUSA or datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def marcheaza_intrerupte(cale=None):
    """Orice început fără sfârșit al cărui proces a murit primește un sfârșit „intrerupt” (la ora la care l-am constatat)."""
    cale = cale or cale_jurnal()
    rows = _citeste(cale)
    inchise = {r[6] for r in rows if len(r) > 6 and r[2] == "sfarsit"}
    for r in rows:
        if len(r) > 7 and r[2] == "inceput" and r[6] not in inchise and not _viu(r[7]):
            _scrie(cale, [r[0], r[1], "sfarsit", _acum(), r[4], "intrerupt", r[6], r[7], "constatat de următorul script"])
            inchise.add(r[6])


def inceput(lot, faza, detalii="", pid=None):
    """`pid` = procesul a cărui moarte înseamnă „întrerupt”: din linia de comandă, shell-ul care a chemat scriptul (nu python-ul de o clipă)."""
    cale = cale_jurnal()
    marcheaza_intrerupte(cale)
    id_ = "%d-%d" % (os.getpid(), time.time() * 1000)
    _scrie(cale, [lot, faza, "inceput", _acum(), _sha(), "-", id_, pid or os.getpid(), detalii])
    return id_


def sfarsit(lot, faza, id_, rezultat, detalii=""):
    cale = cale_jurnal()
    marcheaza_intrerupte(cale)
    pid = next((r[7] for r in _citeste(cale) if len(r) > 7 and r[6] == id_ and r[2] == "inceput"), os.getpid())
    _scrie(cale, [lot, faza, "sfarsit", _acum(), _sha(), rezultat, id_, pid, detalii])


def hash_scripturi(rad=None):
    rad = rad or _git("rev-parse", "--show-toplevel")
    return " ".join("%s=%s" % (os.path.basename(s), L.hash_fisier(os.path.join(rad, s))[:16]) for s in SCRIPTURI_POARTA)


def pornire(lot, praguri=None, ora_reala=None):
    global _ORA_IMPUSA
    rad = _git("rev-parse", "--show-toplevel")
    praguri = praguri or os.path.join(rad, "scripts", "praguri_%s.txt" % L.lot_fisier(lot))
    marca = " reconstituit ora_reala=%s" % ora_reala if ora_reala else ""
    if ora_reala:
        _ORA_IMPUSA = datetime.datetime.fromisoformat(ora_reala).astimezone().isoformat(timespec="seconds")
    try:
        id_ = inceput(lot, "pornire", "praguri=%s praguri_sha256=%s%s" % (os.path.basename(praguri), L.hash_fisier(praguri), marca), pid=os.getpid())
        open(os.path.join(comun(), "lot_curent.txt"), "w", encoding="utf-8").write(lot + "\n")
        sfarsit(lot, "pornire", id_, "ok" if os.path.exists(praguri) else "lipsa_praguri", "scripturi_poarta: " + hash_scripturi(rad) + marca)
    finally:
        _ORA_IMPUSA = None
    return 0 if os.path.exists(praguri) else 1


def cheie_coada():
    """Cheia cozii (~/ghid_incoming/cheie_coada.txt, 600, în afara depozitului; CHEIE_COADA o mută în teste). Lipsa ei = None."""
    try:
        return open(os.environ.get("CHEIE_COADA") or os.path.expanduser("~/ghid_incoming/cheie_coada.txt"), encoding="utf-8").read().strip() or None
    except OSError:
        return None


def marca(cheie, lot, ora):
    """Marcajul de proveniență al rândului „pornire”: sha256(cheie | lot | ora rândului). Numai coada citește cheia la lansare; hash-ul nu se poate recalcula fără ea."""
    return hashlib.sha256(("%s|%s|%s" % (cheie, lot, ora)).encode("utf-8")).hexdigest()


def marca_valida(rand, lot):
    """Rândul „pornire” (început) poartă `coada=1 marca=<hash>` care se recalculează din cheie, lot și ora lui."""
    m = re.search(r"\bcoada=1 marca=([0-9a-f]{64})\b", rand[8] if len(rand) > 8 else "")
    cheie = cheie_coada()
    return bool(m and cheie and m.group(1) == marca(cheie, rand[0], rand[3]))


def _coada_reala(praguri):
    """Praguri din ~/ghid_incoming (lansarea reală din coadă); calibrările și testele cheamă `pornire-coada` cu fișiere din directoare temporare."""
    return os.path.dirname(os.path.abspath(praguri)) == os.path.expanduser("~/ghid_incoming")


def pornire_coada(lot, praguri, cheie_fisier=None, comanda=None):
    """Lansarea din coadă (~/coada_code.sh): rândul „pornire” cu ora reală, hash-ul pragurilor (copia din ~/ghid_incoming), hash-ul pasi_<lot>.txt al arhitectului (dacă există), hash-urile scripturilor porții și marcajul
    de proveniență. Un lot real (NN.M sau NN.M-X) fixează și lotul curent; un lot de probă (PROBA-…) nu."""
    global _ORA_IMPUSA
    if cheie_fisier:
        os.environ["CHEIE_COADA"] = cheie_fisier
    cheie = cheie_coada()
    if not cheie:
        print("[jurnal_lot] REFUZ: lipsește cheia cozii.")
        return 1
    rad = _git("rev-parse", "--show-toplevel")
    ora = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    _ORA_IMPUSA = ora
    try:
        ph = L.hash_fisier(praguri)
        # 16.1-C3 pct.1: hash-ul fișierului arhitectului pasi_<lot>.txt (lângă praguri, în ~/ghid_incoming), dacă există; publica_lot îl compară cu cel de la publicare
        pasi = os.path.join(os.path.dirname(os.path.abspath(praguri)), "pasi_%s.txt" % L.lot_fisier(lot))
        ps = " pasi=%s pasi_sha256=%s" % (os.path.basename(pasi), L.hash_fisier(pasi)) if os.path.exists(pasi) else ""
        id_ = inceput(lot, "pornire", "praguri=%s praguri_sha256=%s%s coada=1 marca=%s comanda=%s" % (os.path.basename(praguri), ph, ps, marca(cheie, lot, ora), os.path.basename(comanda or "-")),
                      pid=os.getpid())
        if re.fullmatch(r"\d+\.\d+(-[A-Z]\d*)?", lot):
            open(os.path.join(comun(), "lot_curent.txt"), "w", encoding="utf-8").write(lot + "\n")
        sfarsit(lot, "pornire", id_, "ok" if os.path.exists(praguri) else "lipsa_praguri", "scripturi_poarta: " + hash_scripturi(rad) + " coada=1")
    finally:
        _ORA_IMPUSA = None
    rezultat = 0 if os.path.exists(praguri) else 1
    if rezultat == 0 and re.fullmatch(r"\d+\.\d+(-[A-Z]\d*)?", lot) and _coada_reala(praguri):
        # 17.2-A: alerta PORNIT către Costin (lanț WhatsApp/email, până la 90 s); nu schimbă nici valoarea întoarsă, nici rândurile din jurnal
        try:
            subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "alerta_whatsapp.py"), "lot", lot, "PORNIT"], timeout=90)
        except Exception as e:  # noqa: BLE001
            print("[jurnal_lot] alerta nu a plecat: %s" % type(e).__name__)
    return rezultat


def durate(lot, cale=None):
    """-> [(faza, id, început, sfârșit, rezultat, secunde)] în ordinea începuturilor."""
    cale = cale or cale_jurnal()
    marcheaza_intrerupte(cale)
    rows = [r for r in _citeste(cale) if r[0] == lot and len(r) > 6]
    sfarsituri = {r[6]: r for r in rows if r[2] == "sfarsit"}
    iesire = []
    for r in rows:
        if r[2] != "inceput":
            continue
        s = sfarsituri.get(r[6])
        sec = ""
        if s:
            sec = round((datetime.datetime.fromisoformat(s[3]) - datetime.datetime.fromisoformat(r[3])).total_seconds())
        iesire.append((r[1], r[6], r[3], s[3] if s else "-", s[5] if s else "intrerupt", sec))
    return iesire


def marcheaza_infra_g2(lot, id_, motiv, durata):
    """[17.5-T, T.5] Marchează prima măsurare a unei faze poarta_pytest / poarta_plasa depășite sub încărcare străină susținută: un al doilea rând «sfarsit» cu același id și rezultatul «infra_g2»
    (`durate` ia ultimul «sfarsit» al id-ului, deci durata marcată iese alta și nu mai contează); motivul și durata reală a primei măsurări stau în detalii."""
    cale = cale_jurnal()
    pid = next((r[7] for r in _citeste(cale) if len(r) > 7 and r[6] == id_ and r[2] == "inceput"), os.getpid())
    faza = next((r[1] for r in _citeste(cale) if len(r) > 7 and r[6] == id_ and r[2] == "inceput"), "?")
    _scrie(cale, [lot, faza, "sfarsit", _acum(), _sha(), "infra_g2", id_, pid, "%s; durata_prima=%s" % (motiv, durata)])


def marcaje_g2(lot, cale=None):
    """{id: (motiv, durata primei măsurări în secunde)} pentru rândurile «sfarsit» cu rezultatul «infra_g2» ale lotului (pentru mesajul depășirii și pentru raport)."""
    iesire = {}
    for r in _citeste(cale or cale_jurnal()):
        if len(r) > 8 and r[0] == lot and r[2] == "sfarsit" and r[5] == "infra_g2":
            motiv, _, dur = r[8].rpartition("; durata_prima=")
            iesire[r[6]] = (motiv, dur)
    return iesire


# --- 17.5-A: citirea pură a jurnalului și fazele timpului de lucru al lui Code (derivate, nu măsurate de hook) ---
FAZE_LUCRU = ("lucru_pana_la_commit", "lucru_pana_la_poarta", "asteptare_poarta", "reparatie_dupa_rosu", "dupa_verde", "dupa_infra", "pana_la_publicare", "pytest_intre_commituri")
_FAZE_POARTA = ("poarta_verificator", "poarta_pytest", "poarta_plasa")


def _t(ora):
    return datetime.datetime.fromisoformat(ora)


def _sec(a, b):
    return round((_t(b) - _t(a)).total_seconds())


def citeste_jurnal(cale=None):
    """Citire pură: rândurile jurnalului, fără `marcheaza_intrerupte` (care scrie)."""
    return _citeste(cale or cale_jurnal())


def rulari(rows, lot):
    """Rulările lotului, fără scrieri: pereche început/sfârșit cu același id (două rânduri «sfarsit» pe același id: ultimul).
    -> [{faza, id, inceput, sfarsit, rezultat, secunde, complet, intrerupt, pid, detalii}] în ordinea începuturilor.
    «intrerupt» = sfârșit cu rezultatul «intrerupt» sau început fără sfârșit al cărui proces nu mai trăiește; «complet» = pereche fără «intrerupt»."""
    rl = [r for r in rows if len(r) > 6 and r[0] == lot]
    sf = {r[6]: r for r in rl if r[2] == "sfarsit"}
    iesire = []
    for r in rl:
        if r[2] != "inceput":
            continue
        s = sf.get(r[6])
        pid = r[7] if len(r) > 7 else ""
        rez = s[5] if s else ("intrerupt" if not _viu(pid) else "in_curs")
        iesire.append({"faza": r[1], "id": r[6], "inceput": r[3], "sfarsit": s[3] if s else None, "rezultat": rez,
                       "secunde": _sec(r[3], s[3]) if s else None, "complet": bool(s) and rez != "intrerupt",
                       "intrerupt": rez == "intrerupt", "pid": pid, "detalii": r[8] if len(r) > 8 else ""})
    return iesire


def _rez_run(rezultate):
    """Ordinea rosu > infra > verde: «verde» dacă toate rezultatele finale sunt verde / verde_cu_restante; «infra» [17.5-U] numai dacă toate sunt verde, verde_*, «infra» sau «infra_g2» [17.5-T] și cel puțin unul e «infra»
    (o rulare fără nicio probă rulată într-o treaptă); altfel «rosu» (rosu_N, intrerupt, stop, lista goală și orice altceva, inclusiv un amestec verde / infra / rosu_1)."""
    if rezultate and all(x == "verde" or x.startswith("verde_") for x in rezultate):
        return "verde"
    if rezultate and all(x == "verde" or x.startswith("verde_") or x in ("infra", "infra_g2") for x in rezultate):   # [17.5-T, T.5] «infra_g2» = prima măsurare marcată de G2: nici verde, nici roșu
        return "infra"
    return "rosu"


def _utc(ora):
    return _t(ora).astimezone(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S")


def intervale_hook_poarta(rows, lot):
    """Intervalele închise [început, sfârșit] ale fazelor hook și poarta_* ale lotului; o fază fără sfârșit are interval de lungime 0 (limită declarată)."""
    return [(x["inceput"], x["sfarsit"] or x["inceput"]) for x in rulari(rows, lot) if x["faza"] == "hook" or x["faza"] in _FAZE_POARTA]


def sesiuni_pytest(rows, lot):
    """Sesiunile fazei «pytest»: lista rulărilor cu cheile `colectare` (--collect-only în argumente) și `in_faza` (pornită în interiorul unei faze hook sau poarta_*, intervale închise)."""
    iv = [(_t(a), _t(b)) for a, b in intervale_hook_poarta(rows, lot)]
    iesire = []
    for x in rulari(rows, lot):
        if x["faza"] != "pytest":
            continue
        p = _t(x["inceput"])
        iesire.append(dict(x, colectare="--collect-only" in x["detalii"], in_faza=any(a <= p <= b for a, b in iv)))
    return iesire


def runde_poarta(rows, lot):
    """Rulările de poartă ale lotului: începe la fiecare «inceput» al lui poarta_verificator și ține până la ultimul «sfarsit» poarta_* dinaintea următorului (în ordinea rândurilor din fișier).
    -> [{inceput, sfarsit (verdictul), rezultat (verde|infra|rosu)}]; reluarea de infrastructură (poarta_pytest / poarta_plasa a doua oară) rămâne în aceeași rulare."""
    rl = [r for r in rows if len(r) > 6 and r[0] == lot]
    starturi = [i for i, r in enumerate(rl) if r[1] == "poarta_verificator" and r[2] == "inceput"]
    iesire = []
    for k, i0 in enumerate(starturi):
        i1 = starturi[k + 1] if k + 1 < len(starturi) else len(rl)
        parte = [r for r in rl[i0:i1] if r[1] in _FAZE_POARTA]
        sfarsituri = [r for r in parte if r[2] == "sfarsit"]
        inchise = {r[6] for r in sfarsituri}
        finale = {}
        for r in sfarsituri:
            finale[r[1]] = r[5]
        for r in parte:
            if r[2] == "inceput" and r[6] not in inchise and r[1] not in finale:
                finale[r[1]] = "intrerupt"
        verdict = max((r[3] for r in sfarsituri), key=_t) if sfarsituri else max((r[3] for r in parte), key=_t)
        iesire.append({"inceput": rl[i0][3], "sfarsit": verdict, "rezultat": _rez_run(list(finale.values()))})
    return iesire


def _publicare_dupa(rows, lot, ora):
    """Primul rând «inceput» al fazei «publicare» cu ora ≥ `ora` (ordinea rândurilor din fișier la ore egale) și numărul rândurilor «inceput» ale fazei."""
    pub = [r for r in rows if len(r) > 6 and r[0] == lot and r[1] == "publicare" and r[2] == "inceput"]
    dupa = [r for r in pub if _t(r[3]) >= _t(ora)]
    return (dupa[0] if dupa else None), len(pub)


def deriva_lucru(rows, lot):
    """Funcția pură a fazelor timpului de lucru (17.5-A, pct.3): rândurile jurnalului -> [{faza, inceput, sfarsit, rezultat, detalii}], fără scrieri.
    Marcajele: început de lot = primul rând al lotului; commit = «inceput» al fazei hook; poartă = rulările din `runde_poarta`."""
    rl = [r for r in rows if len(r) > 6 and r[0] == lot]
    if not rl:
        return []
    t0 = rl[0][3]
    commituri = sorted((r[3] for r in rl if r[1] == "hook" and r[2] == "inceput"), key=_t)
    runde = runde_poarta(rows, lot)
    sesiuni = sesiuni_pytest(rows, lot)
    iesire = []

    def adauga(faza, a, b, rezultat="ok", detalii=""):
        if _t(b) >= _t(a):
            iesire.append({"faza": faza, "inceput": a, "sfarsit": b, "rezultat": rezultat, "detalii": detalii})

    if commituri:
        adauga("lucru_pana_la_commit", t0, commituri[0])
        if runde:
            adauga("lucru_pana_la_poarta", commituri[0], runde[0]["inceput"])
    for k, run in enumerate(runde):
        adauga("asteptare_poarta", run["inceput"], run["sfarsit"], run["rezultat"])
        if k + 1 < len(runde):
            adauga({"rosu": "reparatie_dupa_rosu", "infra": "dupa_infra"}.get(run["rezultat"], "dupa_verde"), run["sfarsit"], runde[k + 1]["inceput"])
    if runde:
        pub, _ = _publicare_dupa(rows, lot, runde[-1]["sfarsit"])
        if pub:
            adauga("pana_la_publicare", runde[-1]["sfarsit"], pub[3])
    limite = [t0] + commituri
    if runde and commituri and _t(commituri[-1]) <= _t(runde[0]["inceput"]):
        limite.append(runde[0]["inceput"])
    for a, b in zip(limite, limite[1:]):
        n = sum(1 for s in sesiuni if not s["colectare"] and not s["in_faza"] and _t(a) <= _t(s["inceput"]) < _t(b))
        m = sum(1 for s in sesiuni if s["colectare"] and _t(a) <= _t(s["inceput"]) < _t(b))
        adauga("pytest_intre_commituri", a, b, "ok", "rulari=%d colectari=%d" % (n, m))
    return iesire


def _id_derivat(lot, faza, ora):
    return "derivat-%s-%s-%s" % (lot, faza, _utc(ora))


def lucru(lot, cale=None):
    """Scrie în jurnal rândurile fazelor de lucru care lipsesc (perechi început/sfârșit, o singură scriere, ora = marcajele); idempotentă. -> numărul rândurilor scrise."""
    cale = cale or cale_jurnal()
    rows = _citeste(cale)
    existente = {r[6] for r in rows if len(r) > 6}
    sha = _sha()
    linii, vazute = [], set(existente)
    for x in deriva_lucru(rows, lot):
        id_ = _id_derivat(lot, x["faza"], x["inceput"])
        if id_ in vazute:
            continue
        vazute.add(id_)
        detalii = ("derivat=1 " + x["detalii"]).strip()
        linii.append([lot, x["faza"], "inceput", x["inceput"], sha, "-", id_, os.getpid(), detalii])
        linii.append([lot, x["faza"], "sfarsit", x["sfarsit"], sha, x["rezultat"], id_, os.getpid(), detalii])
    if linii:
        os.makedirs(os.path.dirname(cale) or ".", exist_ok=True)
        text = "".join("\t".join(str(c).replace("\t", " ").replace("\n", " ") for c in l) + "\n" for l in linii)
        with open(cale, "a", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            f.write(text)
    return len(linii)


def main(a):
    if not a:
        print(__doc__)
        return 2
    if a[0] == "lot-curent":
        print(lot_curent())
    elif a[0] == "inceput":
        print(inceput(a[1], a[2], " ".join(a[3:]), pid=os.getppid()))
    elif a[0] == "sfarsit":
        sfarsit(a[1], a[2], a[3], a[4], " ".join(a[5:]))
    elif a[0] == "pornire":
        ora = a[a.index("--ora-reala") + 1] if "--ora-reala" in a else None
        pozitionale = [x for i, x in enumerate(a[1:], 1) if x != "--ora-reala" and a[i - 1] != "--ora-reala"]
        return pornire(a[1], pozitionale[1] if len(pozitionale) > 1 else None, ora)
    elif a[0] == "pornire-coada":   # pornire-coada <lot> <fișier-praguri> [<fișier-cheie> [<fișier-comandă>]]
        return pornire_coada(a[1], a[2], a[3] if len(a) > 3 else None, a[4] if len(a) > 4 else None)
    elif a[0] == "rezumat":
        for f, i, b, s, r, sec in durate(a[1]):
            print("%-20s %-10s %s -> %s  %ss" % (f, r, b, s, sec))
    elif a[0] == "lucru":   # lucru <lot>: fazele timpului de lucru (17.5-A), idempotent
        print("%d rânduri noi" % lucru(a[1]))
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

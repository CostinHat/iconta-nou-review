# -*- coding: utf-8 -*-
"""GARD [R74, 27.08.2026]: lista deadman-ului se compară cu SISTEMUL, nu cu o copie a ei.

DE UNDE VINE. `spv-poll`, `spv-receive` și `spv-refresh` rulau `/opt/iconta/venv/bin/python3`.
Calea dispăruse pe 27.07 odată cu mutarea venv-ului. Toate trei au ieșit cu **status 203** la
fiecare declanșare — ~48 de porniri pe zi, **~31 de zile**, în tăcere. Nimeni n-a aflat.

DE CE N-A VĂZUT-O NIMIC, și asta e partea de păstrat: `cron.RITMURI` — lista deadman-ului —
avea 8 joburi, **toate din `crontab`**. Cele trei rulează din **timere systemd**, deci lipsa
bătăii lor nu era o lipsă pentru nimeni. Iar gardul care păzea lista,
`test_fiecare_job_din_crontab_are_prag`, compara `RITMURI` cu un **set scris de mână în test**:
nu citea nici `crontab`, nici unitățile. **Un gard care se compară cu propria copie a
răspunsului** nu poate descoperi niciodată un job pe care nu-l știa deja.

Aceeași clasă cu **R70**, un nivel mai jos: acolo *o rută scrisă, gardată și verde, pe care n-o
cheamă nimic*; aici *un job scris, programat, verde în `systemctl list-timers`, care nu
pornește*. În amândouă gărzile verifică ce face lucrul **dacă** rulează; niciuna **dacă** rulează.

CE FACE IMPOSIBIL:
  1. un job de fundal care apare în `crontab` sau într-un timer systemd **fără prag** în
     `cron.RITMURI` — deci fără nimic care să-i supravegheze lipsa;
  2. un prag rămas în `RITMURI` pentru un job care nu mai există nicăieri în sistem (lista care
     păstrează morți alarmează la nesfârșit, iar alarma care sună mereu nu mai e alarmă);
  3. **o unitate systemd care rulează un interpretor inexistent** — chiar defectul de mai sus,
     care nu se putea vedea din cod, ci doar din sistem;
  4. un instrument care se uită în gol: dacă nu vede nici `crontab`, nici unități, **pică**.

CE NU FACE, declarat:
  - **nu verifică dacă jobul chiar a rulat** — aia e treaba lui `cron.verifica_batai`, la
    rulare, nu a unui test.
  - **nu se uită la ce rulează în afara acestei mașini** (limita e deja scrisă în
    `verifica_batai`: un deadman EXTERN ar acoperi și serverul jos; nu se construiește azi).
  - **nu acoperă `iconta-backup`** — e shell, nu modul, deci nu poate chema `bate()`. Motivul e
    scris în `cron.NESUPRAVEGHEATE`, nu lăsat implicit; jobul își alertează singur eșecurile
    consecutive.
  - **nu pornește și nu repară nimic.** Corectarea celor trei unități cere `sudo`.
"""
import os

from core import cron

# BASELINE — **GOL din 27.08.2026**, și asta e chiar povestea lui.
#
# S-a născut în aceeași zi cu trei intrări: `spv-poll`, `spv-receive`, `spv-refresh`, unitățile
# care rulau un interpretor șters cu o lună înainte. Era o **fotografie**, nu o listă de vinovați:
# descria starea din ziua construcției, ca poarta să nu fie retroactivă.
#
# Clichetul avea AMBELE direcții. Prima — o unitate nouă stricată nu poate intra — n-a fost încă
# exercitată. **A doua s-a aprins la prima reparație**: Costin a corectat cele trei `ExecStart`,
# a rulat suita, iar testul a devenit ROȘU cerând exact ce trebuia — *„scoate-le din baseline"*.
# Costin: *„clichetul a funcționat în ambele direcții — a doua, cea care nu păstrează morți, s-a
# aprins la prima reparație."*
#
# Rămâne GOL, nu șters: o mulțime goală spune *„azi nicio unitate nu e stricată"*, ceea ce e o
# afirmație. Absența listei n-ar spune nimic.
_INTERPRETOARE_LIPSA = set()


def _sistem():
    return cron.citeste_sistemul()


def joburi_asteptate(din_crontab, unitati):
    """Numele care TREBUIE să aibă prag: modulele găsite în sistem, fără cele declarate
    nesupravegheate (cu motivul, în `cron.NESUPRAVEGHEATE`)."""
    nume = set(din_crontab) | {u["modul"] for u in unitati if u["modul"]}
    return nume - set(cron.NESUPRAVEGHEATE)


def interpretoare_lipsa(unitati):
    """Unitățile care rulează un binar care nu există pe disc. -> set(nume_service)."""
    return {u["service"] for u in unitati
            if u["interpretor"] and not os.path.exists(u["interpretor"])}


# ============================================================
#  Pe sistemul real
# ============================================================
def test_ANTI_VACUU_instrumentul_chiar_vede_sistemul():
    """Fără asta, o mașină fără `crontab` ar face toate testele de mai jos verzi degeaba —
    exact felul de verde pe care gardul ăsta există ca să-l facă imposibil."""
    ct, unitati = _sistem()
    assert len(ct) >= 6, (
        "doar %d joburi citite din `crontab -l` — instrumentul nu vede sursa, deci nu poate "
        "afirma nimic despre acoperire" % len(ct))
    assert len(unitati) >= 3, (
        "doar %d timere systemd citite din /etc/systemd/system — instrumentul nu vede a doua "
        "sursă, adică exact cea care lipsea în R74" % len(unitati))


def test_fiecare_job_de_fundal_din_SISTEM_are_prag():
    ct, unitati = _sistem()
    lipsa = sorted(joburi_asteptate(ct, unitati) - set(cron.RITMURI))
    assert not lipsa, (
        "joburi de fundal pe care nu le supraveghează nimeni: %s\n"
        "Adaugă-le în `cron.RITMURI` cu pragul lor (ritm × 2 + marjă), sau declară-le în "
        "`cron.NESUPRAVEGHEATE` cu motivul. Un job fără prag arată, când moare, exact ca unul "
        "care n-a avut de lucru." % lipsa)


def test_RITMURI_nu_pastreaza_joburi_care_nu_mai_exista():
    """Cealaltă direcție. Un prag pentru un job scos din `crontab` alarmează la nesfârșit, iar
    o alarmă care sună mereu nu mai e citită — și atunci moare și cea reală, lângă ea."""
    ct, unitati = _sistem()
    fantome = sorted(set(cron.RITMURI) - joburi_asteptate(ct, unitati))
    assert not fantome, (
        "praguri în `cron.RITMURI` pentru joburi care nu mai există nici în `crontab`, nici "
        "într-un timer systemd: %s — scoate-le, sau repune jobul." % fantome)


def test_nicio_unitate_NOUA_nu_ruleaza_un_interpretor_inexistent():
    """Chiar defectul din R74, prins de unde se poate vedea: din sistem."""
    _ct, unitati = _sistem()
    stricate = interpretoare_lipsa(unitati)
    noi = sorted(stricate - _INTERPRETOARE_LIPSA)
    detalii = {u["service"]: u["interpretor"] for u in unitati}
    assert not noi, (
        "unități systemd care rulează un binar inexistent:\n  "
        + "\n  ".join("%s -> %s" % (s, detalii.get(s)) for s in noi)
        + "\n\nIes cu status 203 la fiecare declanșare, fără să scrie nimic în logul lor. "
          "Corectează `ExecStart=`, apoi `sudo systemctl daemon-reload`.")


def test_baseline_de_unitati_stricate_NU_pastreaza_morti():
    """A doua direcție a clichetului. Când Costin repară cele trei, testul ăsta devine ROȘU și
    cere scoaterea lor din listă — altfel baseline-ul ar continua să scuze o problemă rezolvată,
    iar a patra unitate stricată ar putea intra pe locul rămas liber."""
    _ct, unitati = _sistem()
    reparate = sorted(_INTERPRETOARE_LIPSA - interpretoare_lipsa(unitati))
    cunoscute = {u["service"] for u in unitati}
    disparute = sorted(_INTERPRETOARE_LIPSA - cunoscute)
    assert not reparate, (
        "unități din `_INTERPRETOARE_LIPSA` care NU mai sunt stricate: %s — scoate-le din "
        "baseline. (Dacă tocmai le-ai reparat: asta e mesajul care ți-o cere.)" % reparate)
    assert not disparute, (
        "unități din `_INTERPRETOARE_LIPSA` care nu mai există deloc: %s — scoate-le din "
        "baseline." % disparute)


def test_fiecare_modul_supravegheat_chiar_exista_in_repo():
    """Un prag pentru un modul care nu se poate importa e un prag pentru nimic."""
    rad = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    lipsa = [n for n in cron.RITMURI
             if not os.path.isfile(os.path.join(rad, "core", n + ".py"))]
    assert not lipsa, "praguri pentru module inexistente în `core/`: %s" % lipsa


def test_cele_trei_joburi_SPV_trec_prin_ambalajul_care_bate():
    """Fără `cron.ruleaza`, un job poate rula perfect și tot n-ar bate niciodată — atunci
    pragul din `RITMURI` ar alarma la infinit, iar cauza n-ar fi jobul, ci gardul.
    Structural: se caută apelul, nu un comentariu."""
    import ast
    import io
    rad = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fara = []
    for modul in ("spv_poll", "spv_receive", "spv_refresh"):
        arb = ast.parse(io.open(os.path.join(rad, "core", modul + ".py"), encoding="utf-8").read())
        gasit = any(
            isinstance(n, ast.Call)
            and isinstance(n.func, ast.Attribute) and n.func.attr == "ruleaza"
            and isinstance(n.func.value, ast.Name) and n.func.value.id == "cron"
            and n.args and isinstance(n.args[0], ast.Constant) and n.args[0].value == modul
            for n in ast.walk(arb))
        if not gasit:
            fara.append(modul)
    assert not fara, (
        "module care nu trec prin `cron.ruleaza(\"<nume>\", …)`: %s — nu alertează la eșec și "
        "nu bat la reușită." % fara)


# ============================================================
#  CALIBRARE — pe texte, ca să nu depindă de mașină (METODA §22)
# ============================================================
_CRONTAB = """# comentariu: -m core.modul_din_comentariu
0 8 * * * cd /x && /x/venv/bin/python3 -m core.notificari_scadenta >> /x/n.log 2>&1
*/15 * * * * cd /x && /x/venv/bin/python3 -m core.alerta_acces >> /x/a.log 2>&1
15 3 * * * sudo /usr/local/bin/altceva.sh >> /x/b.log 2>&1
"""


def test_CALIBRARE_crontab_vede_modulele_si_sare_peste_comentarii():
    g = cron.joburi_din_crontab(_CRONTAB)
    assert g == {"notificari_scadenta", "alerta_acces"}, g
    assert "modul_din_comentariu" not in g, "o linie comentată nu e un job programat"


def test_CALIBRARE_crontab_gol_NU_inventeaza_joburi():
    assert cron.joburi_din_crontab("") == set()
    assert cron.joburi_din_crontab(None) == set()


_TIMER = "[Timer]\nOnCalendar=*-*-* *:07,37:00\n[Install]\nWantedBy=timers.target\n"
_SERVICE_OK = "[Service]\nExecStart=/home/costin/iconta_nou/venv/bin/python -m core.spv_poll\n"
_SERVICE_SHELL = "[Service]\nExecStart=/usr/local/bin/iconta-backup.sh\n"


def test_CALIBRARE_unitatea_da_modulul_interpretorul_si_calendarul():
    u = cron.unitati_systemd([("spv-poll.timer", _TIMER, "spv-poll.service", _SERVICE_OK)])[0]
    assert u["modul"] == "spv_poll"
    assert u["interpretor"] == "/home/costin/iconta_nou/venv/bin/python"
    assert u["calendar"] == "*-*-* *:07,37:00"


def test_CALIBRARE_un_serviciu_de_SHELL_nu_e_raportat_ca_modul():
    """Direcția «acuză pe nedrept»: `iconta-backup` nu poate bate și nu trebuie cerut în RITMURI."""
    u = cron.unitati_systemd([("b.timer", _TIMER, "b.service", _SERVICE_SHELL)])[0]
    assert u["modul"] is None
    assert joburi_asteptate(set(), [u]) == set()


def test_CALIBRARE_un_timer_cu_Unit_explicit_e_urmarit_la_tinta():
    t = "[Timer]\nUnit=altul.service\nOnCalendar=daily\n"
    u = cron.unitati_systemd([("x.timer", t, "altul.service", _SERVICE_OK)])[0]
    assert u["service"] == "altul.service" and u["modul"] == "spv_poll"


def test_CALIBRARE_interpretorul_inexistent_E_prins_iar_cel_real_NU():
    stricat = cron.unitati_systemd(
        [("x.timer", _TIMER, "x.service",
          "[Service]\nExecStart=/opt/nu/exista/python3 -m core.spv_poll\n")])
    assert interpretoare_lipsa(stricat) == {"x.service"}
    bun = cron.unitati_systemd([("y.timer", _TIMER, "y.service", _SERVICE_OK)])
    assert interpretoare_lipsa(bun) == set(), (
        "interpretorul real al proiectului e raportat ca lipsă — gardul ar fi zgomot pur")


def test_CALIBRARE_un_job_din_timer_fara_prag_E_raportat():
    """Instanța reală a lui R74, reconstruită pe texte: exact ce n-a văzut gardul vechi."""
    u = cron.unitati_systemd([("spv-poll.timer", _TIMER, "spv-poll.service", _SERVICE_OK)])
    lipsa = joburi_asteptate(set(), u) - {"alerta_acces"}          # ritmuri fără spv_poll
    assert lipsa == {"spv_poll"}, lipsa

# -*- coding: utf-8 -*-
"""scripts/infra_g2.py — depășirea de prag sub încărcare străină susținută (17.5-T, T.5, G2). Funcții pure, într-un singur loc; le cheamă scripts/poarta_rulare.py.

Dovada: fișierul ~/ghid_incoming/incarcare_poarta_<lot_fisier>.log, scris de veghea arhitectului (veghe_incarcare.sh, la fiecare minut cât ține o fază poarta_* sau hook):
  un rând de stamp   «AAAA-LL-ZZ HH:MM:SS faza=<fază> load=<a> <b> <c>»
  urmat de rânduri   «   strain: pid <P> cputimes <S> <comanda, cel mult 120 de caractere> (cpu <N>%)»      (<S> = secunde întregi de CPU cumulat; «(cpu N%)» se ignoră)
Un log fără dată în stamp sau fără cputimes pe rândurile «strain» e în formatul vechi și nu e dovadă.
CPU pe interval = (S la un stamp − S la stamp-ul precedent al aceluiași pid) / (secundele dintre stamp-uri), nu procentul din ps (media pe viața procesului).
«Susținută» = peste 30% (strict) la același proces în cel puțin 2 intervale consecutive din fereastra fazei, adică cel puțin 3 stamp-uri CONSECUTIVE cu același pid (un proces care lipsește dintr-un
stamp rupe lanțul), fiecare pereche la cel mult INTERVAL_MAX secunde. Hook și poarta_verificator nu se reclasifică niciodată."""
import datetime
import re

#: fazele la care G2 se aplică; hook și poarta_verificator rămân STOP, oricâtă încărcare ar arăta logul
FAZE_G2 = ("poarta_pytest", "poarta_plasa")
PRAG_CPU = 30                 # procente, strict peste
INTERVALE_MIN = 2             # intervale consecutive peste prag
INTERVAL_MAX = 180            # secunde între două stamp-uri ale aceluiași lanț (veghea scrie la un minut)
#: procesele care nu sunt «străine»: ale porții, ale testelor, ale restaurării bazei și ale veghei arhitectului (comanda conține șirul)
PROCESE_EXCLUSE = ("DUKIntegrator", "core.firma_rezumat", "verificator_conformitate",
                   "veghe_code", "orchestrator", "veghe_incarcare", "alerta_veghe",
                   "iconta_lot", "poarta", "pytest", "e2e_poarta", "uvicorn", "playwright", "chrom", "node", "postgres", "claude", "ps -eo")

_STAMP = re.compile(r"^(\d{4}-\d\d-\d\d) (\d\d:\d\d:\d\d) faza=(\S+) load=")
_STRAIN = re.compile(r"^   strain: pid (\d+) cputimes (\d+) (.*?)(?: \(cpu [\d.]+%\))?\s*$")


def citeste_log(text):
    """-> [(ora naivă, faza, {pid: (cputimes, comanda)})] în ordinea stamp-urilor. Un stamp fără dată nu se recunoaște (format vechi); un rând «strain» fără cputimes nu se recunoaște."""
    stampuri = []
    for ln in (text or "").splitlines():
        m = _STAMP.match(ln)
        if m:
            stampuri.append((datetime.datetime.fromisoformat(m.group(1) + "T" + m.group(2)), m.group(3), {}))
            continue
        m = _STRAIN.match(ln)
        if m and stampuri:
            stampuri[-1][2][int(m.group(1))] = (int(m.group(2)), m.group(3))
    return stampuri


def format_vechi(text):
    """(stamp-uri, rânduri «strain») din logurile care NU sunt în formatul cerut: un stamp fără dată (HH:MM:SS faza=…) sau un rând «strain» fără cputimes. Pentru raport (T.5 iii)."""
    stamp_vechi = sum(1 for ln in (text or "").splitlines() if re.match(r"^\d\d:\d\d:\d\d faza=", ln) or (ln.strip() and not ln.startswith(" ") and "faza=" in ln and not _STAMP.match(ln)))
    strain_vechi = sum(1 for ln in (text or "").splitlines() if ln.startswith("   strain:") and not _STRAIN.match(ln))
    return stamp_vechi, strain_vechi


def _exclus(comanda):
    return any(e in comanda for e in PROCESE_EXCLUSE)


def _naiv(ora_iso):
    """Ora ISO cu fus din jurnalul lotului -> ora locală naivă, comparabilă cu stamp-urile (data și ora serverului)."""
    d = datetime.datetime.fromisoformat(ora_iso)
    return d.astimezone().replace(tzinfo=None) if d.tzinfo else d


def incarcare_sustinuta(text, inceput, sfarsit):
    """Procesul străin cu CPU pe interval > PRAG_CPU în cel puțin INTERVALE_MIN intervale consecutive, din stamp-urile ferestrei [inceput, sfarsit] (ISO din jurnal). -> dict cu pid, comanda,
    cpu (maximul pe intervale, procente întregi în jos), ora (a stamp-ului unde e maximul) sau None. Comparația e în întregi: dS·100 > 30·dt (18 s în 60 s = exact 30% = nu)."""
    t0, t1 = _naiv(inceput), _naiv(sfarsit)
    st = [s for s in citeste_log(text) if t0 <= s[0] <= t1]
    gasit = None
    pids = {p for s in st for p in s[2]}
    for pid in pids:
        serie = 0
        for i in range(1, len(st)):
            a, b = st[i - 1], st[i]
            if pid not in a[2] or pid not in b[2] or _exclus(b[2][pid][1]):
                serie = 0
                continue
            dt = (b[0] - a[0]).total_seconds()
            ds = b[2][pid][0] - a[2][pid][0]
            if 0 < dt <= INTERVAL_MAX and ds * 100 > PRAG_CPU * dt:
                serie += 1
                if serie >= INTERVALE_MIN:
                    cpu = int(ds * 100 // dt)
                    if gasit is None or cpu > gasit["cpu"]:
                        gasit = {"pid": pid, "comanda": b[2][pid][1], "cpu": cpu, "ora": b[0].strftime("%F %H:%M:%S")}
            else:
                serie = 0
    return gasit


def decide(faza, durata, prag, inceput, sfarsit, text_log):
    """Funcția pură a deciziei G2: -> {"decizie": "ok"|"infra"|"stop", "motiv": text, "dovada": dict|None}.
    «ok» = durata nu depășește pragul; «stop» pentru hook, poarta_verificator, orice altă fază, log lipsă (None), log în format vechi sau fără încărcare susținută în fereastră; «infra» numai la
    poarta_pytest / poarta_plasa cu încărcare străină susținută dovedită în fereastră."""
    if prag is None or durata <= prag:
        return {"decizie": "ok", "motiv": "", "dovada": None}
    if faza not in FAZE_G2:
        return {"decizie": "stop", "motiv": "faza %s nu se reclasifică niciodată" % faza, "dovada": None}
    if text_log is None:
        return {"decizie": "stop", "motiv": "fără log de încărcare", "dovada": None}
    d = incarcare_sustinuta(text_log, inceput, sfarsit)
    if not d:
        return {"decizie": "stop", "motiv": "fără încărcare străină susținută în fereastră", "dovada": None}
    return {"decizie": "infra", "motiv": "infra: %d %s peste 30%% susținut" % (d["pid"], d["comanda"]), "dovada": d}

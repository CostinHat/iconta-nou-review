# -*- coding: utf-8 -*-
"""scripts/lacat_test.py — lacătul pe iconta_test și pe serverul de lucru 8019 (comanda 16.1-C3, pct.2). UN singur fișier, în afara depozitului, pentru toate worktree-urile:
~/.iconta/lacat_test (LACAT_TEST_FISIER îl mută numai în calibrări). Conținut: `pid ora_de_start_din_/proc/<pid>/stat [script]`.
  lacat_test.py ia <pid> [script]   ia lacătul pe numele <pid> (shell-ul scriptului). Ieșire 0 = luat sau reentrant; 1 = refuz, cu pid-ul care îl ține.
  lacat_test.py stare               tipărește deținătorul viu sau „liber”
„Pid viu” = kill -0 reușește ȘI ora de start din /proc coincide cu cea scrisă (un pid refolosit nu ține lacătul). Un pid mort sau refolosit = lacăt preluat.
Reentrant: scriptul pornit de procesul care ține lacătul primește LACAT_TEST_PID=<pid deținător> și nu refuză (dacă acel pid e într-adevăr deținătorul viu).
Nu există eliberare explicită: lacătul se pierde odată cu procesul deținătorului (pid mort = preluat), deci și scripturile care se înlocuiesc prin `exec` îl predau corect.
Limită declarată (CLAUDE.md): lacătul oprește intrările scriptate; o comandă pytest sau curl lansată direct de Code pe 8019 nu e oprită."""
import fcntl
import os
import sys

FISIER = os.environ.get("LACAT_TEST_FISIER") or os.path.expanduser("~/.iconta/lacat_test")


def ora_start(pid):
    """Câmpul 22 (starttime, în tacte de la boot) din /proc/<pid>/stat; None dacă procesul nu există. Numele procesului (câmpul 2) poate conține spații: se taie după ultimul „)”."""
    try:
        s = open("/proc/%d/stat" % int(pid), encoding="utf-8", errors="replace").read()
    except (OSError, ValueError):
        return None
    camp = s[s.rindex(")") + 2:].split()
    return camp[19] if len(camp) > 19 else None


def viu(pid, start):
    """kill -0 reușește și ora de start coincide."""
    try:
        os.kill(int(pid), 0)
    except PermissionError:
        pass
    except (OSError, ValueError):
        return False
    return ora_start(pid) == str(start)


def detinator(text):
    """-> (pid, start, script) din conținutul fișierului sau None."""
    p = text.split()
    return (p[0], p[1], p[2] if len(p) > 2 else "") if len(p) >= 2 and p[0].isdigit() else None


def ia(pid, script=""):
    os.makedirs(os.path.dirname(FISIER), exist_ok=True)
    with open(FISIER, "a+", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)   # verificarea și scrierea sunt o singură operație: două porniri simultane nu trec amândouă
        f.seek(0)
        d = detinator(f.read())
        if d and viu(d[0], d[1]):
            if d[0] == str(pid):
                return 0   # același proces (un script care chemă alt script ca el însuși)
            if os.environ.get("LACAT_TEST_PID") == d[0]:
                return 0   # reentrant: pornit de procesul care ține lacătul
            print("[lacat_test] REFUZ: iconta_test și serverul 8019 sunt ținute de pid %s (%s); așteaptă-l sau oprește-l." % (d[0], d[2] or "?"))
            return 1
        start = ora_start(pid)
        if start is None:
            print("[lacat_test] REFUZ: pid-ul %s nu există." % pid)
            return 1
        f.seek(0)
        f.truncate()
        f.write("%s %s %s\n" % (pid, start, script or "-"))
        if d:
            print("[lacat_test] lacăt preluat de la pid %s (mort sau refolosit)" % d[0], file=sys.stderr)
    return 0


def stare():
    try:
        d = detinator(open(FISIER, encoding="utf-8").read())
    except OSError:
        d = None
    print("ținut de pid %s (%s)" % (d[0], d[2]) if d and viu(d[0], d[1]) else "liber")
    return 0


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "ia":
        sys.exit(ia(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else ""))
    if sys.argv[1:2] == ["stare"]:
        sys.exit(stare())
    print(__doc__)
    sys.exit(2)

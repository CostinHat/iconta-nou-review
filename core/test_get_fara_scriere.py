# -*- coding: utf-8 -*-
"""GARD (20.08.2026): o rută GET nu scrie în starea de business. GET trebuie să fie SAFE (RFC 9110 §9.2.1).

CUM A IEȘIT. La auditul tenant_001, o sondă de CITIRE a lăsat 24 de rânduri în `state_plata`. Nu apăsase
niciun buton de salvare — deschisese ecranul Salariați. `GET /tenants/{id}/stat-plata` chema un helper care
făcea `INSERT ... ON CONFLICT DO UPDATE` + `commit()`. Consecințe măsurate:
  • baza legală a indemnizației de concediu medical (OUG 158/2005 art.10 al.4) se citea din acel tabel,
    deci media pe 6 luni depindea de ce luni deschisese cineva în interfață — lunile nedeschise lipseau
    TĂCUT din medie (măsurat pe salariat 55: 409,09 lei/zi pe 2 luni vs 425,06 pe cele 6 reale);
  • poarta din `salariati_api.sterge_salariat` („a fost pe un stat de plată") se închidea din vizitare;
  • orice monitorizare, prefetch de browser sau al doilea tab producea aceleași scrieri.

EXCEPȚIA, numită și motivată: jurnalul de acces. `GET /gdpr/export-cabinet` scrie în `public.audit_log`
cine și când a exportat date personale (GDPR art.5(2) răspundere + art.20 portabilitate). Aceea nu e stare
de business — e urma faptului că citirea a avut loc, și trebuie să existe TOCMAI pentru că e un GET.
Excepția e mecanică (numele tabelului), nu o listă de rute: orice rută poate jurnaliza, niciuna nu poate
scrie altceva.

Mutație probată: `main.py` din backup-copie (cu apelul la `_snapshot_stat_plata` în GET) → roșu, numind ruta.
"""
import ast
import os
import re

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MAIN = os.path.join(_RAD, "main.py")
_SCRIE = re.compile(r"\b(INSERT\s+INTO|UPDATE\s+|DELETE\s+FROM)\s+([\"\w.{}]*)", re.I)
_JURNAL = ("audit_log",)          # singurul destinatar permis dintr-un GET


def _surse():
    src = open(_MAIN, encoding="utf-8").read()
    return src, ast.parse(src)


def _metoda(fn):
    for d in fn.decorator_list:
        f = d.func if isinstance(d, ast.Call) else d
        if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id == "app":
            return f.attr
    return None


def _scrieri(nod, src, helperi, adanc=1):
    """[(fel, tinta)] - scrieri SQL din corpul nodului sau dintr-un helper local chemat."""
    out = []
    seg = ast.get_source_segment(src, nod) or ""
    for m in _SCRIE.finditer(seg):
        out.append((m.group(1).split()[0].upper(), (m.group(2) or "").strip()))
    if adanc > 0:
        for c in ast.walk(nod):
            if isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id in helperi:
                out += _scrieri(helperi[c.func.id], src, helperi, adanc - 1)
    return out


def _rute_get_care_scriu():
    src, arb = _surse()
    helperi, gets = {}, []
    for n in ast.walk(arb):
        if not isinstance(n, ast.FunctionDef):
            continue
        met = _metoda(n)
        if met is None:
            helperi[n.name] = n
        elif met == "get":
            gets.append(n)
    rele = []
    for fn in gets:
        interzise = [(fel, t) for fel, t in _scrieri(fn, src, helperi)
                     if not any(j in t.lower() for j in _JURNAL)]
        if interzise:
            rele.append("%s (linia %d): %s"
                        % (fn.name, fn.lineno,
                           ", ".join("%s %s" % (f, t or "?") for f, t in sorted(set(interzise)))))
    return rele, len(gets)


def test_nicio_ruta_get_nu_scrie_stare_de_business():
    rele, _ = _rute_get_care_scriu()
    assert not rele, (
        "Rute GET care scriu in starea de business (un GET trebuie sa fie SAFE - orice citire, "
        "monitorizare sau prefetch ar produce scrierea):\n  - " + "\n  - ".join(rele))


def test_gardul_chiar_vede_rutele_get():
    """Anti-gard-mort: daca decoratorul se schimba sau parsarea se rupe, testul de mai sus ar trece pe gol."""
    _, n = _rute_get_care_scriu()
    assert n >= 100, "doar %d rute GET gasite in main.py - euristica s-a rupt" % n


def test_exceptia_de_jurnal_e_chiar_folosita():
    """Excepția nu e teoretică: exportul GDPR chiar jurnalizeaza dintr-un GET. Daca dispare, vreau sa
    stiu — o excepție nefolosita e o gaura deschisa degeaba."""
    src, arb = _surse()
    helperi = {n.name: n for n in ast.walk(arb)
               if isinstance(n, ast.FunctionDef) and _metoda(n) is None}
    fn = next((n for n in ast.walk(arb) if isinstance(n, ast.FunctionDef)
               and n.name == "gdpr_export_cabinet"), None)
    assert fn is not None, "gdpr_export_cabinet a disparut - reevalueaza excepția de jurnal"
    tinte = [t for _, t in _scrieri(fn, src, helperi)]
    assert any("audit_log" in t.lower() for t in tinte), \
        "exportul GDPR nu mai jurnalizeaza - excepția de jurnal nu mai are utilizator"

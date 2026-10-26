# -*- coding: utf-8 -*-
"""[lotul 13, deficiențele 670 (a) și 683] Salariatul căruia i se dă un avans spre decontare (contul 542), ales din evidența firmei.

„542 trebuie urmărit pe persoană” (comanda Costin 13.1): rândurile 542 poartă salariatul ca partener (numele și CNP-ul, numai valid).
Punctul UNIC al verificării, chemat de ambele drumuri care scriu 542 din interfață: Operațiuni › Avans / Decont deplasare
(`uc_tenants._salariat_decont`) și Casă › „Avans spre decontare” (`casa_api.adauga`). Temei: CF art.76 alin.(2) lit.k (decontul de
deplasare e al unui salariat)."""
from core import erori as _erori
from core.pdf_util import data_ro
from core import repo_operatiuni


def cif_partener(cnp):
    """[lotul 10, deficiența 430b] Codul persoanei pe rândul notei, numai când e valid (CNP sau CUI): D406 refuză un cod de
    partener invalid, iar D205 numește singur CNP-ul greșit al beneficiarului (`d205.build_xml`)."""
    from core.identitate import valideaza_cnp, valideaza_cui
    c = "".join(ch for ch in str(cnp or "") if ch.isdigit())
    return c if c and (valideaza_cnp(c)[0] or valideaza_cui(c)[0]) else None


def alege(cur, schema, salariat_id, data, camp):
    """Salariatul ales, din salariații firmei: {id, nume, cif}, sau refuz (`DateInvalide`) lângă câmpul `camp` al ecranului:
    nealeas / necunoscut / neangajat la `data` (fără `data` — data dispoziției refuzată separat — nu se verifică angajarea). `cif` = CNP-ul, numai valid (altfel None)."""
    try:
        sid = int(salariat_id)
    except (TypeError, ValueError):
        sid = None
    if not sid:
        raise _erori.DateInvalide({"mesaj": "Alege salariatul care a făcut deplasarea: avansul spre decontare (542) se urmărește pe "
                                            "persoană.", "erori_campuri": [{"camp": camp, "mesaj": "Alege salariatul."}]})
    r = repo_operatiuni.salariat(cur, schema, sid)
    if not r:
        raise _erori.DateInvalide({"mesaj": "Salariatul ales nu e în evidența firmei.",
                                   "erori_campuri": [{"camp": camp, "mesaj": "Alege salariatul din listă."}]})
    nume = " ".join(x for x in (r["nume"], r["prenume"]) if x).strip() or "salariatul ales"
    if data and ((r["data_angajare"] and data < r["data_angajare"]) or (r["data_incetare"] and data > r["data_incetare"])):
        raise _erori.DateInvalide({"mesaj": "%s nu era salariat al firmei la %s: decontul de deplasare e al unui salariat (CF art.76 "
                                            "alin.(2) lit.k)." % (nume, data_ro(data)),
                                   "erori_campuri": [{"camp": camp, "mesaj": "Salariatul nu era angajat la data decontului."}]})
    return {"id": r["id"], "nume": nume, "cif": cif_partener(r["cnp"])}

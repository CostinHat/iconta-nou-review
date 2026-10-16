# -*- coding: utf-8 -*-
"""USE_CASE — trimiterea unei facturi in SPV: orchestrarea, si numai ea.

[P7 · valul D2, 13.09.2026] Ce e aici statea in `core/efactura_send.py`, modul declarat
`FISCAL_ENGINE`. Textul canonic (`PLAN_HARDENING.md:845`) cere, mecanic, ca *„un motor fiscal nu
importa `db`"* — iar acela il importa, cu 8 instructiuni SQL si trei conexiuni deschise de el
insusi. Era SINGURA incalcare `D2` din repo.

**Nimic nu s-a rescris: s-a mutat.** Cele patru porti ale lui `trimite` sunt in aceeasi ordine, pe
aceleasi conditii, cu aceleasi stari intoarse; SQL-ul a trecut, caracter cu caracter, in
`core/repo_efactura.py` si `core/repo_tenants.py`.

**PROPRIETATEA TRANZACTIEI NU S-A MUTAT** — contractul P4 nu se redeschide aici. `trimite` deschide
exact aceleasi TREI conexiuni, la aceleasi locuri in sir, si comite exact unde comitea. S-a schimbat
fisierul care le deschide, nu cine le detine. *Asta e si alegerea lectiei 27: cand o mutare ar putea
schimba hotarele, se tin unde erau si se scrie ca s-au tinut.*

Ce a ramas in `core/efactura_send.py`: generatorul XML UBL 2.1 / CIUS-RO, validatorul de structura
si invelisurile de apel ANAF — adica motorul fiscal, fara baza de date.
"""
import hashlib

import psycopg2.extras as _E

from core import db
from core import efactura_send as _ef
from core import repo_efactura as _repo
from core import spv_conector



#: [deficiența 289b] cabinetul neconectat la SPV — sursa unică a textului (ruta `facturi/{id}/trimite-spv` îl afișează cu butonul spre conectare)
MESAJ_FARA_TOKEN = ("Cabinetul nu e conectat la SPV, deci factura nu poate pleca la ANAF. Conectarea se face o singură dată, din "
                    "Setări cont → Conectare SPV, cu certificatul digital al administratorului.")

def incarca_factura(conn, schema, factura_id):
    """
    Citeste factura + linii + emitent (firma_profil) + cumparator (tert_* pe factura),
    pe schema curenta. Intoarce (factura, linii, furnizor, client) - dict-uri simple.
    Cumparatorul e denormalizat pe factura (tert_nume/tert_cui/tert_adresa); nu mai
    exista tabelul `clienti` cu adresa structurata din build-ul vechi.
    """
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        factura = _repo.factura_pentru_ubl(cur, schema, factura_id)
        if not factura:
            raise ValueError("factura %s inexistentă în %s" % (factura_id, schema))
        linii = _repo.linii_pentru_ubl(cur, schema, factura_id)
        furnizor = _repo.emitent_pentru_ubl(cur, schema)
    if not furnizor:
        raise ValueError("Datele firmei emitente nu sunt completate: completează-le în Date firmă înainte de a trimite factura.")
    if not linii:
        raise ValueError("factura %s nu are linii" % factura_id)
    client = {
        "nume": factura.get("tert_nume"),
        "cui": factura.get("tert_cui"),
        "adresa": factura.get("tert_adresa"),
        "oras": factura.get("tert_oras"),
        "judet": factura.get("tert_judet"),
        "cod_postal": None,   # cod postal cumparator: inca nestructurat (optional BT-53)
        "tara": (factura.get("tert_tara") or "RO").strip().upper() or "RO",   # [274b] BT-55 (și BT-80 la livrarea intracomunitară)
    }
    return dict(factura), [dict(l) for l in linii], dict(furnizor), client


def genereaza_din_factura(conn, schema, factura_id):
    """Convenienta: loader + generator intr-un pas. Intoarce (xml, factura)."""
    factura, linii, furnizor, client = incarca_factura(conn, schema, factura_id)
    return _ef.genereaza_xml(factura, linii, furnizor, client), factura


def trimite(schema, factura_id, principal, mediu="test"):
    """
    Trimite o factura in SPV cu PORTILE IN ORDINE FIXA (niciuna sarita):
      1) TOKEN VIU: principalul are token activ? altfel stare='fara_token' (conecteaza ANAF intai).
      2) VALIDARE/FACT1 (Regula 1): structura valida la validatorul ANAF? altfel stare='nevalidat'
         + erorile BR-RO, FARA upload. Diferentiatorul vs SmartBill: nu trimitem gunoi.
      3) IDEMPOTENCY: exista deja send VIU (incarcat/in_prelucrare/ok) pe factura+mediu? altfel
         stare='deja_trimisa'. Upload-ul ANAF NU e idempotent - dubla trimitere = dubla factura.
      4) UPLOAD prin apel_anaf pe tokenul principalului -> scrie randul INDIFERENT de rezultat
         (ok/eroare_upload + error_message integral).
    Poll-ul (stareMesaj/descarcare) ramane pe cron, NU sincron aici. Intoarce {stare, ...}.
    genereaza_din_factura poate ridica EDateIncomplete (sector Bucuresti lipsa) / NotImplementedError
    (taxare inversa) - apelantul (ruta) le mapeaza la 422.
    """
    # P0: genereaza XML (poate ridica EDateIncomplete/NotImplementedError -> prinse de ruta)
    with db.get_conn() as conn:
        # POARTA 1: token viu?
        if spv_conector.ia_token_activ(conn, principal) is None:
            # [deficiența 289b] textul refuzului, în cuvintele contabilului; ruta îl trimite cu butonul spre Setări cont → Conectare SPV
            return {"stare": "fara_token", "mesaj": MESAJ_FARA_TOKEN}
        with conn.cursor() as cur:
            cif = "".join(c for c in str(_repo.cui_emitent(cur, schema)[0] or "") if c.isdigit())
        # POARTA 1b [17.10.2026, decizia Costin pct.2]: ultima citire a CUI-ului firmei cu tokenul activ a primit „Nu aveti drept in SPV”
        # -> nu se încarcă; refuzul spune exact asta (același text ca starea firmei). O citire nouă, reușită, ridică poarta.
        _st = spv_conector.stare_firma(conn, principal, cif)
        if _st.get("are_drept") is False:
            return {"stare": "fara_drept", "mesaj": _st["mesaj"]}
        xml, _factura = genereaza_din_factura(conn, schema, factura_id)
    sha = hashlib.sha256(xml.encode("utf-8")).hexdigest()

    # POARTA 2: validare structura pe validatorul ANAF - FARA upload daca nok
    val_ok, val_msg = _ef.valideaza(xml)
    extern = (_factura.get("tert_tara") or "RO").strip().upper() not in ("", "RO")
    if not val_ok and extern:
        # [274b] cumpărătorul din afara României: validatorul îl caută în baza contribuabililor români și răspunde mereu
        # „ERRIdentif — nu a fost identificat cui cumparator” (verificat 16.10.2026, cu un cod de TVA UE real). Asta e identificarea, nu
        # structura, și o rezolvă încărcarea cu `extern=DA` (MF, „Prezentare servicii web e-Factura”: „se completeaza doar in cazul in
        # care cumparatorul este din exteriorul Romaniei (nu are CUI sau NIF)”). Orice altă eroare oprește trimiterea, ca până acum.
        val_msg = [m for m in val_msg if not _ef.e_identificare_cumparator(m)]
        val_ok = not val_msg
    if not val_ok:
        return {"stare": "nevalidat", "validare_ok": False, "validare_mesaje": val_msg}

    # POARTA 3: idempotency (send viu existent) + insert 'pregatit' in aceeasi tranzactie
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            viu = _repo.trimitere_vie(cur, schema, factura_id, mediu)
            if viu:
                return {"stare": "deja_trimisa", "trimitere_id": viu[0], "stare_existenta": viu[1]}
            tid = _repo.insereaza_trimitere_pregatita(cur, schema, factura_id, mediu, xml, sha)[0]

    rez = {"trimitere_id": tid, "cif": cif, "xml_sha256": sha, "mediu": mediu, "validare_ok": True}

    # POARTA 4: upload real prin apel_anaf (scrie randul indiferent de rezultat)
    try:
        r = _ef.upload_ubl(principal, cif, xml, mediu, extern=extern)
        text = r.text or ""
        ex, index, errs = _ef._parse_upload(text)
        rez.update({"http": r.status_code, "execution_status": ex,
                    "index_incarcare": index, "errors": errs, "raspuns": text})
        if r.status_code == 200 and ex == 0 and index:
            stare, errmsg = "incarcat", None
        else:
            stare, errmsg = "nok", ("\n".join(errs) if errs else text[:4000])
            if "nu aveti drept" in (errmsg or "").lower():
                # [17.10.2026] refuzul de drept venit la încărcare (200 + mesaj, ca la citire): spus ca la starea firmei
                rez.update({"fara_drept": True, "mesaj": spv_conector.mesaj_fara_drept(cif, errmsg)})
    except spv_conector.EroareSpvFaraDrept as e:
        # 403 = certificatul nu are drept (CIF/serviciu) - NU e eroare de structura
        rez.update({"http": 403, "execution_status": None, "index_incarcare": None,
                    "errors": [], "raspuns": str(e), "fara_drept": True,
                    "mesaj": spv_conector.mesaj_fara_drept(cif, str(e))})   # [17.10.2026] același text ca starea firmei
        stare, errmsg, index, ex = "eroare_upload", "403 fara drept SPV: %s" % e, None, None
    except Exception as e:
        rez.update({"http": None, "execution_status": None, "index_incarcare": None,
                    "errors": [], "raspuns": str(e)})
        stare, errmsg, index, ex = "eroare_upload", "exceptie upload: %s" % str(e)[:2000], None, None

    # 3) scrie rezultatul complet (commit) - INDIFERENT de rezultat
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            _repo.rezultatul_trimiterii(cur, schema, stare, index, ex, errmsg, tid)
    rez["stare"] = stare
    return rez

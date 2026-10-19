# anaf_api.py — validare CUI la ANAF (API public v9) + extragere CUI din fișier.
# Sursă oficială: https://static.anaf.ro/static/10/Anaf/Informatii_R/Servicii_web/doc_WS_V9.txt
# Endpoint: POST https://webservicesp.anaf.ro/api/PlatitorTvaRest/v9/tva
# Body: [{"cui": Numar, "data": "AAAA-LL-ZZ"}]  (max 100 CUI / cerere, max 1 cerere/sec)

import requests
from datetime import date

ANAF_URL = "https://webservicesp.anaf.ro/api/PlatitorTvaRest/v9/tva"
MAX_CUI = 100


def _curata(cui_brut):
    """Extrage doar cifrele (acceptă 'RO12345', ' 12345 ', etc.). None dacă nimic."""
    cifre = "".join(ch for ch in str(cui_brut) if ch.isdigit())
    return cifre or None


def extrage_cui_din_fisier(continut, nume_fisier=""):
    """
    Extrage CUI-urile dintr-un CSV / TXT / XLSX / XLS (citit prin `core.import_tabel`).
    Coloana CUI după antet („Cod fiscal”, „CUI”, „CIF”); fără antet recunoscut, prima coloană.
    Curăță fiecare valoare la cifre, păstrează doar 2–10 cifre, fără duplicate.
    """
    # [14.10.2026, comanda Costin „Importul din SAGA”] citirea trece prin `core.import_tabel`: Windows-1250 recunoscut sau
    # refuzat numit, XLS acceptat, antetul căutat sub titluri; coloana CUI = „Cod fiscal”, „CUI”, „CIF” (cuvinte întregi).
    from core import import_tabel as _it
    randuri = [r for r in _it.citeste(continut, nume_fisier) if not _it.rand_gol(r)]
    if not randuri:
        return []
    campuri = {"cui": ("cod fiscal cnp", "cod fiscal", "cui", "cif", "cod unic de inregistrare")}
    try:
        antet, start = _it.gaseste_antet(randuri, campuri, obligatorii=("cui",), nume_fisier=nume_fisier)
        col = _it.coloana(antet, campuri["cui"], camp="CUI")
    except _it.ColoaneAmbigue:
        raise
    except _it.FisierNecitit:
        col, start = 0, 0                       # fără antet: prima coloană, de pe primul rând (ca până acum)
    randuri = [[_it.celula(r, j) for j in range(len(r))] for r in randuri[start:]]

    cui_uri, vazute = [], set()
    for r in randuri:
        bruta = r[col] if col < len(r) else ""
        cifre = _curata(bruta)
        if cifre and 2 <= len(cifre) <= 10 and cifre not in vazute:
            vazute.add(cifre)
            cui_uri.append(cifre)
    return cui_uri


def _tva_inceput_activ(tva):
    """Data începerii înregistrării TVA ACTIVE (perioada fără data_sfarsit), 'YYYY-MM-DD' sau None.
    Doar dacă scpTVA=True. Fapt de la ANAF (inregistrare_scop_Tva.perioade_TVA[].data_inceput_ScpTVA)."""
    if not tva.get("scpTVA"):
        return None
    for p in (tva.get("perioade_TVA") or tva.get("perioadeTVA") or []):
        if not (p.get("data_sfarsit_ScpTVA") or "").strip():   # perioada activă (fără sfârșit)
            return (p.get("data_inceput_ScpTVA") or "").strip() or None
    return None


def _tva_perioade(tva):
    """TOATE perioadele de inregistrare in scop TVA de la ANAF (nu doar cea activa) - INTREG, ca sa NU se
    arunce istoricul: [{inceput, sfarsit}] ('sfarsit' gol = perioada activa). ANAF le trimite in
    perioade_TVA[]; sunt exact ce cere backfill-ul clasificarii istorice (data facturii in perioada)."""
    out = []
    for p in (tva.get("perioade_TVA") or tva.get("perioadeTVA") or []):
        out.append({"inceput": (p.get("data_inceput_ScpTVA") or "").strip() or None,
                    "sfarsit": (p.get("data_sfarsit_ScpTVA") or "").strip() or None})
    return out


def platitor_tva_freeze(cui, fallback=None):
    """Statutul de platitor TVA al unui CUI, INGHETAT din ANAF F004 (best-effort) - pentru stocare pe factura
    (fapt contabil imutabil). ANAF indisponibil / CUI negasit -> `fallback` (declaratia contabilului / semantica
    operatiunii). NU ridica: nu blocheaza emiterea facturii pe ANAF-jos."""
    try:
        r = valideaza_cui([cui])
        if r and r[0].get("gasit"):
            return bool(r[0].get("platitor_tva"))
    except Exception:  # noqa: BLE001
        pass
    return fallback


def furnizor_incasare_freeze(cui, fallback=False, data=None):
    """[A9 art.297 alin.2 CF] Statutul TVA-la-incasare al FURNIZORULUI, INGHETAT din ANAF
    (RTVAI.statusTvaIncasare, best-effort) - pentru stocare pe factura primita: decide deducerea
    amanata (D300) si tipul AI (D394). ANAF indisponibil / CUI negasit -> `fallback` (ce a declarat
    contabilul). NU ridica: nu blocheaza ingestia facturii pe ANAF-jos. Oglinda `platitor_tva_freeze`,
    aceeasi sursa unica `valideaza_cui` (campul `tva_la_incasare`, RTVAI.statusTvaIncasare)."""
    try:
        # [3j · HG 1/2016 titlul VII pct.67(6)] statutul RTVAI se citeste asa cum era LA DATA EMITERII
        # facturii (`data`), nu azi: dreptul de deducere al beneficiarului depinde de regimul furnizorului
        # "la data emiterii unei facturi". data=None -> comportament vechi (azi).
        r = valideaza_cui([cui], data_interogare=data)
        if r and r[0].get("gasit"):
            return bool(r[0].get("tva_la_incasare"))
    except Exception:  # noqa: BLE001
        pass
    return fallback


def statut_furnizori(furnizori, interogare=None):
    """[deficiența 418a, comanda Costin 9.3] „Statutul se află din XML (CompanyID cu prefix RO în PartyTaxScheme/VAT) și din verificarea
    ANAF pe care aplicația o face deja; TVA la încasare se verifică în registrul ANAF. Contabilul nu trebuie să-l introducă manual.”

    `furnizori` = [(cui, data facturii ISO, codul de TVA din XML (BT-31) sau None)] -> {(cui, data): {platitor_tva, sursa_platitor,
    tva_la_incasare, sursa_incasare}}; o valoare None = nu se poate afla (ANAF nu răspunde și XML-ul nu transează) — atunci, și numai
    atunci, o spune contabilul. ANAF: registrul contribuabililor (scpTVA) și Registrul TVA la încasare (statusTvaIncasare), interogate
    la DATA FACTURII (HG 1/2016 titlul VII pct.67 alin.(6): dreptul de deducere urmează regimul furnizorului „la data emiterii unei
    facturi”). XML: BT-31 cu prefixul RO = înregistrat în scopuri de TVA în România (CF art.316)."""
    from core.pdf_util import data_ro
    interogare = interogare or valideaza_cui   # testele o simulează (core/conftest.py), niciodată ANAF real
    out, pe_data = {}, {}
    for cui, data, cod in furnizori:
        out[(cui, data)] = {"platitor_tva": None, "sursa_platitor": None, "tva_la_incasare": None, "sursa_incasare": None, "_cod": cod}
        pe_data.setdefault(data, []).append(cui)
    for data, cuii in pe_data.items():
        try:
            gasite = {str(r["cui"]): r for r in interogare(cuii, data_interogare=data) if r.get("gasit")}
        except Exception:  # noqa: BLE001 — ANAF indisponibil: rămâne XML-ul
            gasite = {}
        for cui in cuii:
            r, st = gasite.get(_curata(cui)), out[(cui, data)]
            if r:
                st.update(platitor_tva=bool(r["platitor_tva"]), tva_la_incasare=bool(r["tva_la_incasare"]),
                          sursa_platitor="ANAF, registrul contribuabililor la %s" % data_ro(data),
                          sursa_incasare="ANAF, Registrul persoanelor care aplică TVA la încasare, la %s" % data_ro(data))
            elif str(st["_cod"] or "").upper().startswith("RO"):
                st.update(platitor_tva=True, sursa_platitor="XML-ul facturii: codul de TVA %s al furnizorului (BT-31)" % st["_cod"])
    for st in out.values():
        st.pop("_cod")
    return out


def separa_cui(lista_cui):
    """Imparte intrarile brute in (curatate_unice, ignorate).
    'ignorate' = intrari care nu contin nicio cifra -> nu pot fi un CUI (antet de coloana, nume, typo).
    Regula 4 (fara default tacut) + Regula 14.4: intrarea care nu-i CUI NU dispare in tacere - o intoarcem
    ca ecranul s-o arate contabilului ('verifica daca lipseste o firma'). Duplicatele se dedup (nu-s ignorate).
    Randurile pur goale nu se raporteaza (nu-s intrari reale)."""
    curatate, vazute, ignorate = [], set(), []
    for c in lista_cui:
        cifre = _curata(c)
        if not cifre:
            brut = str(c).strip()
            if brut:
                ignorate.append(brut)
            continue
        if cifre not in vazute:
            vazute.add(cifre)
            curatate.append(int(cifre))
    return curatate, ignorate


#: [deficiențele 303 + 317, comanda Costin 17.10.2026 7.2] ANAF care nu răspunde (aștepare peste `timeout`, conexiune căzută) nu e o
#: eroare a aplicației: refuzul spune ce s-a întâmplat și ce faci, nu textul bibliotecii („HTTPSConnectionPool(...) Read timed out”).
MESAJ_ANAF_NU_RASPUNDE = ("ANAF nu răspunde acum la verificarea CUI (serviciul lor n-a răspuns în 20 de secunde). Încearcă din nou peste "
                          "un minut; până atunci poți completa datele de mână.")


def mesaj_indisponibil(e):
    """Textul refuzului pentru o verificare la ANAF care n-a reușit: ANAF a răspuns cu o eroare (codul ei), altfel n-a răspuns deloc
    (timeout, conexiune căzută) — niciodată textul excepției."""
    cod = getattr(getattr(e, "response", None), "status_code", None)
    return ("ANAF a refuzat verificarea CUI (răspunsul serviciului: %s). Încearcă din nou peste un minut." % cod if cod
            else MESAJ_ANAF_NU_RASPUNDE)


def valideaza_cui(lista_cui, data_interogare=None):
    """Întoarce [{cui, denumire, platitor_tva, tva_data_inceput, stare, inactiv, adresa, localitate, judet, ..., gasit}], ordine păstrată."""
    azi = data_interogare or date.today().isoformat()

    curatate, _ignorate = separa_cui(lista_cui)
    if not curatate:
        return []

    rezultate = []
    for i in range(0, len(curatate), MAX_CUI):
        if i > 0:
            import time
            time.sleep(1.1)  # ANAF: max 1 cerere/sec
        lot = curatate[i:i + MAX_CUI]
        payload = [{"cui": c, "data": azi} for c in lot]
        r = requests.post(ANAF_URL, json=payload, timeout=20,
                          headers={"Content-Type": "application/json"})
        # anaf_404_notfound_v1: ANAF intoarce 404 cu body valid cand CUI e notFound
        if r.status_code not in (200, 404):
            r.raise_for_status()
        dj = r.json()
        for f in dj.get("found", []):
            dg = f.get("date_generale", f.get("dategenerale", {})) or {}
            tva = f.get("inregistrare_scop_Tva", f.get("inregistrarescopTva", {})) or {}
            inactiv = f.get("stare_inactiv", {}) or {}
            rtvai = f.get("inregistrare_RTVAI", {}) or {}   # TVA la incasare
            dfisc = f.get("adresa_domiciliu_fiscal", {}) or {}   # [C61] structura din anaf_surse/doc_WS_V9.txt
            rezultate.append({
                "cui": str(dg.get("cui", "")),
                "denumire": (dg.get("denumire") or "").strip(),
                "platitor_tva": bool(tva.get("scpTVA")),
                "tva_data_inceput": _tva_inceput_activ(tva),   # data începerii înregistrării TVA active (fapt ANAF)
                "tva_perioade": _tva_perioade(tva),   # TOATE perioadele (istoric intreg, pt backfill)
                "tva_la_incasare": bool(rtvai.get("statusTvaIncasare")),   # F188: RTVAI.statusTvaIncasare
                "stare": (dg.get("stare_inregistrare") or dg.get("stareinregistrare") or "").strip(),
                "inactiv": bool(inactiv.get("statusInactivi")),
                "adresa": (dg.get("adresa") or "").strip(),
                # v9 real: campul e 'cod_CAEN' (underscore); 'codCAEN' = fallback compat
                "cod_caen": (dg.get("cod_CAEN") or dg.get("codCAEN") or "").strip(),
                "nr_reg_com": (dg.get("nrRegCom") or "").strip(),          # F188
                # [comanda Costin 05.10.2026 pct.2] documentat în doc_WS_V9.txt (date_generale.forma_juridica), văzut pe răspuns real
                "forma_juridica": (dg.get("forma_juridica") or "").strip(),
                # [deficiența 229, 12.10.2026] documentat în doc_WS_V9.txt (date_generale.data_inregistrare, „Data inregistrare”),
                # văzut pe răspuns real: '2002-01-23' pentru J2002000372404 — data înființării, de la care curge primul exercițiu
                "data_inregistrare": (dg.get("data_inregistrare") or "").strip() or None,
                # [C61, 19.10.2026] documentat în doc_WS_V9.txt (adresa_domiciliu_fiscal.ddenumire_Localitate / dcod_JudetAuto), văzut pe
                # răspuns real (14399840: „Sector 2 Mun. Bucureşti” / „B”). Domiciliul FISCAL, nu sediul social (adresa_sediu_social.s…):
                # e aceeași adresă ca `adresa` (date_generale.adresa), deci localitatea și județul se potrivesc cu ce scrie pe factură.
                "localitate": (dfisc.get("ddenumire_Localitate") or "").strip(),
                "judet": (dfisc.get("dcod_JudetAuto") or "").strip(),
                "gasit": True,
            })
        for c in dj.get("notFound", []):
            rezultate.append({
                "cui": str(c), "denumire": "", "platitor_tva": False, "tva_data_inceput": None, "tva_la_incasare": False,
                "stare": "", "inactiv": False, "adresa": "", "cod_caen": "", "nr_reg_com": "", "data_inregistrare": None,
                "localitate": "", "judet": "", "gasit": False,
            })
    return rezultate

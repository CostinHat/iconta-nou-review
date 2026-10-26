"""
core/raportari_ai.py - triaj AI al sesizarilor (stratul 5 Raportari).
La sesizare noua: Claude primeste textul + baza de cunostinte (FUNCTIONALITATI.csv,
pozitiile LIVE) si decide: raspunde cu ghidaj de folosire SAU escaladeaza la admin
(pentru_admin=true). Reguli stricte in promptul de sistem: doar ghidaj pe ce exista,
zero sfaturi fiscale, zero promisiuni; orice incertitudine = escaladare.
Fallback sigur: AI indisponibil/eroare -> escaladare (comportamentul de dinainte).
"""
import csv, json, pathlib, re
from core import ai_client
from core.cache_declarat import Declaratie as _Dec

_BAZA = None
_BAZA_DECLARATIE = _Dec(
    rol="baza de cunostinte trimisa lui Claude la fiecare sesizare — pozitiile LIVE din registru, "
        "gata formatate",
    sursa="FUNCTIONALITATI.csv, coloana 7 (`LIVE`) — acelasi fisier versionat ca la `ajutor`",
    motiv="parsarea CSV-ului plus filtrarea si formatarea celor ~200 de linii, la fiecare sesizare",
    invalidare="la repornirea procesului; acelasi rationament ca la `ajutor._CACHE` — sursa e "
               "versionata, iar orice schimbare a ei trece prin commit, deci prin repornire",
    dovada="core/test_cache_declarat.py::test_baza_ai_se_reconstruieste_identic",
)

def _baza_cunostinte():
    global _BAZA
    if _BAZA is None:
        cale = pathlib.Path(__file__).resolve().parent.parent / "FUNCTIONALITATI.csv"
        linii = []
        with open(cale, encoding="utf-8-sig") as f:
            for r in csv.reader(f):
                # [lotul 13, 572] numai funcțiile pe care le folosesc cabinetele (nu ale platformei: nivel `admin`), cu rolurile din cod
                # spuse în cuvintele aplicației — modelul le copia în răspuns („superadmin/admin_firma/angajat”)
                if len(r) > 7 and str(r[7]).startswith("LIVE") and str(r[3]).strip() != "admin":
                    linii.append("- %s: %s (unde în aplicație: %s)" % (r[0], fara_roluri_interne(r[1][:220]), fara_roluri_interne(r[4])))
        _BAZA = "\n".join(linii)
    return _BAZA

# [lotul 13, deficiențele 572 / 573 — anexa: „Răspuns la «Cum adaug un asistent nou?»: fără diacritice, ghicit («de obicei '+'…»), roluri
# interne din cod (superadmin/admin_firma/angajat) în loc de drepturile reale, aliniat la dreapta. Când nu știe sigur, trebuie să
# escaladeze.” · „La sesizarea escaladată nu se vede clasificarea/motivul AI; mesajul automat către utilizator e fără diacritice.”]
# Promptul cere română cu diacritice, numai pași scriși în lista primită, drepturile pe numele lor din aplicație; iar CODUL verifică
# răspunsul (`verifica_raspuns`): unul care ghicește, numește un rol din cod sau e scris fără diacritice NU pleacă la om — sesizarea se
# escaladează, cu motivul păstrat (`raportari_api.scrie_triajul`), pe care echipa îl vede în Panou Admin → Raportări.
SISTEM = (
    "Ești asistentul AI al aplicației românești de contabilitate iConta.eu. Primești sesizări de la contabili. Decizi: RĂSPUNZI (numai "
    "întrebări despre CUM SE FOLOSEȘTE aplicația, când lista de funcționalități primită spune EXPLICIT unde și cum se face) sau "
    "ESCALADEZI la echipa iConta. ESCALADEZI OBLIGATORIU: erori sau comportament greșit, cereri de funcționalități noi, probleme de date "
    "sau de cont, orice întrebare fiscală sau contabilă de speță (nu dai NICIODATĂ sfaturi fiscale) și ORICE întrebare la care lista nu "
    "spune exact pașii — nu ghicești, nu scrii „de obicei”, „probabil”, „ar trebui”. Nu promiți remedieri sau termene. Nu inventezi "
    "funcționalități, butoane sau meniuri. Drepturile le numești ca în aplicație: «administratorul cabinetului», «asistent», drepturile "
    "«Poate pregăti», «Poate valida», «Poate depune» — niciodată nume din cod (superadmin, admin_firma, angajat). Răspunsul către "
    "utilizator: limba română CU DIACRITICE, politicos, concis, concret (unde în aplicație + pașii), TEXT SIMPLU, fără Markdown. "
    'Răspunzi STRICT cu JSON, fără alt text: {"decizie": "raspund", "raspuns": "..."} '
    'SAU {"decizie": "escaladez", "motiv": "..."} (motivul, pe scurt, pentru echipa iConta).'
)

#: [572] rolurile din cod și cuvintele aplicației pentru ele (baza de cunoștințe și verificarea răspunsului)
ROLURI_INTERNE = {"superadmin": "administratorul platformei iConta.eu", "admin_firma": "administratorul cabinetului",
                  "patronul": "administratorul cabinetului", "patron": "administratorul cabinetului"}
_RE_ROL = re.compile(r"\b(superadmin|admin_firma|patronul|patron)\b|\(?\b(?:superadmin|admin_firma)/[\w/]+\)?", re.I)
#: [572] ghicitul: răspunsul care nu știe sigur nu pleacă la om
_RE_GHICIT = re.compile(r"\b(de obicei|probabil|posibil ca|s-ar putea|ar trebui s[ăa] (?:existe|fie|g[ăa]se[sș]ti)|cred c[ăa]|"
                                      r"în general|in general|de regul[ăa])\b", re.I)
_DIACRITICE = set("ăâîșțĂÂÎȘȚşţŞŢ")


def fara_roluri_interne(text):
    """PURĂ. [572] Rolurile din cod spuse în cuvintele aplicației (lista „superadmin/admin_firma/angajat/client” -> „rolul utilizatorului”)."""
    t = re.sub(r"\(?\b(?:superadmin|admin_firma|angajat|client)(?:/(?:superadmin|admin_firma|angajat|client))+\)?", "rolul utilizatorului",
               str(text or ""))
    for cod, om in ROLURI_INTERNE.items():
        t = re.sub(r"\b%s\b" % cod, om, t)
    return t


def verifica_raspuns(text):
    """PURĂ. [572] None dacă răspunsul poate pleca la om; altfel motivul pentru care se escaladează."""
    t = str(text or "")
    if _RE_ROL.search(t):
        return "răspunsul numea un rol din cod (%s)" % _RE_ROL.search(t).group(0)
    m = _RE_GHICIT.search(t)
    if m:
        return "răspunsul nu era sigur („%s”)" % m.group(0)
    litere = [c for c in t if c.isalpha()]
    if len(litere) >= 40 and not any(c in _DIACRITICE for c in t):
        return "răspunsul era scris fără diacritice"
    return None

def triaj(subiect, text):
    """Intoarce {"decizie": "raspund", "raspuns": ...} sau {"decizie": "escaladez", "motiv": ...}."""
    if not ai_client.disponibil():
        return {"decizie": "escaladez", "motiv": "Asistentul AI nu e configurat pe acest server."}
    prompt = ("FUNCTIONALITATILE APLICATIEI (singura sursa de adevar):\n%s\n\n"
              "SESIZAREA:\nSubiect: %s\nText: %s" % (_baza_cunostinte(), subiect or "(fara)", text))
    try:
        brut = ai_client.genereaza_text(prompt, sistem=SISTEM, max_tokens=700, temperatura=0.2,
                                        model="claude-haiku-4-5")  # triaj = sarcina de clasificare+ghidaj: modelul rapid
        d = json.loads(brut.replace("```json", "").replace("```", "").strip())
        if d.get("decizie") == "raspund" and (d.get("raspuns") or "").strip():
            raspuns = ai_client.text_simplu(d["raspuns"].strip())   # [lot 06.10 pct.14]
            motiv_nu = verifica_raspuns(raspuns)   # [lotul 13, 572] ghicit / rol din cod / fără diacritice -> nu pleacă la om
            if not motiv_nu:
                return {"decizie": "raspund", "raspuns": raspuns}
            motiv = "Asistentul AI a încercat să răspundă, dar %s." % motiv_nu
        else:
            motiv = (d.get("motiv") or "asistentul AI nu a spus motivul")[:300]
        # [lotul 13, 572] o singură escaladare pentru ambele drumuri (AI-ul escaladează / răspunsul lui e oprit de verifica_raspuns)
        return {"decizie": "escaladez", "motiv": motiv}
    except Exception as e:
        return {"decizie": "escaladez", "motiv": ("Asistentul AI nu a răspuns (%s)." % type(e).__name__)[:300]}

def proceseaza(raportare_id, subiect, text):
    """Triaj + scriere rezultat. Apelata in thread separat (nu blocheaza crearea)."""
    from core import db, raportari_api
    r = triaj(subiect, text)
    try:
        with db.get_conn() as conn:
            if r["decizie"] == "raspund":
                raportari_api.adauga_mesaj(conn, raportare_id, None, "ai", r["raspuns"])
                raportari_api.scrie_triajul(conn, raportare_id, "raspuns")   # [lotul 13, 573]
            else:
                raportari_api.seteaza_pentru_admin(conn, raportare_id, True)
                raportari_api.scrie_triajul(conn, raportare_id, "escaladare", r.get("motiv"))   # [573] motivul, pentru echipa iConta
                raportari_api.adauga_mesaj(conn, raportare_id, None, "ai", raportari_api.TEXT_ESCALADARE,   # [573] cu diacritice
                    schimba_stare=False, veste=False)   # [291] ecoul cererii, nu o veste: nu aprinde bulina
            conn.commit()
    except Exception as e:  # noqa: BLE001 — crearea sesizarii a reusit deja; esecul triajului nu o strica, dar nu e tacut
        from core import observare as _obs
        _obs.esec_secundar("triaj AI al sesizarii %s" % raportare_id, e)

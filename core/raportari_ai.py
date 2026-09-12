"""
core/raportari_ai.py - triaj AI al sesizarilor (stratul 5 Raportari).
La sesizare noua: Claude primeste textul + baza de cunostinte (FUNCTIONALITATI.csv,
pozitiile LIVE) si decide: raspunde cu ghidaj de folosire SAU escaladeaza la admin
(pentru_admin=true). Reguli stricte in promptul de sistem: doar ghidaj pe ce exista,
zero sfaturi fiscale, zero promisiuni; orice incertitudine = escaladare.
Fallback sigur: AI indisponibil/eroare -> escaladare (comportamentul de dinainte).
"""
import csv, json, pathlib
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
                if len(r) > 7 and str(r[7]).startswith("LIVE"):
                    linii.append("- %s: %s (unde in aplicatie: %s)" % (r[0], r[1][:220], r[4]))
        _BAZA = "\n".join(linii)
    return _BAZA

SISTEM = (
    "Esti asistentul AI al aplicatiei romanesti de contabilitate iConta. Primesti sesizari de la "
    "contabili si clienti. Decizi: RASPUNZI (doar intrebari despre CUM SE FOLOSESTE aplicatia, pe baza "
    "listei de functionalitati primite) sau ESCALADEZI la administratorul uman. ESCALADEZI OBLIGATORIU: "
    "bug-uri/erori/comportament gresit, cereri de functionalitati noi, probleme de date sau cont, "
    "orice intrebare fiscala/contabila de speta (nu dai NICIODATA sfaturi fiscale), orice incertitudine. "
    "Nu promiti remedieri sau termene. Nu inventezi functionalitati. Raspunsul catre utilizator: "
    "romana, politicos, concis, concret (unde in aplicatie + pasii), TEXT SIMPLU fara Markdown/asteriscuri. "
    'Raspunzi STRICT cu JSON, fara alt text: {"decizie": "raspund", "raspuns": "..."} '
    'SAU {"decizie": "escaladez", "motiv": "..."}'
)

def triaj(subiect, text):
    """Intoarce {"decizie": "raspund", "raspuns": ...} sau {"decizie": "escaladez", "motiv": ...}."""
    if not ai_client.disponibil():
        return {"decizie": "escaladez", "motiv": "AI indisponibil"}
    prompt = ("FUNCTIONALITATILE APLICATIEI (singura sursa de adevar):\n%s\n\n"
              "SESIZAREA:\nSubiect: %s\nText: %s" % (_baza_cunostinte(), subiect or "(fara)", text))
    try:
        brut = ai_client.genereaza_text(prompt, sistem=SISTEM, max_tokens=700, temperatura=0.2,
                                        model="claude-haiku-4-5")  # triaj = sarcina de clasificare+ghidaj: modelul rapid
        d = json.loads(brut.replace("```json", "").replace("```", "").strip())
        if d.get("decizie") == "raspund" and (d.get("raspuns") or "").strip():
            return {"decizie": "raspund", "raspuns": d["raspuns"].strip()}
        return {"decizie": "escaladez", "motiv": (d.get("motiv") or "nespecificat")[:300]}
    except Exception as e:
        return {"decizie": "escaladez", "motiv": ("eroare AI: %s" % e)[:300]}

def proceseaza(raportare_id, subiect, text):
    """Triaj + scriere rezultat. Apelata in thread separat (nu blocheaza crearea)."""
    from core import db, raportari_api
    r = triaj(subiect, text)
    try:
        with db.get_conn() as conn:
            if r["decizie"] == "raspund":
                raportari_api.adauga_mesaj(conn, raportare_id, None, "ai", r["raspuns"])
            else:
                raportari_api.seteaza_pentru_admin(conn, raportare_id, True)
                raportari_api.adauga_mesaj(conn, raportare_id, None, "ai",
                    "Sesizarea ta a fost transmisa echipei iConta. Vei primi raspuns aici, in acest fir.",
                    schimba_stare=False)
            conn.commit()
    except Exception:
        pass  # crearea sesizarii a reusit deja; esecul triajului nu strica nimic

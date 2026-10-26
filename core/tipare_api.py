"""
core/tipare_api.py — Ecran G: Educatie pe tipare (statistic, fara AI).
Agregate deterministe pe declaratii_coada, materia prima pentru viitorul
strat AI. Trei perspective, toate pe cabinet (doar patron):
  1. Motive de respingere recurente
  2. Tipuri de declaratii cu rata de respingere
  3. Firme cu cele mai multe respingeri

La teste se umple singur. AI-ul (stratul 5) va citi exact aceste agregate.

[validare_note, 06.10.2026] Coada poartă și note (`fel='nota'`); tiparele de aici sunt ale DECLARAȚIILOR — filtrate explicit.
[lotul 13, deficiența 574 — „«Înlocuită de declarația generată din nou» (automat) e numărată ca respingere: D300 67% umflat; notele respinse
de om (ex. Asist Test azi) lipsesc.”] Tiparele sunt ale RESPINGERILOR FĂCUTE DE OM, pe declarații ȘI pe note: înlocuirea (automată, sau
retragerea propriei declarații urmată de regenerare — `coada_api.sql_inlocuita`, 458.1) nu e o respingere; nota respinsă la validare este.
"""
import psycopg2.extras as _E

from core.common import cate as _cate


def tipare(conn, cabinet_id):
    """[lotul 11, 458] Agregatele vin dintr-o SINGURĂ listă de PREGĂTIRI ale declarațiilor (`coada_api.sql_cheie_pregatire`: firma, tipul,
    perioada — oricâte rânduri a lăsat în coadă), nu din rânduri de coadă: „Generează din nou” lasă un rând nou pe aceeași declarație, iar
    rândurile numărau de câte ori fusese generată. Respingere = a omului (`coada_api.sql_inlocuita`): înlocuirea nu e o greșeală — pe
    cabinetul de test motivul nr.1 era „Înlocuită de declarația generată din nou …” (n=3). Fiecare pregătire respinsă e un rând al motivului
    ULTIMEI ei respingeri, deci Σ motive = Σ respinse pe tipuri = Σ respinse pe firme = `respinse`."""
    from core.coada_api import sql_cheie_pregatire as _cheie, sql_inlocuita
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "WITH x AS (SELECT d.tenant_id, d.tip, d.id, d.respins_la, d.motiv_respingere, " + _cheie("d") + " AS cheie, "
            "  (d.respins_la IS NOT NULL AND NOT " + sql_inlocuita("d") + ") AS respingere "
            "  FROM public.declaratii_coada d WHERE d.cabinet_id = %s AND d.fel IN ('declaratie', 'nota')), "   # [574] și notele
            "p AS (SELECT cheie, MIN(tenant_id) AS tenant_id, MIN(tip) AS tip, bool_or(respingere) AS respinsa, "
            "  (array_agg(COALESCE(NULLIF(TRIM(motiv_respingere), ''), '(fără motiv)') ORDER BY respins_la DESC, id DESC) "
            "     FILTER (WHERE respingere))[1] AS motiv "
            "  FROM x GROUP BY cheie) "
            "SELECT p.tenant_id, p.tip, p.respinsa, p.motiv, t.nume, t.cui "
            "  FROM p LEFT JOIN public.tenants t ON t.id = p.tenant_id",
            (cabinet_id,))
        prg = [dict(r) for r in cur.fetchall()]

    # ---------- 1) MOTIVE DE RESPINGERE recurente ----------
    pe_motiv = {}
    for x in prg:
        if x["respinsa"]:
            pe_motiv[x["motiv"]] = pe_motiv.get(x["motiv"], 0) + 1
    motive = [{"motiv": m, "n": n} for m, n in sorted(pe_motiv.items(), key=lambda kv: (-kv[1], kv[0]))]

    # ---------- 2) TIPURI cu rata de respingere ----------
    # total = pregătiri ale tipului; respinse = pregătiri respinse (de om) măcar o dată
    pe_tip = {}
    for x in prg:
        g = pe_tip.setdefault(x["tip"], [0, 0])
        g[0] += 1
        g[1] += 1 if x["respinsa"] else 0
    tipuri = [{"tip": tip, "total": tot, "respinse": resp,
               "pct": int(round(100.0 * resp / tot)) if tot else 0}  # round-ok: indicator (procent), nu sumă fiscală
              for tip, (tot, resp) in sorted(pe_tip.items(), key=lambda kv: (-kv[1][1], kv[0]))]

    # ---------- 3) FIRME cu cele mai multe respingeri ----------
    pe_firma = {}
    for x in prg:
        g = pe_firma.setdefault(x["tenant_id"], {"tenant_id": x["tenant_id"], "nume": x["nume"] or "(firmă necunoscută)",
                                                  "cui": x["cui"] or "", "respinse": 0, "total": 0})
        g["total"] += 1
        g["respinse"] += 1 if x["respinsa"] else 0
    firme = sorted((g for g in pe_firma.values() if g["respinse"] > 0), key=lambda g: (-g["respinse"], g["nume"]))

    out = {"ok": True, "motive": motive[:15], "tipuri": tipuri, "firme": firme[:15],
           "respinse": sum(n for n in pe_motiv.values())}   # totalul = Σ rândurilor motivelor (aceeași listă)
    # rezumat: avem date sau nu (pentru mesajul de gol)
    out["are_date"] = bool(out["motive"] or any(t["respinse"] for t in out["tipuri"]))
    return out


# ============================================================
#  F120 — strat AI generativ peste agregatele de mai sus
# ============================================================
def analiza_ai(date):
    """[F120] Analiza generativa: primeste agregatele deterministe (`tipare`, citite de apelant) si cere lui Claude o
    explicatie a tiparelor + recomandari CONCRETE. GROUNDED strict pe datele furnizate (fara cifre
    inventate). Refoloseste core.ai_client (model ales de proiect). Fallback curat daca AI indisponibil
    sau nu-s date - apelantul afiseaza mesajul, nu crapa ecranul.
    [R193, 10.10.2026] Nu primeste conexiune: agregatele se citesc inainte, iar modelul se intreaba cu pool-ul liber."""
    from core import ai_client
    if not date.get("are_date"):
        return {"disponibil": False, "motiv": "Nu există încă respingeri de analizat."}
    # [lotul 13, 576] „«prea puține cazuri» sub prag”: dintr-o mână de respingeri nu iese un tipar — modelul generaliza dintr-un caz
    if (date.get("respinse") or 0) < PRAG_ANALIZA:
        return {"disponibil": False, "motiv": "Prea puține respingeri pentru o analiză: %s; analiza pornește de la %d." % (
            _cate(date.get("respinse") or 0, "respingere", "respingeri"), PRAG_ANALIZA)}
    if not ai_client.disponibil():
        return {"disponibil": False, "motiv": "Asistentul AI nu e configurat pe acest server."}

    motive = "\n".join("- %s: %s" % (m["motiv"], _cate(m["n"], "respingere", "respingeri")) for m in date["motive"][:15])
    tipuri = "\n".join("- %s: %d din %d respinse (%d%%)" % (eticheta_tip(t["tip"]), t["respinse"], t["total"], t["pct"])
                       for t in date["tipuri"] if t["respinse"] > 0)
    firme = "\n".join("- %s: %d respinse din %d" % (f["nume"], f["respinse"], f["total"]) for f in date["firme"][:10])
    prompt = ("Date agregate ale cabinetului (respingeri făcute la validare, de un om; regenerările automate nu sunt incluse):\n\n"
              "MOTIVE DE RESPINGERE:\n%s\n\n"
              "DECLARAȚII ȘI NOTE, CU RATA DE RESPINGERE:\n%s\n\n"
              "FIRME CU CELE MAI MULTE RESPINGERI:\n%s\n\n"
              "Analizează tiparele și propune recomandări."
              % (motive or "(niciunul)", tipuri or "(niciunul)", firme or "(niciuna)"))
    try:
        text = ai_client.genereaza_text(prompt, sistem=SISTEM_ANALIZA, max_tokens=1000, temperatura=0.2)
    except Exception as e:
        return {"disponibil": False, "motiv": "Nu s-a putut genera analiza acum (%s)." % type(e).__name__}
    return {"disponibil": True, "analiza": curata_analiza(ai_client.text_simplu(text))}   # [lot 06.10 pct.14] fără marcaje brute pe ecran


#: [lotul 13, 576] sub atâtea respingeri (ale omului) nu se cere analiza: „prea puține cazuri”. Pragul nu e o valoare fiscală; e cât
#: de puțin poate susține un „tipar” (un motiv repetat de cel puțin două ori, pe cel puțin două pregătiri) — ales cel mai prudent.
PRAG_ANALIZA = 5
#: un motiv se poate numi „sistematic” / „repetat” numai de la atâtea cazuri (promptul o cere; garda de text o verifică)
PRAG_SISTEMATIC = 3

#: [lotul 13, 576 — „Construiește pe cifrele umflate și inventează: «Sesiunea A» inexistentă, check-out în Excel, «omite sistematic» dintr-un
#: singur caz; «---» afișat ca atare.”] Reguli, cu diacritice: numai ce e în date (niciun nume, niciun instrument, nicio procedură
#: nepomenite), „sistematic” numai de la PRAG_SISTEMATIC cazuri, text simplu fără linii-separator.
SISTEM_ANALIZA = ("Ești asistentul unui cabinet de contabilitate din România. Analizezi motivele pentru care colegii au respins la validare "
                  "declarații și note contabile și propui recomandări concrete pentru a le reduce. Reguli stricte: folosești NUMAI datele "
                  "primite — nu numești firme, persoane, sesiuni, programe (Excel etc.) sau proceduri care nu apar în ele și nu inventezi "
                  "cifre; un motiv îl numești „repetat” sau „sistematic” numai dacă are cel puțin %s, altfel spui că e un caz "
                  "izolat; dacă datele nu ajung pentru o concluzie, spui asta. Scrii în limba română, cu diacritice, concis: întâi ce "
                  "observi (2–3 fraze), apoi cel mult 5 recomandări, fiecare pe un rând care începe cu „- ”. Text simplu: fără titluri, "
                  "fără linii de separare („---”), fără formule de politețe." % _cate(PRAG_SISTEMATIC, "caz", "cazuri"))


def eticheta_tip(tip):
    """PURĂ. Cum se numește pe ecran și în analiză felul pregătirii: notele contabile, sau codul declarației (D300)."""
    return "Note contabile" if (tip or "") == "nota" else (tip or "").upper()


def curata_analiza(text):
    """PURĂ. [576] Liniile-separator (`---`, `***`, `___`) ies din textul arătat; restul rămâne cum l-a scris modelul."""
    import re
    return "\n".join(l for l in (text or "").splitlines() if not re.fullmatch(r"\s*[-*_=]{3,}\s*", l)).strip()

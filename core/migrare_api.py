"""
core/migrare_api.py — starea migrării unui cabinet, pe straturi.

Fiecare strat de migrare (firme, solduri, salariați, asociați, mijloace fixe)
are o stare per cabinet: 'gata' sau 'in_lucru'. La 'in_lucru' contabilul scrie
o notă (de ce nu e gata) — apare ca reminder pe cardul Firme.

Tabelul se auto-creează (CREATE TABLE IF NOT EXISTS) la pornire.
"""
from __future__ import annotations

# straturile de migrare, în ordinea logică (firme întâi — creează tenant-urile)
# 'regim' = pentru ce tip de firma se aplica stratul:
#   'ambele' -> SRL si PFA; 'dubla' -> doar SRL (partida dubla); 'simpla' -> doar PFA (RIP).
# [deficiențele 368 + 371, comanda Costin 8.2, 18.10.2026] SURSA UNICĂ a straturilor, pentru Migrare cabinet ȘI meniul per firmă: „la PFA se
# ascund Solduri, Solduri parteneri, Asociați, Plan de conturi; Mijloace fixe rămâne vizibil și la PFA” (registrul de amortizare există și
# în partida simplă); Migrare cabinet arată toate straturile — inclusiv Import RIP, Articole și stoc inițial, Rețete.
STRATURI_META = [
    ("firme",              "ambele"),
    ("vector_fiscal",      "ambele"),
    ("solduri",            "dubla"),
    ("solduri_parteneri",  "dubla"),
    ("salariati",          "ambele"),
    ("asociati",           "dubla"),
    ("mijloace_fixe",      "ambele"),
    ("istoric_declaratii", "ambele"),
    ("plan_conturi",       "dubla"),
    ("rip",                "simpla"),
    ("articole",           "ambele"),
    ("retete",             "ambele"),
]  # [p82_vector] [p95_plan_conturi] [p_pfa_rip 20.07]
STRATURI = [s for s, _ in STRATURI_META]


def tip_firma_nrm(tip_firma):
    """tip_firma normalizat (lower+trim), default 'srl' la lipsă/None — UNICUL loc cu default-ul de creare
    (srl = partidă dublă implicit). Nu validează în {srl,pfa} (CHECK-ul DB o face); doar normalizează.
    Consumatorii (auth_api, tenant_provisioning, regim_contabil) îl folosesc — NU redau `or "srl"` inline.
    Vezi DESIGN_SYSTEM cap. DEFAULT_FISCAL_TACIT + DECIZII 23.07."""
    return (tip_firma or "srl").strip().lower()


def regim_contabil(tip_firma):
    """'dubla' | 'simpla' din tip_firma — UN SINGUR loc unde scrie faptul (srl=partidă dublă, pfa=partidă
    simplă). straturi_pentru() + regim_efectiv() îl folosesc; regula NU se recopiază. Vezi DECIZII 23.07."""
    return "simpla" if tip_firma_nrm(tip_firma) == "pfa" else "dubla"


def straturi_pentru(tip_firma):
    """Straturile aplicabile unui tip de firma ('srl' | 'pfa')."""
    vrut = regim_contabil(tip_firma)   # 'dubla' | 'simpla' — fapt UNIC (regim_contabil), nu recopiat
    return [s for s, regim in STRATURI_META if regim in ("ambele", vrut)]


def regim_efectiv(profil: dict) -> str | None:
    """Regimul CIT EFECTIV al firmei: 'micro' | 'profit' | None. Partidă simplă (pfa) => None NECONDIȚIONAT
    (profesie liberală/PFA: impozit pe venit prin D212, nu regim CIT), oricât ar scrie regim_fiscal. Contract
    STRICT: profil TREBUIE să aibă 'tip_firma' + 'regim_fiscal' (KeyError altfel — fără .get, fără fallback;
    callerul dă profil complet). Vezi DECIZII 23.07."""
    if regim_contabil(profil["tip_firma"]) == "simpla":
        return None
    rf = profil["regim_fiscal"]
    return rf.strip().lower() if rf else None
STARI = ("gata", "in_lucru")


def asigura_tabel(conn, comite=True):
    """Creează tabelul de status dacă nu există. Idempotent.

    `comite=False` cerut de calea de PORNIRE (`main.lifespan`), si numai de ea. Motivul, masurat pe
    productie pe 12.09.2026: acolo apelul asta sta imediat dupa `pg_advisory_xact_lock`, iar un
    `commit` incheie tranzactia — deci ELIBEREAZA blocajul de pornire inainte ca el sa fi aparat
    ceva. Sectiunea critica rula neserializata, si la fiecare repornire cu doi workeri unul murea
    cu `tuple concurrently updated`.

    Implicitul ramane `True`, deci ceilalti apelanti (rutele de migrare, care isi deschid propria
    conexiune si se asteapta ca tabelul sa existe dupa apel) nu se schimba cu nimic."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS public.migrare_status (
                id SERIAL PRIMARY KEY,
                accounting_firm_id INTEGER NOT NULL,
                strat TEXT NOT NULL,
                stare TEXT NOT NULL DEFAULT 'in_lucru',
                nota TEXT NOT NULL DEFAULT '',
                actualizat_la TIMESTAMPTZ NOT NULL DEFAULT now(),
                UNIQUE (accounting_firm_id, strat)
            )
        """)
    if comite:
        conn.commit()


def citeste_status(conn, firm_id):
    """
    Întoarce starea fiecărui strat pentru cabinet:
    {strat: {"stare": ..., "nota": ...}}. Straturile neîncepute lipsesc din dict.
    """
    with conn.cursor() as cur:
        cur.execute(
            "SELECT strat, stare, nota FROM public.migrare_status "
            "WHERE accounting_firm_id = %s",
            (firm_id,),
        )
        randuri = cur.fetchall()
    out = {}
    for strat, stare, nota in randuri:
        out[strat] = {"stare": stare, "nota": nota or ""}
    return out


def seteaza_status(conn, firm_id, strat, stare, nota=""):
    """Upsert starea unui strat. La 'in_lucru' nota e obligatorie."""
    if strat not in STRATURI:
        raise ValueError(f"strat necunoscut: {strat}")
    if stare not in STARI:
        raise ValueError(f"stare necunoscută: {stare}")
    if stare == "in_lucru" and not (nota or "").strip():
        raise ValueError("nota e obligatorie când importul nu e gata")

    with conn.cursor() as cur:
        # upsert-ok: set stare strat import pe (firma,strat) - actualizare intentionata a statusului
        cur.execute(
            "INSERT INTO public.migrare_status "
            "  (accounting_firm_id, strat, stare, nota, actualizat_la) "
            "VALUES (%s, %s, %s, %s, now()) "
            "ON CONFLICT (accounting_firm_id, strat) DO UPDATE SET "
            "  stare = EXCLUDED.stare, nota = EXCLUDED.nota, actualizat_la = now()",
            (firm_id, strat, stare, (nota or "").strip()),
        )
    conn.commit()
    return {"strat": strat, "stare": stare, "nota": (nota or "").strip()}


def reminder(conn, firm_id, tip_firma="srl"):
    """
    Pentru cardul Firme: straturile care NU sunt 'gata' și au fost declarate
    'in_lucru' (cu notă). Întoarce listă [{strat, nota}].
    Filtrat pe tip_firma: PFA nu vede straturi de partida dubla, SRL nu vede rip.
    """
    status = citeste_status(conn, firm_id)
    out = []
    for strat in straturi_pentru(tip_firma):
        s = status.get(strat)
        if s and s["stare"] == "in_lucru":
            out.append({"strat": strat, "nota": s["nota"]})
    return out


def erori_verifica(rez):
    """Normalizeaza rezultatul verifica_randuri (lista SAU tuplu (erori, bune)) la lista de erori
    [{rand, motiv, mesaj}]. POARTA UNICA preview<->salvare (DS cap.24): previzualizarea intoarce
    ACEEASI verdict ca verifica_randuri - poarta pe care importa() o aplica la scriere - nu o a doua
    validare din extrage (flaguri cnp_valid/ok) care drifteaza (un camp verificat intr-un capat si nu
    in celalalt). Frontendul consuma `erori` si blocheaza Salvarea pe randurile respinse (cap.6)."""
    if isinstance(rez, tuple):
        return rez[0] or []
    return rez or []


# ─────────────────────────────────────────────────────────────────────────────
# [P8/C, 21.08.2026] RESPINGERILE DE RAND LA IMPORT SUNT AFIRMATII, cu regula NUMITA.
#
# Pana azi fiecare modul isi inventa codurile. Masurat: 46 de respingeri in 12 module, din care 27
# purtau deja un cod masinal si 9 doar proza. ZERO coliziuni intre module (verificat, nu presupus),
# deci nomenclatorul se poate INCHIDE fara sa cimenteze o ambiguitate.
#
# DE CE conteaza, cu instanta: `migrare.js` numara duplicatele cu
# `erori.filter(e => (e.mesaj || "").includes("există deja"))` - o clasificare prin potrivire de
# PROZA. Cine reformuleaza mesajul strica tacut numaratoarea, iar ecranul spune „0 firme erau deja in
# portofoliu" despre un import in care erau. Un cod inchis nu se schimba cand se rescrie textul.
#
# `fel` de aici NU e felul afirmatiei (ala e mereu `neconformitate`), ci FORMA respingerii - ce s-a
# intamplat cu valoarea. Randorul poate grupa dupa el fara sa citeasca textul.
REGULI = {
    # --- lipsa: campul nu are valoare, iar fara ea nu se poate merge mai departe
    "cod_lipsa":        {"fel": "lipsa", "inseamna": "mijloc fix fara cod de inventar"},
    "durata_lipsa":     {"fel": "lipsa", "inseamna": "durata de amortizare lipseste sau nu e pozitiva"},
    "norma_lipsa":      {"fel": "lipsa", "inseamna": "norma de lucru (intreaga/partiala) lipseste - ceruta de D112"},
    "salariu_lipsa":    {"fel": "lipsa", "inseamna": "salariul de baza lipseste sau nu e mai mare ca 0"},
    # [decizia Costin 07.10, pct.4] faptele cerute explicit și la import (aceeași regulă ca pe ecran); [PIVOT 14.10 pct.4] scutirea de
    # contribuția minimă lipsă NU mai refuză rândul — se importă „nescutit” și se marchează de verificat (`salariati.de_verificat`)
    "functie_baza_lipsa": {"fel": "lipsa", "inseamna": "funcția de bază la acest angajator (Da/Nu) lipsește - decide deducerea personală"},
    "ore_lipsa":        {"fel": "lipsa", "inseamna": "orele pe zi ale normei parțiale lipsesc - baza D112 la normă parțială"},
    # [14.10.2026, importul din SAGA] „Norma pe zi” = 0 la SAGA = contract cu ore pe lună, fără normă zilnică
    "norma_ore_luna":   {"fel": "lipsa", "inseamna": "norma pe zi e 0 (ore pe luna): orele pe zi ale normei nu sunt in fisier"},
    "valoare_lipsa":    {"fel": "lipsa", "inseamna": "valoarea de intrare lipseste sau nu e pozitiva"},
    "data_lipsa":       {"fel": "lipsa", "inseamna": "data operatiunii lipseste"},
    "explicatie_lipsa": {"fel": "lipsa", "inseamna": "explicatia operatiunii lipseste (coloana e NOT NULL)"},
    # scos pe 21.08 fiindca era declarat si nefolosit; repus pe 22.08 cand importul de retete a
    # capatat un producator real. Nomenclatorul urmeaza codul, nu invers.
    "denumire_lipsa":   {"fel": "lipsa", "inseamna": "denumirea lipseste dintr-un rand importat"},

    # --- invalid: valoarea E acolo, dar nu satisface regula
    "cnp_invalid":      {"fel": "invalid", "inseamna": "CNP care nu trece cifra de control"},
    "cui_invalid":      {"fel": "invalid", "inseamna": "CUI care nu trece cifra de control"},
    "iban_invalid":     {"fel": "invalid", "inseamna": "IBAN care nu trece mod-97 (ISO 13616)"},
    "judet_invalid":    {"fel": "invalid", "inseamna": "judet inexistent in nomenclatorul oficial"},
    "ore_invalide":     {"fel": "invalid", "inseamna": "ore/zi peste norma legala"},
    "an_invalid":       {"fel": "invalid", "inseamna": "anul e in afara intervalului acceptat"},
    "luna_invalida":    {"fel": "invalid", "inseamna": "luna nu e intre 1 si 12, sau nu e numar"},
    "data_invalida":    {"fel": "invalid", "inseamna": "data nu se poate interpreta"},
    "data_viitor":      {"fel": "invalid", "inseamna": "data e in viitor, unde nu poate fi"},
    "tip_necunoscut":   {"fel": "invalid", "inseamna": "tipul nu exista in nomenclatorul asteptat"},
    "suma_invalida":    {"fel": "invalid", "inseamna": "suma e 0 sau neinterpretabila"},
    # [C24, 14.10.2026] motorul de amortizare refuza randul (ex. metoda accelerata pe un cont neclasificat)
    "amortizare_necalculabila": {"fel": "invalid", "inseamna": "amortizarea nu se poate calcula din datele randului"},
    "cantitate_pret_negativ": {"fel": "invalid",
                               "inseamna": "cantitate sau pret negativ la un articol de stoc"},
    "pret_zero_cu_stoc": {"fel": "invalid",
                          "inseamna": "articol cu stoc dar pret unitar 0 - valoarea stocului ar fi 0"},
    "balanta_nu_se_echilibreaza": {"fel": "incoerent",
                                   "inseamna": "totalul debitor difera de cel creditor in fisierul incarcat"},
    "cont_nepartener":  {"fel": "invalid", "inseamna": "contul nu tine solduri pe parteneri"},

    # --- duplicat: valoarea intra in conflict cu una care exista deja
    "cod_duplicat":     {"fel": "duplicat", "inseamna": "acelasi cod de inventar apare de doua ori in fisier"},
    "deja_exista":      {"fel": "duplicat", "inseamna": "inregistrarea exista deja si nu se dubleaza"},

    # --- esec: nu datele sunt de vina, ci operatiunea s-a rupt. Sta in ACEEASI lista pe care o vede
    # contabilul, deci trebuie sa se poata DEOSEBI de o respingere de date - altfel „N firme nu au
    # putut fi adaugate" amesteca „CUI invalid" cu „baza de date a picat", si omul cauta in locul gresit.
    "creare_esuata":    {"fel": "esec", "inseamna": "crearea inregistrarii s-a oprit cu o eroare tehnica"},
    # [10.10.2026, deficiența C7] comanda din magazin pe care emiterea o refuză (cota sau contul nedeterminat, o linie incompletă)
    "emitere_refuzata": {"fel": "invalid", "inseamna": "factura comenzii nu s-a emis: emiterea a refuzat-o, cu motivul ei"},

    # --- incoerent: doua valori ale aceluiasi rand (sau set) nu pot fi amandoua adevarate
    "rezidual_peste_intrare": {"fel": "incoerent",
                               "inseamna": "valoarea ramasa depaseste valoarea de intrare"},
    "cote_nu_dau_suta":       {"fel": "incoerent",
                               "inseamna": "cotele asociatilor nu insumeaza 100%"},
    "data_inainte_de_perioada": {"fel": "incoerent",
                                 "inseamna": "depunerea e datata inaintea sfarsitului perioadei raportate"},
    # [361 / 362, comanda Costin 8.2] mijloace fixe: metoda din afara CF art.28; conturi care nu sunt de imobilizări / nu-i corespund
    "metoda_necunoscuta": {"fel": "invalid", "inseamna": "metoda de amortizare nu e una din cele ale CF art.28"},
    "cont_imobilizare_invalid": {"fel": "invalid", "inseamna": "contul mijlocului fix nu e de imobilizari (clasa 2)"},
    "cont_amortizare_necorespunzator": {"fel": "incoerent", "inseamna": "contul de amortizare nu corespunde contului de imobilizare"},
    "amortizare_peste_valoare": {"fel": "incoerent", "inseamna": "amortizarea preluata depaseste valoarea amortizabila"},
    # [346] soldurile pe parteneri ale unui cont nu dau soldul contului la data preluarii (balanta de deschidere / contabilitate)
    "parteneri_nu_dau_soldul": {"fel": "incoerent", "inseamna": "partenerii unui cont nu dau soldul contului la data preluarii"},
    # [353, comanda Costin 8.2] același rând (aceeași declarație pe aceeași perioadă) de două ori în fișier: intră o singură dată
    # [364–367, comanda Costin 8.2] asociații: fără identificator, același CNP/CUI de două ori, cotă în afara 0–100, CUI confruntat cu ANAF
    "identificator_lipsa": {"fel": "lipsa", "inseamna": "asociatul n-are CNP/CUI: nu poate aparea in D205"},
    "identificator_dublat": {"fel": "duplicat", "inseamna": "acelasi CNP/CUI pe doua randuri; un asociat / salariat se trece o data"},
    # [385, lotul 9] articolul de pe două rânduri intra de două ori, fără observație (celelalte importuri resping dublurile)
    # [362, lotul 9] terenul cu durată de amortizare; amenajarea de teren cu altă durată decât cea din lege (10 ani)
    "durata_teren":     {"fel": "incoerent", "inseamna": "terenul nu se amortizeaza, dar fisierul ii da o durata"},
    "durata_amenajare_teren": {"fel": "incoerent", "inseamna": "amenajarile de terenuri se amortizeaza liniar pe 10 ani (CF art.28 alin.(12) lit.e))"},
    "articol_dublat":   {"fel": "duplicat", "inseamna": "aceeasi denumire de articol pe doua randuri; un articol se trece o data, cu stocul lui total"},
    "cota_invalida":    {"fel": "invalid", "inseamna": "cota de participare nu e intre 0 si 100"},
    # [373, comanda Costin 8.2] articole / stoc inițial: nimic completat din oficiu
    "um_lipsa":         {"fel": "lipsa", "inseamna": "articolul n-are unitatea de masura; nu se presupune buc"},
    "cantitate_invalida": {"fel": "invalid", "inseamna": "cantitatea nu e un numar"},
    "pret_invalid":     {"fel": "invalid", "inseamna": "pretul nu e un numar"},
    "cont_stoc_lipsa":  {"fel": "lipsa", "inseamna": "articolul n-are contul de stoc"},
    "cont_stoc_invalid": {"fel": "invalid", "inseamna": "contul de stoc nu e din clasa 3"},
    "cont_cheltuiala_lipsa": {"fel": "lipsa", "inseamna": "contul de cheltuiala lipseste si nu se deduce din contul de stoc"},
    # [375, comanda Costin 8.2] rețete: nimic ales sau completat în tăcere
    "ingredient_lipsa": {"fel": "lipsa", "inseamna": "randul de reteta n-are ingredientul"},
    "ingredient_negasit": {"fel": "invalid", "inseamna": "ingredientul nu e in articolele din stoc"},
    "pret_lipsa":       {"fel": "lipsa", "inseamna": "reteta n-are pret de vanzare (sau e 0)"},
    "pret_contradictoriu": {"fel": "incoerent", "inseamna": "aceeasi reteta are preturi diferite in fisier"},
    "reteta_incompleta": {"fel": "incoerent", "inseamna": "alt rand al aceleiasi retete e respins; reteta intra intreaga sau deloc"},
    "metoda_plata_necunoscuta": {"fel": "invalid", "inseamna": "metoda operatiunii RIP nu e banca sau numerar"},
    "cui_negasit_anaf": {"fel": "invalid", "inseamna": "CUI-ul nu e gasit la ANAF"},
    "nume_diferit_anaf": {"fel": "incoerent", "inseamna": "numele din fisier difera de cel de la ANAF pentru acelasi CUI"},
    "rand_dublat":      {"fel": "duplicat", "inseamna": "acelasi rand apare de doua ori in fisier; intra o singura data"},

    # --- semnal: rândul INTRĂ, dar are ceva de știut (comanda Costin 8.2 pct.4: „orice rând citit e afișat sau semnalat cu motiv”).
    # Nu oprește salvarea și nu e numărat cu respingerile — `semnaleaza`, nu `respinge`.
    "data_depunere_lipsa": {"fel": "semnal", "inseamna": "rândul n-are data depunerii: se importă, dar termenul nu se poate confrunta"},
    "an_vechi":         {"fel": "semnal", "inseamna": "anul e mai vechi decât anul curent și precedentul, pe care le urmărește aplicația"},
    "suma_lipsa_d100":  {"fel": "semnal", "inseamna": "D100 fără suma declarată: D100 pe profit de mai târziu n-o poate scădea"},
    "cont_cheltuiala_dedus": {"fel": "semnal", "inseamna": "contul de cheltuiala e dedus din contul de stoc (lipsea din fisier)"},
    "ingredient_aproximativ": {"fel": "semnal", "inseamna": "ingredientul e potrivit pe un articol cu denumire neidentica"},
    "metoda_plata_lipsa": {"fel": "semnal", "inseamna": "operatiunea RIP n-are metoda: intra prin banca, spus pe rand"},
    "categorie_lipsa":  {"fel": "semnal", "inseamna": "operatiunea RIP n-are categorie: intra neclasificat, spus pe rand"},
    "suma_negativa_rip": {"fel": "semnal", "inseamna": "suma RIP negativa: intra cu valoarea absoluta, sensul il da tipul"},
    "anaf_neverificat": {"fel": "semnal", "inseamna": "serviciul ANAF n-a raspuns: CUI-ul si numele nu s-au putut confrunta"},
    "cor_lipsa":        {"fel": "semnal", "inseamna": "salariatul n-are cod COR în fișier: intră fără cod, se alege în fișa lui"},
    "persoane_lipsa":   {"fel": "semnal", "inseamna": "persoanele în întreținere lipsesc: intră cu 0, salariatul e marcat de verificat"},
    "scutire_lipsa":    {"fel": "semnal", "inseamna": "scutirea de contribuția minimă lipsește: intră nescutit, marcat de verificat"},
    # [lotul 10, deficiența 420] norma și funcția de bază lipsă din fișier: propuse pe ecran (editabile), intră marcate de verificat
    "norma_propusa":    {"fel": "semnal", "inseamna": "norma lipsește din fișier: propusă (întreagă, 8 ore), editabilă, marcată de verificat"},
    "functie_baza_propusa": {"fel": "semnal", "inseamna": "funcția de bază lipsește din fișier: propusă „Da”, editabilă, marcată de verificat"},
}

#: [comanda Costin 8.2 pct.4] formele care NU opresc rândul — `semnaleaza` le cere, `respinge` le refuză
FORME_SEMNAL = ("semnal",)


def semnaleaza(tip, unde, regula, mesaj, **campuri):
    """Un SEMNAL de rând (comanda Costin 8.2 pct.4): rândul intră, dar ceva despre el trebuie spus. Aceeași formă ca `respinge` (afirmație cu
    regula numită și `rand`), cu `forma` „semnal”; un cod care nu e semnal se refuză, ca o respingere să nu treacă drept observație."""
    if REGULI.get(regula, {}).get("fel") not in FORME_SEMNAL:
        raise RuntimeError("regula %r nu e un semnal; respingerile trec prin `respinge`" % (regula,))   # greșeală de programare, nu a fișierului
    return _respingere_sau_semnal(tip, unde, regula, mesaj, **campuri)


def respinge(tip, unde, regula, mesaj, **campuri):
    """O respingere de rând (rândul NU intră). Pentru observațiile care lasă rândul să intre: `semnaleaza`."""
    if REGULI.get(regula, {}).get("fel") in FORME_SEMNAL:
        raise RuntimeError("regula %r e un semnal: rândul intră, deci trece prin `semnaleaza`, nu prin `respinge`" % (regula,))   # programare
    return _respingere_sau_semnal(tip, unde, regula, mesaj, **campuri)


def _respingere_sau_semnal(tip, unde, regula, mesaj, **campuri):
    """O respingere de rand, ca AFIRMATIE. Constructorul UNIC - un cod care nu e in REGULI nu poate
    fi produs, deci o greseala de tastare nu mai trece tacut ca o categorie noua.

    CIOCNIRE DE VOCABULAR, rezolvata explicit (21.08.2026): pana azi cheia "motiv" purta CODUL in
    importuri si TEXTUL in afirmatii - acelasi nume, doua intelesuri, exact capcana pe care o vaneaza
    campania. De-acum "motiv" e TEXTUL peste tot; codul traieste in "regula". Consumatorii au fost
    NUMARATI inainte, nu presupusi: trei fisiere de test si fallback-ul din migrare.js. Modulul
    tipare_api grupeaza respingerile ANAF din baza - alt camp cu acelasi nume, care nu se atinge.

    Cheia "mesaj" ramane, cu ACEEASI valoare ca "motiv", fiindca frontendul o randeaza; testul
    asertaza ca nu pot diverge. Cheia "rand" e domeniul concret, pe langa "unde" care il scrie in
    limba omului."""
    from core import afirmatii as _af
    if regula not in REGULI:
        raise ValueError(  # invariant-intern-ok: nomenclatorul de reguli e cod
            "regula %r nu e în nomenclator; cele declarate: %s. Un cod nou se ADAUGĂ în REGULI, cu "
            "ce înseamnă - altfel randorul primește o categorie despre care nu știe nimic."
            % (regula, ", ".join(sorted(REGULI))))
    if unde is None or str(unde).strip() == "":
        raise ValueError("respingerea cere domeniul: fără el, contabilul nu știe ce să corecteze")
    if not (mesaj or "").strip():
        raise ValueError("respingerea cere un text pentru om, nu doar codul %r" % regula)
    # DOMENIUL nu e mereu un rand. Prima forma cerea `rand`, si era peste-croita pe importurile din
    # fisier: `articole_import` si `retete_import` identifica prin DENUMIRE, iar coerenta cotelor e
    # despre SETUL de asociati. A doua constructor pentru „acelasi lucru, alt domeniu" ar fi fost
    # exact logica paralela pe care o evitam. Aici: numarul devine „randul N", restul se scrie ca atare.
    e_rand = isinstance(unde, int) or (isinstance(unde, str) and unde.strip().isdigit())
    a = _af.afirmatie("neconformitate", tip, mesaj,
                      unde=("rândul %s" % unde) if e_rand else str(unde), regula=regula)
    if e_rand:
        a["rand"] = int(unde)      # cheia pe care o citeste poarta unica preview<->salvare
    a["mesaj"] = mesaj
    a["forma"] = REGULI[regula]["fel"]   # lipsa | invalid | duplicat | incoerent - pt grupare la randare
    a.update(campuri)
    return a


# ---------------------------------------------------------------------------------------------------------------------------------
# [lotul 10, deficiența 426 — CLASA] ÎNLOCUIREA CONFIRMATĂ, comună importurilor de migrare care înlocuiesc ce exista.
# Comanda Costin 10.1 (verbatim în DECIZII „Comanda 10.1”): „al doilea import de balanță pentru aceeași firmă o înlocuiește pe prima
# fără avertisment. Înainte de înlocuire: spune că există deja o balanță, arată totalurile vechi și noi, cere confirmare; dacă există
# note pe lunile de după preluare, spune că soldurile lor se recalculează.” Clasa: ORICE import de migrare care șterge / suprascrie ce
# exista (balanța, soldurile pe parteneri, registrul mijloacelor fixe, istoricul declarațiilor, fișele salariaților). Fiecare modul își
# spune ce există și ce aduce fișierul (textul, cu cifrele lui); poarta e una singură, aici. Gard: core/test_lot10_inlocuire_clasa.py
# (orice `importa` dintr-un modul de import care șterge (`DELETE FROM`) sau suprascrie printr-un upsert trece pe aici, cu `inlocuieste`).
# ---------------------------------------------------------------------------------------------------------------------------------

#: fraza de încheiere a refuzului, aceeași peste toate importurile (ecranul deschide confirmarea pe 409)
CERE_CONFIRMAREA = "Confirmă înlocuirea și salvează din nou."


class InlocuireNeconfirmata(ValueError):
    """Importul ar înlocui date existente ale firmei, iar cererea n-a confirmat înlocuirea. `vechi` / `nou` = ce există și ce aduce
    fișierul; `dependente` = ce se sprijină pe datele înlocuite. Use-case-ul o traduce în `erori.Conflict` (409), cu textul ei."""

    def __init__(self, mesaj, vechi=None, nou=None, dependente=None):
        super().__init__(mesaj)
        self.vechi, self.nou, self.dependente = vechi, nou, dependente


def cere_confirmarea_inlocuirii(exista, inlocuieste, text, vechi=None, nou=None, dependente=None, exceptie=InlocuireNeconfirmata):
    """Poarta unică a înlocuirii: când firma are deja datele pe care importul le înlocuiește (`exista`) și cererea n-a confirmat
    (`inlocuieste` fals) -> `exceptie` (o `InlocuireNeconfirmata`) cu `text` + `CERE_CONFIRMAREA`. Se cheamă ÎNAINTE de orice scriere."""
    if exista and not inlocuieste:
        raise exceptie("%s %s" % (str(text).rstrip(), CERE_CONFIRMAREA), vechi, nou, dependente)


def randuri_care_intra(randuri, erori):
    """[426] Rândurile previzualizate care intră la salvare (fără cele respinse în `erori`, pe numărul rândului din fișier — aceeași
    regulă ca `importa`: `import_tabel.nr_rand`). Din ele se spune, înainte de salvare, ce aduce fișierul nou."""
    from core import import_tabel as _it
    resp = {e.get("rand") for e in erori or [] if e.get("rand") is not None}
    return [r for i, r in enumerate(randuri or [], start=2) if _it.nr_rand(r, i) not in resp]

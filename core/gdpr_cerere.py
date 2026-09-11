"""GDPR art.17 — cererea de stergere DEPUSA de cabinet (NU executa nimic).

Cabinetul CERE din aplicatie; superadminul executa manual (core.gdpr_sterge,
care face DROP SCHEMA — ireversibil). Aici doar:
  1) valideaza typed-back (retastarea denumirii cabinetului),
  2) jurnalizeaza cererea in public.gdpr_cereri_stergere (dovada ca a fost
     primita si cand),
  3) anunta echipa pe canalul comun (core.observare -> Brevo -> contact@iconta.eu).

Reutilizeaza observare._trimite_brevo (F164/F202) — NU construi canal paralel.
"""
from core import observare


def _nume_cabinet(conn, cabinet_id):
    with conn.cursor() as cur:
        cur.execute("SELECT nume FROM public.accounting_firms WHERE id=%s", (cabinet_id,))
        r = cur.fetchone()
    return r[0] if r else None


#: Subiectul anuntului. Constanta, nu literal repetat: o proba care asserteaza pe el nu
#: trebuie sa-l poarte a doua oara — un literal repetat e a doua definitie a aceleiasi
#: propozitii, si prima care ramane in urma.
SUBIECT_ANUNT = "Cerere de stergere cont (GDPR art.17)"


def corp_anunt(cabinet_id, nume, cerere_id, user_id, cerut_la, motiv=None):
    """Corpul e-mailului catre echipa. PURA — se compara pe EGALITATE, nu cautand subsiruri.

    Scoasa din `depune_cerere` pe 11.09.2026: cat timp continutul se construia in mijlocul
    functiei care si scria in baza, singurul fel de a-l verifica era un `in` pe text — adica
    exact ce interzice clichetul 50. Cu nume, proba compara valoarea intreaga, iar o
    reformulare de maine cade acolo unde trebuie, nu tacut."""
    return ("Cabinet #%s \"%s\" a depus o cerere de stergere.\n"
            "Cerere #%s, user #%s, la %s.\n"
            "Motiv: %s\n\n"
            "Executie MANUALA (superadmin, dupa verificare):\n"
            "  POST /gdpr/sterge-cabinet/%s/executa"
            % (cabinet_id, nume, cerere_id, user_id, cerut_la, motiv or "(nespecificat)", cabinet_id))


def depune_cerere(conn, cabinet_id, user_id, confirmare_nume, motiv=None):
    """Inregistreaza o cerere de stergere, si NU trimite niciun e-mail.

    Ridica ValueError daca typed-back-ul nu se potriveste. Intoarce
    `{ok, cerere_id, termen_zile_lucratoare, anunt}`, unde `anunt` e TUPLUL `(subiect, corp)` pe
    care apelantul il da lui `anunta_echipa` DUPA commit — vezi nota de mai jos."""
    nume = _nume_cabinet(conn, cabinet_id)
    if not nume:
        raise ValueError("cabinet inexistent")
    if (confirmare_nume or "").strip() != (nume or "").strip():
        raise ValueError("Denumirea retastata nu se potriveste cu numele cabinetului.")
    motiv = (motiv or "").strip() or None
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO public.gdpr_cereri_stergere "
            "(cabinet_id, cerut_de_user_id, nume_cabinet, motiv) "
            "VALUES (%s,%s,%s,%s) RETURNING id, cerut_la",
            (cabinet_id, user_id, nume, motiv))
        cid, cerut_la = cur.fetchone()
    # [P5 val 3, 10.09.2026] E-MAILUL NU MAI PLEACA DE AICI. Comentariul de dinainte spunea
    # „esecul emailului NU anuleaza cererea (deja jurnalizata)" — dar cererea NU era jurnalizata
    # inca: `INSERT`-ul era necomis, iar ruta comitea abia dupa ce functia asta se intorcea. Deci
    # un esec de dupa email intorcea cererea, si ramanea un e-mail despre o cerere care nu exista.
    # Plus conexiunea din pool, tinuta 10 s peste apelul la Brevo.
    #
    # Acum se intoarce CE trebuie anuntat; ruta comite, iese din bloc, si abia atunci cheama
    # `anunta_echipa`. Efectul ireversibil vine ULTIMUL, dupa ce tranzactia a reusit sigur.
    # TUPLU, nu dictionar: un dict cu chei ca `motiv` e citit de gardul afirmatiilor tipate
    # ca o afirmatie despre datele firmei. Nu e — e continutul unui e-mail, deci nu-i dau
    # forma aia. (A doua oara cand cheia `motiv` aprinde un gard; prima, in registrul P4.)
    anunt = (SUBIECT_ANUNT,
             corp_anunt(cabinet_id, nume, cid, user_id, cerut_la, motiv))
    return {"ok": True, "cerere_id": cid, "termen_zile_lucratoare": 5, "anunt": anunt}


def anunta_echipa(anunt):
    """Trimite e-mailul despre o cerere de stergere DEJA COMISA. Intoarce True/False.

    Se cheama DUPA `conn.commit()` si DUPA iesirea din blocul de conexiune. Un esec de trimitere nu
    mai poate intoarce nimic — cererea e deja in evidenta —, dar nu se inghite tacut: se consemneaza
    prin `esec_secundar`, care alerteaza in fundal.
    """
    if not anunt:
        return False
    subiect, corp = anunt
    try:
        return observare._trimite_brevo(subiect, corp)
    except Exception as e:      # noqa: BLE001 — nu opreste cererea, dar NU dispare
        observare.esec_secundar("email cerere stergere GDPR", e, alerta=True)
        return False

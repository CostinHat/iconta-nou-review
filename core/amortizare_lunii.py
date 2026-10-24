# -*- coding: utf-8 -*-
"""core/amortizare_lunii.py — rândurile notei de amortizare a unei luni, din registrul mijloacelor fixe de ACUM (lotul 11, deficiența 451).

Comanda Costin 11.1 pct.6, verbatim: „ciornele generate înainte de o reparație rămân validabile cu regula veche. [...] Toate trebuie
refăcute din sursă sau marcate depășite și oprite de la validare, pe toate firmele.” Ciorna de amortizare se compară la validare cu ce ar
scrie ACUM „Generează amortizarea” (`ciorne_depasite`); ca cele două să nu poată spune lucruri diferite, rândurile se calculează într-un
singur loc — aici —, iar `uc_tenants.tenant_amortizare` îl cheamă (patch-ul cerut în raportul lotului 11, S: corpul buclei lui de acum
e chiar funcția de mai jos, mutată).

Calculul: metoda reală a fiecărui mijloc fix (CF art.28, `d406_active.amortizare_luna`), pe mijloacele fixe active, cu PIF și durată;
contul de amortizare al mijlocului (implicit 2813), cheltuiala pe 6811.
"""
#: contul de cheltuială al notei de amortizare (`repo_contabilitate.adauga_linie_cheltuiala_amortizare`)
CONT_CHELTUIALA = "6811"


#: [C129, lotul 12] unde se completează contul lipsă al unei fișe (registrul nu are editare de conturi; importul îl înlocuiește)
UNDE_SE_COMPLETEAZA = "Migrare → Mijloace fixe (reîncarcă registrul cu contul pe rândul lui)"


def conturile_fisei(denumire, cont_imobilizare, cont_amortizare, cu_amortizare=True, cu_imobilizare=True):
    """(cont_imobilizare, cont_amortizare) ale fișei din registru, curățate, sau ValueError cu motivul pentru contabil.

    [C129, lotul 12] Importul registrului păstrează golul („neclasificat”, `mijloace_fixe_import_api`), deci o fișă poate avea contul de
    imobilizare (sau de amortizare) gol. Reevaluarea, casarea și amortizarea lunii scriau atunci nota cu un cont gol (reevaluarea: „ = 105”,
    contul activului reevaluat lipsă) sau cu 2813 pus tăcut. Orice notă scrisă din fișă ia conturile de aici: fără cont, nu se scrie nota.
    `cu_amortizare=False`: nota nu atinge contul de amortizare (nimic amortizat); `cu_imobilizare=False`: nota nu atinge contul activului
    (amortizarea lunii, 6811 = 28xx) — fiecare cont se cere numai unde nota îl scrie."""
    ci, ca = str(cont_imobilizare or "").strip(), str(cont_amortizare or "").strip()
    lipsa = ([] if ci or not cu_imobilizare else ["contul de imobilizare"]) + ([] if ca or not cu_amortizare else ["contul de amortizare"])
    if lipsa:   # refuz de FORMĂ, fără temei normativ: un rând de notă fără cont nu e o înregistrare
        raise ValueError("Mijlocul fix %s nu are %s în registru, deci nota n-ar avea contul. Completează ce lipsește din %s, "
                         "apoi reia operația." % (denumire, " și ".join(lipsa), UNDE_SE_COMPLETEAZA))
    return ci, ca


def numar(an, luna):
    """Numărul notei de amortizare a lunii (cheia ei: `repo_contabilitate.nota_de_amortizare`)."""
    return "AMORT-%d-%02d" % (int(an), int(luna))


def linii(cur, schema, an, luna):
    """[(cont_amortizare, rata, denumirea mijlocului fix)] — o linie pe mijloc fix cu rată pozitivă în luna cerută. Ridică ValueError cu
    motivul pentru contabil („Amortizarea nu se poate genera pentru <mijloc> până nu corectezi fișa lui: <motiv>”). Nu scrie nimic."""
    from core import d406_active as _d406, repo_mijloace_fixe
    with cur.connection.cursor() as c:   # rândurile de tuplu ale depozitului, oricare ar fi cursorul apelantului
        mf = repo_mijloace_fixe.de_amortizat(c, schema)
    out = []
    # [lotul 12, clasa 440] toate fișele de corectat deodată, fiecare cu motivul ei (nu numai prima), într-un singur refuz
    from core.erori import ErorileFormularului
    er = ErorileFormularului("Amortizarea lunii nu se poate genera")
    for mid, den, cont_am, val, rez, dnf, pif, cont_imob, met, reev, dcd, prel, dprel in mf:
        if not pif or not dnf:
            continue
        mf_d = {"cod": den, "denumire": den, "cont_imobilizare": cont_imob,
                "cont_amortizare": cont_am, "valoare": val, "rezidual": rez,
                "dnf_luni": dnf, "data_pif": pif, "metoda": met, "reevaluari": reev,
                "destinatie_cd": dcd, "amortizare_preluata": prel, "data_preluare": dprel}   # [359, A.1]
        try:
            rata = _d406.amortizare_luna(mf_d, an, luna)   # metoda reala (CF art.28), nu liniar
        except ValueError as e:
            er.fara_camp(f"Amortizarea nu se poate genera pentru {den} până nu corectezi fișa lui: {e}")
            continue
        if rata > 0:
            # [C129, clasa] contul de amortizare al fișei, nu 2813 pus tăcut: o fișă de 205 sau 2131 cu contul gol ar fi amortizat pe alt cont
            try:
                _ci, cont_am = conturile_fisei(den, cont_imob, cont_am, cu_imobilizare=False)
            except ValueError as e:
                er.fara_camp(f"Amortizarea lunii nu poate fi generată: {e}")
                continue
            out.append((cont_am, float(rata), den))
    if er:
        raise ValueError(er.detaliu()["mesaj"])   # ValueError, ca înainte: apelanții (generarea notei, regenerarea ciornei) îl prind așa
    return out

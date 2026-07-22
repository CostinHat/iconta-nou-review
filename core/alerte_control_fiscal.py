# -*- coding: utf-8 -*-
"""
core/alerte_control_fiscal.py — stratul pull->push al controlului fiscal.

PROBLEMA (restanta 17.07): findingurile ROSII din control_incrucisat (verifica_tva /
verifica_d112 / verifica_d390) se calculeaza DOAR cand contabilul deschide ecranul de
control fiscal (pull). Un stat de plata necontabilizat (D112 rosu) ramane invizibil daca
nimeni nu deschide ecranul. Lipsea stratul de PUSH.

SOLUTIE: NU un canal nou. Reutilizeaza clopotelul in-app existent (notificari_api.adauga +
validatorii_cabinetului). Un cron zilnic (agatat de core.notificari_scadenta, care ruleaza
deja la 08:00 - nu timer nou) itereaza firmele, ruleaza verificatorii, si pentru fiecare firma
cu ROSU NOU/reaparut scrie O notificare AGREGATA in clopotelul contabililor.

GARDURI (decizii Costin 19.07):
1. DOAR ROSU se pusheaza. Gri ("nu pot verifica") ramane pull - e informatie, nu actiune;
   nu spamam contabilul cu ce nu poate rezolva. Verde/tacut = nimic.
2. DESTINATAR = validatorii_cabinetului (contabilii, cere_cabinet) - ei corecteaza, nu patronul.
3. GRANULARITATE = agregat per FIRMA: "Firma X: N controale in rosu (D112, D390)" cu
   link=control-fiscal:{tenant_id}. O notificare per firma, NU per finding (consecvent cu
   filtrarea anti-dublura din portofoliu).
4. DEDUP prin jurnal public.alerte_control_emise (pattern public.alerte_emise / F103), cheie
   (tenant, verificator, perioada). GARDUL CRITIC: un rosu care PERSISTA neschimbat = O SINGURA
   alerta, nu una pe zi. Re-notifica DOAR daca: apare un verificator rosu NOU pe firma, SAU un
   rosu dispare si reapare (rezolvat -> se sterge din jurnal -> reaparitia conteaza ca nou).
   Doua rulari in aceeasi zi nu produc doua alerte (idempotent).

NU atinge engine-ul (control_incrucisat) si NU atinge ecranul de control fiscal (ramane pull,
sursa de adevar). Cheama verificatorii DIRECT (aceeasi sursa ca ecranul, care tot pe ei ii cheama),
ca sa nu importe aplicatia web (main.py) intr-un cron.
"""
from core import db
from core import notificari_api

REGULI = "2026.1"
MODUL = "alerte_control_fiscal"


def _verificatori(ci):
    """(cheie, eticheta, functie) - ordine canonica. Legat lazy de control_incrucisat."""
    return (
        ("tva", "TVA", ci.verifica_tva),
        ("d112", "D112 (salarii)", ci.verifica_d112),
        ("d390", "D390 (intracom.)", ci.verifica_d390),
        ("cota_tva", "cotă TVA facturi", ci.verifica_cota_tva),   # F184 (value-aware)
    )


def verificatori_rosii(conn, schema, an, luna):
    """Lista [(cheie, eticheta)] a verificatorilor in ROSU. Esec la un verificator = gri
    (nu pot verifica) -> NU se pusheaza (gri ramane pull); se logheaza, nu se ascunde tacit."""
    from core import control_incrucisat as ci
    out = []
    for cheie, eticheta, fn in _verificatori(ci):
        try:
            r = fn(conn, schema, an, luna)
        except Exception as e:
            print("    [%s] %s esec -> gri (nu se pusheaza): %s" % (schema, cheie, e))
            continue
        if (r or {}).get("stare") == "rosu":
            out.append((cheie, eticheta))
    return out


def decide(rosii_chei, deja_notificate):
    """PURA - gardul de dedup (punctul critic). rosii_chei: set de verificatori curent in rosu;
    deja_notificate: set din jurnal pentru (firma, perioada). Intoarce (noi, rezolvate, notifica):
      - noi = rosii ne-notificate inca (apar in jurnal dupa notificare)
      - rezolvate = notificate care nu mai sunt rosii (de sters -> reaparitia va conta ca nou)
      - notifica = True DOAR daca exista macar un rosu NOU (persistenta neschimbata nu re-notifica)."""
    rosii_chei = set(rosii_chei or ())
    deja_notificate = set(deja_notificate or ())
    noi = rosii_chei - deja_notificate
    rezolvate = deja_notificate - rosii_chei
    return noi, rezolvate, bool(noi)


def text_alerta(nume_firma, rosii):
    """Textul AGREGAT per firma. rosii = [(cheie, eticheta)] in ordine canonica."""
    etichete = ", ".join(e for _, e in rosii)
    n = len(rosii)
    cuv = "control fiscal" if n == 1 else "controale fiscale"
    return "%s: %d %s în roșu (%s)" % (nume_firma or "Firmă", n, cuv, etichete)


# Jurnal de idempotenta (pattern public.alerte_emise / F103) al alertelor de control.
# Schema in core/migrare_alerte_control_emise.py (migrare public normala, rulata ca iconta_user).


def emite_pentru_firma(tenant_id, nume, schema, cabinet_id, an, luna):
    """Pentru O firma: ruleaza verificatorii (pe schema), aplica dedup (jurnal public), si daca exista
    rosu NOU scrie O notificare agregata in clopotelul contabililor. Intoarce dict de raport."""
    perioada = "%04d-%02d" % (an, luna)
    with db.get_conn(schema) as cs:
        rosii = verificatori_rosii(cs, schema, an, luna)
    rosii_chei = {c for c, _ in rosii}

    with db.get_conn() as cp:
        with cp.cursor() as cur:
            cur.execute("SELECT verificator FROM public.alerte_control_emise "
                        "WHERE tenant_id = %s AND perioada = %s", (tenant_id, perioada))
            deja = {r[0] for r in cur.fetchall()}
        noi, rezolvate, vrea_notif = decide(rosii_chei, deja)
        destinatari = 0
        livrat = False
        with cp.cursor() as cur:
            # rezolvatele ies din jurnal INDIFERENT de livrare -> reaparitia va conta ca nou
            if rezolvate:
                cur.execute("DELETE FROM public.alerte_control_emise WHERE tenant_id = %s AND "
                            "perioada = %s AND verificator = ANY(%s)",
                            (tenant_id, perioada, list(rezolvate)))
            if vrea_notif:
                ids = notificari_api.validatorii_cabinetului(cp, cabinet_id)
                if ids:
                    notificari_api.adauga_multi(cp, ids, "control_fiscal", text_alerta(nume, rosii),
                                                link="control-fiscal:%d" % tenant_id)
                    destinatari = len(ids)
                    livrat = True
                    # jurnalizeaza DOAR ce s-a LIVRAT efectiv -> daca n-ai contabili de notificat,
                    # nu marca "notificat" (ar suprima alertarea cand apar validatori mai tarziu)
                    for c in noi:
                        cur.execute("INSERT INTO public.alerte_control_emise (tenant_id, verificator, perioada) "
                                    "VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", (tenant_id, c, perioada))
    return {"notificat": livrat, "vrea_notif": vrea_notif, "noi": sorted(noi),
            "rezolvate": sorted(rezolvate), "rosii": len(rosii_chei), "destinatari": destinatari}


def ruleaza(azi=None):
    """Cron: itereaza firmele de cabinet active, push in-app pe rosu nou/reaparut. Perioada = luna
    curenta (ca ecranul de control). Firme standalone (fara cabinet) sar (n-au contabili de notificat)."""
    from core.common import azi_ro
    azi = azi or azi_ro()   # [fus] cronul decide ce declaratii sunt datorate = zi RO, robust la OS TZ
    an, luna = azi.year, azi.month
    with db.get_conn() as cp:
        with cp.cursor() as cur:
            cur.execute("SELECT id, nume, schema_name, accounting_firm_id FROM public.tenants "
                        "WHERE accounting_firm_id IS NOT NULL AND activ = true "
                        "  AND schema_name ~ '^tenant_[0-9]+$' ORDER BY id")
            firme = cur.fetchall()
    tot = {"firme": 0, "notificate": 0, "rosii": 0}
    for tid, nume, schema, cabinet_id in firme:
        try:
            r = emite_pentru_firma(tid, nume, schema, cabinet_id, an, luna)
            tot["firme"] += 1
            tot["rosii"] += r["rosii"]
            if r["notificat"]:
                tot["notificate"] += 1
                print("  %s (%s): %d rosii, notificat %d contabili (noi: %s)"
                      % (schema, nume, r["rosii"], r["destinatari"], ",".join(r["noi"])))
        except Exception as e:
            print("  ESEC %s: %s" % (schema, e))
    print("Alerte control fiscal: firme=%d, notificate=%d, total rosii=%d"
          % (tot["firme"], tot["notificate"], tot["rosii"]))
    return tot


def _main():
    db.init_pool()
    ruleaza()


if __name__ == "__main__":
    _main()

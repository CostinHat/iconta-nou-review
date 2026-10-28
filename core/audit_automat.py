"""[715, comanda 14.2] Ce cereri face aplicația singură, nu omul.

Fiecare ecran își încarcă, la deschidere, contoarele și listele de pornire (drepturile, semaforul, coada, termenele, firmele scoase…):
omul a apăsat o singură dată, aplicația a făcut zeci de cereri. În `public.audit_log` rămân toate (sunt faptele cerute serverului), dar
alerta de acces anormal și numărătoarea „acțiunilor” din Fișa cabinetului le lasă deoparte: o alertă pe 394 de „acțiuni” ale unui cont de test
(27.10.2026, 17:15) era același ecran deschis de verificator, nu un acces neobișnuit. Regula se aplică la CITIRE, pe textul acțiunii
(`GET /cale`), deci acoperă și rândurile scrise înainte de ea — nicio migrare pe jurnal. Numai citiri (GET) fără date de firmă dincolo de ce
arată ecranul de pornire. O singură definiție: expresia, pentru Postgres (`actiune ~ MODEL`) și pentru Python (`este_automata`)."""
EXACTE = ("GET /eu/drepturi", "GET /eu/patru-ochi", "GET /eu/ciorne", "GET /eu/cautare", "GET /asistenti/echipa/semafor", "GET /tenants",
          "GET /termene", "GET /coada", "GET /control-fiscal", "GET /migrare/status", "GET /spv/autorizare", "GET /firme-scoase")
#: `LIKE` pentru starea SPV a unei firme (`GET /tenants/<id>/spv/stare`)
LIKE_SPV = "GET /tenants/%/spv/stare"
# Egalitate și `LIKE`, nu expresie regulată: pe jurnalul de milioane de rânduri al Panoului Admin o expresie regulată pe fiecare rând ținea
# lista cabinetelor peste termenul de 30 s al probei.


def este_automata(metoda, cale):
    actiune = "%s %s" % (metoda, cale.rstrip("/") if cale != "/" else cale)
    return actiune in EXACTE or (actiune.startswith("GET /tenants/") and actiune.endswith("/spv/stare") and actiune[13:-10].isdigit())


def sql_actiune_omului(alias):
    """Predicatul SQL al acțiunilor omului, cu aliasul rândului de jurnal; are DOUĂ `%s`, în ordinea `PARAM_OMULUI`."""
    return "(%s.actiune <> ALL(%%s) AND %s.actiune NOT LIKE %%s)" % (alias, alias)


PARAM_OMULUI = (list(EXACTE), LIKE_SPV)

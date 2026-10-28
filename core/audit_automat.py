"""[715, comanda 14.2] Ce cereri face aplicația singură, nu omul.

Fiecare ecran își încarcă, la deschidere, contoarele și listele de pornire (drepturile, semaforul, coada, termenele, firmele scoase…):
omul a apăsat o singură dată, aplicația a făcut zeci de cereri. În `public.audit_log` rămân toate (sunt faptele cerute serverului), dar
alerta de acces anormal și numărătoarea „acțiunilor” din Fișa cabinetului le lasă deoparte: o alertă pe 394 de „acțiuni” ale unui cont de test
(27.10.2026, 17:15) era același ecran deschis de verificator, nu un acces neobișnuit. Regula se aplică la CITIRE, pe textul acțiunii
(`GET /cale`), deci acoperă și rândurile scrise înainte de ea — nicio migrare pe jurnal. Numai citiri (GET) fără date de firmă dincolo de ce
arată ecranul de pornire. O singură definiție: expresia, pentru Postgres (`actiune ~ MODEL`) și pentru Python (`este_automata`)."""
import re

MODEL = (r"^GET (?:/eu/(?:drepturi|patru-ochi|ciorne|cautare)|/asistenti/echipa/semafor|/tenants|/termene|/coada|/control-fiscal"
         r"|/migrare/status|/spv/autorizare|/firme-scoase|/tenants/[0-9]+/spv/stare)/?$")
_AUTOMATE = re.compile(MODEL)

#: predicatul SQL al acțiunilor omului (pentru `cur.execute(... % ACTIUNE_OMULUI ..., (MODEL,))`): coloana `actiune` a jurnalului nu e cerere automată
ACTIUNE_OMULUI = "{col} !~ %s"


def este_automata(metoda, cale):
    return bool(_AUTOMATE.match("%s %s" % (metoda, cale)))

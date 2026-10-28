"""[715, comanda 14.2] Ce cereri face aplicația singură, nu omul.

Fiecare ecran își încarcă, la deschidere, contoarele și listele de pornire (drepturile, semaforul, coada, termenele, firmele scoase…):
omul a apăsat o singură dată, aplicația a făcut zeci de cereri. În `public.audit_log` rămân toate (sunt faptele cerute serverului), dar
rândul poartă `automat: true`, iar alerta de acces anormal și numărătoarea „acțiunilor” din Fișa cabinetului le lasă deoparte: o alertă
pe 394 de „acțiuni” a unui cont de test (27.10.2026, 17:15) era același ecran deschis de verificator, nu un acces neobișnuit.
Numai citiri (GET) fără date de firmă dincolo de ce arată ecranul de pornire."""
import re

_AUTOMATE = re.compile(
    r"^(?:/eu/(?:drepturi|patru-ochi|ciorne|cautare)"
    r"|/asistenti/echipa/semafor"
    r"|/tenants"
    r"|/termene"
    r"|/coada"
    r"|/control-fiscal"
    r"|/migrare/status"
    r"|/spv/autorizare"
    r"|/firme-scoase"
    r"|/tenants/\d+/spv/stare"
    r")/?$")


def este_automata(metoda, cale):
    return metoda == "GET" and bool(_AUTOMATE.match(cale))

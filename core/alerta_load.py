# -*- coding: utf-8 -*-
"""core/alerta_load.py — când pleacă alerta de load (comanda Costin 15.10.2026 noaptea, „Lotul 5 — comanda 3” pct.6b, verbatim în
DECIZII: „Alerta de load pleacă doar dacă media pe 15 minute depășește un prag calculat pe numărul de procesoare și rămâne așa; nu pleacă
în timpul rulărilor tale de teste.”).

Până acum: `load1 ≥ 0,7 × procesoare` la o singură măsurătoare — pe 2 procesoare, 1,4; orice rulare de teste îl depășea, iar alerta pleca
în serie (o dată pe oră, cât ținea rularea). Acum, din istoricul buclei de sănătate (`public.metrici_sanatate`, un rând la 5 minute):
  · PRAGUL = numărul de procesoare (`prag(cpu)`): media pe 15 minute arată toate procesoarele ocupate;
  · „RĂMÂNE AȘA” = toate rândurile din ultimele `TINUT_MIN` minute (cel puțin `MIN_RANDURI`) au `load15 ≥ prag`;
  · „NU ÎN TIMPUL TESTELOR” = niciun rând din ultimele `FARA_TESTE_MIN` minute n-a văzut o rulare de teste (`core.rulari_teste`): media pe
    15 minute a ferestrei ținute ar conține încă încărcarea lor.
Gard: core/test_alerta_load.py.

[deficiența 296, 16.10.2026, comanda Costin verbatim în DECIZII: „alertele de sănătate server prea dese: se trimit numai cele care cer o
acțiune”] Regula se generalizează la toată alerta de sănătate:
  · fiecare categorie are în `ACTIUNI` ce face omul care o primește; un rând de alertă se compune numai prin `rand(categorie, ...)`, deci
    o categorie fără acțiune nu poate pleca (gard: `core/test_alerte_sanatate_296.py`);
  · o condiție TRECĂTOARE (RAM, conexiuni DB, încărcare — `TINUTE`) nu cere nimic dacă trece singură: pleacă numai dacă rămâne peste prag
    `TINUT_MIN` minute și nu e o rulare de teste (`tinut`, aceeași regulă ca la load); disc, erori 500 și infrastructura P2 cer acțiune
    din prima măsurătoare.
Măsurat pe producție, 02–16.10.2026 (4.056 de rânduri): RAM max 64% (prag 75%), conexiunile au atins pragul (30) o dată, pe 05.10 —
singura alertă `conexiuni_db` —, erori 500: 0; încărcarea pe regula veche: 1.037 de rânduri peste 1,4 = o alertă pe oră."""
import datetime

#: ce face omul care primește alerta — o categorie fără rând aici nu se trimite
ACTIUNI = {
    "p2_infrastructura": "rulează din nou migrarea care lipsește (Panou Admin → Sănătate server o numește); până atunci contoarele "
                         "firmelor nu se mai actualizează",
    "disc": "eliberează spațiu pe server (jurnalele vechi, copiile de siguranță deja mutate în afara serverului) sau mărește discul",
    "ram": "vezi în Panou Admin → Sănătate server procesul care ține memoria; dacă nu e o rulare a ta, repornește serviciul în afara "
           "orelor de lucru ale cabinetelor",
    "conexiuni_db": "vezi în Panou Admin → Sănătate server cererile lente: conexiunile ținute peste prag blochează celelalte cereri",
    "erori": "deschide jurnalul erorilor (Panou Admin → Sănătate server): fiecare eroare 500 e un defect de reparat",
    "load": "vezi ce proces încarcă serverul (Panou Admin → Sănătate server); dacă nu e o rulare a ta, oprește-o sau mărește serverul",
    # [460] cursul zilei lipsă: facturile în valută primesc un curs mai vechi decât ultimul comunicat (CF art.290 alin.(2))
    "curs_bnr": "verifică de pe server că https://curs.bnr.ro/files/xml/years/nbrfxrates<an>.xml răspunde (Panou Admin → Sănătate "
                "server arată zilele lipsă); aplicația reîncearcă singură la 10 minute, iar contabilul vede pe factură ce curs se folosește",
}
#: condițiile trecătoare: alertă numai dacă rămân (`tinut`)
TINUTE = ("ram", "conexiuni_db", "load")


def rand(categorie, constatare):
    """Rândul din emailul de alertă: ce s-a constatat + ce faci. KeyError pentru o categorie fără acțiune (nu pleacă)."""
    return "%s — Ce faci: %s." % (constatare, ACTIUNI[categorie])


TINUT_MIN = 15
MIN_RANDURI = 3
FARA_TESTE_MIN = 30


def prag(cpu):
    return float(max(1, int(cpu or 1)))


def de_alertat(istoric, cpu, acum):
    """PURĂ. `istoric` = [(creat_la, load15, teste)] (orice ordine), `acum` = ora ultimului rând. -> `(alerta, motiv)`."""
    return tinut(istoric, prag(cpu), acum, "media pe 15 minute", "%.0f (numărul de procesoare)")


def tinut(istoric, p, acum, ce="valoarea", cum_prag="%.0f"):
    """PURĂ. [296] Condiția trecătoare care cere acțiune: `istoric` = [(creat_la, valoare, teste)], toate rândurile din ultimele
    `TINUT_MIN` minute (cel puțin `MIN_RANDURI`) au valoarea ≥ prag `p`, iar în ultimele `FARA_TESTE_MIN` minute n-a rulat nicio probă.
    -> `(alerta, motiv)`."""
    ramase = [r for r in istoric if r[0] > acum - datetime.timedelta(minutes=TINUT_MIN)]
    cu_teste = [r for r in istoric if r[0] > acum - datetime.timedelta(minutes=FARA_TESTE_MIN) and r[2]]
    if cu_teste:
        return False, "rulare de teste în ultimele %d de minute" % FARA_TESTE_MIN
    if len(ramase) < MIN_RANDURI:
        return False, "istoric prea scurt (%d rânduri în %d minute)" % (len(ramase), TINUT_MIN)
    if any(r[1] is None or float(r[1]) < p for r in ramase):
        return False, "%s nu stă peste %s" % (ce, cum_prag % p)
    return True, "%s peste %s la %d măsurători la rând, din 5 în 5 minute: %s" % (
        ce, cum_prag % p, len(ramase), ", ".join("%.2f" % float(r[1]) for r in sorted(ramase)))

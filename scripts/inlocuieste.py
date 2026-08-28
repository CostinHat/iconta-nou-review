# -*- coding: utf-8 -*-
"""Inlocuire de text intr-un document, care AFIRMA ca a gasit potrivirea.

DE CE EXISTA (28.08.2026, a treia recurenta). Scripturile de peticit documente scriu, de regula:

    t = io.open(cale).read()
    io.open(cale, "w").write(t.replace(vechi, nou))

Daca `vechi` nu se mai potriveste - fiindca documentul s-a schimbat intre timp -, `str.replace`
**nu se plange**: intoarce textul neatins, scriptul tipareste „OK", iar documentul ramane in forma
VECHE, care de acum arata curenta. S-a intamplat de trei ori pe tabelul de restante din
`PREDARE_LANT.md`: sablonul local ramasese in urma peticului aplicat pe server, iar inlocuirile
urmatoare n-au mai potrivit nimic - tacut.

*Un `replace` fara aserttiune nu e o modificare, e o speranta.*

REGULA: `METODA_VERIFICARE.md` §28.

    from scripts.inlocuieste import inlocuieste, intre_marcaje
    inlocuieste("PREDARE_LANT.md", vechi, nou)              # cere EXACT o potrivire
    inlocuieste("X.md", vechi, nou, de_cate_ori=3)          # sau exact cate ceri
    intre_marcaje("GARZI.md", MARCA_START, MARCA_STOP, bloc)  # bloc generat, intre marcaje

CE NU FACE, declarat: nu verifica daca inlocuirea e CORECTA - doar ca s-a produs. Un `nou` gresit
trece la fel de bine. Ce apara e clasa in care modificarea nu s-a produs deloc si nimeni n-a aflat.
"""
import io
import os

__all__ = ["inlocuieste", "intre_marcaje", "InlocuireRatata"]


class InlocuireRatata(AssertionError):
    """Potrivirea n-a fost gasita, sau nu de cate ori s-a cerut.

    POARTA MOTIVUL CA DATE, nu doar in mesaj — `motiv`, `gasite`, `cerute`. Un gard care ar
    verifica felul ratarii cautand un sir in mesaj ar pazi formularea, nu comportamentul: mesajul
    se poate rescrie fara ca nimic sa cada (clichetul 50 / METODA §23). Felurile:
    `fara_potrivire` · `ambigua` · `identice` · `crlf` · `lipsa` · `marcaj` · `ordine`."""

    def __init__(self, mesaj, motiv=None, gasite=None, cerute=None):
        super().__init__(mesaj)
        self.motiv = motiv
        self.gasite = gasite
        self.cerute = cerute


def _citeste(cale):
    b = io.open(cale, "rb").read()
    if b.count(b"\r\n"):
        raise InlocuireRatata(
            "%s are CRLF. Un patch rulat pe Windows trece fisierul la CRLF in tacere si face "
            "fiecare diff urmator zgomotos - se ruleaza PE SERVER." % cale, motiv="crlf")
    return b.decode("utf-8")


def _scrie(cale, text):
    io.open(cale, "wb").write(text.encode("utf-8"))


def inlocuieste(cale, vechi, nou, de_cate_ori=1):
    """Inlocuieste `vechi` cu `nou` in `cale`. RIDICA daca nu se potriveste de exact atatea ori.

    Intoarce numarul de inlocuiri (egal cu `de_cate_ori`), ca apelantul sa-l poata tipari."""
    if not os.path.isfile(cale):
        raise InlocuireRatata("%s nu exista" % cale, motiv="lipsa")
    if vechi == nou:
        raise InlocuireRatata(
            "%s: `vechi` si `nou` sunt identice - inlocuirea n-ar schimba nimic, iar un apel care "
            "nu schimba nimic e chiar clasa pe care fisierul asta o apara" % cale, motiv="identice")
    t = _citeste(cale)
    gasite = t.count(vechi)
    if gasite != de_cate_ori:
        raise InlocuireRatata(
            "%s: ancora se potriveste de %d ori, s-au cerut %d.%s\n  ancora: %r"
            % (cale, gasite, de_cate_ori,
               "  Documentul s-a schimbat sub script: forma pe care o astepti nu mai e acolo."
               if gasite == 0 else "  Ancora nu e unica - alege una mai lunga.",
               vechi[:120]),
            motiv=("fara_potrivire" if gasite == 0 else "ambigua"),
            gasite=gasite, cerute=de_cate_ori)
    _scrie(cale, t.replace(vechi, nou))
    return gasite


def intre_marcaje(cale, marca_start, marca_stop, bloc):
    """Rescrie ce e intre doua marcaje cu `bloc` (marcajele incluse in `bloc`, ca la generatoare).

    RIDICA daca vreun marcaj lipseste sau apare de mai multe ori - un bloc generat care nu-si mai
    gaseste locul ar trece tacut peste, iar documentul ar ramane pe generatia veche."""
    t = _citeste(cale)
    for m in (marca_start, marca_stop):
        n = t.count(m)
        if n != 1:
            raise InlocuireRatata("%s: marcajul %r apare de %d ori, nu o data" % (cale, m, n),
                                  motiv="marcaj", gasite=n, cerute=1)
    a = t.index(marca_start)
    b = t.index(marca_stop) + len(marca_stop)
    if a >= b:
        raise InlocuireRatata("%s: marcajul de STOP e inaintea celui de START" % cale,
                              motiv="ordine")
    nou = t[:a] + bloc + t[b:]
    _scrie(cale, nou)
    return len(nou) - len(t)

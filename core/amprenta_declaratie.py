# -*- coding: utf-8 -*-
"""
core/amprenta_declaratie.py — C3 (integritate in TIMP): snapshot+hash la depunere + regenerare-diff.

A doua cale reala pentru clasa "declaratie depusa regenerata altfel" (editare retroactiva in luna inchisa): la
DEPUNERE se ingheata o AMPRENTA (hash) a XML-ului emis; la orice regenerare ulterioara pe aceeasi perioada se compara
amprenta CURENTA cu cea DEPUSA - o divergenta = datele s-au schimbat sub o declaratie deja depusa (schema NU previne
editarea retroactiva; DUK nu vede istoria). NON-TAUTOLOGIE: compara PREZENTUL (regenerare) cu SINELE TRECUT (amprenta
depusa) - axa e TIMPUL, nu o recalculare a aceleiasi formule.

Amprenta se ia pe CONTINUTUL fiscal normalizat (nu pe octetii bruti): se scot spatiile dintre taguri, ca reformatarea
sa nu dea fals-pozitiv. LIMITA: persistarea amprentei la depunere (tabel snapshot) e wiring de produs - state_plata
snapshot deja DECIS in GARZI INVENTAR A; aici e MOTORUL (amprenta + verifica_regenerare), testabil pur.
"""
import hashlib
import re


def _normalizeaza(xml):
    """Continut fiscal, fara zgomot de formatare: colapseaza spatiile dintre taguri si la capete."""
    x = re.sub(r">\s+<", "><", (xml or "").strip())
    return x


def amprenta(xml):
    """SHA-256 hex al continutului fiscal normalizat. Deterministic: aceeasi declaratie -> aceeasi amprenta."""
    return hashlib.sha256(_normalizeaza(xml).encode("utf-8")).hexdigest()


class DeclaratieModificataDupaDepunere(Exception):
    """HARD-BLOCK: declaratia regenerata difera de cea DEPUSA (amprenta) - datele s-au schimbat retroactiv."""
    pass


def verifica_regenerare(xml_regenerat, amprenta_depusa):
    """Compara amprenta declaratiei REGENERATE cu amprenta DEPUSA. Divergenta = hard-block (numeste ambele amprente).
    Regula bazei nule: o amprenta depusa LIPSA (None/'') nu se interpreteaza ca 'coincide' - se semnaleaza."""
    if not amprenta_depusa:
        raise DeclaratieModificataDupaDepunere(
            "amprenta depusa LIPSA - nu se poate confirma ca declaratia regenerata coincide cu cea depusa")
    curenta = amprenta(xml_regenerat)
    if curenta != amprenta_depusa:
        raise DeclaratieModificataDupaDepunere(
            "declaratia regenerata DIFERA de cea depusa: amprenta depusa %s..., curenta %s... - datele s-au "
            "schimbat retroactiv sub o declaratie deja depusa" % (amprenta_depusa[:12], curenta[:12]))
    return True

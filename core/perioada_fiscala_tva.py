# -*- coding: utf-8 -*-
"""Perioada fiscală a TVA — luna sau trimestrul, și pe ce se sprijină. PUR.

DE CE E UN MODUL, nu două constante în dispecer. Prima formă a reparației punea `TEMEI_TVA_*` în
`core/declaratii_api.py`. **Decizia 73** (R151) spune de ce nu se poate: un singur nume `TEMEI*`
face fișierul „modul care citează legea", iar toate refuzurile lui vechi intră în datorie dintr-odată
— `declaratii_api` are refuzuri de formă („an invalid: %r") amestecate cu refuzuri normative, iar
*„un clichet pe o populație amestecată e prea mare ca să scadă și prea vag ca să însemne ceva"*.
Iar ieșirea prin `_TEMEI_...`, cu underscore, ca `scan_refuzuri` să nu-l vadă pe AST, e **eludare
prin numire** — numită și interzisă în aceeași decizie. Deci regula stă aici, singură, iar dispecerul
o cheamă.

CE FACE, și atât: dă fraza normei și temeiul ei, pentru declarațiile a căror perioadă fiscală **e**
perioada fiscală a TVA. Nu decide periodicitatea firmei (aia vine din `tip_decont` — v.
`declaratii_api.periodicitate_firma`) și nu o verifică: `art. 322` spune ce ÎNSEAMNĂ lunar și
trimestrial, nu care e cazul firmei.

CE NU FACE, declarat: **nu numără plafonul.** Cifra din alin. (2) n-are cheie în registrul de cote —
e chiar instanța consemnată la interdicția 1 pe `migrare.js` —, iar vigoarea ei nu se poate verifica
mecanic: `scripts/vigoare_articol.py` cere identificatorul de portal al actului, și Codul fiscal
n-are unul în corpus. *O regulă citată fără cifră nu îmbătrânește; una cu cifră ar îmbătrâni tăcut.*
"""
from core import common as _c

#: Verbatim din `anaf_surse/cod_fiscal_227_2015_consolidat.txt` (citit la sursă 06.09.2026).
TEMEI_322_1 = _c.Temei(
    "CF", art="322", alin="1", nivel_sursa="MO",
    de_cine="Code/Costin", verificat_la="2026-09-06",
    url="anaf_surse/cod_fiscal_227_2015_consolidat.txt",
    text_citat="Perioada fiscală este luna calendaristică.")

TEMEI_322_2 = _c.Temei(
    "CF", art="322", alin="2", nivel_sursa="MO",
    de_cine="Code/Costin", verificat_la="2026-09-06",
    url="anaf_surse/cod_fiscal_227_2015_consolidat.txt",
    text_citat=("Prin excepție de la prevederile alin. (1), perioada fiscală este trimestrul "
                "calendaristic pentru persoana impozabilă care în cursul anului calendaristic "
                "precedent a realizat o cifră de afaceri din operațiuni taxabile și/sau scutite cu "
                "drept de deducere și/sau neimpozabile în România conform art. 275 și 278, dar care "
                "dau drept de deducere conform art. 297 alin. (4) lit. b), care nu a depășit "
                "plafonul de 100.000 euro al cărui echivalent în lei se calculează conform normelor "
                "metodologice, cu excepția situației în care persoana impozabilă a efectuat în "
                "cursul anului calendaristic precedent una sau mai multe achiziții intracomunitare "
                "de bunuri."))

#: Declarațiile a căror perioadă fiscală ESTE perioada fiscală a TVA (urmează `tip_decont`-ul firmei).
#: Setul e ținut aici, lângă temei, fiindcă apartenența la el e chiar condiția ca art. 322 să fie
#: temeiul potrivit. `declaratii_api._TVA_PERIODIC` îl importă, ca să nu existe două liste.
SET_TVA_DECONT = frozenset({"d300", "d394", "d406"})

#: Nomenclator ÎNCHIS: art. 322 numește exact două perioade fiscale, nu o listă exemplificativă.
#: cheie = periodicitatea efectivă a firmei · valoare = (fraza normei, temeiul ei)
#: Proza spune REGULA, nu articolul: citarea canonică o lipește `norma()`, o singură dată.
NORME = {
    "lunar": ("perioada fiscală a TVA e luna calendaristică", TEMEI_322_1),
    "trimestrial": ("perioada fiscală a TVA e trimestrul calendaristic la firma care în anul "
                    "precedent nu a depășit plafonul de cifră de afaceri și nu a făcut achiziții "
                    "intracomunitare de bunuri", TEMEI_322_2),
}


def norma(tip, periodicitate):
    """Fraza normei + citarea canonică, gata de lipit la un refuz. `None` unde art. 322 NU e temeiul.

    `None` nu e un eșec, e jumătate din regulă: `d100` e trimestrial din temeiul impozitului pe
    profit, `d112` lunar din altul. **Art. 322 lipit pe ele ar fi un temei FALS — mai rău decât
    niciunul**, fiindcă un temei greșit se citește ca verificat.
    """
    if tip not in SET_TVA_DECONT:
        return None
    n = NORME.get(periodicitate)
    return None if n is None else " — %s (%s)" % (n[0], n[1])

# -*- coding: utf-8 -*-
"""core/bon_tva_deductibil.py — [lotul 17.5-P, AC153 și AC154; decizii_17_5_P.txt D2–D9] deductibilitatea TVA a unui bon fiscal pozat
și notele de cont ale articolelor lui.

DE CE: bonul fiscal ține loc de factură simplificată, deci justifică deducerea TVA, numai dacă poartă codul de înregistrare în scopuri de TVA
al beneficiarului (HG 1/2016 pct. 69 alin. (6)) și nu depășește 100 euro cu TVA (Cod fiscal art. 319 alin. (12) lit. a), cursul de la
art. 290 alin. (2)). Până la acest lot TVA al oricărui bon se trecea la 4426 fără nicio verificare.

CE FACE: `verdict` (funcție pură: codul de pe bon, codul firmei, totalul cu TVA în lei, cursul EUR) -> (stare, motiv), cu precedența din D2;
`text` (textele impuse ale motivelor); `nota_cont` / `note_conturi` (limitele conturilor 6022 și 623, numai semnalare, fără calcul);
`curs_euro` (cursul EUR al zilei bonului numai din cache, prin `core.curs_bnr.curs_pentru`: fără rețea, fără scriere).
Codurile se compară în forma `core.cui_forma.stocare` (fără spații, fără «RO» în fața cifrelor).
"""
from datetime import date
from decimal import Decimal

from core import cui_forma
from core import curs_bnr

#: stările verdictului: «da» (TVA dedus), «nu» (TVA nedeductibil: valoarea cu TVA intră în cheltuială), «de_verificat» (TVA dedus, cu observație)
STARI = ("da", "nu", "de_verificat")

_TEXTE = {
    "fara_cod": "TVA nedeductibil: pe bon nu este înscris codul fiscal al firmei cumpărătoare. Un bon fiscal ține loc de factură simplificată, "
                "deci justifică deducerea TVA, numai dacă poartă codul de înregistrare în scopuri de TVA al beneficiarului (HG 1/2016 pct. 69 "
                "alin. (6); Cod fiscal art. 319 alin. (12) și (21)). TVA intră în cheltuială. Verifică pe poză dacă codul chiar lipsește.",
    "alt_cod": "TVA nedeductibil: codul fiscal de pe bon (%s) nu este al firmei (%s). Bonul justifică deducerea TVA numai cu codul firmei "
               "cumpărătoare (HG 1/2016 pct. 69 alin. (6); Cod fiscal art. 319 alin. (21) lit. f). TVA intră în cheltuială. Verifică pe poză codul citit.",
    "neextras": "Codul cumpărătorului nu a fost citit de pe acest bon (încărcat înainte de această verificare). TVA rămâne dedus ca până acum; "
                "verifică pe poză că bonul poartă codul firmei (HG 1/2016 pct. 69 alin. (6)).",
    "firma_fara_cod": "Firma nu are codul fiscal completat în Date firmă, deci codul de pe bon nu se poate compara. TVA rămâne dedus; "
                      "completează codul firmei.",
    "curs_lipsa": "Pragul de 100 euro (Cod fiscal art. 319 alin. (12) lit. a) nu s-a putut verifica: lipsește cursul BNR al zilei bonului. "
                  "TVA rămâne dedus; verifică înainte de a certifica.",
    "peste_100": "Bonul depășește 100 euro (la cursul BNR din ziua bonului, Cod fiscal art. 290 alin. (2)). Ține loc de factură simplificată "
                 "numai în condițiile art. 319 alin. (13) din Codul fiscal (peste 100 și sub 400 euro, cu aprobarea furnizorului prin ordin al "
                 "ministrului finanțelor, HG 1/2016 pct. 94 alin. (2)); aprobarea nu se vede pe bon și nu este verificată în aplicație. "
                 "TVA rămâne dedus; verifică înainte de a certifica.",
    "ok": "TVA deductibil: bonul poartă codul firmei și nu depășește 100 euro (Cod fiscal art. 319 alin. (12) lit. a; HG 1/2016 pct. 69 alin. (6)).",
}

_NOTE = {
    "6022": "Combustibil: deductibilitatea cheltuielii e limitată la 50% pentru vehiculele care nu sunt folosite exclusiv în activitatea "
            "economică (Cod fiscal art. 25 alin. (3) lit. l), iar deducerea TVA aferentă tot la 50% (art. 298 alin. (1)); excepțiile din "
            "aceleași articole nu se verifică aici. Verifică folosirea vehiculului înainte de a certifica.",
    "623": "Protocol: cheltuielile de protocol au deductibilitate limitată, în limita unei cote de 2% (Cod fiscal art. 25 alin. (3) lit. a). "
           "Apa sau cafeaua pentru salariați nu sunt automat protocol: verifică destinația înainte de a păstra contul 623.",
}

#: pragul facturii simplificate, în euro, cu TVA inclus (Cod fiscal art. 319 alin. (12) lit. a)
PRAG_EURO = Decimal("100")


def verdict(cui_cumparator, cui_firma, total, curs_eur):
    """(stare, motiv) cu precedența din D2: necitit, cod absent, firma fără cod, alt cod, curs lipsă, peste 100 euro, altfel «da»."""
    if cui_cumparator is None:
        return "de_verificat", "neextras"
    cod = cui_forma.stocare(cui_cumparator)
    if not cod:
        return "nu", "fara_cod"
    firma = cui_forma.stocare(cui_firma)
    if not firma:
        return "de_verificat", "firma_fara_cod"
    if cod != firma:
        return "nu", "alt_cod"
    if curs_eur is None:
        return "de_verificat", "curs_lipsa"
    if Decimal(str(total)) > PRAG_EURO * Decimal(str(curs_eur)):
        return "de_verificat", "peste_100"
    return "da", "ok"


def text(motiv, cui_bon=None, cui_firma=None):
    """Textul impus al motivului; la «alt_cod», codul de pe bon și codul firmei în forma `cui_forma.stocare`."""
    t = _TEXTE[motiv]
    if motiv == "alt_cod":
        return t % (cui_forma.stocare(cui_bon) or "", cui_forma.stocare(cui_firma) or "")
    return t


def nota_cont(cont):
    """Nota de limită a contului (6022, 623); None pentru orice alt cont."""
    return _NOTE.get(str(cont).strip()) if cont else None


def note_conturi(articole):
    """Notele conturilor propuse ale articolelor, în ordinea primei apariții, fără dubluri."""
    note = []
    for a in articole or []:
        n = nota_cont(a.get("cont_propus")) if isinstance(a, dict) else None
        if n and n not in note:
            note.append(n)
    return note


def curs_euro(conn, data):
    """Cursul EUR al zilei bonului (CF art. 290 alin. (2), regula operațiunii), numai din cache; None fără dată validă sau fără curs."""
    if isinstance(data, date):
        zi = data
    elif isinstance(data, str):
        try:
            zi = date.fromisoformat(data)
        except ValueError:
            return None
    else:
        return None
    try:
        return Decimal(str(curs_bnr.curs_pentru(conn, "EUR", zi)[0]))
    except (curs_bnr.CursIndisponibil, curs_bnr.CursPreaVechi, curs_bnr.MonedaNecotata):
        return None

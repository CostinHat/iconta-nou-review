# -*- coding: utf-8 -*-
"""VOCABULARUL DE REFUZ al stratului use-case — ce spune aplicația, nu în ce protocol o spune.

DE CE EXISTĂ (13.09.2026, valul use-case al lui P7). Textul canonic cere două lucruri deodată:
*«use-case — deține tranzacția (P4), orchestrează»* (`PLAN_HARDENING.md:840`) și *«un use-case nu
construiește `HTTPException`»* (`:811`). În `main.py` erau **212 rute** care ridicau `HTTPException`
**dinăuntrul** tranzacției: decizia care produce refuzul se ia acolo unde se citesc datele. Mutând
tranzacția fără vocabular, `HTTPException` ar fi plecat cu ea și al doilea criteriu ar fi căzut.

**CE FACE POSIBILĂ TRADUCEREA, și e o măsurătoare, nu o speranță:** `HTTPException` **nu e prinsă
nicăieri** în aplicație — zero `except HTTPException` pe tot repo-ul. Deci rolul ei e exclusiv de
ieșire, iar înlocuirea cu o excepție de domeniu pe care stratul HTTP o traduce înapoi **nu poate
schimba niciun flux de control**. La fel s-a măsurat că **niciun obiect de răspuns** (`Response`,
`FileResponse`, …) nu se construiește înăuntrul unei tranzacții.

## CE E CINSTIT ȘI CE NU, scris aici ca să nu se citească altfel

Clasele de mai jos numesc **condiția** (*inexistent*, *fără drept*, *conflict*, *date invalide*), nu
codul. Traducerea condiție → cod HTTP e **o singură hartă, în stratul HTTP** (`main.py`), unde îi e
locul. Asta e partea cinstită.

**Partea care NU trebuie înfrumusețată:** harta e azi aproape unu-la-unu cu codurile pe care le
înlocuiește, fiindcă aplicația chiar avea șapte feluri de refuz, câte unul per cod. Vocabularul ăsta
**nu adaugă înțeles** — el mută decizia despre protocol acolo unde protocolul e cunoscut. Un val
viitor care descoperă că două refuzuri diferite trăiau sub același `404` le poate despărți aici, iar
harta din HTTP rămâne singurul loc care se atinge.

**Ce se păstrează, literă cu literă:** codul întors și textul mesajului. `core/test_p7_uc.py`
confruntă, rută cu rută, perechile (cod, mesaj) de dinainte cu cele de după — altfel „contractul HTTP
neschimbat" ar fi o afirmație, nu o măsurătoare.
"""


class EroareDeDomeniu(Exception):
    """Un refuz al aplicației, spus în limbajul ei. Stratul HTTP îl traduce; nimeni nu-l prinde ca
    să decidă altceva — exact cum `HTTPException` nu era prinsă nicăieri.

    **Detaliul se păstrează ca OBIECT, nu ca text.** Douăzeci de refuzuri ale aplicației poartă un
    dicționar (`{"mesaj": …, "erori_campuri": [...]}`), pe care ecranul îl desface ca să pună
    eroarea lângă câmpul vinovat. Un `str(e)` l-ar fi trimis ca reprezentare Python, iar contractul
    G10 s-ar fi rupt fără ca vreo probă de rutare să observe.
    """

    def __init__(self, detaliu=""):
        super().__init__(detaliu)
        self.detaliu = detaliu


class Inexistent(EroareDeDomeniu):
    """Lucrul cerut nu există, sau cine cere nu are cum să-l vadă — cele două nu se deosebesc
    dinadins, ca absența să nu spună dacă lucrul există la altcineva."""


class FaraDrept(EroareDeDomeniu):
    """Lucrul există și se vede, dar rolul cererii nu-l poate atinge."""


class Neautentificat(EroareDeDomeniu):
    """Nu se știe cine cere."""


class DateInvalide(EroareDeDomeniu):
    """Ce s-a trimis nu poate fi consemnat așa cum e: lipsește un câmp, o valoare nu e în domeniu,
    o normă o refuză."""


class CerereGresita(EroareDeDomeniu):
    """Cererea e formulată greșit ca operațiune — nu conținutul ei, ci ce se cere să se facă."""


class Conflict(EroareDeDomeniu):
    """Starea de acum nu îngăduie operațiunea: e deja făcută, e închisă, sau altcineva a luat-o."""


class Blocat(EroareDeDomeniu):
    """Resursa e ținută de altcineva chiar acum."""



# [P7 · valul use-case, lotul 2, 13.09.2026] Sase conditii pe care aplicatia le deosebea deja prin
# cod, dar nu le numea. Fara ele, treisprezece corpuri de ruta n-ar putea pleca in use-case — nu
# fiindca refuzul ar fi altul, ci fiindca harta n-ar avea unde sa-l puna. Regula e neschimbata:
# use-case-ul numeste CONDITIA, stratul HTTP alege codul, dintr-o singura harta.


class IntrarePreaMare(EroareDeDomeniu):
    """Ce s-a trimis e mai mare decât limita primită — nu e invalid, e prea mult."""


class FormatNeacceptat(EroareDeDomeniu):
    """Formatul trimis nu e dintre cele pe care operațiunea le poate citi."""


class PreaDes(EroareDeDomeniu):
    """S-a cerut prea des. Nu e un refuz despre conținut, ci despre ritm."""


class EsecIntern(EroareDeDomeniu):
    """Ceva al nostru a cedat, iar operațiunea nu s-a putut duce până la capăt."""


class ServiciuStrainCazut(EroareDeDomeniu):
    """Un serviciu din afară a răspuns, dar greșit — nu e vina cererii."""


class ServiciuIndisponibil(EroareDeDomeniu):
    """Un serviciu din afară nu răspunde acum. Se poate încerca mai târziu."""


#: Toate clasele vocabularului — o mulțime ÎNCHISĂ. O probă cere ca harta din stratul HTTP să le
#: acopere pe toate: o clasă nouă fără traducere ar ieși din aplicație ca `500`.
TOATE = (Inexistent, FaraDrept, Neautentificat, DateInvalide, CerereGresita, Conflict, Blocat,
         IntrarePreaMare, FormatNeacceptat, PreaDes, EsecIntern, ServiciuStrainCazut, ServiciuIndisponibil)

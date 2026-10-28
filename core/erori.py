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


#: Ecranul-țintă al unui refuz, în limba contabilului (`unde` al afirmației de refuz). O singură tabelă pentru refuzurile cu țintă
#: de ecran: `uc_comun.refuz_spre_ecran` și `RefuzGenerare.detaliu` (mutată aici din `uc_comun`, lotul 10, ca refuzul generatoarelor
#: să aibă aceeași formă tipată fără ca acest modul de vocabular să importe un use-case).
UNDE_ECRAN = {"date_firma": "Date firmă", "conectare_spv": "Setări cont → Conectare SPV", "produse": "Produse",
              # [lotul 11, decizia Costin 10.3] refuzul D406 / D394 trimite la fișa partenerului, bilanțul la întocmitorul cabinetului
              "clienti": "Clienți (fișa clientului)", "furnizori": "Furnizori (fișa furnizorului)",
              "date_cabinet": "Setări cont → Date cabinet",
              # [lotul 14, 683 / 695] declarația sau bilanțul care începe înainte de preluare trimite la importul balanței cu rulajele anului
              "import_solduri": "Import date › Solduri inițiale"}


class ErorileFormularului:
    """[lotul 11, deficiența 440, comanda Costin 11.1 pct.16: „toate erorile apar deodată, fiecare cu textul ei, în casetă și lângă câmp.”]
    Colectorul unic al validării unui formular pe server: în loc de `raise` la primul câmp (inventarul lotului 11: 310 funcții cu
    două sau mai multe refuzuri în șir, numai ~10 adunau lista), fiecare problemă se ADAUGĂ, iar la capăt se refuză o dată, cu toate:

        er = ErorileFormularului()
        if not corp.nume: er.camp("nume", "Numele firmei lipsește.")
        if not cui_valid(corp.cui): er.camp("cui", "CUI-ul nu are cifra de control corectă.")
        er.refuza()          # DateInvalide({"mesaj": …, "erori_campuri": [{camp, mesaj}, …]}) dacă e ceva; altfel nimic

    `camp` = id-ul câmpului pe ecran (contractul G10, DS cap.6 v2.30) sau numele din cerere, pe care ecranul îl traduce
    (`api.arataRefuzul(…, {campuri})`); `fara_camp(mesaj)` = o regulă a formularului întreg (intră în `mesaj`). Ecranul pune fiecare
    eroare lângă câmpul ei și pe toate în caseta „NU s-a salvat.” (api.js, DS cap.6 v2.99). Gard: `core/test_lot11_u0_erori_server.py`."""

    def __init__(self, titlu="Formularul nu s-a salvat"):
        self.titlu = titlu
        self.campuri = []
        self.generale = []

    def camp(self, camp, mesaj):
        if not any(c["camp"] == camp and c["mesaj"] == mesaj for c in self.campuri):
            self.campuri.append({"camp": camp, "mesaj": mesaj})
        return self

    def fara_camp(self, mesaj):
        if mesaj not in self.generale:
            self.generale.append(mesaj)
        return self

    def __bool__(self):
        return bool(self.campuri or self.generale)

    def detaliu(self):
        """{mesaj, erori_campuri}: `mesaj` spune toate problemele, fiecare cu textul ei, rând cu rând (DS cap.6 v2.89, `white-space:
        pre-line`) — și pentru un ecran care ar citi numai fraza."""
        texte = self.generale + [c["mesaj"] for c in self.campuri]
        mesaj = texte[0] if len(texte) == 1 else "%s:\n%s" % (self.titlu, "\n".join("— " + t for t in texte))
        return {"mesaj": mesaj, "erori_campuri": list(self.campuri)}

    def refuza(self):
        if self:
            raise DateInvalide(self.detaliu())


class RefuzGenerare(ValueError):
    """[lotul 10, deficiența 431 — „mesajul de refuz trimite la ce lipsește”] Refuzul unui generator de declarație care spune și UNDE se
    repară: notele de deschis (`note` = [{nota_id, eticheta, data}], aceeași formă ca `coada_trimite.legaturiNote`) și / sau ecranul
    de deschis (`ecran`, ex. „date_firma”). E `ValueError`, deci orice cale care prindea refuzul ca text îl prinde la fel; use-case-ul
    declarațiilor îl trimite ecranului ca obiect (`detaliu`), nu doar ca frază."""

    #: ce document refuză să se genereze (`tip` al afirmației); subclasele îl numesc pe al lor (`efactura_send.EDateIncomplete`)
    TIP = "generare document"

    def __init__(self, mesaj, note=None, ecran=None, camp_ecran=None):
        super().__init__(mesaj)
        self.note = list(note or [])
        self.ecran = ecran
        self.camp_ecran = camp_ecran   # câmpul adus în vedere pe ecranul de destinație (ca `detail.camp_ecran`, `core/mesaje`)

    def detaliu(self):
        """Corpul refuzului, ca AFIRMAȚIE TIPATĂ (`neconformitate`, decizia Costin 21.08.2026: afirmațiile despre datele firmei sunt
        obiecte), în aceeași formă ca `uc_comun.refuz_spre_ecran`: `unde` = ecranul sau notele unde se repară, plus cheile pe care
        le citește ecranul (`mesaj`, `note`, `ecran`, `camp_ecran`)."""
        from core import afirmatii as _af
        unde = UNDE_ECRAN.get(self.ecran, self.ecran) if self.ecran else ("notele contabile numite" if self.note else self.TIP)
        return _af.afirmatie("neconformitate", self.TIP, str(self), unde=unde, regula="refuz de generare, cu ținta reparării",
                             mesaj=str(self), note=self.note, ecran=self.ecran, camp_ecran=self.camp_ecran)

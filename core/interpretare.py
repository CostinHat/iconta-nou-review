# -*- coding: utf-8 -*-
"""core/interpretare.py — o INTERPRETARE e un obiect declarabil. (P11, 22.08.2026)

DE CE. Intre lege si cifra exista un pas de interpretare, iar acel pas nu are voie sa fie ingropat
intr-o conditie din cod. O alegere care poarta marcajul unui fapt legal devine imposibil de
contestat: nimeni nu discuta un articol de lege, deci o alegere gresita supravietuieste la nesfarsit
sub aparenta unei obligatii.

TREI CAZURI REALE, din aceeasi saptamana (anexa ARHITECTURA_NORMATIV):
  - «incadrat cu salariul de baza minim brut": egalitate stricta sau prag? Legea nu spune. Alegerea a
    trait intr-o comparatie din cod. Costa salariatul 82 de lei la un leu peste minim.
  - facilitatea la baza minima part-time: legea zice norma intreaga, structura ANAF o scade totusi.
    S-a ales legea, contra arbitrului, cu rationament in comentariu - dar nu ca dezacord marcat. Doua
    saptamani mai tarziu semnalul care contrazicea fusese inghetat ca asteptat, iar a doua cale
    aliniata la prima.
  - codificarea trimestriala 09: arata a eroare, era codificarea autoritatii. O ora de investigatie.

CE DEOSEBESTE O INTERPRETARE DE O VALOARE: **variantele**. «O interpretare fara variantele enumerate
nu e o interpretare, e o valoare deghizata. Daca nu poti numi cealalta varianta, legea nu lasa loc."
Minimul e DOUA - cea aleasa si cel putin o alta.

CE NU FACE, declarat: nu verifica daca alegerea e CORECTA. Nicio masina nu poate. Face imposibil ca
alegerea sa fie invizibila - atat, si atat se promite.
"""

# Formele de incertitudine, INCHISE. Fara ele, «legea lasa loc" devine o formula magica pe care o poti
# scrie oriunde. Enumerate din cele trei cazuri reale + lectura Partii III.
INCERTITUDINI = {
    "termen_nedefinit": {
        "inseamna": "textul foloseste un termen pe care nu-l defineste (incadrat cu, in mod "
                    "regulat), iar intelesul schimba rezultatul"},
    "tacere": {
        "inseamna": "textul nu spune nimic despre situatia concreta; regula trebuie dedusa din "
                    "vecinatati sau din scopul normei"},
    "texte_care_nu_se_acorda": {
        "inseamna": "doua texte in vigoare duc la rezultate diferite pentru acelasi caz"},
    "delegare_neimplinita": {
        "inseamna": "textul trimite la o norma de aplicare / un ordin care nu exista sau nu acopera "
                    "cazul"},
    "forma_publicata_difera_de_text": {
        "inseamna": "structura sau validatorul autoritatii implementeaza altceva decat pare sa spuna "
                    "textul - cazul part-time"},
}


class InterpretareIncompleta(ValueError):
    """Un camp cerut lipseste, sau variantele nu descriu o alegere reala."""


class Interpretare:
    """O alegere pe care legea a lasat-o deschisa, declarata ca atare.

    Se deosebeste de `common.Temei` prin CE SE POATE FACE CU EA: un temei se verifica, o interpretare
    se DISCUTA. De-aia poarta variante, autor si data - un temei n-are nevoie de ele, fiindca nu e
    alegerea nimanui.

    Imutabila dupa construire: un dezacord cu arbitrul NU se poate stinge prin atribuire. Se stinge
    doar construind o interpretare NOUA (alta alegere) sau prin confirmarea arbitrului. Aceeasi forma
    ca la contradictia din statul de plata: ce se deriva nu se poate pune pe zero prin apasare.
    """

    __slots__ = ("cheie", "text_citat", "de_ce_lasa_loc", "forma", "variante", "ales", "motiv",
                 "de_cine", "la_data", "arbitru", "arbitru_confirma", "arbitru_spune", "temei_legat")

    def __init__(self, cheie, text_citat, de_ce_lasa_loc, forma, variante, ales, motiv,
                 de_cine, la_data, arbitru=None, arbitru_confirma=None, arbitru_spune=None,
                 temei_legat=None):
        def cere(v, nume, explic):
            if not (v or "").strip() if isinstance(v, str) or v is None else not v:
                raise InterpretareIncompleta("interpretarea %r fara `%s`: %s" % (cheie, nume, explic))

        cere(cheie, "cheie", "fara nume nu poate fi ceruta de nimeni")
        cere(text_citat, "text_citat",
             "fara textul care a lasat loc nu se poate verifica DACA legea lasa loc - iar atunci "
             "«interpretare\" devine un permis de a scrie orice")
        cere(de_ce_lasa_loc, "de_ce_lasa_loc", "ce anume nu determina legea singura")
        cere(motiv, "motiv", "de ce s-a ales varianta asta si nu alta")
        cere(de_cine, "de_cine", "o alegere anonima nu e o decizie")
        cere(la_data, "la_data", "o alegere fara data nu se poate revizui in ordine")

        if forma not in INCERTITUDINI:
            raise InterpretareIncompleta(
                "forma de incertitudine %r nu e in nomenclator; cele declarate: %s. Daca alegerea ta "
                "nu incape in niciuna, e semn ca nu legea a lasat loc."
                % (forma, ", ".join(sorted(INCERTITUDINI))))

        v = list(variante or [])
        if len(v) < 2:
            raise InterpretareIncompleta(
                "interpretarea %r are %d variante. O interpretare FARA variantele enumerate nu e o "
                "interpretare, e o valoare deghizata: daca nu poti numi CEALALTA varianta, legea nu "
                "lasa loc si ce ai facut e o citire, nu o alegere." % (cheie, len(v)))
        nume_var = [x[0] for x in v]
        if ales not in nume_var:
            raise InterpretareIncompleta(
                "varianta aleasa %r nu e printre cele enumerate (%s) - atunci lista nu descrie "
                "spatiul real al alegerii." % (ales, ", ".join(nume_var)))
        if arbitru_confirma is False and not (arbitru_spune or "").strip():
            raise InterpretareIncompleta(
                "interpretarea %r spune ca arbitrul o CONTRAZICE, dar nu spune CE zice. Un dezacord "
                "nedocumentat e un dezacord ascuns (P8)." % cheie)

        for k, val in (("cheie", cheie), ("text_citat", text_citat),
                       ("de_ce_lasa_loc", de_ce_lasa_loc), ("forma", forma),
                       ("variante", tuple(tuple(x) for x in v)), ("ales", ales), ("motiv", motiv),
                       ("de_cine", de_cine), ("la_data", la_data), ("arbitru", arbitru),
                       ("arbitru_confirma", arbitru_confirma), ("arbitru_spune", arbitru_spune),
                       ("temei_legat", temei_legat)):
            super().__setattr__(k, val)

    @property
    def dezacord_deschis(self):
        """Se DERIVA din `arbitru_confirma`, nu se tine intr-un camp: nu exista nimic de pus pe zero
        ca sa dispara. Aceeasi regula ca la contradictia dintre statul emis si recalcul."""
        return self.arbitru_confirma is False

    def __repr__(self):
        return "Interpretare(%r -> %r%s)" % (
            self.cheie, self.ales, ", DEZACORD DESCHIS" if self.dezacord_deschis else "")


def interpretari_deschise(lista):
    """Cele pe care arbitrul le contrazice si care asteapta lamurire."""
    return [i for i in lista if i.dezacord_deschis]

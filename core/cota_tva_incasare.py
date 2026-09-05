# -*- coding: utf-8 -*-
"""Care dată decide cota la TVA la încasare — cele două ramuri ale art. 291 alin. (5). PUR.

DE CE E UN MODUL, nu patru rânduri în rută. Regula e o normă fiscală, nu o operațiune de rutare, iar
un modul care aplică o normă trebuie să o poată **numi**: fiecare refuz de aici poartă
`TEMEI_291_5` ca date, nu ca proză.

*Și e chiar ce a arătat clichetul refuzurilor.* Prima formă a reparației punea constanta `TEMEI_291_5`
în `main.py`. Efectul, măsurat: `main.py 0 -> 389` — un singur nume `TEMEI*` face fișierul „modul care
citează legea", iar toate cele 389 de refuzuri ale lui intră în datorie dintr-odată. Norma
interdicției 77 spune ea însăși de ce asta ar fi fost rău: *„un clichet pe o populație amestecată e
prea mare ca să scadă și prea vag ca să însemne ceva"* — cele 389 amestecă refuzuri de formă cu
refuzuri normative. Aici regula stă singură, deci datoria fișierului e **zero prin construcție**: n-are
niciun refuz care să nu-și numească temeiul.

CE NU FACE, spus: nu caută factura sau avansul în evidența firmei. Varianta derivării din documente a
fost respinsă explicit de Costin (05.09.2026) — *„data facturii vs. data livrării nu se poate stabili
mecanic din datele de azi; a ghici ar produce o cifră validă și falsă"* —, iar legătura dintre nota de
TVA la încasare și documentul care a produs-o oricum nu există azi.
"""
from collections import namedtuple

from core import common as _c

#: Verbatim din `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, l. 18154 (citit la sursă 05.09.2026).
TEMEI_291_5 = _c.Temei(
    "CF", art="291", alin="5", nivel_sursa="MO",
    de_cine="Code/Costin", verificat_la="2026-09-05",
    url="anaf_surse/cod_fiscal_227_2015_consolidat.txt",
    text_citat=("În cazul operațiunilor supuse sistemului TVA la încasare, cota aplicabilă este cea "
                "în vigoare la data la care intervine faptul generator, cu excepția situațiilor în "
                "care este emisă o factură sau este încasat un avans, înainte de data "
                "livrării/prestării, pentru care se aplică cota în vigoare la data la care a fost "
                "emisă factura ori la data la care a fost încasat avansul."))

#: Nomenclator ÎNCHIS: norma numește exact două situații, nu o listă exemplificativă.
#: Cheia e ce trimite ecranul; valoarea, cum se numește situația într-un refuz sau într-o notă.
RAMURI = {
    "fapt_generator": "livrarea sau prestarea a fost prima",
    "factura_avans": "factura ori avansul au fost înainte de livrare",
}

Alegere = namedtuple("Alegere", "ramura data_cotei data_fapt_generator data_document")


class RefuzAlegere(ValueError):
    """Refuz de FOND, ca obiect cu atribute — nu ca propoziție.

    `cod` spune CARE din cele patru feluri de a nu ști e ăsta. Fără el, un test care cere doar „un
    ValueError" trece și când refuzul vine din alt motiv decât cel probat: mutația care a scos
    verificarea ramurii lăsa alegerea să cadă prin `else` pe ramura de excepție, unde era refuzată
    pentru lipsa datei documentului — rezultat corect, motiv greșit, gardă verde.

    Temeiul e lipit de propoziție: un refuz în numele unei norme numește norma.
    """

    CODURI = ("fara_fapt_generator", "ramura_nealeasa", "fara_data_document",
              "document_dupa_livrare")

    def __init__(self, cod, mesaj, temei=TEMEI_291_5):
        assert cod in self.CODURI, cod
        self.cod, self.temei = cod, temei
        super().__init__("%s (%s)" % (mesaj, temei))


def _cere(cod, mesaj):
    raise RefuzAlegere(cod, mesaj)


def alegerea(corp):
    """(ramura, data_cotei, data_fapt_generator, data_document) dintr-un corp de cerere.

    Data cotei se ia din ramura ALEASĂ de contabil. Patru feluri de a nu ști, patru refuzuri,
    fiecare cu `cod` propriu — ca un test să poată cere refuzul POTRIVIT, nu orice refuz:
      0. fără data faptului generator — nu există nicio ramură fără ea;
      1. ramura nealeasă — nu se ghicește (decizia lui Costin, 05.09.2026);
      2. ramura de excepție fără data documentului — norma spune „cota la data ACELUI document";
      3. documentul DUPĂ livrare — **contradicție, nu lipsă**: aici aplicația are amândouă datele,
         deci nu întreabă, ci arată. *Se cere ce nu se poate deriva; nu se cere ce se poate verifica.*
    """
    dfg = (corp or {}).get("data_fapt_generator")
    if not dfg:
        _cere("fara_fapt_generator", "Data faptului generator (livrarea sau prestarea) e obligatorie: la TVA la încasare "
              "cota se ia din legea în vigoare ATUNCI, nu la data încasării")

    ramura = (corp or {}).get("ramura_291_5")
    if ramura not in RAMURI:
        _cere("ramura_nealeasa", "Alege care din cele două situații ale art. 291 alin. (5) e a operațiunii: "
              "«%s» — cota e cea de la data livrării; sau «%s» — cota e cea de la data facturii "
              "ori a avansului. Aplicația nu poate deduce singură: datele operațiunii nu spun care "
              "document a fost primul, iar o alegere ghicită ar da o cifră validă și falsă"
              % (RAMURI["fapt_generator"], RAMURI["factura_avans"]))

    if ramura == "fapt_generator":
        return Alegere(ramura, dfg, dfg, None)

    doc = (corp or {}).get("data_factura_avans")
    if not doc:
        _cere("fara_data_document", "Ai ales situația în care factura ori avansul au precedat livrarea. Atunci cota e cea "
              "în vigoare la data ACELUI document, deci data lui e obligatorie: fără ea nu există "
              "cotă de verificat")
    if str(doc) >= str(dfg):
        _cere("document_dupa_livrare", "Excepția se aplică numai dacă factura ori avansul au fost ÎNAINTE de livrare, iar "
              "aici documentul e din %s și livrarea din %s. Ori corectezi una din date, ori "
              "operațiunea e în situația generală, cu cota de la data livrării" % (doc, dfg))
    return Alegere(ramura, doc, dfg, doc)


def descrierea(a):
    """Fraza care lipește cota de motivul ei, pentru descrierea implicită a notei.

    Peste șase luni, cine citește nota trebuie să poată reconstitui **de ce** cota e aia și nu alta.
    """
    if a.ramura == "fapt_generator":
        return "cota de la livrarea din %s" % a.data_fapt_generator
    return ("cota de la factura/avansul din %s, anterior livrării din %s"
            % (a.data_document, a.data_fapt_generator))

"""Judecă un martor brut E sau C, separat de aplicație. python ... ID observatie.json"""
import json
import sys
from collections import Counter

def set_egal(a,b):
    return bool(a) and len(a)==len(set(a)) and Counter(a)==Counter(b)

def judeca(id, m):
    if id=="datorate":
        return (m["scrolluri_lista"]==0 and m["scrolluri_traseu"]==1 and m["id_ultim_sursa"] and
                m["id_ultim_sursa"]==m["id_selectat"] and m["perioada_destinatie"]==m["perioada_sursa"])
    if id=="control":
        gr=m["grupe"]; ids=m["id_sursa"]
        return ((bool(gr) or not ids) and m["firma_ui"]==m["firma_sursa"] and m["perioada_ui"]==m["perioada_sursa"]
                and m["total_sumar"]==len(ids) and m["id_initial"]==ids[:1]
                and (m["viewport"]!=[1366,768] or m["scroll_corp_initial"]<=m["inaltime_corp_initial"]+1)
                and (set_egal(ids,[x for g in gr for x in g["id_la_deschidere"]]) if ids else not any(g["id_la_deschidere"] for g in gr))
                and all(g["clicuri"]==1 for g in gr) and m["context_revenire"]==m["context_intrare"])
    if id=="pagini":
        pag=m["pagini"]; ids=m["id_sursa"]
        return (len(ids)>8 and len(ids)%8!=0 and len(pag)>=2 and all(len(x)==8 for x in pag[:-1])
                and 1<=len(pag[-1])<8 and set_egal(ids,[i for x in pag for i in x])
                and m["ultim_deschis"]==pag[-1][-1] and m["total_sumar"]==len(ids)
                and bool(m["filtru_asteptat"]) and set_egal(m["filtru_asteptat"],m["filtru_observat"])
                and m["filtru_fara_rezultat"]==[] and m["filtru_dupa_revenire"]==m["filtru_initial"]
                and m["pagina_dupa_revenire"]==m["pagina_dinainte"] and m["pagina_dupa_filtru"]==1
                and m["sumar_vizibil"] and m["filtru_vizibil"] and m["scrolluri_verticale"]<=1)
    if id=="cif":
        erori=m["respingeri_sursa"]
        return (len(erori)>=2 and m["initial_siruri_motiv"]==0 and m["sumare_initiale"]==1
                and m["numar_sumar"]==len(erori) and m["detalii_deschise"]==erori and m["clicuri_deschidere"]==1
                and m["motive_dupa_pliere"]==0)
    if id=="f025a":
        return (m["total_coloane"]>=10 and m["latime_corp"]>0 and m["scroll_corp"]<=m["latime_corp"]+1
                and set_egal(m["campuri_sursa"],m["campuri_accesibile"]) and m["id_sursa"]==m["id_detaliu"])
    if id=="f025s":
        return (m["butoane_total"]==1 and m["id_unic"] is True and m["actionabil"] is True
                and m["clicuri_desfasurare"]==0 and m["clicuri_deschidere"]==1
                and (not m["blocaj"] or (m["rand_reevaluare_vizibil_initial"] is True and m["buton_vizibil_initial"] is True))
                and (not m["blocaj"] or m["coduri_blocaje_sursa"][0]=="REEVALUARE_VALUTA" or m["primul_blocaj_vizibil_initial"] is True)
                and m["butoane_rand"]==int(m["blocaj"])
                and m["butoane_fixe"]==int(not m["blocaj"]) and m["destinatie"]=="Reevaluare valută"
                and m["firma_luna_intrare"]==m["firma_luna_destinatie"]
                and m["suma_sursa"]==m["suma_ui"] and bool(m["explicatie_ui"]))
    if id=="f043a":
        return (m["latime_corp"]>0 and m["scroll_corp"]<=m["latime_corp"]+1 and m["numar_suprapuneri"]==0
                and len(m["linii_xml"])>=2 and m["clasificari_ui"]==m["linii_xml"]
                and m["id_document_initial"]==m["id_document_dupa"])
    if id=="f043s":
        return (m["grupe_taxare_initiale_pe_aceeasi_linie"]==1 and m["control_activ"]==m["permis_sursa"]
                and (m["control_activ"] or bool(m["motiv_vizibil"])) and m["valori_dupa"]==m["valori_inainte"])
    if id=="f078":
        return (0<m["campuri_initiale"]<m["campuri_E_reprodus"] and m["scrolluri_banda_erori"]==0
                and set_egal(m["campuri_necesare"],m["campuri_accesibile"]) and "13" in m["motiv_cnp_invalid"])
    if id=="f080":
        return (0<m["actiuni_initiale"]<m["actiuni_E_reprodus"] and 0<=m["clicuri_compozitie"]<=1
                and m["fluturas_sursa"]==m["fluturas_ui"] and len(m["fluturas_sursa"])>=4)
    if id=="f085":
        return (m["afisari_refuz"]==1 and m["cont"] in ["401","4111"] and bool(m["motiv_sursa"])
                and m["motiv_sursa"] in m["motiv_ui"] and m["solduri_dupa"]==m["solduri_inainte"]
                and m["clicuri_detalii_tva"]<=1 and bool(m["detaliu_tva"]))
    if id=="istoric":
        return (m["cale"] in ["meniu","fisa"] and m["latime_lista"]>0 and m["scroll_lista"]<=m["latime_lista"]+1
                and m["latime_corp"]>0 and m["scroll_corp"]<=m["latime_corp"]+1 and len(m["date_sursa"])>=4
                and m["date_sursa"]==m["date_detaliu"] and bool(m["actiune_accesibila"])
                and m["id_revenire"]==m["date_sursa"]["id"])
    if id=="cota":
        return (m["descriere_dupa"]==m["descriere_initiala"] and bool(m["motiv_asteptat"])
                and m["motiv_vizibil"]==m["motiv_asteptat"] and any(c in m["motiv_vizibil"] for c in "ăâîșțĂÂÎȘȚ")
                and m["cota_dupa_acceptare"]==m["cota_fixture"])
    if id=="poarta":
        return (m["cod_raspuns"]=="INTREABA_PLEACA_MARFA" and m["alegeri_active"]==["Da, pleacă marfa","Nu, doar factură"]
                and m["emite_activ"] is False and bool(m["motiv_vizibil"]) and m["facturi_initiale"]==m["facturi_finale"])
    if id=="primita":
        return (set(m["factura_sursa"])=={"id","furnizor","total","moneda"} and m["factura_sursa"]==m["factura_detaliu"]
                and m["id_lista"]==m["id_revenire"]==m["factura_sursa"]["id"] and m["provenienta"]=="SPV simulat")
    if id=="invitat":
        return (m["folosiri_initiale"]==0 and m["rol"]=="asistent" and set_egal(m["firme_atribuite"],m["firme_vizibile"])
                and m["firma_aleasa"] in m["firme_atribuite"] and m["acces_firma_neatribuita"] in [403,404]
                and m["drepturi_efective"]==m["drepturi_atribuite"] and m["actiuni_principale"]==1
                and m["suprapuneri"]==0 and bool(m["ajutor_vizibil"]) and m["clicuri_pas_urmator"]==1
                and m["context_revenire"]==m["context_initial"] and m["context_reload"]==m["context_final"])
    raise ValueError("ID necunoscut: "+id)

if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("Utilizare: ID observatie.json")
    with open(sys.argv[2],encoding="utf-8") as f:d=json.load(f)
    try:ok=judeca(sys.argv[1],d)
    except (KeyError,TypeError,ValueError) as e:raise SystemExit("NEEXECUTAT: martor invalid "+str(e))
    print(sys.argv[1],"trece" if ok else "pica")
    raise SystemExit(0 if ok else 1)

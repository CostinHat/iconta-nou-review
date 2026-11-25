"""Judecă exportul E sau C al unui caz DS. python oracol_ds_Q7.py ID masuri.json
Valorile lipsă produc eroare de măsurare. Un verdict fals este o abatere observată."""
import json
import sys
from decimal import Decimal

def egal_nevid(a,b):
    return isinstance(a,list) and len(a)>0 and a==b
def judeca(caz,m):
    if caz=="tabel":
        return (m["latime_corp"]>0 and 0<m["latime_continut"]<=m["latime_corp"]+1
                and m["scrolluri_verticale_fara_preview_xml"]<=1 and m["celule_trunchiate"]==0
                and egal_nevid(m["campuri_sursa"],m["campuri_accesibile"])
                and (m["rezolutie"]!="603x590" or m["randuri_in_bloc"] is True)
                and (not m["registru_jurnal"] or m["rezolutie"]!="603x590" or m["inaltime_utila"]>88))
    if caz=="principala":
        return (m["principale_vizibile"]==1 and bool(m["eticheta_asteptata"])
                and m["eticheta_ui"]==m["eticheta_asteptata"] and m["in_viewport_initial"] is True
                and m["principale_pe_randuri"]==0)
    if caz=="inutile":
        return (bool(m["inutile_in_stare"]) and set(m["inutile_in_stare"]).isdisjoint(m["controale_vizibile"])
                and set(m["actiuni_permisesursa"])<=set(m["actiuni_accesibile"]))
    if caz=="alegere":
        return (m["grupuri_vizibile"]==1 and egal_nevid(m["valori_sursa"],m["valori_accesibile"])
                and m["valoare_dupa"]==m["valoare_aleasa"])
    if caz=="erori":
        return (bool(m["obligatorii_goale"]) and set(m["obligatorii_goale"])==set(m["semnalate"])
                and m["semnalari_duplicate"]==0 and m["casete_imbricate"]==0)
    if caz=="motiv":
        return (m["camp_completat"] not in m["campuri_lipsa_ui"] and bool(m["campuri_lipsa_sursa"])
                and set(m["campuri_lipsa_ui"])==set(m["campuri_lipsa_sursa"]) and m["motiv_vizibil"] is True)
    if caz=="cautare":
        return (m["termen"]=="Marfa A" and m["optiune_aleasa"]==m["termen"] and m["mesaje_absenta"]==0)
    if caz=="text":
        return (bool(m["esantioane"]) and all(x["text_ui"]==x["text_asteptat"] and x["text_asteptat"] for x in m["esantioane"])
                and m["fraze_duplicate"]==0 and m["lipiri"]==0)
    if caz=="avertisment":
        return (m["sumare_initiale"]==1 and m["detalii_initiale"]==0 and m["clicuri_detalii"]==1
                and egal_nevid(m["iduri_sursa"],m["iduri_dupa_deschidere"]) and m["texte_ui"]==m["texte_integrale"])
    if caz=="declaratii":
        return (m["anterioare_initial_pliat"] is False and m["continua_vizibil_dupa_selectie"] is True
                and m["continua_activ"] is True and m["declaratie_ui"]==m["declaratie_sursa"]
                and egal_nevid(m["perechi_tip_perioada_sursa"],m["perechi_tip_perioada_accesibile"]))
    if caz=="nota":
        return (m["drept_validare"] is False and m["stare_nota"]=="la validare" and m["id_sursa"]==m["id_ui"]
                and m["id_ui"] and m["editeaza_vizibil"] is False and m["sterge_vizibil"] is False)
    if caz=="salariu":
        asteptat=dict(brut=5000,cas=1250,cass=500,deducere=562,impozit=269,net=2981)
        return (m["perioada"]=="2026-11" and m["persoane"]==0 and m["functie_baza"] is True
                and all(Decimal(str(m[k]))==v for k,v in asteptat.items()))
    raise ValueError("Caz DS necunoscut")
if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit(__doc__)
    with open(sys.argv[2],encoding="utf8") as f:m=json.load(f)
    verdict=judeca(sys.argv[1],m)
    print("trece" if verdict else "pica");raise SystemExit(0 if verdict else 1)

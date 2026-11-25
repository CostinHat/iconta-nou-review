"""Compară exporturile de produs cu documentele-sursă ale fiecărei probe de candidat.
python oracol_fluxuri_Q7.py dosar/probe_fluxuri.json
Înregistrare: id, rezolutie, masuri, produs și sursa (cale relativă, sha256, localizare).
Fișa de măsurare transpune câmpurile indicate în ramurile de mai jos din martorii originali.
"""
import hashlib
import json
import re
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

DIM = ("1366x768", "603x590")
IDS = [f"FISC.{i}" for i in range(1,9)] + [f"STOC.{i}" for i in range(1,7)] + [f"FINAL.{i}" for i in range(1,10)] + ["FINAL.10a","FINAL.10b","FINAL.10c"]

def bani(x):
    if isinstance(x,bool):
        raise ValueError("Sumă booleană")
    d=Decimal(str(x))
    if not d.is_finite():
        raise ValueError("Sumă nefinita")
    return d

def lista(x):
    return isinstance(x,list) and len(x)>0

def identic(x,y):
    return lista(x) and len(x)==len(set(x)) and sorted(x)==sorted(y)

def judeca(caz,m):
    if caz=="FISC.1":
        return (m["cui_balanta"] == "401002001" and m["cont_sursa"] == "707"
                and m["perioada_rulaj"] == "2026-07" and bani(m["rulaj_creditor_iulie"]) == bani(m["baza_707"])
                and m["trimestru"]=="2026-T3" and m["data_balanta"]=="2026-07-31" and m["cod"]=="121"
                and bani(m["baza_707"])==1000 and bani(m["cota"])==1 and bani(m["suma_xml"])==10
                and m["erori_duk"]==[] and m["confruntare_efectuata"] is True)
    if caz=="FISC.2":
        return (identic(m["doc_de_blocat_sursa"],m["doc_blocaj"]) and identic(m["doc_diferenta"],m["iduri_link_deschis"])
                and m["in_coada"] is False and bani(m["tva_de"])==21
                and (m["de_in_xml"] is False and m["de_semnalat"] is True and m["de_id"] in m["doc_blocaj"] and re.search(r"F1A\s*(?:nr\.?\s*)?17(?!\d)", m["motiv_de"], re.I) is not None and m["refuz_coada_de"] is True and m["caz_eligibil_acceptat"] is True))
    if caz=="FISC.3":
        return (m["fara_nc_emisa"] is False and bool(m["motiv_refuz"].strip()) and m["cu_nc_id"] in m["operatiuni_luna"]
                and identic(m["operatiuni_luna"],m["operatiuni_declarate_sau_semnalate"])
                and identic(m["istorice_fara_nc"],m["iduri_link_corectare"]))
    if caz=="FISC.4":
        return (m["nota_id"]==146 and m["descriere_sursa"] and m["descriere_sursa"]==m["descriere_reparata"]
                and m["stornare_noua_sursa"] and m["stornare_noua"]==m["stornare_noua_sursa"]
                and m["jurnal_z"]==m["jurnal_z_sursa"] and m["jurnal_z"].casefold()!="diverse"
                and identic(m["facturi_ciorna"],m["iduri_blocaj"]) and m["in_coada"] is False)
    if caz=="FISC.5":
        return (m["factura"]=="F1A 13" and m["bon"]=="0002" and m["data_bon"]=="2026-10-22"
                and m["vanzari_z"]==1 and m["vanzari_factura_d300"]==m["note_factura"]==0
                and m["fara_nota_d406"] is False and m["de_preluat"] is False and m["contare_refuzata"] is True
                and bool(m["explicatie_contare"]) and "bon" in m["text_fisa"].casefold())
    if caz=="FISC.6":
        return identic(m["deschise_eligibile"],m["optiuni"]) and not (set(m["incasate"]+m["pe_bon"]) & set(m["optiuni"])) and "F1A 13" in m["pe_bon"]
    if caz=="FISC.7":
        stari=set()
        for r in m["comparatii"]:
            stari.add(r["culoare"])
            if r["culoare"]=="gri":
                if not r["motiv_indisponibil"].strip(): return False
                continue
            a,b=bani(r["declaratie_sursa"]),bani(r["contabilitate_sursa"])
            if (bani(r["declaratie_ui"]),bani(r["contabilitate_ui"]))!=(a,b) or r["culoare"]!=("verde" if a==b else "roșu"): return False
            if a!=b and (not identic(r["iduri_note"],r["linkuri_deschise"]) or sum(map(bani,r["sume_note"]))!=a-b): return False
        return stari=={"gri","verde","roșu"} and {"D112","D300"}<={r["tip"] for r in m["comparatii"]}
    if caz=="FISC.8":
        return (identic(m["luni_eligibile"],m["luni_ui"]) and min(m["luni_ui"])>=m["prima_luna"]
                and bool(m["text_d390_sursa"]) and m["text_d390_sursa"]==m["text_d390_ui"] and m["aparitii_diferenta_tva"]==1)
    if caz=="STOC.1":
        return (bani(m["stoc_la_data"])==0 and bani(m["iesire_ceruta"])==150 and m["refuzata"] is True
                and bani(m["disponibil_afisat"])==0 and m["iduri_dupa_refuz"]==m["iduri_inainte"] and m["status_fisa"]==200
                and m["id_istoric_eronat"] in m["iduri_semnalate"] and m["anulare_din_ui"] is True
                and identic(m["miscari_sursa"],m["miscari_fisa"]) and identic(m["miscari_sursa"],m["miscari_borderou"])
                and lista(m["articole_dupa"]) and m["confirmare_salvare"].strip()!="")
    if caz=="STOC.2":
        return (all(m["ubl"][k] and m["ubl"][k]==m["ui"][k] for k in ("scadenta","cumparator","um_linii"))
                and bani(m["transport_ubl"])>0 and bani(m["cost_repartizat"])+bani(m["transport_pe_cont"])==bani(m["transport_ubl"])
                and m["articole_transport_noi"]==0 and m["pasi"].index("alegere NIR")<m["pasi"].index("confirmare"))
    if caz=="STOC.3":
        return (m["titlu"]==f'Stornare factura {m["serie"]} nr. {m["numar"]} din {date.fromisoformat(m["data_original"]).strftime("%d.%m.%Y")}'
                and m["ordine_validari"]==["original","stornare"] and m["refuz_ordine_inversa"] is True and m["stari_dupa"]==["validată","validată"] and m["inainte_refuz"]==m["dupa_refuz"] and len(m["dupa_refuz"])==2)
    if caz=="STOC.4":
        return (bani(m["sold_371_sursa"])!=0 and m["finalizat_fara_metoda"] is False and bool(m["metoda_aleasa"])
                and m["metoda_aleasa"]==m["metoda_persistata"] and bani(m["sold_371_dupa"])==bani(m["sold_371_sursa"]))
    if caz=="STOC.5":
        return (set(m["facturi_fara_scadenta"])=={66,71} and m["numar_fara_scadenta"]==2 and m["fb7_fara_scadenta"] is True
                and m["mesaje_nu_e_cazul"]==1 and m["alerte_rosii_firma_fara_sold"]==0)
    if caz=="STOC.6":
        return (m["ciorna_reluata"] is True and m["intrebare_reafisata"] is True and m["emiteri_inainte_de_raspuns"]==0
                and m["miscari_inainte_de_raspuns"]==0 and m["miscari_dupa_da"]==1 and m["miscari_dupa_nu"]==0)
    if caz=="FINAL.1":
        asteptat = {"fara_potrivire": 4, "comision_627_5121": 1}
        return (m["mesaj"] == m["randuri"] == asteptat
                and set(m["cip_inainte"]) == set(m["cip_dupa"]) == set(asteptat)
                and all(m["cip_dupa"][k] - m["cip_inainte"][k] == n for k, n in asteptat.items())
                and m["cip_dupa_redeschidere"] == m["cip_dupa"])
    if caz=="FINAL.2":
        return (all(re.fullmatch("[0-9a-f]{64}",m[k]) for k in ("sha_import","sha_reimport"))
                and m["sha_import"] != m["sha_reimport"] and m["formate"] == ["csv","xlsx"]
                and len(m["miscari_csv"]) == len(m["miscari_xlsx"]) == 5
                and sorted(m["miscari_csv"]) == sorted(m["miscari_xlsx"])
                and 200 <= m["status_reimport"] < 300 and m["erori_incarcare"] == []
                and lista(m["linii_inainte"]) and m["linii_dupa"]==m["linii_inainte"] and m["linii_ui"]==m["linii_inainte"]
                and "nicio linie nouă" in m["mesaj"].casefold())
    if caz=="FINAL.3":
        return (m["nume_cautat"] and m["id_gasit"]==m["id_partener"] and m["nume_casa"]==m["nume_registru"]
                and "sold" in m["text_chitanta"].casefold() and "factura sold" not in m["text_chitanta"].casefold())
    if caz=="FINAL.4":
        return (m["id_creat"] and m["id_creat"]==m["id_gasit"]==m["id_editat"]==m["id_sters"] and m["fise_dupa_stergere"]==0
                and len(set(m["registre_accesate"]))==1 and len(m["registre_accesate"])==3 and m["salveaza_pe_rand_client"] is True and m["salveaza_pe_rand_furnizor"] is True)
    if caz=="FINAL.5":
        return (bool(m["adresa_cumparator"].strip()) and m["adresa_cumparator"] in m["text_pdf"]
                and m["nume_descarcat"].lower().endswith(".pdf") and re.search(re.escape(m["serie"])+r"[\s._-]*(?:nr[. _-]*)?0*"+str(int(m["numar"]))+r"(?!\d)",m["nume_descarcat"],re.I) is not None)
    if caz=="FINAL.6":
        return (m["nr_produse_inainte"]==m["nr_produse_dupa"] and m["dublura_semnalata"] is True and m["temei_pe_rand_vizibil"] is True
                and m["ai_sursa_corectata"] and m["temei_citit_pe_rand"]==m["ai_sursa_corectata"])
    if caz=="FINAL.7":
        return (m["evenimente_ui"]==m["jurnal"] and {"blocare","deblocare"}<={r["actiune"] for r in m["jurnal"]}
                and all(all(r[k] for k in ("actor","moment","motiv")) for r in m["jurnal"]))
    if caz=="FINAL.8":
        return bool(m["emitent_certificat"].strip()) and m["emitent_ui"]==m["emitent_certificat"]
    if caz=="FINAL.9":
        return bool(m["divergente_sursa"]) and m["importuri_deschise_pe_divergenta"]==m["divergente_sursa"] and m["firma_dupa"]==m["firma_sursa"]
    if caz=="FINAL.10a":
        return (m["data_nota"]=="2026-07-15" and m["data_nota"]<m["data_preluare"] and m["avertisment_inainte_de_scriere"] is True and m["avertisment_data_admisa"] is False)
    if caz=="FINAL.10b":
        return (m["firma"]=="F5" and m["data"]=="2026-10-20" and m["platitoare"] is False and bani(m["suma_document"])==126
                and bani(m["debit_4426"])==0 and bani(m["cheltuiala_din_suma"])==126 and bani(m["total_debit"])==bani(m["total_credit"]))
    if caz=="FINAL.10c":
        return (len(m["randuri_sursa"])==len(m["randuri_importate"])==5 and m["randuri_importate"]==m["randuri_sursa"]
                and len({r["id_linie_extras"] for r in m["randuri_sursa"]})==5 and all(date.fromisoformat(r["data"]) and bani(r["suma"]).is_finite() for r in m["randuri_sursa"]))
    raise ValueError("Caz necunoscut: "+caz)

def verifica(f):
    manifest=json.loads(f.read_text())
    dorite={(i,z) for i in IDS for z in DIM}
    vazute=set()
    rele=[]
    root=f.resolve().parent
    for r in manifest:
        cheie=(r["id"],r["rezolutie"])
        if cheie not in dorite or cheie in vazute:
            raise ValueError(f"Probă duplicată sau necunoscută: {cheie}")
        vazute.add(cheie)
        surse=[]
        for nume in ("produs","sursa"):
            doc=r[nume]
            cale=Path(doc["cale"])
            martor=(root/cale).resolve()
            if (cale.is_absolute() or not martor.is_relative_to(root) or martor==f.resolve() or not martor.is_file()
                or not martor.stat().st_size or hashlib.sha256(martor.read_bytes()).hexdigest()!=doc["sha256"] or not doc["localizare"].strip()):
                raise ValueError(f"Martor invalid: {cheie} {nume}")
            surse.append((martor,doc["localizare"]))
        if r["id"] == "FINAL.10c" and r["sursa"]["sha256"] != "3b5f1de7d0a5496fcc25d0f8e54619ac3ca7962e96917e4a2d84ae0cbd57a9af":
            raise ValueError("FINAL.10c: lipsește originalul bancar din importul 9")
        if surse[0]==surse[1]:
            raise ValueError(f"Produs și referință identice: {cheie}")
        if not judeca(r["id"],r["masuri"]):
            rele.append(cheie)
    if vazute!=dorite:
        raise ValueError(f"Probe lipsă: {sorted(dorite-vazute)}")
    return rele

if __name__=="__main__":
    abateri=verifica(Path(sys.argv[1]))
    print(json.dumps(abateri,ensure_ascii=False))
    raise SystemExit(int(bool(abateri)))

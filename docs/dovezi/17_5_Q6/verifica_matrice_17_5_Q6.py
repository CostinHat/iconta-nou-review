"""python verifica_matrice_17_5_Q6.py MATRICE.tsv INDEX.tsv SHA_E SHA_C DIRECTOR"""
from pathlib import Path
import csv
import hashlib
import json
import re
import sys
from xml.etree import ElementTree as ET

# Preflight poate porni interpretorul în mod izolat, din alt director.
sys.path.insert(0,str(Path(__file__).resolve().parent))
from oracol_reparatii_17_5_Q6 import judeca
from citeste_rezultat_Q6 import incarca_test, verifica_png

def tabel(path):
    with path.open(encoding="utf-8",newline="") as f:return list(csv.DictReader(f,delimiter="\t"))

def valoare_original(camp, regula, cale):
    """Citește o valoare din artefactul de intrare. Niciun extractor nu execută cod primit."""
    tip = regula["format"]
    if tip == "ubl_factura":
        if camp != "factura_sursa":
            raise ValueError("Extractor UBL pe alt câmp")
        root = ET.parse(cale).getroot()
        ns = {"b":"urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
              "a":"urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"}
        cai = {"id":"b:ID","moneda":"b:DocumentCurrencyCode","total":"a:LegalMonetaryTotal/b:TaxInclusiveAmount",
               "furnizor":"a:AccountingSupplierParty/a:Party/a:PartyLegalEntity/b:RegistrationName"}
        valori = {n:(root.findtext(xpath, namespaces=ns) or "").strip() for n,xpath in cai.items()}
        if not all(valori.values()):
            raise ValueError("Factură UBL incompletă")
        return valori
    if tip not in {"json","coduri_blocaje","are_reevaluare"}:
        raise ValueError("Format de extracție necunoscut")
    data = json.loads(cale.read_text(encoding="utf-8"))
    if tip in {"coduri_blocaje", "are_reevaluare"}:
        cale_blocaje = ["controale", "blocaje"]
        if regula.get("cale") != cale_blocaje:
            raise ValueError("Calea F025-S trebuie să fie controale.blocaje")
        controale = data.get("controale") if isinstance(data, dict) else None
        blocaje = controale.get("blocaje") if isinstance(controale, dict) else None
        if not isinstance(blocaje, list):
            raise ValueError("Originalul trebuie să conțină lista controale.blocaje")
        coduri = []
        for bloc in blocaje:
            cod = bloc.get("cod") if isinstance(bloc, dict) else None
            if not isinstance(cod, str) or not cod.strip():
                raise ValueError("Cod de blocaj invalid în controale.blocaje")
            coduri.append(cod)
        return coduri if tip == "coduri_blocaje" else "REEVALUARE_VALUTA" in coduri
    for token in regula["cale"]:
        if isinstance(data,list) and type(token) is int and token >= 0:
            data = data[token]
        elif isinstance(data,dict) and isinstance(token,str):
            data = data[token]
        else:
            raise ValueError("Cale de extracție invalidă")
    return data


def verifica_originalele(sursa, masuri, chei, scenariu, artifact, excluse):
    reguli = sursa["extrageri"]
    if set(reguli) != set(chei):
        raise ValueError("Trebuie declarată extracția fiecărei ancore")
    for camp in chei:
        regula = reguli[camp]
        sursa_camp = regula if "original" in regula else sursa
        p = artifact(sursa_camp,"original")
        if p in excluse:
            raise ValueError("Originalul este o ieșire a verificatorului")
        mod_impus = {("primita","factura_sursa"):"ubl_factura",("f025s","coduri_blocaje_sursa"):"coduri_blocaje",
                     ("f025s","blocaj"):"are_reevaluare"}.get((scenariu,camp))
        if mod_impus and regula["format"] != mod_impus:
            raise ValueError("Se cere extractorul "+mod_impus)
        if mod_impus in {"coduri_blocaje","are_reevaluare"} and p != artifact(sursa,"original"):
            raise ValueError("Starea se citește din răspunsul original al controalelor lunii")
        valoare = valoare_original(camp, regula, p)
        # JSON canonical keeps booleans distinct from 0/1, including nested records.
        canon = lambda x: json.dumps(x,sort_keys=True,ensure_ascii=False,allow_nan=False)
        if camp not in masuri or canon(valoare) != canon(sursa["valori"][camp]) or canon(valoare) != canon(masuri[camp]):
            raise ValueError("Măsura nu corespunde sursei: "+camp)


def verificare(matrice,index,e,c,root):
    if e!="aca6f8287825f9e4352e8feb14f93b8d28ba198d" or not re.fullmatch("[0-9a-f]{40}",c) or e==c:raise ValueError("Pereche E/C lipsă")
    expected={(r["scenariu"],cas,dim) for r in tabel(matrice) for cas in r["cazuri"].split(",") for dim in r["rezolutii"].split(",")}
    nume_sursa = Path(__file__).with_name("chei_sursa_17_5_Q6.tsv")
    ancore = {r["scenariu"]:r["chei_din_sursa"].split() for r in tabel(nume_sursa)}
    rows=tabel(index)
    def artifact(r,k):
        p=(root/r[k]).resolve()
        if Path(r[k]).is_absolute() or not p.is_relative_to(root.resolve()) or not p.is_file():raise ValueError("Lipsă "+k)
        data=p.read_bytes()
        if not data or hashlib.sha256(data).hexdigest()!=r["sha256_"+k]:raise ValueError("SHA "+k)
        return p
    seen={};states={"reparat","trece pe E","deschis","neexecutat","nejudecat"}
    for r in rows:
        key=r["scenariu"],r["caz"],r["rezolutie"]
        if key not in expected or key in seen or r["stare"] not in states:raise ValueError(str(key))
        seen[key]=r["stare"]
        if r["stare"] in {"deschis","neexecutat","nejudecat"}:
            if not r["motiv"].strip():raise ValueError("Motiv lipsă "+str(key))
            continue
        result=[]
        for phase,commit in (("E",e),("C",c)):
            if r["commit_"+phase]!=commit:raise ValueError("Commit "+phase)
            path=artifact(r,"masuri_"+phase); src=artifact(r,"sursa_"+phase)
            if path==src or path.read_bytes()==src.read_bytes():raise ValueError("Sursa trebuie să fie distinctă")
            png=artifact(r,"captura_"+phase);dim=tuple(map(int,key[2].split("x")));verifica_png(png,dim)
            m=json.loads(path.read_text())
            sursa = json.loads(src.read_text())
            if (sursa["commit"],sursa["scenariu"],sursa["caz"],sursa["rezolutie"]) != (commit,*key):
                raise ValueError("Sursa este de la altă operație")
            brut = artifact(sursa,"original")
            if brut in {path,src,png} or not sursa["localizare"].strip():
                raise ValueError("Lipsește originalul independent identificabil")
            verifica_originalele(sursa,m,ancore[key[0]],key[0],artifact,{path,src,png})
            if key[0] in ("e.1","e.2"):
                ok=incarca_test().rezultat(key[0],m)
            else:
                if key[0]=="control" and (m["viewport"]!=list(dim) or m["firma_caz"]!=key[1]):raise ValueError("Altă firmă sau rezoluție")
                if key[0]=="f025s":
                    coduri=m["coduri_blocaje_sursa"]
                    exista="REEVALUARE_VALUTA" in coduri
                    if m["viewport"]!=list(dim) or m["blocaj"] is not exista or exista!=(key[1]!="fara_blocaj"):
                        raise ValueError("Stare sau rezoluție F025-S diferită")
                    if key[1]=="cu_blocaj" and coduri!=["REEVALUARE_VALUTA"]:
                        raise ValueError("Cazul cu blocaj unic nu a fost pregătit")
                    if key[1]=="cu_blocaj_anterior" and (coduri.count("REEVALUARE_VALUTA")!=1 or coduri.index("REEVALUARE_VALUTA")==0):
                        raise ValueError("Lipsește un blocaj anterior reevaluării")
                if key[0]=="istoric" and m["cale"]!=key[1]:raise ValueError("Altă cale")
                if key[0]=="cota" and (m["descriere_initiala"]=="")!=(key[1]=="gol"):raise ValueError("Altă descriere")
                if key[0]=="f085" and m["cont"]!=key[1]:raise ValueError("Alt cont")
                if key[0]=="f043s" and m["permis_sursa"]!=(key[1]=="permis"):raise ValueError("Alt drept")
                ok=judeca(key[0],m)
            result.append(bool(ok))
        if result!=[r["stare"]=="trece pe E",True]:raise ValueError("Verdict fără suport: "+str(key))
    if seen.keys()!=expected:raise ValueError("Cazuri lipsă: "+str(sorted(expected-seen.keys())))
    return {k:sum(v==k for v in seen.values()) for k in sorted(states)}
def proba():
    # Exercițiu end-to-end cu fișiere temporare. Fără server, biblioteci externe sau registru.
    import csv
    import struct
    import tempfile
    import zlib

    def scrie_tsv(p, rows, campuri):
        with p.open("w",newline="",encoding="utf-8") as out:
            w=csv.DictWriter(out,campuri,delimiter="\t")
            w.writeheader()
            w.writerows(rows)

    def chunk(t, b):
        return struct.pack(">I",len(b))+t+b+struct.pack(">I",zlib.crc32(t+b))

    def respinge(fn, motiv):
        try:
            fn()
        except ValueError as err:
            if motiv not in str(err):
                raise
        else:
            raise RuntimeError("Verificarea a acceptat: "+motiv)

    with tempfile.TemporaryDirectory(prefix="q6_matrice_") as tmp:
        rad=Path(tmp)
        mtx,idx=rad/"matrice.tsv",rad/"index.tsv"
        loc="603x590"
        k=dict(scenariu="datorate",caz="unic",rezolutie=loc,stare="reparat",motiv="")
        scrie_tsv(mtx,[dict(scenariu="datorate",cazuri="unic",rezolutii=loc)],["scenariu","cazuri","rezolutii"])
        E="aca6f8287825f9e4352e8feb14f93b8d28ba198d"
        C="c"*40
        def digest(p):
            return hashlib.sha256(p.read_bytes()).hexdigest()
        def note(p,obj):
            p.write_text(json.dumps(obj),encoding="utf-8")
        def scrie_idx(rows):
            scrie_tsv(idx,rows,list(k))
        def aplica():
            return verificare(mtx,idx,E,C,rad)
        for faza,commit in (("E",E),("C",C)):
            sursa=rad/(faza+"-s.json")
            masuri=rad/(faza+"-m.json")
            original=rad/(faza+"-o.json")
            imagine=rad/(faza+".png")
            ancora={"id_ultim_sursa":"d300","perioada_sursa":"10/2026"}
            note(original,{"date":ancora})
            meta=dict(commit=commit,scenariu="datorate",caz="unic",rezolutie=loc,original=original.name,sha256_original=digest(original),
                      localizare="date",valori=ancora,extrageri={a:{"format":"json","cale":["date",a]} for a in ancora})
            note(sursa,meta)
            note(masuri,dict(ancora,id_selectat="d300",perioada_destinatie="10/2026",scrolluri_lista=0,scrolluri_traseu=2 if faza=="E" else 1))
            w,h=603,590
            imagine.write_bytes(b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",struct.pack(">IIBBBBB",w,h,8,0,0,0,0))+
                                chunk(b"IDAT",zlib.compress(bytes((w+1)*h)))+chunk(b"IEND",b""))
            k["commit_"+faza]=commit
            for col,p in (("sursa",sursa),("masuri",masuri),("captura",imagine)):
                k[col+"_"+faza]=p.name
                k["sha256_"+col+"_"+faza]=digest(p)
        scrie_idx([k])
        if aplica()["reparat"]!=1:
            raise RuntimeError("Martorul pozitiv nu a trecut")
        scrie_idx([])
        respinge(aplica,"Cazuri lipsă")
        # Schimbăm împreună măsura și transcrierea și refacem ambele hashuri.
        # Originalul brut păstrat trebuie să fie suficient pentru refuz.
        for col in ("masuri","sursa"):
            p=rad/k[col+"_C"];d=json.loads(p.read_text())
            (d["valori"] if col=="sursa" else d)["id_ultim_sursa"]="alt"
            note(p,d);k["sha256_"+col+"_C"]=digest(p)
        scrie_idx([k])
        respinge(aplica,"nu corespunde sursei")
    print("PROBE OK — martor pozitiv, combinație lipsă și transcriere contrazisă de original")


if __name__=="__main__":
    if sys.argv[1:]==["--proba"]:
        proba()
        raise SystemExit(0)
    if len(sys.argv)!=6:raise SystemExit(__doc__)
    a,b,e,c,r=sys.argv[1:];print(json.dumps(verificare(Path(a),Path(b),e,c,Path(r)),ensure_ascii=False))

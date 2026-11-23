"""python scor_17_5_Q6.py intrare_Q4.csv iesire_C.csv probe.tsv SHA_C director_dovezi index_matrice.tsv"""
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

CRIT=("Funcțional","Aspect","Design","Simplitate","Conformitate","Stabilitate")
DOMENIU=set("F019 F022 F025 F026 F028 F031 F034 F035 F043 F045 F046 F070 F078 F080 F085 F126 F162 F169 F172 F176 F179 X02".split())
INTRARE="e189b4eae9dbb5615a71897be26b77d682f71c76064636a786d962277f32d535"
def citeste(p):
    with p.open(encoding="utf-8-sig",newline="") as f:
        rows=list(csv.DictReader(f))
    val={r["Cod"]:tuple(r[c].strip() for c in CRIT) for r in rows}
    if len(rows)!=45 or len(val)!=45 or "F050" in val or any(x not in {"0","1","-"} for v in val.values() for x in v):
        raise ValueError("Inventar Pilot invalid")
    return val

def calculeaza(intrare,iesire,probe,commit,rad):
    if hashlib.sha256(intrare.read_bytes()).hexdigest()!=INTRARE or not re.fullmatch(r"[0-9a-f]{40}",commit):
        raise ValueError("Identitatea bazei sau candidatului")
    a,b=citeste(intrare),citeste(iesire)
    if set(a)!=set(b):raise ValueError("Coduri schimbate")
    ok=lambda d:{cod for cod,v in d.items() if v==("1",)*6}
    initial,final=ok(a),ok(b)
    if initial!={"F081","F089"}:raise ValueError("Bilanț de intrare neașteptat")
    vazut={}
    with probe.open(encoding="utf-8",newline="") as f:
        for r in csv.DictReader(f,delimiter="\t"):
            k=(r["cod"],r["criteriu"],r["rezolutie"])
            if k in vazut or k[0] not in b or k[1] not in CRIT or k[2] not in {"1366x768","603x590"}:
                raise ValueError(f"Cheie de probă invalidă {k}")
            if r["commit"]!=commit or r["valoare"] not in {"0","1"} or b[k[0]][CRIT.index(k[1])]=="-":
                raise ValueError(f"Scor sau commit neconcordant {k}")
            for camp in ("sursa","observatie"):
                rel=Path(r[camp]); p=(rad/rel).resolve()
                if rel.is_absolute() or not p.is_relative_to(rad.resolve()) or not p.is_file() or p.stat().st_size==0:
                    raise ValueError(f"Martor absent {k}")
                if hashlib.sha256(p.read_bytes()).hexdigest()!=r["sha256_"+camp]:raise ValueError(f"SHA martor {k}")
            if r["sha256_sursa"]==r["sha256_observatie"] or not r["rezultat_masurat"].strip():raise ValueError(f"Independența martorului {k}")
            vazut[k]=r["valoare"]
    for cod,vals in b.items():
        for j,criteriu in enumerate(CRIT):
            masurat=any((cod,criteriu,size) in vazut for size in ("1366x768","603x590"))
            if vals[j]!="-" and (cod in final or vals[j]!=a[cod][j] or masurat):
                for size in ("1366x768","603x590"):
                    if (cod,criteriu,size) not in vazut:raise ValueError(f"Probă lipsă {cod} {criteriu} {size}")
                agregat=min(vazut[cod,criteriu,size] for size in ("1366x768","603x590"))
                if vals[j]!=agregat:raise ValueError(f"Valoarea agregată diferă de probe: {cod} {criteriu}")
    noi=final-initial
    return {"baza":2,"dupa":len(final),"numitor":45,"noi":sorted(noi),"redeschise_sau_pierdute":sorted(initial-final),"net":len(final)-2,
            "redeschise":sorted(k for k in initial-final if "0" in b[k]),
            "pierdute_din_acoperire":sorted(k for k in initial-final if "0" not in b[k]),
            "criterii_masurate":sum(v!="-" for row in b.values() for v in row),
            "noi_in_obiectiv":sorted(noi&DOMENIU),"tinta_atinsa":len(noi&DOMENIU)>=3 and initial<=final and len(final)>=5}
if __name__=="__main__":
    if len(sys.argv)!=7:raise SystemExit(__doc__)
    from verifica_matrice_17_5_Q6 import verificare, tabel
    a,b,t,c,r,idx=sys.argv[1:]
    norm=Path(__file__).resolve().parent
    matrice=norm/"matrice_probe_17_5_Q6.tsv"
    verificare(matrice,Path(idx),"aca6f8287825f9e4352e8feb14f93b8d28ba198d",c,Path(r))
    v=calculeaza(Path(a),Path(b),Path(t),c,Path(r))
    ids={row["id"]:row["coduri"].split() for row in tabel(norm/"acceptare_17_5_Q6.tsv")}
    coduri={row["scenariu"]:ids[row["id"]] for row in tabel(matrice)}
    coduri.update(f078=["F078"],f080=["F080"])
    for row in tabel(Path(idx)):
        if row["stare"] in {"deschis","neexecutat","nejudecat"} and set(coduri[row["scenariu"]]).intersection(v["noi"]):
            raise ValueError("Închidere Pilot incompatibilă cu matricea: "+row["scenariu"])
    print(json.dumps(v,ensure_ascii=False,indent=2));raise SystemExit(0 if v["tinta_atinsa"] else 1)

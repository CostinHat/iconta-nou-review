# BRIEF_CODE_PUNTE_STOC — factura -> stoc prin poarta obligatorie

## Decizia (DECIZII.md — reciteste intai intrarea "Punte factura -> stoc")
Poarta obligatorie la emitere: "Pleaca marfa acum? DA/NU". DA -> descarca gestiunea pe
liniile cu articol. NU -> factura pur fiscala, stoc neatins. Avizul ramane pentru livrare
decuplata. Structura: articol_id pe factura_linii + factura_id pe miscari_stoc. Refoloseste
iesire() existent + rulaje_interval.

## ACEASTA TEMA ATINGE EMITEREA LIVE — cea mai multa grija
Emiterea e fluxul central al produsului. Regula supraordonata: cine emite factura FARA
marfa (NU, sau servicii) trebuie sa aiba fluxul EXACT ca azi, neatins. Poarta e ADITIVA.
Daca la un moment dat vezi ca modifici comportamentul emiterii pentru cazul "fara marfa",
STOP - ai iesit din scop.

## Autonomie
Executie completa fara opriri pe implementare, DAR aceasta tema are mai multe porti decat
de obicei (schema + cod LIVE). Porti unde STOP si intrebi:
- orice schimbare care ar afecta emiterea pentru facturile FARA marfa (NU)
- orice regula Design System inexistenta pentru poarta la emitere (ecran-poarta nou)
- orice ambiguitate fiscala pe descarcare (ce nota contabila, ce cont) neconfirmabila la sursa

## FAZA 0 — verifica la sursa inainte de schema (regula de aur)
1. Fluxul de emitere azi: POST /facturi/emite -> creeaza_factura (facturi_api.py:48).
   Citeste-l COMPLET inainte de a-l atinge. Unde se emite, ce corp, ce se intampla dupa.
2. iesire() / /stocuri/iesire (main.py:5050, stocuri_cv_api.py): ce semnatura are, ce
   corp cere (articol_id, data, cantitate), ce nota produce. Puntea il CHEAMA - trebuie
   sa stii exact cum.
3. factura_linii: DDL actual (fara articol_id confirmat). miscari_stoc: DDL actual (fara
   factura_id confirmat, are articol_id, inregistrare_id, document).
4. Configurare emitere existenta (F153 ecran-poarta numerotare+regim TVA, regim-tva ruta):
   pattern-ul de ecran-poarta la emitere exista deja. Poarta "pleaca marfa" e acelasi
   pattern - refoloseste-l, nu inventa altul.

## FAZA 1 — schema (STOP intai daca gasesti alt design mai bun; altfel executa)
- articol_id pe factura_linii: NULL-able (liniile de serviciu raman NULL). FK spre
  nomenclatorul de articole CV. Migrare in tenant_template.sql + toate schemele existente.
- factura_id pe miscari_stoc: NULL-able (miscarile manuale existente raman NULL). FK spre
  facturi. Migrare idem.
- Nu strica datele existente: coloane noi NULL-able, nimic retroactiv.

## FAZA 2 — poarta la emitere
- La emitere factura (nu proforma, nu aviz): daca firma e CV (are gestiune cantitativa)
  SI factura are cel putin o linie cu articol de stoc -> poarta OBLIGATORIE
  "Pleaca marfa acum? DA / NU". Fara raspuns, nu se emite.
- Firma GV sau factura fara linii de stoc -> NU se afiseaza poarta (nimic de descarcat).
- DA -> dupa emitere, pentru fiecare linie cu articol_id: cheama iesire() existent cu
  articol+cantitate+data facturii, seteaza factura_id pe miscarea generata. Descarcarea
  = nota ciorna (patru-ochi intact, ca restul stocului CV). Liniile fara articol: ignora.
- NU -> emitere normala, stoc neatins. Flux IDENTIC cu azi.

## FAZA 3 — articol pe linia de factura (UI emitere)
- La adaugarea unei linii de factura, la firma CV: camp optional de selectare articol din
  nomenclator (F141 barcode/cautare exista - refoloseste). Linia fara articol = serviciu.
- Cota TVA vine tot din nomenclator (F023), ca azi. articol_id doar leaga linia de stoc.

## FAZA 4 — profit-pe-produs (raportul care era decizie deschisa, F144)
- Acum JOIN-ul exista: factura_linii.articol_id (venit) <-> miscari_stoc pe factura_id
  la CMP (cost). Profit pe produs = venit - cost, pe articol.
- Refoloseste rulaje_interval / patternul de citire fapte de la semafor B (c377746).
- LIMITA declarata in raport: GV ramane GRI (cost pe articol nu exista). Doar CV are profit.
- F144 se actualizeaza din "decizie deschisa" in LIVE pentru CV.

## Reguli permanente (CLAUDE.md)
- Verificare functionala reala pe tenant_002 (CV): emite factura cu DA -> confirma
  miscari_stoc generata cu factura_id + stoc scazut; emite cu NU -> confirma stoc neatins;
  emite factura de serviciu -> confirma ca poarta nu apare. Nu py_compile.
- Descarcarea = nota ciorna status validare intact (nu se sare patru-ochi).
- Rotunjire Decimal+ROUND_HALF_UP. Diacritice: afisat CU, cod FARA.
- Design System: poarta la emitere = ecran-poarta. Citeste regula pattern-ului existent
  (Configurare emitere F153). Daca lipseste regula pentru poarta noua, STOP.
- verificator TOTAL 0. FUNCTIONALITATI.csv: F144 -> LIVE (CV), pozitie noua pentru punte
  daca e cazul, ACELASI commit. DECIZII.md: actualizeaza intrarea ca livrata + limita GV.
- Restart: sudo systemctl restart iconta-nou.

## Ce raportezi
Commit(uri), ce ai gasit in Faza 0, exemplu functional pe tenant_002 (DA / NU / serviciu),
un exemplu de profit-pe-produs pe un articol real, si limita GV declarata. Daca vreo poarta
s-a atins (ai avut nevoie de decizie), spune care si de ce.

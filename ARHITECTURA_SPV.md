# ARHITECTURA SPV / ANAF — decizii si temeiuri
Stabilit 17.07.2026. Verificat la sursa oficiala. Fisier normativ: se suprascrie, nu se acumuleaza copii datate.

## DECIZIA 1 — modelul certificatului (17.07.2026)
iConta = APLICATIE inrolata la ANAF, cu UN SINGUR Client ID + Client Secret.
Fiecare cabinet autorizeaza cu certificatul LUI. iConta NU e imputernicit, NU detine certificat.
Temei: procedura oficiala ANAF - dezvoltatorul e identificat printr-un client app id;
utilizatorii sunt identificati prin serialul certificatului digital calificat.
Token-urile sunt generate pentru certificat si identifica utilizatorul, nu aplicatia.
Coerent cu produsul: iConta e platforma de cabinet; contabilul depune, iConta e unealta.

## LINIA DE DESPARTIRE (temei tehnic, nu preferinta)
| Serviciu                          | OAuth | Server-side |
|-----------------------------------|-------|-------------|
| e-Factura, e-Transport            | DA    | DA          |
| Mesaje SPV, rapoarte, declaratii  | NU    | NU          |
OAuth exista tocmai ca aplicatiile web sa NU aiba nevoie de certificat pe server:
contabilul autorizeaza O DATA in browserul lui, cu stickul introdus; serverul primeste
refresh token 365 zile si lucreaza fara certificat.

## BLOCANTUL CERTIFICATULUI (de ce SPVWS2 nu se poate server-side)
SPVWS2 (webserviced.anaf.ro) se autentifica prin mTLS cu certificat calificat LOCAL:
- token USB -> PKCS#11, driver local (clientul oficial MfpAnaf/ClientSPV, Sign.java:
  KeyStore.Builder.newInstance("PKCS11", ...))
- cloud (certSIGN Paperless) -> cere aplicatia vToken pe Windows/macOS
Sub eIDAS cheia privata NU paraseste dispozitivul calificat. Nu ajunge pe serverul Linux.
Nu e limitare ANAF, e arhitectura QSCD. Nu exista portita.
LIMITA DECLARATA: verificat certSIGN (1 din 4 furnizori). DigiSign/Trans Sped/AlfaTrust
sunt sub aceeasi arhitectura QSCD, dar documentatia lor nu a fost citita.

## PARAMETRI OAUTH (verificati la sursa 17.07.2026)
Sursa: static.anaf.ro/static/10/Anaf/Informatii_R/API/Oauth_procedura_inregistrare_aplicatii_portal_ANAF.pdf
- Authorize: https://logincert.anaf.ro/anaf-oauth2/v1/authorize
- Token:     https://logincert.anaf.ro/anaf-oauth2/v1/token
- Grant type: authorization_code | Client auth: Basic Auth header
- token_content_type=jwt : pe QUERY la authorize SI in BODY la token
- ACCESS TOKEN: 90 zile (129600 min) | REFRESH TOKEN: 365 zile (525600 min)
- Fereastra de obtinere token: 60 secunde, apoi se reseteaza conexiunea
- Limita: 1000 apeluri/minut -> 429 Too Many Requests | 403 = request neautorizat
- Nomenclator servicii la inrolare: DOAR e-Factura si e-Transport (+ TestOauth)
- Certificatul cabinetului trebuie sa aiba drept SPV PJ
  (reprezentant legal / reprezentant desemnat / imputernicit)
- Test: https://api.anaf.ro/TestOauth/jaxrs/hello?name=X (orice token valid il poate apela)

## DE DECIS INAINTE DE INROLARE (nu la implementare)
- CALLBACK URL: propus https://iconta.eu/anaf/oauth/callback — unul singur, ambele servicii.
  Se declara la inrolare, greu de schimbat ulterior.
- Client Secret -> ~/.iconta/api_keys.env (NU in git)
- Un certificat acoperă MAI MULTE firme. Modelul NU e token-per-firma:
  spv_token per accounting_firm_id + lista de CUI-uri acoperite, DESCOPERITA nu presupusa.
- Refresh la 90 zile = cron obligatoriu. Fara el, cabinetul reface autorizarea cu stickul.
  Cu refresh 365 zile, cabinetul care nu intra un an pierde accesul oricum.

## SPVWS2 — ce ofera (blocat de certificat, consemnat pentru cand/daca se deschide)
Client oficial: github.com/MfpAnaf/ClientSPV (MIT). Ultimul jurnal de modificari: 06.11.2018.
- /SPVWS2/rest/listaMesaje?zile=N[&cif=X]  -> id, detalii, cif, data_creare, tip (ex. RECIPISA)
  Raspunsul contine si lista de CUI-uri acoperite de certificat + serialul.
- /SPVWS2/rest/descarcare?id=N            -> PDF-ul mesajului
- /SPVWS2/rest/cerere?tip=...&cui=...     -> VECTOR FISCAL, Situatie Sintetica (debite),
  Obligatii de plata, Istoric declaratii, NeconcordanteD112CNP (D112 vs REVISAL),
  NeconcordanteD394, Duplicat Recipisa, Fisa Rol, Bilant anual/semestrial etc.
VALOARE PIERDUTA ODATA CU F128: astea erau materia prima pentru verificatoare incrucisate
cu sursa de adevar la ANAF (nu doar in baza proprie). Se redeschid impreuna cu F128.
Contact tehnic ANAF: spv.webservice@mfinante.ro
INTREBARE TRIMISA 17.07.2026 catre spv.webservice@mfinante.ro, doua puncte:
  (1) exista/se planifica transmitere declaratii prin WS?  -> deblocheaza F127
  (2) se planifica OAuth pentru SPVWS2?                    -> deblocheaza F128 + rapoartele 'cerere'
Fara raspuns pana la 17.08.2026: F127/F128 raman AMANAT. Raspunsul se consemneaza AICI.

## STARE FUNCTIONALITATI (17.07.2026)
- F126, F160, F121 : temei tehnic confirmat prin OAuth. Se pot construi server-side.
- F127 (transmitere declaratii): AMANAT. Nu exista API. README oficial il listeaza
  la "pentru viitor". De confirmat la spv.webservice@mfinante.ro inainte de RESPINS.
- F128 (monitorizare mesaje SPV): AMANAT. Blocant structural (certificat local).
  Singura cale = agent desktop la cabinet = ALT PRODUS. Se redeschide daca ANAF
  adauga OAuth la SPVWS2.

## ORDINEA DE CONSTRUCTIE
Conectorul SPV se construieste O DATA (OAuth + stocare token + refresh + retry/coada),
apoi F126, F160, F121 sunt apeluri peste el. Cinci pozitii, un singur auth.

# ============================================================
# LECTII DIN CONCURENTA (verificat la sursa 17.07.2026)
# ============================================================
Surse: ajutor.smartbill.ro/article/982, smartbill.ro/e-factura, smartbill.ro/totul-despre-efactura,
certsign.ro (interviu Mircea Capatana). Limita: verificat SmartBill; Oblio/FGO/EasyBill
au acelasi flux dupa documentatia lor publica, dar nu au fost citite in detaliu.

## CONFIRMARE: nu exista cale ascunsa
SmartBill face IDENTIC ce face iConta: aplicatie inrolata o data, utilizatorul autorizeaza
cu certificatul lui, 90 de zile, reinnoire automata care uneori esueaza -> email + reautorizare
manuala. Aceleasi constrangeri ANAF pentru toata lumea.
"SmartBill va putea accesa doar sectiunea e-Factura, nu si alte informatii ale companiei
tale care se regasesc in SPV" -> NICI SMARTBILL NU ARE MESAJE SPV. F128 nu e o gaura
in produsul iConta, e limita platformei ANAF pentru toti jucatorii cloud.

## AVANTAJ STRUCTURAL iCONTA (decurge din decizia model (1))
SmartBill autorizeaza PER FIRMA: fiecare client, cont propriu, autorizare proprie, 90 zile.
Cabinet cu 40 de firme in SmartBill = 40 de autorizari, fiecare la 90 de zile.
iConta autorizeaza PER CABINET: contabilul autorizeaza O DATA, tokenul acopera toate
firmele pe care certificatul lui are drept. UNA, la 90 de zile, si aia automata.
Nu e detaliu tehnic - e argument de vanzare. Vine direct din "platforma de cabinet",
nu "platforma de firma".

## DE APLICAT IN ECRANUL DE CONECTARE (cand se stabileste cu DS - Regula 0)
1. AVERTISMENT 24 DE ORE: dupa inrolarea certificatului in SPV trebuie asteptate 24h
   pana functioneaza (sursa: certSIGN/SmartBill). Fara mesaj explicit, cabinetul incearca
   imediat, primeste eroare si crede ca e vina iConta. Text in ecran, nu in FAQ.
2. LINK DE AUTORIZARE TRIMISIBIL: SmartBill genereaza un link pe care il trimiti celui
   care are certificatul. La iConta contabilul E utilizatorul, deci nu e necesar la baza -
   DAR tiparul e util invers: cabinetul trimite linkul unui client care are certificat propriu.
   De evaluat cand se face ecranul.
3. CERTIFICAT CLOUD = OK pentru autorizare, daca e instalat local prin vToken
   ("versiunea digitala a certificatului, daca este instalata pe calculator, este echivalenta
   cu un certificat pe token"). Deci contabilul cu certificat cloud POATE autoriza iConta.
   Nu confunda cu blocantul SPVWS2 (acolo problema e serverul, nu clientul).

## PENTRU TERMENI SI CONDITII (nu tehnic, dar decurge din arhitectura)
Formularea SmartBill, de folosit ca model: "Trimiterea e-Facturii e obligatia intocmitorului
si nu are nicio legatura cu procesul de autorizare in SPV a contului SmartBill."
Aplicat la iConta: contabilul depune cu certificatul lui, pe firmele lui; iConta e unealta.
Raspunderea pe depunere NU trece la iConta. Modelul (2) ar fi mutat-o.
Firma (SRL) = vehicul comercial (contracte, facturi, GDPR-procesator), NU intra in lantul ANAF.
Contul de dezvoltator OAuth e pe persoana fizica (CNP), nu pe CUI.

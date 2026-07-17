# BRIEF CLAUDE CODE — CONECTORUL SPV (17.07.2026)

## CITESTE INTAI
ARHITECTURA_SPV.md — sectiunea "CONECTORUL SPV". Contine schema completa, fluxul OAuth,
capcana rotatiei refresh, semnatura apel_anaf, ordinea de executie. NU o rescrie, NU o
reinterpreta. Daca ceva de acolo pare gresit -> STOP si spune, nu corecta din proprie initiativa.
Parametrii ANAF (endpointuri, 90/365 zile, limita 1000/min) sunt VERIFICATI LA SURSA OFICIALA.
Nu-i cauta din nou, nu-i "corecta" din memorie.

## STARE VERIFICATA LA SURSA 17.07.2026 (nu reverifica, e facut)
- Client ID/Secret OBTINUTE de la ANAF. In ~/.iconta/api_keys.env:
  ANAF_CLIENT_ID, ANAF_CLIENT_SECRET, ANAF_REDIRECT_URI, ANAF_AUTHORIZE_URL,
  ANAF_TOKEN_URL, ANAF_REVOKE_URL, SPV_FERNET_KEY. Fisierul e deja in EnvironmentFile
  la iconta-nou.service. NU-l pune in git. NU-l afisa in conversatie.
- Aplicatia inrolata la ANAF: denumire "iConta", servicii e-Factura + e-Transport,
  callback inregistrat = https://iconta.eu/anaf/oauth/callback
- COD MORT EXISTENT in main.py (~liniile 4953-5015): 3 rute OAuth scrise orb, netestate:
  /anaf/oauth/start, /efactura/callback, /anaf/oauth/stare
  Dovezi ca n-au rulat NICIODATA: tabelul public.anaf_tokens NU EXISTA in iconta_v2
  (verificat cu psql: relation does not exist), iar CREATE TABLE era in handler.
  Zero consumatori: grep in *.js/*.html pe "anaf/oauth|efactura/callback" = 0 rezultate.
  Ruta /efactura/callback NU corespunde cu ce e inregistrat la ANAF -> ar da 404 oricum.
  DECI: "nu umbla peste ce functioneaza" NU se aplica - n-a functionat niciodata.

## CE FACI
1. STERGE INTAI cele 3 rute moarte din main.py (regula 0a: reparatie reala, fara cod
   mort ramas). Fa asta ca prim pas, inainte de migrare - elimina orice referinta la
   anaf_tokens (tabelul inexistent) inainte sa existe risc de confuzie cu tabelele noi.
2. MIGRARE: spv_token + spv_cui_acoperit in public (schema exacta in ARHITECTURA_SPV.md,
   sectiunea CONECTORUL SPV -> SCHEMA). Daca vrei sa adaugi coloane suplimentare fata de
   schema din ARHITECTURA_SPV.md (ex. token_content_type, actualizat_la) -> STOP, propune,
   nu adauga direct - schema e deja decizie de arhitectura, nu se extinde din mers.
   In tenant_template: NIMIC. Nu e per tenant.
3. spv_conector.py: auth, refresh cu ROTATIE (vezi CAPCANA CRITICA in ARHITECTURA_SPV.md),
   apel_anaf().
4. spv_rute.py: GET /spv/autorizare + GET /anaf/oauth/callback (URL-ul inregistrat, exact).
5. Teste: test_spv_conector.py, pe MOCK nu pe ANAF real. Obligatoriu un test care dovedeste
   ca refresh-ul salveaza AMBELE valori noi (access + refresh).

## STOP-URI (nu treci de ele fara Costin)
- Orice UI/ecran de conectare -> STOP. Regula 0: se citeste DESIGN_SYSTEM.md si se
  stabileste cu Costin. Nu inventa ecran.
- Orice apel real catre ANAF -> STOP. Testul real il face Costin cu certificatul lui.
- Orice logica de e-Factura/e-Transport -> STOP. Alea sunt F126/F160/F121, construite
  PESTE conector. Daca intra logica de facturi in conector, scopul e ratat.
- Cronul de refresh (spv_refresh.py) -> abia dupa ce testul real trece. Nu acum.
- Orice schimbare fata de schema exacta din ARHITECTURA_SPV.md -> STOP, propune, nu decide.

## VERIFICARE (regula 0c)
py_compile NU e test. Dupa migrare: psql real, arata tabelele. Dupa spv_conector.py:
pytest cu mock. Dupa stergerea rutelor: grep care dovedeste ca nu mai exista si ca
serviciul porneste (sudo systemctl restart iconta-nou && systemctl is-active iconta-nou).
verificator_conformitate.py trebuie sa ramana TOTAL 0.

## DUPA
Raportezi. Costin face testul real: autorizare cu certificatul lui ->
https://api.anaf.ro/TestOauth/jaxrs/hello?name=test -> decodare JWT pe jwt.io.
Abia atunci se afla ce contine tokenul si se populeaza spv_cui_acoperit
(vezi NECUNOSCUTA DECLARATA in ARHITECTURA_SPV.md).

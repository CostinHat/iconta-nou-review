# -*- coding: utf-8 -*-
"""core/mesaje.py — strat central de mesaje user-facing (C-5 conformitate cap.6).

G1: cod de business -> propoziție umană (nu codul-mașină brut la utilizator). cap.6: spune CE e greșit
și, unde remediul nu e evident, CE trebuie făcut. `cod`-ul rămâne pe canalul intern (r["cod"]); aici se
traduce DOAR ce se afișează.

(G2 va extinde acest modul cu constantele de mesaje repetate — familia email, cabinet, CUI etc.)
"""

_FALLBACK = "A apărut o eroare. Reîncearcă; dacă persistă, contactează cabinetul."

MESAJ_COD = {
    # AI / servicii externe
    "AI_EROARE": "Serviciul AI a întâmpinat o eroare. Reîncearcă sau completează manual.",
    "AI_INDISPONIBIL": "Serviciul AI e temporar indisponibil. Reîncearcă mai târziu sau completează manual.",
    "CURS_INDISPONIBIL": "Cursul BNR nu e disponibil pentru data cerută. Reîncearcă sau introdu cursul manual.",
    "EMAIL_ESUAT": "Trimiterea emailului a eșuat. Reîncearcă; dacă persistă, verifică adresa.",
    # blocaje de stare / dependențe
    "ARE_FACTURI": "Nu se poate șterge: există facturi legate. Șterge sau reatribuie întâi facturile.",
    "ARE_LUNI_DECLARATE": "Nu se poate modifica: există luni deja declarate. Retrage întâi declarațiile afectate.",
    "DEJA_IN_COADA": "Declarația e deja în coadă. Verifică lista de validare.",
    "NEAPROBATA": "Declarația nu e aprobată. Trebuie aprobată înainte de depunere.",
    "STARE_GRESITA": "Acțiunea nu e permisă în starea curentă a declarației.",
    "STARE_INVALIDA": "Stare invalidă pentru această acțiune.",
    "NIMIC": "Nu e nimic de procesat.",
    "NIMIC_DE_SCHIMBAT": "Nu e nimic de schimbat.",
    # câmpuri obligatorii goale
    "CONTINUT_GOL": "Conținutul e obligatoriu. Completează-l înainte de a salva.",
    "DESCRIERE_GOALA": "Descrierea e obligatorie. Completeaz-o înainte de a salva.",
    "MOTIV_LIPSA": "Motivul respingerii e obligatoriu. Scrie-l înainte de a respinge.",
    "NUME_GOL": "Numele e obligatoriu. Completează-l.",
    "TEXT_GOL": "Textul e obligatoriu. Completează-l înainte de a trimite.",
    "GOL": "Câmpul e obligatoriu. Completează-l.",
    "FARA_EMAIL": "Adresa de email lipsește. Completeaz-o.",
    "FARA_DESTINATAR": "Alege întâi destinatarii.",
    "FARA_IDENTITATE": "Firma nu are datele de identificare completate. Completează Profilul firmei.",
    "FARA_PROFIL": "Profilul firmei lipsește. Completează-l întâi.",
    # valori invalide / nedeterminate
    "DECONT_INVALID": "Periodicitatea decontului TVA e invalidă. Alege lunar sau trimestrial.",
    "DIRECTIE_INVALIDA": "Direcția aleasă e invalidă. Alege o valoare validă.",
    "MARCAJ_INVALID": "Marcaj de contract invalid. Alege unul din lista disponibilă.",
    "REGIM_INVALID": "Regimul fiscal ales e invalid. Alege micro sau profit.",
    "REGIM_LA_PARTIDA_SIMPLA": "La partidă simplă regimul fiscal se lasă gol.",
    "TIP_INVALID": "Tipul ales e invalid. Alege o valoare validă.",
    "ROL_INVALID": "Rol invalid pentru această acțiune.",
    "IC_LIPSA": "Specifică dacă firma are operațiuni intracomunitare.",
    "NEDETERMINAT": "Valoarea nu a putut fi determinată automat. Completeaz-o manual.",
    # existență / duplicat
    "EMAIL_EXISTA": "Există deja un cont cu acest email. Folosește alt email sau autentifică-te.",
    "NUME_EXISTA": "Există deja o intrare cu acest nume. Alege alt nume.",
    "INEXISTENT": "Elementul cerut nu există sau a fost șters.",
    "MESAJ_INEXISTENT": "Mesajul cerut nu există sau a fost șters.",
    "USER_INEXISTENT": "Utilizatorul cerut nu există.",
    # acces / control
    "CABINET_SUSPENDAT": "Cabinetul este suspendat. Contactează furnizorul pentru reactivare.",
    "AUTH_ESEC": "Autentificare eșuată. Verifică emailul și parola.",
    "PATRU_OCHI": ("Nu poți aproba o declarație pe care ai pregătit-o tu însuți "
                   "(control intern: pregătirea și validarea se fac de persoane diferite)."),
}


def mesaj_din_cod(cod, fallback=None):
    """Propoziția umană pentru un cod de business. Cod necunoscut/None -> fallback (implicit generic)."""
    if cod and cod in MESAJ_COD:
        return MESAJ_COD[cod]
    return fallback or _FALLBACK


# --- G2/G4: mesaje repetate consolidate (un singur șir canonic, referit din toate siturile) ---
FARA_CABINET = "Nu ești asociat niciunui cabinet. Contactează administratorul cabinetului pentru acces."
EMAIL_INVALID = "Adresă de email invalidă. Verifică formatul (exemplu: nume@exemplu.ro)."
EMAIL_EXISTA = "Există deja un cont cu acest email. Autentifică-te sau folosește alt email."
EMAIL_NICIUNUL_VALID = "Niciunul dintre emailuri nu e valid. Verifică lista de adrese."
CUI_FIRMA_LIPSA = "CUI-ul firmei lipsește din Profilul firmei. Completează-l înainte de a genera declarația."
PERIOADA_INCHISA = ("Perioada e blocată (luna închisă). Cere-i administratorului cabinetului să o "
                    "redeschidă sau înregistrează în luna curentă.")

# [R61, 26.08.2026] Refuzul NUMEȘTE ce s-a găsit și spune ce se face cu el — nu „duplicat".
MESAJ_Z_DUPLICAT = ("Raportul Z %(numar)s e deja înregistrat pe %(data)s (nota #%(id)s, "
                    "%(cum)s). Un raport Z e unic pe casă de marcat și pe zi. Dacă e o "
                    "corecție, stornează nota existentă; dacă e alt aparat, folosește NUI-ul lui.")
# [R62, 26.08.2026] Portalul clientului: izolarea între cabinete, și confirmarea adresei.
MESAJ_CLIENT_ALT_CABINET = ("Adresa asta aparține unui cont dezactivat al altui cabinet. Nu poate fi reactivat de aici — datele unui cabinet nu trec la altul. Folosește altă adresă, sau cere-i cabinetului care deține contul să-l elibereze.")
# [R62 (b), 26.08.2026] Titularul = PRIMUL cont de client al firmei. Refuzul spune REGULA,
# nu doar ca nu ai voie: altfel omul nu poate sti pe cine sa intrebe.
# [R66, 26.08.2026] Un document care se produce cu un gol e interdictia 20 in forma ei de zi cu
# zi. Refuzul numeste DOCUMENTUL si UNDE se completeaza — altfel muta munca fara s-o indrume.
# UNDE se completează, ca valoare cu nume — nu ca bucată de frază. Gardul asertează pe
# STRUCTURĂ: că mesajul e COMPUS din constanta asta, nu că fraza conține un anumit șir
# (clichetul 50 / METODA §23). Același tipar ca `cont_valid.UNDE_SE_CREEAZA`.
UNDE_ADMINISTRATOR = "Date firmă › Nume administrator"
# [R46, 26.08.2026] Un câmp care decide CE SE DATOREAZĂ nu se schimbă peste o perioadă închisă:
# ar rescrie trecutul pentru luni în care declarațiile s-au depus deja. Refuzul spune ce s-a
# oprit, de ce, și pe ce cale se face totuși — trei acte consemnate în loc de unul tăcut.
UNDE_PERIOADE = "Perioade blocate"
# [R73 (c), 26.08.2026] Nu se afirmă ce nu se știe. Vechiul text spunea „ai primit linkul de
# logare" — o afirmație despre o trimitere care poate să fi eșuat, iar eșecul era înghițit.
# Costin: *„nu e o schimbare de formulare — e diferența dintre a afirma și a presupune."*
# Ce spune acum: cererea a fost primită, iar linkul vine DACĂ adresa e în sistem.
MESAJ_LINK_LOGARE_CERUT = ("Am primit cererea. Dacă adresa e în sistem, linkul de logare "
                           "ajunge în câteva minute — verifică și în Spam.")
MESAJ_PESTE_PERIOADA_INCHISA = (
    "%(ce)s nu se poate schimba: firma are perioade închise (prima: %(an)s-%(luna)02d). "
    "Câmpul ăsta decide ce se datorează, iar pentru lunile închise declarațiile s-au depus "
    "deja — o schimbare peste ele ar rescrie trecutul. Dacă e nevoie: redeschide perioada din "
    + UNDE_PERIOADE + ", cu motiv, schimbă, apoi închide la loc.")
MESAJ_FARA_ADMINISTRATOR = ("%s nu se poate emite: lipsește numele administratorului. "
                            "Completează-l în " + UNDE_ADMINISTRATOR + ".")
MESAJ_DOAR_TITULARUL = ("Doar titularul contului firmei poate face asta — titularul e primul cont de client al firmei. Cere-i lui, sau contabilului tău.")
MESAJ_EMAIL_ACELASI = "Adresa nouă e aceeași cu cea curentă. Nu e nimic de schimbat."
MESAJ_EMAIL_TOKEN_INVALID = ("Linkul de confirmare e expirat sau a fost deja folosit. Cere din nou schimbarea adresei din Acces cont.")
MESAJ_EMAIL_DE_CONFIRMAT = ("Ți-am trimis un link de confirmare pe adresa nouă. Adresa se schimbă abia după ce îl deschizi — până atunci intri tot cu cea veche.")
MESAJ_Z_FARA_CHEIE = ("NUI-ul casei de marcat și numărul raportului Z sunt obligatorii — ele fac "
                      "raportul unic. Le găsești pe bonul de raport Z tipărit, în antet.")


# --- G3: garduri de rol/acces (403) — explicit: ce drept lipsește + cine îl acordă ---
ROL_INSUFICIENT = "Nu ai rolul necesar pentru această acțiune. Cere-i administratorului cabinetului dreptul potrivit."
DOAR_ADMIN_ICONTA = "Acțiune rezervată administratorului iConta (furnizorul aplicației)."
DOAR_ADMIN_CABINET = "Acțiune rezervată administratorului cabinetului. Cere-i lui să o facă."
DOAR_PATRON = "Acțiune rezervată patronului cabinetului. Cere-i lui să o facă."
FARA_DREPT_VALIDARE = "Nu ai dreptul de a valida declarații. Cere-i administratorului cabinetului să ți-l acorde."
FARA_DREPT_DEPUNERE = "Nu ai dreptul de a depune declarații. Cere-i administratorului cabinetului să ți-l acorde."
FARA_ACCES_TENANT = "Nu ai acces la această firmă. Cere-i administratorului cabinetului să ți-o atribuie."
FARA_ACCES_RAPORTARE = "Nu ai acces la această raportare."
FARA_ACCES = "Nu ai acces la această resursă."

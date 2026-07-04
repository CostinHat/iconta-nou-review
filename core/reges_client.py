# -*- coding: utf-8 -*-
"""Client REGES-ONLINE (api.inspectiamuncii.ro / api.dev.inspectiamuncii.org).
Sursa: github.com/reges-ro/integrare (documentatia oficiala Inspectia Muncii).
- Auth: OpenID password grant, client_id=reges-api, user/parola per CUI din
  aplicatia Angajator (Setari -> Acces -> Chei API).
- Mesaje XML pe schema http://www.inspectiamuncii.ro/reges2025, Header cu
  MessageId/ClientApplication/Version=5/Operation/AuthorId/SessionId/User/Timestamp.
- Raspuns sincron = MessageResponse (recipisa); rezultat asincron = MessageResult
  (contine ReferintaSalariat/ReferintaContract - se SALVEAZA obligatoriu).
- Citire raspunsuri: POST /api/Status/PollMessage (citeste+consuma)."""
import uuid
import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from xml.sax.saxutils import escape

CLIENT_ID = "reges-api"
CLIENT_APP = "iConta"

MEDII = {
    "test": {"api": "https://api.dev.inspectiamuncii.org",
             "token": "https://api.dev.inspectiamuncii.org/auth/realms/reges/protocol/openid-connect/token"},
    "prod": {"api": "https://api.inspectiamuncii.ro",
             "token": "https://api.inspectiamuncii.ro/auth/realms/reges/protocol/openid-connect/token"},
}

def _acum():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

def _header(operation, author_id, user, session_id=None, message_id=None):
    e = escape
    return f"""    <Header>
        <MessageId>{message_id or uuid.uuid4()}</MessageId>
        <ClientApplication>{CLIENT_APP}</ClientApplication>
        <Version>5</Version>
        <Operation>{e(operation)}</Operation>
        <AuthorId>{author_id}</AuthorId>
        <SessionId>{session_id or uuid.uuid4()}</SessionId>
        <User>{e(user)}</User>
        <Timestamp>{_acum()}</Timestamp>
    </Header>"""

def _msg(tip, header, corp):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Message xsi:type="{tip}" xmlns="http://www.inspectiamuncii.ro/reges2025"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
 xsi:schemaLocation="http://www.inspectiamuncii.ro/reges2025">
{header}
{corp}
</Message>"""

def mesaj_inregistrare_salariat(salariat, author_id, user, **kw):
    """salariat: {cnp, nume, prenume, adresa, nationalitate?, tara?, tip_act?}."""
    e = escape
    if not salariat.get("cnp") or not salariat.get("nume"):
        raise ValueError("cnp si nume obligatorii")
    corp = f"""    <Info>
        <Adresa>{e(salariat.get('adresa') or '-')}</Adresa>
        <Cnp>{e(str(salariat['cnp']))}</Cnp>
        <Nume>{e(salariat['nume'].upper())}</Nume>
        <Prenume>{e((salariat.get('prenume') or '-').upper())}</Prenume>
        <Nationalitate>
            <Nume>{e(salariat.get('nationalitate') or 'ROMÂNIA')}</Nume>
        </Nationalitate>
        <TaraDomiciliu>
            <Nume>{e(salariat.get('tara') or 'ROMÂNIA')}</Nume>
        </TaraDomiciliu>
        <TipActIdentitate>{e(salariat.get('tip_act') or 'CarteIdentitate')}</TipActIdentitate>
    </Info>"""
    return _msg("Salariat", _header("InregistrareSalariat", author_id, user, **kw), corp)

def mesaj_adaugare_contract(contract, referinta_salariat, author_id, user, **kw):
    """contract: {numar, data_contract, data_inceput, salariu, cor, cor_versiune?,
    norma?, repartizare?, tip_contract?, tip_durata?, tip_norma?}."""
    e = escape
    for c in ("numar", "data_contract", "data_inceput", "salariu", "cor"):
        if not contract.get(c):
            raise ValueError(f"camp obligatoriu lipsa: {c}")
    corp = f"""    <Continut>
        <ReferintaSalariat>
            <Id>{referinta_salariat}</Id>
        </ReferintaSalariat>
        <Cor>
            <Cod>{e(str(contract['cor']))}</Cod>
            <Versiune>{e(str(contract.get('cor_versiune') or 10))}</Versiune>
        </Cor>
        <DataConsemnare>{_acum()}</DataConsemnare>
        <DataContract>{e(contract['data_contract'])}T00:00:00.000Z</DataContract>
        <DataInceputContract>{e(contract['data_inceput'])}T00:00:00.000Z</DataInceputContract>
        <NumarContract>{e(str(contract['numar']))}</NumarContract>
        <Radiat>false</Radiat>
        <Salariu>{e(str(contract['salariu']))}</Salariu>
        <StareCurenta>
        </StareCurenta>
        <TimpMunca>
            <Norma>{e(contract.get('norma') or 'NormaIntreaga840')}</Norma>
            <Repartizare>{e(contract.get('repartizare') or 'OreDeZi')}</Repartizare>
        </TimpMunca>
        <TipContract>{e(contract.get('tip_contract') or 'ContractIndividualMunca')}</TipContract>
        <TipDurata>{e(contract.get('tip_durata') or 'Nedeterminata')}</TipDurata>
        <TipNorma>{e(contract.get('tip_norma') or 'NormaIntreaga')}</TipNorma>
    </Continut>"""
    return _msg("Contract", _header("AdaugareContract", author_id, user, **kw), corp)

def mesaj_incetare_contract(referinta_contract, data_incetare, temei, explicatie,
                            author_id, user, **kw):
    e = escape
    corp = f"""    <ReferintaContract>
        <Id>{referinta_contract}</Id>
    </ReferintaContract>
    <Actiune xsi:type="ActiuneIncetare">
        <DataIncetare>{e(data_incetare)}T00:00:00.000Z</DataIncetare>
        <Explicatie>{e(explicatie)}</Explicatie>
        <TemeiLegal>{e(temei)}</TemeiLegal>
    </Actiune>"""
    return _msg("Contract", _header("ModificareContract", author_id, user, **kw), corp)

class RegesClient:
    def __init__(self, username, parola, mediu="test", client_secret=None):
        cfg = MEDII[mediu]
        self.api = cfg["api"]
        self.token_url = cfg["token"]
        self.username = username
        self.parola = parola
        self.client_secret = client_secret
        self._token = None

    def _obtine_token(self):
        date = {"grant_type": "password", "client_id": CLIENT_ID,
                "username": self.username, "password": self.parola}
        if self.client_secret:
            date["client_secret"] = self.client_secret
        req = urllib.request.Request(self.token_url,
                                     data=urllib.parse.urlencode(date).encode(),
                                     headers={"Content-Type": "application/x-www-form-urlencoded"})
        with urllib.request.urlopen(req, timeout=30) as r:
            self._token = json.loads(r.read())["access_token"]
        return self._token

    def _post(self, cale, xml):
        if not self._token:
            self._obtine_token()
        req = urllib.request.Request(self.api + cale, data=xml.encode("utf-8"),
                                     headers={"Content-Type": "application/xml",
                                              "Authorization": "Bearer " + self._token})
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.read().decode("utf-8", errors="replace")

    def trimite_salariat(self, xml):
        return self._post("/api/Salariat", xml)

    def trimite_contract(self, xml):
        return self._post("/api/Contract", xml)

    def poll_mesaj(self):
        return self._post("/api/Status/PollMessage", "")

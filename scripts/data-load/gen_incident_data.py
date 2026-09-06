#!/usr/bin/env python3
import json, csv, random, datetime, os
random.seed(61)
OUT = os.path.dirname(os.path.abspath(__file__))
TODAY = datetime.date(2026, 9, 6)
ADMIN = "005g8000004iYenAAE"
RAFAEL = "005g8000009K1pBAAS"
ANA = "005g8000009JzgwAAC"

ships = json.load(open(f"{OUT}/ships_inc.json"))["result"]["records"]
random.shuffle(ships)
ships = ships[:44]   # lean

TYPE_BY_STATUS = {
 "Retido": ["Retido na Base", "Retido com Motorista"],
 "Sem Movimentacao": ["Sem Movimentacao"],
 "Extraviado": ["Suspeita de Extravio", "Avaria em Transporte"],
 "Devolvido ao Remetente": ["Retido na Base"],
}
ROOTC = ["Endereco Incorreto", "Cliente Ausente", "Falha de Triagem", "Extravio Interno",
         "Avaria", "Falha Sistemica", "Postura do Motorista", "Fora da Area de Cobertura"]
RESTYPE = ["Entregue", "Reagendada", "Devolvida ao Remetente", "Encaminhada para Extravio",
           "Localizada e Reintegrada", "Sem Acao Necessaria"]

rows = []
for i, s in enumerate(ships):
    st = s["LT_Status__c"]
    itype = random.choice(TYPE_BY_STATUS.get(st, ["Retido na Base"]))
    detected = TODAY - datetime.timedelta(days=random.randint(1, 22))
    prio = random.choices(["Baixa", "Media", "Alta", "Critica"], weights=[10, 35, 40, 15])[0]
    add_days = {"Critica": 1, "Alta": 2, "Media": 4, "Baixa": 7}[prio]
    deadline = detected + datetime.timedelta(days=add_days)
    # status of the incident
    r = random.random()
    if r < 0.40:
        istatus = "Resolvida"
    elif r < 0.55:
        istatus = "Em Tratamento"
    elif r < 0.68:
        istatus = "Aberta"
    elif r < 0.80:
        istatus = "Aguardando Terceiro"
    elif r < 0.92:
        istatus = "Escalada"
    else:
        istatus = "Cancelada"
    row = {
        "LT_Shipment__c": s["Id"],
        "LT_Incident_Type__c": itype,
        "LT_Status__c": istatus,
        "LT_Priority__c": prio,
        "LT_Detected_Date__c": detected.isoformat(),
        "LT_Resolution_Deadline__c": deadline.isoformat(),
        "LT_Owner_Unit__c": s.get("LT_Delivery_Base__c") or "",
        "LT_Assigned_To__c": random.choice([RAFAEL, ANA, ADMIN]) if istatus in ("Em Tratamento", "Escalada", "Aguardando Terceiro", "Resolvida") else "",
        "LT_Description__c": f"Ocorrencia de {itype} na remessa com destino {s.get('LT_Dest_City__c','')}.",
        "OwnerId": ADMIN,
    }
    if itype == "Retido com Motorista" and s.get("LT_Last_Mile_Driver__c"):
        row["LT_Responsible_Driver__c"] = s["LT_Last_Mile_Driver__c"]
    elif itype == "Retido com Motorista":
        row["LT_Incident_Type__c"] = "Retido na Base"
    if istatus == "Resolvida":
        rd = detected + datetime.timedelta(days=random.randint(1, 12))
        row["LT_Resolved_Date__c"] = rd.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        row["LT_Resolution_Type__c"] = random.choice(RESTYPE)
        row["LT_Root_Cause__c"] = random.choice(ROOTC)
        row["LT_Resolution_Notes__c"] = "Tratativa concluida pela equipe da base."
    if istatus == "Escalada":
        row["LT_Escalated__c"] = "true"
        row["LT_Escalation_Date__c"] = (detected + datetime.timedelta(days=random.randint(3, 10))).isoformat()
        row["LT_Root_Cause__c"] = random.choice(ROOTC)
    rows.append(row)

keys = []
for r in rows:
    for k in r:
        if k not in keys:
            keys.append(k)
with open(f"{OUT}/incidents.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=keys)
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k, "") for k in keys})

from collections import Counter
print("incidents:", len(rows), Counter(r["LT_Status__c"] for r in rows))

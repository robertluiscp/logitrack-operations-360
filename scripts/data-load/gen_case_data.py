#!/usr/bin/env python3
import json, csv, random, datetime, os
random.seed(71)
OUT = os.path.dirname(os.path.abspath(__file__))
TODAY = datetime.date(2026, 9, 6)
ADMIN = "005g8000004iYenAAE"

rts = {r["DeveloperName"]: r["Id"] for r in json.load(open(f"{OUT}/case_rts.json"))["result"]["records"]}
ships = json.load(open(f"{OUT}/ships_for_cases.json"))["result"]["records"]
by_status = {}
for s in ships:
    by_status.setdefault(s["LT_Status__c"], []).append(s)

PRIO = ["Low", "Medium", "High"]
CHAN = ["Telefone", "Chat", "E-mail", "Marketplace", "App do Cliente"]
MKT = ["Shopee", "Mercado Livre", "Shein", "TikTok Shop", "Amazon", "Magalu"]
ROOTC = ["Falha do Motorista", "Falha da Base", "Endereco Incorreto", "Extravio Interno",
         "Avaria em Transporte", "Problema Sistemico", "Sem Culpa da LogiTrack"]

# (RT dev, count, preferred shipment statuses, subject template)
PLAN = [
 ("LT_Assinado_Nao_Recebido", 10, ["Entregue", "Devolvido ao Remetente"], "Assinado nao recebido - cliente nao recebeu o pacote"),
 ("LT_Agilizacao", 8, ["Retido", "Sem Movimentacao", "Tentativa de Entrega"], "Solicitacao de agilizacao da entrega"),
 ("LT_Avaria_Pos_Entrega", 6, ["Entregue"], "Pacote entregue avariado"),
 ("LT_Postura_Motorista", 6, ["Entregue", "Tentativa de Entrega"], "Reclamacao sobre postura do motorista"),
 ("LT_PNR", 4, ["Extraviado", "Devolvido ao Remetente"], "PNR - paguei e nao recebi"),
]

rows = []
for rtdev, n, statuses, subj in PLAN:
    pool = []
    for st in statuses:
        pool += by_status.get(st, [])
    random.shuffle(pool)
    for i in range(n):
        sp = pool[i % len(pool)] if pool else random.choice(ships)
        opened_days = random.randint(0, 25)
        prio = random.choices(PRIO, weights=[20, 45, 35])[0]
        r = random.random()
        if rtdev == "LT_PNR":
            status = random.choice(["Escalated", "Escalated", "Closed"])
        elif r < 0.45:
            status = "Closed"
        elif r < 0.62:
            status = "Working"
        elif r < 0.78:
            status = "New"
        else:
            status = "Escalated"
        row = {
            "RecordTypeId": rts[rtdev],
            "Subject": subj,
            "Description": f"Chamado registrado pelo SAC. {subj}.",
            "Status": status,
            "Priority": prio,
            "Origin": random.choice(["Phone", "Email", "Web"]),
            "LT_Customer_Channel__c": random.choice(CHAN),
            "LT_Marketplace__c": random.choice(MKT),
            "LT_Shipment__c": sp["Id"],
            "LT_Base__c": sp.get("LT_Delivery_Base__c") or "",
            "OwnerId": ADMIN,
        }
        if rtdev in ("LT_Assinado_Nao_Recebido", "LT_Avaria_Pos_Entrega", "LT_Postura_Motorista") and sp.get("LT_Last_Mile_Driver__c"):
            row["LT_Driver_Involved__c"] = sp["LT_Last_Mile_Driver__c"]
        if status in ("Working", "Escalated", "Closed"):
            row["LT_First_Response_Date__c"] = (datetime.datetime(2026, 9, 6, 10, 0) - datetime.timedelta(days=opened_days) + datetime.timedelta(hours=random.randint(1, 6))).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        if rtdev == "LT_Assinado_Nao_Recebido" and status in ("Working", "Escalated", "Closed"):
            fw = datetime.datetime(2026, 9, 6, 12, 0) - datetime.timedelta(days=max(0, opened_days - 1))
            row["LT_Forwarded_To_Driver_Date__c"] = fw.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            row["LT_Driver_Response_Deadline__c"] = (fw + datetime.timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        if rtdev == "LT_PNR" or (rtdev == "LT_Assinado_Nao_Recebido" and status == "Escalated" and random.random() < 0.5):
            row["LT_PNR_Flag__c"] = "true"
        if rtdev in ("LT_PNR", "LT_Avaria_Pos_Entrega") and status in ("Escalated", "Closed"):
            row["LT_Reimbursement_Value__c"] = round(float(sp.get("LT_Declared_Value__c") or random.uniform(40, 900)), 2)
            row["LT_Root_Cause__c"] = random.choice(ROOTC)
        if rtdev == "LT_Postura_Motorista" and status == "Closed" and random.random() < 0.6:
            row["LT_Driver_Penalized__c"] = "true"
            row["LT_Root_Cause__c"] = "Falha do Motorista"
        if status in ("Closed",) and "LT_Root_Cause__c" not in row:
            row["LT_Root_Cause__c"] = random.choice(ROOTC)
        rows.append(row)

keys = []
for r in rows:
    for k in r:
        if k not in keys:
            keys.append(k)
with open(f"{OUT}/cases.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=keys)
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k, "") for k in keys})

from collections import Counter
print("cases:", len(rows), Counter(r["Status"] for r in rows))

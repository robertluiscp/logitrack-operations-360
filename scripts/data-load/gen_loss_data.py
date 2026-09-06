#!/usr/bin/env python3
import json, csv, random, datetime, os
random.seed(83)
OUT = os.path.dirname(os.path.abspath(__file__))
TODAY = datetime.date(2026, 9, 6)
ADMIN = "005g8000004iYenAAE"

ships = json.load(open(f"{OUT}/ships_loss.json"))["result"]["records"]
cases = json.load(open(f"{OUT}/cases_loss.json"))["result"]["records"]
mans = [m["Id"] for m in json.load(open(f"{OUT}/manifests_loss.json"))["result"]["records"]]

REASON = {
 "Extraviado": ["PNR - Paguei Nao Recebi", "Assinado Nao Recebido", "Roubo / Furto de Carga", "Endereco Inexistente"],
 "Retido": ["Retido +10 dias"],
 "Sem Movimentacao": ["Sem Movimentacao +10 dias"],
 "Devolvido ao Remetente": ["Endereco Inexistente", "Assinado Nao Recebido"],
}
RESP = ["Motorista", "Base", "Transporte (SC / MR / Coleta)", "Cliente / Embarcador", "Terceiro", "Sem Responsavel Definido"]
LCSTATUS_W = [("Ressarcido", 40), ("Aprovado", 15), ("Em Apuracao", 20), ("Em Aprovacao", 12), ("Indeferido", 13)]
lcstat = [s for s, w in LCSTATUS_W for _ in range(w)]

claims = []
used_ship = set()
batch_ct = 0
pool = [s for s in ships]
random.shuffle(pool)
for i, sp in enumerate(pool[:24]):
    if sp["Id"] in used_ship:
        continue
    used_ship.add(sp["Id"])
    st = sp["LT_Status__c"]
    reason = random.choice(REASON.get(st, ["Outro"]))
    resp = "Motorista" if reason in ("Assinado Nao Recebido", "PNR - Paguei Nao Recebi") and random.random() < 0.6 else random.choice(RESP)
    detected = TODAY - datetime.timedelta(days=random.randint(3, 40))
    status = random.choice(lcstat)
    declared = round(float(sp.get("LT_Declared_Value__c") or random.uniform(40, 1000)), 2)
    tag = f"LOSSBATCH-{i:04d}"
    row = {
        "_tag": tag,
        "LT_Shipment__c": sp["Id"],
        "LT_Loss_Reason__c": reason,
        "LT_Responsibility__c": resp,
        "LT_Status__c": status,
        "LT_Detected_Date__c": detected.isoformat(),
        "LT_Declared_Value__c": declared,
        "LT_Description__c": f"Extravio da remessa apos apuracao. Motivo: {reason}.",
        "OwnerId": ADMIN,
    }
    if sp.get("LT_Delivery_Base__c"):
        row["LT_Responsible_Base__c"] = sp["LT_Delivery_Base__c"] if resp == "Base" else ""
    if resp == "Motorista" and sp.get("LT_Last_Mile_Driver__c"):
        row["LT_Responsible_Driver__c"] = sp["LT_Last_Mile_Driver__c"]
    elif resp == "Motorista":
        row["LT_Responsibility__c"] = "Transporte (SC / MR / Coleta)"
        resp = "Transporte (SC / MR / Coleta)"
    if random.random() < 0.35:
        batch_ct += 1
        row["LT_Batch_Reference__c"] = f"LOTE-2026-{(detected.month):02d}-{batch_ct:03d}"
    if status in ("Aprovado", "Ressarcido"):
        reimb = round(declared * random.uniform(0.7, 1.0), 2)
        row["LT_Reimbursement_Value__c"] = reimb
        row["LT_Approved_By__c"] = ADMIN
        row["LT_Approval_Date__c"] = (detected + datetime.timedelta(days=random.randint(3, 15))).isoformat()
        if row["LT_Responsibility__c"] == "Motorista":
            row["LT_Driver_Charge_Value__c"] = round(reimb * random.uniform(0.4, 0.9), 2)
        row["LT_Resolution_Notes__c"] = "Ressarcimento aprovado apos confirmacao da responsabilidade."
    if status == "Ressarcido":
        row["LT_Reimbursement_Date__c"] = (detected + datetime.timedelta(days=random.randint(10, 30))).isoformat()
    if status == "Indeferido":
        row["LT_Resolution_Notes__c"] = random.choice([
            "Indeferido: entrega comprovada por foto e assinatura.",
            "Indeferido: sem culpa da LogiTrack (endereco fornecido incorreto pelo cliente).",
            "Indeferido: fora do prazo de reclamacao do embarcador."])
    claims.append(row)

keys = []
for r in claims:
    for k in r:
        if k not in keys:
            keys.append(k)
with open(f"{OUT}/loss_claims.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=keys)
    w.writeheader()
    for r in claims:
        w.writerow({k: r.get(k, "") for k in keys})

# standalone penalties from Postura cases + Avaria
PTYPE_STANDALONE = ["Advertencia (Postura)", "Suspensao Temporaria", "Multa Contratual", "Desconto por Avaria"]
pen = []
drv_cases = [c for c in cases if c["RecordType"]["DeveloperName"] == "LT_Postura_Motorista" and c.get("LT_Driver_Involved__c")]
for i, c in enumerate(drv_cases):
    pt = random.choice(["Advertencia (Postura)", "Advertencia (Postura)", "Suspensao Temporaria", "Multa Contratual"])
    ref = TODAY - datetime.timedelta(days=random.randint(5, 30))
    contested = random.random() < 0.3
    outcome = "Pendente"
    status = "Registrada"
    if contested:
        status = random.choice(["Em Contestacao", "Confirmada", "Revertida"])
        outcome = "Pendente" if status == "Em Contestacao" else random.choice(["Mantida", "Reduzida", "Cancelada"])
        if status == "Revertida":
            outcome = "Cancelada"
    elif random.random() < 0.5:
        status = random.choice(["Confirmada", "Descontada"])
    row = {
        "LT_Driver__c": c["LT_Driver_Involved__c"],
        "LT_Penalty_Type__c": pt,
        "LT_Origin__c": "Chamado SAC",
        "LT_Status__c": status,
        "LT_Case__c": c["Id"],
        "LT_Reference_Date__c": ref.isoformat(),
        "LT_Applied_By__c": ADMIN,
        "LT_Description__c": "Penalizacao aplicada apos apuracao de reclamacao de postura pelo SAC.",
        "OwnerId": ADMIN,
    }
    if pt in ("Multa Contratual", "Desconto por Avaria"):
        row["LT_Amount__c"] = round(random.uniform(50, 400), 2)
    if contested:
        row["LT_Contested__c"] = "true"
        row["LT_Contest_Date__c"] = (ref + datetime.timedelta(days=random.randint(2, 10))).isoformat()
        row["LT_Contest_Outcome__c"] = outcome
    if status == "Descontada" and mans:
        row["LT_Applied_In_Manifest__c"] = random.choice(mans)
    pen.append(row)

keys2 = []
for r in pen:
    for k in r:
        if k not in keys2:
            keys2.append(k)
with open(f"{OUT}/penalties_standalone.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=keys2)
    w.writeheader()
    for r in pen:
        w.writerow({k: r.get(k, "") for k in keys2})

from collections import Counter
print("loss claims:", len(claims), Counter(r["LT_Status__c"] for r in claims))
print("standalone penalties:", len(pen))

#!/usr/bin/env python3
import csv, random, datetime, os
random.seed(41)
OUT = os.path.dirname(os.path.abspath(__file__))
TODAY = datetime.date(2026, 9, 6)
RT_PARTNER = "012g8000002pYbBAAU"
RAFAEL = "005g8000009K1pBAAS"
ANA = "005g8000009JzgwAAC"
ADMIN = "005g8000004iYenAAE"

DRIVERS = [
 ("a0Fg8000006qKpEEAU", "Coleta", "PR"), ("a0Fg8000006qKpHEAU", "Coleta", "SC"),
 ("a0Fg8000006qKpIEAU", "Coleta", "SC"), ("a0Fg8000006qKpJEAU", "Coleta", "PR"),
 ("a0Fg8000006qKpKEAU", "Coleta", "RS"),
 ("a0Fg8000006qKpOEAU", "MR", "PR"), ("a0Fg8000006qKpQEAU", "MR", "PR"), ("a0Fg8000006qKpREAU", "MR", "RS"),
]
SHIPPERS = ["001g800000kdoNSAAY", "001g800000kdoNTAAY", "001g800000kdoNUAAY", "001g800000kdoNVAAY",
            "001g800000kdoNWAAY", "001g800000kdoNXAAY", "001g800000kdoNYAAY", "001g800000kdoNZAAY"]
CD = {"PR": "PR SJS", "SC": "SC BNU", "RS": "RS NSR"}
CITY = {"PR": ["Curitiba", "Londrina", "Maringa", "Cascavel", "Ponta Grossa"],
        "SC": ["Joinville", "Florianopolis", "Blumenau", "Chapeco", "Criciuma"],
        "RS": ["Porto Alegre", "Caxias do Sul", "Pelotas", "Canoas", "Santa Maria"]}

# ---- DropOff point partner accounts ----
dropoffs = [
 ("Ponto Expresso Centro - Curitiba", "PR", "Curitiba"),
 ("Papelaria Rapida DropOff - Londrina", "PR", "Londrina"),
 ("Loja Conveniencia Sul - Maringa", "PR", "Maringa"),
 ("Mercado do Bairro - Joinville", "SC", "Joinville"),
 ("Lotericas Ilha DropOff - Florianopolis", "SC", "Florianopolis"),
 ("Tabacaria Central - Blumenau", "SC", "Blumenau"),
 ("Armazem do Vale DropOff - Porto Alegre", "RS", "Porto Alegre"),
 ("Ponto Serra - Caxias do Sul", "RS", "Caxias do Sul"),
]
acc_rows = []
for i, (nm, uf, city) in enumerate(dropoffs, start=1):
    a = 60 + i; b = (i * 313) % 1000; c = (i * 877) % 1000; d = (i * 41) % 100
    acc_rows.append({
        "Name": nm, "RecordTypeId": RT_PARTNER,
        "LT_Operating_Partner_Type__c": "Parceiro DropOff",
        "LT_CNPJ__c": f"{a:02d}.{b:03d}.{c:03d}/0001-{d:02d}",
        "LT_Partner_Status__c": "Ativo", "Type": "Ponto de Coleta",
        "BillingCity": city, "BillingState": uf, "BillingCountry": "Brasil",
        "Description": f"Ponto de Coleta (DropOff) da LogiTrack em {city}/{uf}.",
    })
with open(f"{OUT}/dropoff_partners.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(acc_rows[0].keys()))
    w.writeheader(); w.writerows(acc_rows)
dropoff_cnpjs = {(uf): [] for uf in ("PR", "SC", "RS")}
for r, (nm, uf, city) in zip(acc_rows, dropoffs):
    dropoff_cnpjs[uf].append(r["LT_CNPJ__c"])

# ---- pickup requests ----
PSTATUS_W = [("Coletada", 55), ("Solicitada", 8), ("Agendada", 12), ("Motorista a Caminho", 5),
             ("Nao Realizada", 6), ("Cancelada", 4)]
pstat = []
for s, w in PSTATUS_W:
    pstat += [s] * w

coleta_drv = [d for d in DRIVERS if d[1] == "Coleta"]
pickups = []
for i in range(1, 96):
    ptype = random.choices(["Coleta no Seller", "Coleta no DropOff", "C2C - Venda de Etiqueta"], weights=[52, 30, 18])[0]
    st = random.choice(pstat)
    drv = random.choice(coleta_drv)
    uf = drv[2]
    city = random.choice(CITY[uf])
    posted = TODAY - datetime.timedelta(days=random.randint(0, 35))
    sched = posted + datetime.timedelta(days=random.randint(0, 2))
    est = random.randint(15, 400) if ptype != "C2C - Venda de Etiqueta" else 1
    row = {
        "LT_Pickup_Type__c": ptype,
        "LT_Status__c": st,
        "LT_First_Mile_Driver__c": drv[0] if st in ("Agendada", "Motorista a Caminho", "Coletada", "Nao Realizada") else "",
        "LT_Origin_Base__c": "", "LT_Destination_CD__r.Unit_Code__c": CD[uf],
        "LT_Requested_By__c": random.choice(["Central de Coletas", "App do Embarcador", "SAC", "Comercial"]),
        "LT_Pickup_Address__c": f"Rua {random.choice(['A','B','C','D'])}, {random.randint(10,2000)}",
        "LT_Pickup_City__c": city, "LT_Pickup_State__c": uf,
        "LT_Scheduled_Date__c": sched.isoformat() if st in ("Agendada", "Motorista a Caminho", "Coletada", "Nao Realizada") else "",
        "LT_Estimated_Packages__c": est,
        "LT_Collected_Packages__c": max(0, int(est * random.uniform(0.7, 1.05))) if st == "Coletada" else "",
        "LT_Completed_DateTime__c": (datetime.datetime.combine(sched, datetime.time(random.randint(9,18), 0))).strftime("%Y-%m-%dT%H:%M:%S.000Z") if st == "Coletada" else "",
        "OwnerId": RAFAEL,
    }
    if ptype == "Coleta no Seller":
        row["LT_Shipper__c"] = random.choice(SHIPPERS)
    elif ptype == "Coleta no DropOff":
        row["LT_Pickup_Point__r.LT_CNPJ__c"] = random.choice(dropoff_cnpjs[uf]) if dropoff_cnpjs[uf] else random.choice(sum(dropoff_cnpjs.values(), []))
    else:
        row["LT_C2C_Sender_Name__c"] = random.choice(["Cliente Balcao", "Pessoa Fisica"]) + f" {random.randint(1,99)}"
        row["LT_C2C_Recipient_Name__c"] = "Destinatario " + str(random.randint(1, 999))
        row["LT_C2C_Dest_City__c"] = random.choice(sum(CITY.values(), []))
    pickups.append(row)

keys = sorted({k for r in pickups for k in r})
# reorder for readability
front = ["LT_Pickup_Type__c", "LT_Status__c", "LT_Shipper__c", "LT_Pickup_Point__r.LT_CNPJ__c",
         "LT_First_Mile_Driver__c", "LT_Destination_CD__r.Unit_Code__c"]
keys = front + [k for k in keys if k not in front]
with open(f"{OUT}/pickup_requests.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=keys)
    w.writeheader()
    for r in pickups:
        w.writerow({k: r.get(k, "") for k in keys})

# ---- manifests + lines ----
MSTATUS_W = [("Pago", 45), ("Aprovado", 18), ("Em Conferencia", 25), ("Rejeitado", 12)]
mstat = []
for s, w in MSTATUS_W:
    mstat += [s] * w

manifests = []   # ext key via a temp code we won't load; we load by autonum -> use a placeholder external? no external id.
# Manifests have no external id. We'll load them, query back, then load lines.
# For now write manifests with a synthetic "LT_Notes__c" carrying a batch tag to map later.
lines = []
mi = 0
for drv, cat, uf in DRIVERS:
    n = random.randint(4, 8) if cat == "Coleta" else random.randint(2, 4)
    for _ in range(n):
        mi += 1
        ref = TODAY - datetime.timedelta(days=random.randint(1, 40))
        mtype = "Coleta (First Mile)" if cat == "Coleta" else "Mini Transferencia (MR)"
        rate = round(random.uniform(0.45, 1.30), 2) if cat == "Coleta" else round(random.uniform(0.30, 0.75), 2)
        pst = random.choice(mstat)
        tag = f"BATCH-{mi:04d}"
        dist = "" if cat == "Coleta" else random.choice([72, 85, 110, 140, 190, 240])
        m = {
            "LT_Driver__c": drv, "LT_Manifest_Type__c": mtype,
            "LT_Reference_Date__c": ref.isoformat(),
            "LT_Origin_Unit__r.Unit_Code__c": CD[uf],
            "LT_Distance_Km__c": dist,
            "LT_Rate_Per_Package__c": rate,
            "LT_Bonus_Adjustment__c": round(random.choice([0, 0, 0, 25, 40, -15]), 2),
            "LT_Payment_Status__c": pst,
            "LT_Approved_By__c": ADMIN if pst in ("Aprovado", "Pago") else "",
            "LT_Payment_Date__c": (ref + datetime.timedelta(days=random.randint(5, 20))).isoformat() if pst == "Pago" else "",
            "LT_Notes__c": tag,
            "OwnerId": RAFAEL,
        }
        if cat == "MR":
            # pick a destination base in another/same state
            dest_uf = uf
            m["LT_Destination_Unit__r.Unit_Code__c"] = random.choice(["CWB 02-PR", "BNU-SC", "POA-RS", "CAC-PR", "JOI-SC", "PEL-RS"])
        manifests.append(m)
        # lines
        nl = random.randint(2, 6)
        for _ in range(nl):
            lines.append({
                "_tag": tag,
                "LT_Package_Count__c": random.randint(8, 220) if cat == "Coleta" else random.randint(40, 800),
                "LT_Collection_City__c": random.choice(CITY[uf]),
                "LT_Description__c": random.choice(["Coleta consolidada", "Rota manha", "Rota tarde", "Transferencia noturna", "Reforco"]),
            })

with open(f"{OUT}/manifests.csv", "w", newline="", encoding="utf-8") as f:
    keys = sorted({k for r in manifests for k in r})
    w = csv.DictWriter(f, fieldnames=keys)
    w.writeheader()
    for r in manifests:
        w.writerow({k: r.get(k, "") for k in keys})
with open(f"{OUT}/manifest_lines.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["_tag", "LT_Package_Count__c", "LT_Collection_City__c", "LT_Description__c"])
    w.writeheader(); w.writerows(lines)

from collections import Counter
print("dropoffs:", len(acc_rows), "pickups:", len(pickups), "manifests:", len(manifests), "lines:", len(lines))
print(Counter(p["LT_Status__c"] for p in pickups))

#!/usr/bin/env python3
import csv, random, datetime, os, subprocess, json
random.seed(53)
OUT = os.path.dirname(os.path.abspath(__file__))
TODAY = datetime.date(2026, 9, 6)
NOW = datetime.datetime(2026, 9, 6, 12, 0, 0)
RUN = r"C:\Users\Robert Luis\AppData\Roaming\npm\node_modules\@salesforce\cli\bin\run.js"
NODE = r"C:\Program Files\nodejs\node.exe"

DRIVERS = [l.split("|") for l in """a0Fg8000006qKonEAE|TAC|ARP-PR
a0Fg8000006qKooEAE|TAC|ARP-PR
a0Fg8000006qKopEAE|TAC|TUB-SC
a0Fg8000006qKorEAE|TAC|CCM-SC
a0Fg8000006qKosEAE|TAC|CXJ-RS
a0Fg8000006qKp1EAE|MEI|CLB-PR
a0Fg8000006qKp3EAE|MEI|TUB-SC
a0Fg8000006qKp5EAE|MEI|ALM-PR
a0Fg8000006qKp7EAE|MEI|POA-RS
a0Fg8000006qKp8EAE|MEI|CIC-PR
a0Fg8000006qKpCEAU|ETC|CWB 02-PR
a0Fg8000006qKpEEAU|Coleta|F ARP-PR
a0Fg8000006qKpHEAU|Coleta|SJE-SC
a0Fg8000006qKpJEAU|Coleta|ARP-PR""".splitlines()]


# delivery-capable shipments with a base
import json as _j; ships = _j.load(open(OUT + "/ships_for_routes.json", encoding="utf-8-sig"))["result"]["records"]
by_base = {}
for s in ships:
    b = s["LT_Delivery_Base__r"]["Unit_Code__c"] if s.get("LT_Delivery_Base__r") else None
    by_base.setdefault(b, []).append(s)

RSTATUS_W = [("Concluida", 60), ("Em Rota", 12), ("Carregada", 8), ("Planejada", 8), ("Em Triagem", 6), ("Cancelada", 6)]
rstat = [s for s, w in RSTATUS_W for _ in range(w)]
RESULT_FAIL = ["Destinatario Ausente", "Endereco Nao Localizado", "Recusado pelo Destinatario", "Estabelecimento Fechado"]

routes = []       # dict + _tag
attempts = []     # dict with _route_tag
used_ship = set()
ri = 0
for drv, cat, base in DRIVERS:
    for _ in range(random.randint(2, 4)):
        ri += 1
        tag = f"RT-{ri:04d}"
        rdate = TODAY - datetime.timedelta(days=random.randint(0, 28))
        status = random.choice(rstat)
        is_mr = (cat in ("ETC",) and random.random() < 0.15)
        rtype = "Mini Transferencia" if is_mr else "Last Mile (Entrega)"
        planned = random.randint(40, 260) if cat != "ETC" else random.randint(300, 1200)
        loaded = int(planned * random.uniform(0.85, 1.0)) if status not in ("Planejada", "Em Triagem") else ""
        pool = by_base.get(base, []) or ships
        dep = datetime.datetime.combine(rdate, datetime.time(random.randint(7, 10), 0))
        ret = dep + datetime.timedelta(hours=random.randint(4, 9))
        r = {
            "_tag": tag,
            "LT_Base__r.Unit_Code__c": base,
            "LT_Route_Date__c": rdate.isoformat(),
            "LT_Route_Type__c": rtype,
            "LT_Status__c": status,
            "LT_Driver__c": drv if status not in ("Planejada", "Em Triagem") else "",
            "LT_Target_City__c": (random.choice(pool)["LT_Dest_City__c"] if pool else ""),
            "LT_Cage_Code__c": f"G{random.randint(1,40):02d}",
            "LT_Planned_Packages__c": planned,
            "LT_Loaded_Packages__c": loaded,
            "LT_Departure_Time__c": dep.strftime("%Y-%m-%dT%H:%M:%S.000Z") if status in ("Em Rota", "Concluida") else "",
            "LT_Return_Time__c": ret.strftime("%Y-%m-%dT%H:%M:%S.000Z") if status == "Concluida" else "",
            "LT_Notes__c": tag,
            "OwnerId": "005g8000004iYenAAE",
        }
        if is_mr:
            r["LT_Distance_Km__c"] = random.choice([80, 110, 150, 210])
            r["LT_Destination_Unit__r.Unit_Code__c"] = random.choice(["BNU-SC", "POA-RS", "CAC-PR", "PEL-RS"])
        routes.append(r)
        # attempts only for routes that ran
        if status in ("Em Rota", "Concluida") and pool:
            k = random.randint(2, 4)
            picks = random.sample(pool, min(k, len(pool)))
            for j, sp in enumerate(picks, start=1):
                if sp["Id"] in used_ship:
                    continue
                used_ship.add(sp["Id"])
                delivered = sp["LT_Status__c"] == "Entregue" or (sp["LT_Status__c"] == "Devolvido ao Remetente" and random.random() < 0.3)
                res = "Entregue" if delivered else random.choice(RESULT_FAIL)
                adt = dep + datetime.timedelta(hours=random.randint(1, 7))
                if adt > NOW:
                    adt = NOW - datetime.timedelta(hours=random.randint(2, 20))
                attempts.append({
                    "_route_tag": tag,
                    "LT_Shipment__c": sp["Id"],
                    "LT_Driver__c": drv,
                    "LT_Attempt_Number__c": j,
                    "LT_Attempt_DateTime__c": adt.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                    "LT_Result__c": res,
                    "LT_Recipient_Doc__c": f"{random.randint(100,999)}.{random.randint(100,999)}.{random.randint(100,999)}-{random.randint(10,99)}" if delivered else "",
                    "LT_Recipient_Relationship__c": random.choice(["Proprio", "Familiar", "Porteiro", "Vizinho"]) if delivered else "",
                    "LT_Notes__c": "" if delivered else "Nova tentativa a agendar.",
                })

with open(f"{OUT}/routes.csv", "w", newline="", encoding="utf-8") as f:
    keys = [k for k in routes[0].keys()]
    for r in routes:
        for k in r:
            if k not in keys: keys.append(k)
    w = csv.DictWriter(f, fieldnames=keys)
    w.writeheader()
    for r in routes:
        w.writerow({k: r.get(k, "") for k in keys})
with open(f"{OUT}/delivery_attempts_raw.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(attempts[0].keys()))
    w.writeheader(); w.writerows(attempts)

print("routes:", len(routes), "attempts:", len(attempts))

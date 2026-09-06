#!/usr/bin/env python3
"""Top-up de Operational_Indicator__c: indicadores diarios por unidade."""
import json, csv, random, datetime, os
random.seed(360)
SCR = r"C:\Users\ROBERT~1\AppData\Local\Temp\claude\C--Users-Robert-Luis-Desktop-LogiTrack-SFDX\9f02e204-5a31-476e-ba33-4a01f545d640\scratchpad"
ADMIN = "005g8000004iYenAAE"

units = json.load(open(os.path.join(SCR, "oi_units.json"), encoding="utf-8"))["result"]["records"]
# perfis de desempenho por unidade (para variar entre "dentro da meta" / "atencao" / "critico")
profile = {}
for u in units:
    profile[u["Id"]] = random.choice(["bom", "bom", "medio", "medio", "ruim"])

dates = [datetime.date(2026, 8, 31) + datetime.timedelta(days=i) for i in range(6)]  # 31/08 a 05/09

rows = []
for u in units:
    base_vol = {"Regional": 900, "Centro de Distribuição": 600}.get(u["Unit_Type__c"], random.randint(70, 180))
    prof = profile[u["Id"]]
    for d in dates:
        if d.weekday() == 6:  # domingo sem operacao
            continue
        total = max(20, int(base_vol * random.uniform(0.8, 1.2)))
        if prof == "bom":
            deliv_rate = random.uniform(0.88, 0.96)
            ontime_rate = random.uniform(0.90, 0.98)
        elif prof == "medio":
            deliv_rate = random.uniform(0.75, 0.87)
            ontime_rate = random.uniform(0.78, 0.90)
        else:
            deliv_rate = random.uniform(0.55, 0.72)
            ontime_rate = random.uniform(0.55, 0.75)
        delivered = int(total * deliv_rate)
        undelivered = total - delivered
        ontime = int(delivered * ontime_rate)
        late = delivered - ontime
        openp = int(undelivered * random.uniform(0.4, 0.9))
        over3 = int(openp * random.uniform(0.1, 0.5))
        wh_not_disp = int(total * random.uniform(0.01, 0.06))
        rows.append({
            "Logistics_Unit__c": u["Id"],
            "Reference_Date__c": d.isoformat(),
            "Total_Orders__c": total,
            "Delivered_Orders__c": delivered,
            "Undelivered_Orders__c": undelivered,
            "On_Time_Deliveries__c": ontime,
            "Late_Deliveries__c": late,
            "Open_Packages__c": openp,
            "Packages_Over_3_Days_No_Movement__c": over3,
            "Warehouse_Entry_Not_Dispatched__c": wh_not_disp,
        })

keys = list(rows[0].keys())
with open(os.path.join(SCR, "indicators_topup.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=keys)
    w.writeheader()
    for r in rows:
        w.writerow(r)
print("indicadores gerados:", len(rows), "| unidades:", len(units), "| datas:", len(dates))

#!/usr/bin/env python3
import csv, random, datetime
random.seed(11)
OUT = r"C:\Users\ROBERT~1\AppData\Local\Temp\claude\C--Users-Robert-Luis-Desktop-LogiTrack-SFDX\9f02e204-5a31-476e-ba33-4a01f545d640\scratchpad"

# agreementId | shipperId | name | ppp | monthlyVol | sla
DATA = """a0Cg800000siChWEAU|001g800000kdoNSAAY|Xitou Marketplace|6.3|48000|0.97
a0Cg800000siChXEAU|001g800000kdoNTAAY|Compria Marketplace|8.78|65000|0.92
a0Cg800000siChYEAU|001g800000kdoNUAAY|ShopLivre|7.21|39000|0.92
a0Cg800000siChZEAU|001g800000kdoNVAAY|VendeMais Online|9.73|31000|0.9
a0Cg800000siChaEAE|001g800000kdqDxAAI|ModaMix Confeccoes|5.47|12000|0.97
a0Cg800000siChbEAE|001g800000kdqDyAAI|TechNova BR|5.12|8600|0.92
a0Cg800000siChcEAE|001g800000kdqDzAAI|Casa e Cor Online|11.63|5400|0.9
a0Cg800000siChdEAE|001g800000kdqE0AAI|PetLar Suprimentos|5.72|9100|0.9
a0Cg800000siCheEAE|001g800000kdqE1AAI|SuplementaBR|8.06|7300|0.97
a0Cg800000siChfEAE|001g800000kdoNWAAY|Calcados Prime|7.21|4200|0.9
a0Cg800000siChgEAE|001g800000kdoNXAAY|Livraria Pagina Viva|8.04|2600|0.95
a0Cg800000siChhEAE|001g800000kdoNYAAY|AutoPecas do Sul|10.5|6800|0.9
a0Cg800000siChiEAE|001g800000kdoNZAAY|FerramentasMax|11.95|5900|0.92
a0Cg800000siChjEAE|001g800000kdoNaAAI|Distribuidora Farmasul|7.75|15400|0.92
a0Cg800000siChkEAE|001g800000kdqE2AAI|Moveis Serra Sul|7.65|3400|0.92
a0Cg800000siChlEAE|001g800000kdqE4AAI|Confeccoes Vale do Itajai|7.82|4700|0.92"""

today = datetime.date(2026, 9, 6)
def month_first(offset):
    y, m = today.year, today.month - offset
    while m <= 0:
        m += 12; y -= 1
    return datetime.date(y, m, 1)

rows = []
for line in DATA.strip().splitlines():
    agr, shipper, name, ppp, vol, sla = line.split("|")
    ppp = float(ppp); vol = int(vol); sla = float(sla)
    nmonths = random.randint(4, 6)
    for k in range(nmonths, 0, -1):  # oldest -> newest
        ref = month_first(k)
        shipped = int(vol * random.uniform(0.82, 1.15))
        delivered = int(shipped * random.uniform(0.90, 0.985))
        adj = 0
        if random.random() < 0.35:
            adj = round(random.uniform(-1, 1) * delivered * ppp * random.uniform(0.01, 0.04), 2)
        # status by recency
        if k == 1:
            status = "Em Apuracao"
        elif k == 2:
            status = random.choice(["Fechado", "Faturado"])
        else:
            status = random.choice(["Faturado", "Pago", "Pago"])
        inv = "" if status in ("Em Apuracao", "Fechado") else f"NF-{random.randint(100000,999999)}"
        rows.append({
            "LT_Shipper__c": shipper,
            "LT_Agreement__c": agr,
            "LT_Reference_Month__c": ref.isoformat(),
            "LT_Packages_Shipped__c": shipped,
            "LT_Packages_Delivered__c": delivered,
            "LT_Price_Per_Package__c": ppp,
            "LT_Adjustments__c": adj,
            "LT_Invoice_Number__c": inv,
            "LT_Billing_Status__c": status,
        })

with open(f"{OUT}/shipper_billings.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"billings: {len(rows)}")

#!/usr/bin/env python3
"""Module J phase 1: LT_Payment_Request__c sample data."""
import json, csv, random, datetime, os

SCR = r"C:\Users\ROBERT~1\AppData\Local\Temp\claude\C--Users-Robert-Luis-Desktop-LogiTrack-SFDX\9f02e204-5a31-476e-ba33-4a01f545d640\scratchpad"
OUT = SCR
random.seed(360)
TODAY = datetime.date(2026, 9, 6)
ADMIN = "005g8000004iYenAAE"

g = lambda f: json.load(open(os.path.join(SCR, f), encoding="utf-8"))["result"]["records"]
claims = g("j_claims.json")
manifests = g("j_manifests.json")
drivers = {d["Id"]: d for d in g("j_drivers.json")}
bases = g("j_bases.json")

rows = []

def add(**kw):
    kw.setdefault("LT_Request_Date__c", "")
    kw.setdefault("OwnerId", ADMIN)
    kw.setdefault("LT_Requested_By__c", ADMIN)
    rows.append(kw)

def dts(d): return d.isoformat()

# ---- 1. Ressarcimento a embarcador (from loss claims) ----
for i, c in enumerate(claims):
    shipper = c["LT_Shipment__r"]["LT_Shipper__c"]
    sname = c["LT_Shipment__r"]["LT_Shipper__r"]["Name"]
    amount = round(float(c["LT_Reimbursement_Value__c"]), 2)
    paid = c["LT_Status__c"] == "Ressarcido"
    req_d = TODAY - datetime.timedelta(days=random.randint(20, 55))
    due_d = req_d + datetime.timedelta(days=random.randint(7, 20))
    add(
        LT_Request_Type__c="Pagamento a Embarcador (Ressarcimento)",
        LT_Status__c="Paga" if paid else "Aprovada",
        LT_Priority__c="Normal",
        LT_Cost_Center__c="Operacao - Ultima Milha",
        LT_Payment_Method__c="PIX",
        LT_Shipper__c=shipper,
        LT_Loss_Claim__c=c["Id"],
        LT_Amount__c=amount,
        LT_Request_Date__c=dts(req_d),
        LT_Due_Date__c=dts(due_d),
        LT_Approval_Date__c=dts(req_d + datetime.timedelta(days=random.randint(1, 5))),
        LT_Approved_By__c=ADMIN,
        LT_Payee_Name__c=sname,
        LT_Payee_Document__c=f"{random.randint(10,99)}.{random.randint(100,999)}.{random.randint(100,999)}/0001-{random.randint(10,99)}",
        LT_Description__c=f"Ressarcimento ao embarcador {sname} referente ao extravio {c['Name']}, conforme apuracao da prevencao de perdas.",
        LT_Invoice_Number__c=f"RESS-{c['Name'].split('-')[1]}",
    )

# ---- 2. Pagamento a motorista (romaneio) ----
pago = [m for m in manifests if m["LT_Payment_Status__c"] == "Pago"][:9]
aprov = [m for m in manifests if m["LT_Payment_Status__c"] == "Aprovado"][:2]
for m in pago + aprov:
    drv = drivers.get(m["LT_Driver__c"], {})
    amount = round(float(m["LT_Net_Amount__c"]), 2)
    ref = datetime.date.fromisoformat(m["LT_Reference_Date__c"]) if m.get("LT_Reference_Date__c") else TODAY - datetime.timedelta(days=15)
    req_d = ref + datetime.timedelta(days=random.randint(1, 3))
    due_d = req_d + datetime.timedelta(days=random.randint(3, 10))
    is_pago = m["LT_Payment_Status__c"] == "Pago"
    add(
        LT_Request_Type__c="Pagamento a Motorista (Romaneio)",
        LT_Status__c="Paga" if is_pago else "Aprovada",
        LT_Priority__c="Normal",
        LT_Cost_Center__c="Operacao - Ultima Milha",
        LT_Payment_Method__c="PIX",
        LT_Driver__c=m["LT_Driver__c"],
        LT_Manifest__c=m["Id"],
        LT_Amount__c=amount,
        LT_Request_Date__c=dts(req_d),
        LT_Due_Date__c=dts(due_d),
        LT_Approval_Date__c=dts(req_d + datetime.timedelta(days=1)),
        LT_Approved_By__c=ADMIN,
        LT_Payee_Name__c=m["LT_Driver__r"]["Name"],
        LT_Payee_Document__c=drv.get("LT_CNPJ__c") or drv.get("LT_CPF__c") or "",
        LT_Payee_Pix_Key__c=drv.get("LT_PIX_Key__c") or "",
        LT_Description__c=f"Pagamento do romaneio {m['Name']} ao motorista {m['LT_Driver__r']['Name']} (frete de ultima milha).",
        LT_Invoice_Number__c=f"RMN-{m['Name'].split('-')[1]}",
    )

# ---- 3. Folha de pagamento ----
for i, (mes, val, st) in enumerate([("Agosto/2026", 42800.00, "Paga"), ("Setembro/2026", 43650.00, "Aprovada"),
                                    ("13o Salario - 1a parcela", 21300.00, "Em Aprovacao")]):
    req_d = TODAY - datetime.timedelta(days=random.randint(2, 25))
    add(
        LT_Request_Type__c="Folha de Pagamento (Funcionarios)",
        LT_Status__c=st,
        LT_Priority__c="Alta",
        LT_Cost_Center__c="Administrativo / RH",
        LT_Payment_Method__c="TED / Transferencia",
        LT_Amount__c=val,
        LT_Recurring__c="true",
        LT_Request_Date__c=dts(req_d),
        LT_Due_Date__c=dts(req_d + datetime.timedelta(days=5)),
        LT_Approval_Date__c=dts(req_d + datetime.timedelta(days=1)) if st in ("Paga", "Aprovada") else "",
        LT_Approved_By__c=ADMIN if st in ("Paga", "Aprovada") else "",
        LT_Payee_Name__c="Folha LogiTrack Brasil",
        LT_Description__c=f"Folha de pagamento dos funcionarios administrativos e de base - competencia {mes}.",
        LT_Invoice_Number__c=f"FOLHA-{i:02d}",
    )

# ---- 4. Insumos para base ----
supp = ["Grafica Sul Embalagens", "Distribuidora EPI Curitiba", "Papelao & Cia", "Suprimentos Log Ltda"]
for i, bs in enumerate(random.sample(bases, 3)):
    val = round(random.uniform(650, 3200), 2)
    req_d = TODAY - datetime.timedelta(days=random.randint(3, 30))
    st = random.choice(["Paga", "Aprovada", "Em Aprovacao"])
    add(
        LT_Request_Type__c="Insumos para Base/Escritorio",
        LT_Status__c=st,
        LT_Priority__c="Normal",
        LT_Cost_Center__c="Operacao - Ultima Milha",
        LT_Payment_Method__c="Boleto",
        LT_Base__c=bs["Id"],
        LT_Amount__c=val,
        LT_Request_Date__c=dts(req_d),
        LT_Due_Date__c=dts(req_d + datetime.timedelta(days=random.randint(10, 25))),
        LT_Approval_Date__c=dts(req_d + datetime.timedelta(days=2)) if st in ("Paga", "Aprovada") else "",
        LT_Approved_By__c=ADMIN if st in ("Paga", "Aprovada") else "",
        LT_Payee_Name__c=supp[i % len(supp)],
        LT_Payee_Document__c=f"{random.randint(10,99)}.{random.randint(100,999)}.{random.randint(100,999)}/0001-{random.randint(10,99)}",
        LT_Description__c=f"Compra de insumos operacionais (embalagens, EPIs, material de escritorio) para a {bs['Name']}.",
        LT_Invoice_Number__c=f"NF-{random.randint(10000,99999)}",
    )

# ---- 5. Verba para viagem / projeto ----
req_d = TODAY - datetime.timedelta(days=4)
add(
    LT_Request_Type__c="Verba para Viagem/Projeto",
    LT_Status__c="Em Aprovacao",
    LT_Priority__c="Alta",
    LT_Cost_Center__c="Expansao / Novas Bases",
    LT_Payment_Method__c="Cartao Corporativo",
    LT_Amount__c=5400.00,
    LT_Request_Date__c=dts(req_d),
    LT_Due_Date__c=dts(req_d + datetime.timedelta(days=8)),
    LT_Payee_Name__c="Bruno Tavares (Coord. Expansao)",
    LT_Description__c="Verba de viagem para prospeccao de galpao e visita a candidatos a franqueado no oeste de SC (5 dias).",
    LT_Invoice_Number__c="VIA-001",
)

# ---- 6. Abertura de galpao / nova base ----
req_d = TODAY - datetime.timedelta(days=9)
add(
    LT_Request_Type__c="Abertura de Galpao/Nova Base",
    LT_Status__c="Em Aprovacao",
    LT_Priority__c="Urgente",
    LT_Cost_Center__c="Expansao / Novas Bases",
    LT_Payment_Method__c="TED / Transferencia",
    LT_Amount__c=28900.00,
    LT_Request_Date__c=dts(req_d),
    LT_Due_Date__c=dts(req_d + datetime.timedelta(days=15)),
    LT_Payee_Name__c="Imobiliaria Oeste Catarinense",
    LT_Payee_Document__c="18.442.771/0001-90",
    LT_Description__c="Caucao e primeiro aluguel do galpao da nova base de Chapeco (SC): 3 meses de deposito + adaptacoes.",
    LT_Invoice_Number__c="EXP-CHA-01",
)

# ---- 7. Fornecedor / prestador ----
req_d = TODAY - datetime.timedelta(days=12)
add(
    LT_Request_Type__c="Fornecedor / Prestador de Servico",
    LT_Status__c="Aprovada",
    LT_Priority__c="Normal",
    LT_Cost_Center__c="Financeiro",
    LT_Payment_Method__c="Boleto",
    LT_Amount__c=6250.00,
    LT_Recurring__c="true",
    LT_Request_Date__c=dts(req_d),
    LT_Due_Date__c=dts(req_d + datetime.timedelta(days=20)),
    LT_Approval_Date__c=dts(req_d + datetime.timedelta(days=2)),
    LT_Approved_By__c=ADMIN,
    LT_Payee_Name__c="ContabilSul Assessoria Contabil",
    LT_Payee_Document__c="09.877.201/0001-45",
    LT_Description__c="Honorarios mensais do escritorio de contabilidade (competencia agosto/2026).",
    LT_Invoice_Number__c="NF-70233",
)

# ---- 8. Reembolso de despesa ----
req_d = TODAY - datetime.timedelta(days=18)
add(
    LT_Request_Type__c="Reembolso de Despesa",
    LT_Status__c="Paga",
    LT_Priority__c="Baixa",
    LT_Cost_Center__c="Comercial",
    LT_Payment_Method__c="PIX",
    LT_Amount__c=386.40,
    LT_Request_Date__c=dts(req_d),
    LT_Due_Date__c=dts(req_d + datetime.timedelta(days=7)),
    LT_Approval_Date__c=dts(req_d + datetime.timedelta(days=1)),
    LT_Approved_By__c=ADMIN,
    LT_Payee_Name__c="Ana Beatriz Correia",
    LT_Description__c="Reembolso de combustivel e pedagio em visitas a embarcadores na regiao de Joinville.",
    LT_Invoice_Number__c="REEMB-014",
)

# ---- 9. Reprovada ----
req_d = TODAY - datetime.timedelta(days=14)
add(
    LT_Request_Type__c="Insumos para Base/Escritorio",
    LT_Status__c="Reprovada",
    LT_Priority__c="Normal",
    LT_Cost_Center__c="Operacao - Ultima Milha",
    LT_Payment_Method__c="Boleto",
    LT_Amount__c=15800.00,
    LT_Request_Date__c=dts(req_d),
    LT_Due_Date__c=dts(req_d + datetime.timedelta(days=20)),
    LT_Payee_Name__c="MegaOffice Distribuidora",
    LT_Description__c="Compra de 40 coletores de codigo de barras novos para as bases da regional.",
    LT_Rejection_Reason__c="Reprovado pela diretoria: volume acima do previsto no orcamento do trimestre. Reapresentar em 3 lotes menores no proximo ciclo.",
    LT_Invoice_Number__c="COT-9981",
)

# ---- 10. Rascunho ----
add(
    LT_Request_Type__c="Outro",
    LT_Status__c="Rascunho",
    LT_Priority__c="Baixa",
    LT_Cost_Center__c="Administrativo / RH",
    LT_Payment_Method__c="PIX",
    LT_Amount__c=1200.00,
    LT_Request_Date__c=dts(TODAY),
    LT_Due_Date__c=dts(TODAY + datetime.timedelta(days=15)),
    LT_Payee_Name__c="A definir",
    LT_Invoice_Number__c="RASC-001",
)

keys = []
for r in rows:
    for k in r:
        if k not in keys:
            keys.append(k)
path = os.path.join(OUT, "payment_requests.csv")
with open(path, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=keys)
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k, "") for k in keys})

from collections import Counter
print("payment requests:", len(rows))
print(Counter(r["LT_Status__c"] for r in rows))
print(Counter(r["LT_Request_Type__c"] for r in rows))
print("->", path)

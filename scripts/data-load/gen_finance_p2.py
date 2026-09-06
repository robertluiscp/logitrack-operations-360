#!/usr/bin/env python3
"""Module J phase 2: LT_Payment__c + LT_Expense__c sample data."""
import json, csv, random, datetime, os

SCR = r"C:\Users\ROBERT~1\AppData\Local\Temp\claude\C--Users-Robert-Luis-Desktop-LogiTrack-SFDX\9f02e204-5a31-476e-ba33-4a01f545d640\scratchpad"
random.seed(361)
TODAY = datetime.date(2026, 9, 6)
ADMIN = "005g8000004iYenAAE"

pr = json.load(open(os.path.join(SCR, "j_pr.json"), encoding="utf-8"))["result"]["records"]
bases = json.load(open(os.path.join(SCR, "j_bases.json"), encoding="utf-8"))["result"]["records"]
by_inv = {p["LT_Invoice_Number__c"]: p for p in pr}

def d(s): return datetime.date.fromisoformat(s[:10]) if s else None
def dts(x): return x.isoformat()

BANKS = ["Conta Corrente - Itau", "Conta Corrente - Bradesco", "Conta Pagamentos - Nubank PJ"]
pays = []

for p in pr:
    method = {"PIX": "PIX", "TED / Transferencia": "TED / Transferencia", "Boleto": "Boleto"}.get(
        p.get("LT_Request_Type__c"), "PIX")
    appr = d(p.get("LT_Approval_Date__c")) or (TODAY - datetime.timedelta(days=10))
    due = d(p.get("LT_Due_Date__c")) or (appr + datetime.timedelta(days=7))
    if p["LT_Status__c"] == "Paga":
        pdate = appr + datetime.timedelta(days=random.randint(1, max(1, (due - appr).days)))
        if pdate > TODAY:
            pdate = TODAY - datetime.timedelta(days=random.randint(0, 3))
        mth = random.choice(["PIX", "PIX", "TED / Transferencia", "Boleto"])
        fee = 0 if mth == "PIX" else round(random.uniform(1.9, 8.5), 2)
        reconciled = random.random() < 0.8
        rec_date = pdate + datetime.timedelta(days=random.randint(1, 6))
        if rec_date > TODAY:
            reconciled = False
        pays.append({
            "LT_Payment_Request__c": p["Id"],
            "LT_Amount__c": p["LT_Amount__c"],
            "LT_Payment_Date__c": dts(pdate),
            "LT_Status__c": "Confirmado",
            "LT_Payment_Method__c": mth,
            "LT_Bank_Account__c": random.choice(BANKS),
            "LT_Transaction_Id__c": f"TX{pdate.strftime('%Y%m%d')}{random.randint(100000,999999)}",
            "LT_Paid_By__c": ADMIN,
            "LT_Fee_Amount__c": fee,
            "LT_Reconciled__c": "true" if reconciled else "false",
            "LT_Reconciliation_Date__c": dts(rec_date) if reconciled else "",
            "LT_Notes__c": "Pagamento liquidado e conferido contra o extrato." if reconciled else "Pagamento liquidado, conciliacao pendente.",
        })

# two scheduled payments against "Aprovada" requests (kept Aprovada: not Confirmado -> roll-up ignores)
for inv in ["FOLHA-01", "NF-70233"]:
    p = by_inv[inv]
    appr = d(p.get("LT_Approval_Date__c")) or TODAY
    pays.append({
        "LT_Payment_Request__c": p["Id"],
        "LT_Amount__c": p["LT_Amount__c"],
        "LT_Payment_Date__c": dts(d(p["LT_Due_Date__c"])),
        "LT_Status__c": "Agendado",
        "LT_Payment_Method__c": "TED / Transferencia",
        "LT_Bank_Account__c": "Conta Corrente - Itau",
        "LT_Paid_By__c": ADMIN,
        "LT_Notes__c": "Pagamento agendado para a data de vencimento.",
    })

order = ["LT_Payment_Request__c", "LT_Amount__c", "LT_Payment_Date__c", "LT_Status__c", "LT_Payment_Method__c",
         "LT_Bank_Account__c", "LT_Transaction_Id__c", "LT_Paid_By__c", "LT_Fee_Amount__c", "LT_Reconciled__c",
         "LT_Reconciliation_Date__c", "LT_Notes__c"]
with open(os.path.join(SCR, "payments.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=order)
    w.writeheader()
    for r in pays:
        w.writerow({k: r.get(k, "") for k in order})

# ---------------- Expenses ----------------
exp = []
def E(**kw):
    kw.setdefault("OwnerId", ADMIN)
    kw.setdefault("LT_Recurring__c", "false")
    kw.setdefault("LT_Pass_Through__c", "false")
    exp.append(kw)

MONTHS = ["2026-06", "2026-07", "2026-08"]
bs = random.sample(bases, 8)

# recurring base costs
for i, b in enumerate(bs[:4]):
    for m in MONTHS:
        pass
for i, b in enumerate(bs[:3]):
    E(LT_Expense_Category__c="Aluguel de Base/Galpao", LT_Status__c="Paga", LT_Cost_Center__c="Operacao - Ultima Milha",
      LT_Amount__c=round(random.uniform(2800, 6500), 2), LT_Expense_Date__c="2026-08-05", LT_Competency_Month__c="2026-08",
      LT_Base__c=b["Id"], LT_Supplier__c="Imobiliaria local", LT_Invoice_Number__c=f"ALUG-{i:03d}", LT_Recurring__c="true",
      LT_Description__c=f"Aluguel mensal do imovel da {b['Name']}.")

for i, b in enumerate(bs[3:6]):
    E(LT_Expense_Category__c="Energia / Agua / Internet", LT_Status__c=random.choice(["Paga", "Realizada"]),
      LT_Cost_Center__c="Operacao - Ultima Milha", LT_Amount__c=round(random.uniform(380, 1400), 2),
      LT_Expense_Date__c="2026-08-12", LT_Competency_Month__c="2026-08", LT_Base__c=b["Id"],
      LT_Supplier__c="Concessionarias / provedores", LT_Invoice_Number__c=f"UTIL-{i:03d}", LT_Recurring__c="true",
      LT_Description__c=f"Contas de energia, agua e internet da {b['Name']}.")

E(LT_Expense_Category__c="Combustivel", LT_Status__c="Paga", LT_Cost_Center__c="Operacao - Primeira Milha",
  LT_Amount__c=8940.55, LT_Expense_Date__c="2026-08-28", LT_Competency_Month__c="2026-08",
  LT_Supplier__c="Rede de Postos Ipiranga", LT_Invoice_Number__c="COMB-0826", LT_Recurring__c="true",
  LT_Description__c="Combustivel da frota de transferencia (SC/MR) da regional Sul em agosto.")
E(LT_Expense_Category__c="Combustivel", LT_Status__c="Realizada", LT_Cost_Center__c="Operacao - Primeira Milha",
  LT_Amount__c=7710.20, LT_Expense_Date__c="2026-07-30", LT_Competency_Month__c="2026-07",
  LT_Supplier__c="Rede de Postos Ipiranga", LT_Invoice_Number__c="COMB-0726", LT_Recurring__c="true",
  LT_Description__c="Combustivel da frota de transferencia da regional Sul em julho.")

E(LT_Expense_Category__c="Manutencao de Veiculos", LT_Status__c="Paga", LT_Cost_Center__c="Cadastro / Frota",
  LT_Amount__c=3120.00, LT_Expense_Date__c="2026-08-18", LT_Competency_Month__c="2026-08",
  LT_Supplier__c="Oficina Diesel Sul", LT_Invoice_Number__c="MANUT-441",
  LT_Description__c="Revisao preventiva e troca de pneus de dois caminhoes de transferencia.")

E(LT_Expense_Category__c="Folha / Encargos", LT_Status__c="Paga", LT_Cost_Center__c="Administrativo / RH",
  LT_Amount__c=42800.00, LT_Expense_Date__c="2026-08-30", LT_Competency_Month__c="2026-08",
  LT_Payment_Request__c=by_inv["FOLHA-00"]["Id"], LT_Supplier__c="Folha LogiTrack Brasil", LT_Recurring__c="true",
  LT_Description__c="Folha de pagamento de agosto/2026 (reconhecimento contabil da despesa).")

E(LT_Expense_Category__c="Material de Embalagem", LT_Status__c="Paga", LT_Cost_Center__c="Operacao - Ultima Milha",
  LT_Amount__c=3192.10, LT_Expense_Date__c="2026-08-22", LT_Competency_Month__c="2026-08",
  LT_Payment_Request__c=by_inv["NF-90418"]["Id"], LT_Base__c=bs[0]["Id"], LT_Supplier__c="Papelao & Cia",
  LT_Invoice_Number__c="NF-90418", LT_Description__c="Caixas, plastico bolha e fitas para as bases da regional.")

E(LT_Expense_Category__c="Servicos de Terceiros", LT_Status__c="Realizada", LT_Cost_Center__c="Financeiro",
  LT_Amount__c=6250.00, LT_Expense_Date__c="2026-08-31", LT_Competency_Month__c="2026-08",
  LT_Payment_Request__c=by_inv["NF-70233"]["Id"], LT_Supplier__c="ContabilSul Assessoria Contabil",
  LT_Invoice_Number__c="NF-70233", LT_Recurring__c="true", LT_Description__c="Honorarios contabeis de agosto/2026.")

E(LT_Expense_Category__c="Frete / Transferencia (SC/MR)", LT_Status__c="Realizada", LT_Cost_Center__c="Operacao - Primeira Milha",
  LT_Amount__c=12430.00, LT_Expense_Date__c="2026-08-31", LT_Competency_Month__c="2026-08", LT_Pass_Through__c="true",
  LT_Supplier__c="Motoristas MR/Coleta (repasse)", LT_Description__c="Repasse de frete de primeira milha aos motoristas MR e de coleta em agosto.")

E(LT_Expense_Category__c="Ressarcimento a Embarcador", LT_Status__c="Paga", LT_Cost_Center__c="Operacao - Ultima Milha",
  LT_Amount__c=4863.00, LT_Expense_Date__c="2026-08-25", LT_Competency_Month__c="2026-08",
  LT_Invoice_Number__c="RESS-AGO-2026", LT_Supplier__c="Diversos embarcadores",
  LT_Description__c="Total de ressarcimentos por extravio pagos a embarcadores em agosto (prevencao de perdas).")

E(LT_Expense_Category__c="Viagem / Diaria", LT_Status__c="Prevista", LT_Cost_Center__c="Expansao / Novas Bases",
  LT_Amount__c=5400.00, LT_Expense_Date__c="2026-09-15", LT_Competency_Month__c="2026-09",
  LT_Payment_Request__c=by_inv["VIA-001"]["Id"], LT_Supplier__c="Viagem prospeccao oeste SC",
  LT_Description__c="Diarias e deslocamento da viagem de prospeccao de galpao no oeste de SC.")

E(LT_Expense_Category__c="Aluguel de Base/Galpao", LT_Status__c="Prevista", LT_Cost_Center__c="Expansao / Novas Bases",
  LT_Amount__c=28900.00, LT_Expense_Date__c="2026-09-20", LT_Competency_Month__c="2026-09",
  LT_Payment_Request__c=by_inv["EXP-CHA-01"]["Id"], LT_Supplier__c="Imobiliaria Oeste Catarinense",
  LT_Description__c="Caucao e primeiro aluguel do galpao da nova base de Chapeco.")

E(LT_Expense_Category__c="Equipamentos / EPI", LT_Status__c="Cancelada", LT_Cost_Center__c="Operacao - Ultima Milha",
  LT_Amount__c=15800.00, LT_Expense_Date__c="2026-08-14", LT_Competency_Month__c="2026-08",
  LT_Supplier__c="MegaOffice Distribuidora", LT_Description__c="Compra de coletores nova - cancelada apos reprovacao da solicitacao COT-9981.")

order_e = ["LT_Expense_Category__c", "LT_Status__c", "LT_Cost_Center__c", "LT_Amount__c", "LT_Expense_Date__c",
           "LT_Competency_Month__c", "LT_Base__c", "LT_Payment_Request__c", "LT_Supplier__c", "LT_Invoice_Number__c",
           "LT_Recurring__c", "LT_Pass_Through__c", "LT_Description__c", "OwnerId"]
with open(os.path.join(SCR, "expenses.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=order_e)
    w.writeheader()
    for r in exp:
        w.writerow({k: r.get(k, "") for k in order_e})

from collections import Counter
print("payments:", len(pays), Counter(p["LT_Status__c"] for p in pays))
print("expenses:", len(exp), Counter(e["LT_Status__c"] for e in exp))

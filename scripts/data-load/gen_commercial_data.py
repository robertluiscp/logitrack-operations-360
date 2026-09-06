#!/usr/bin/env python3
import csv, random, os
random.seed(7)
OUT = r"C:\Users\ROBERT~1\AppData\Local\Temp\claude\C--Users-Robert-Luis-Desktop-LogiTrack-SFDX\9f02e204-5a31-476e-ba33-4a01f545d640\scratchpad"
RT_SHIPPER = "012g...SET"  # replaced below via arg
REP_ID = "005g8000009JzgwAAC"  # Ana Beatriz Correia
ADMIN_ID = "005g8000004iYenAAE"

import sys
RT_SHIPPER = sys.argv[1]

# (name, segment, status, vol, pickup, marketplaces, city, uf, site)
shippers = [
 ("Xitou Marketplace", "Marketplace", "Ativo", 48000, "Coleta no Seller", "Xitou, Compria", "Curitiba", "PR", "www.xitou.com.br"),
 ("Compria Marketplace", "Marketplace", "Ativo", 65000, "Coleta no Seller", "Compria", "Sao Jose dos Pinhais", "PR", "www.compria.com.br"),
 ("ShopLivre", "Marketplace", "Ativo", 39000, "Ambos", "ShopLivre", "Porto Alegre", "RS", "www.shoplivre.com.br"),
 ("MegaShop BR", "Marketplace", "Em Homologação", 27000, "Coleta no Seller", "MegaShop", "Joinville", "SC", "www.megashop.com.br"),
 ("VendeMais Online", "Marketplace", "Ativo", 31000, "Coleta no DropOff", "VendeMais", "Blumenau", "SC", "www.vendemais.com.br"),
 ("ModaMix Confeccoes", "E-commerce Próprio", "Ativo", 12000, "Coleta no Seller", "Loja propria, Xitou", "Cianorte", "PR", "www.modamix.com.br"),
 ("TechNova BR", "E-commerce Próprio", "Ativo", 8600, "Coleta no Seller", "Loja propria", "Florianopolis", "SC", "www.technova.com.br"),
 ("Casa e Cor Online", "E-commerce Próprio", "Ativo", 5400, "Coleta no DropOff", "Loja propria, Compria", "Caxias do Sul", "RS", "www.casaecor.com.br"),
 ("PetLar Suprimentos", "E-commerce Próprio", "Ativo", 9100, "Coleta no Seller", "Loja propria, ShopLivre", "Londrina", "PR", "www.petlar.com.br"),
 ("SuplementaBR", "E-commerce Próprio", "Ativo", 7300, "Coleta no Seller", "Loja propria", "Maringa", "PR", "www.suplementabr.com.br"),
 ("Calcados Prime", "Varejo", "Ativo", 4200, "Coleta no DropOff", "Loja propria, Xitou", "Novo Hamburgo", "RS", "www.calcadosprime.com.br"),
 ("Bella Cosmeticos", "Varejo", "Em Homologação", 3100, "Coleta no DropOff", "Compria", "Chapeco", "SC", "www.bellacosmeticos.com.br"),
 ("Livraria Pagina Viva", "Varejo", "Ativo", 2600, "Coleta no DropOff", "ShopLivre", "Pelotas", "RS", "www.paginaviva.com.br"),
 ("AutoPecas do Sul", "Distribuidor", "Ativo", 6800, "Coleta no Seller", "Loja propria, Compria", "Cascavel", "PR", "www.autopecasdosul.com.br"),
 ("FerramentasMax", "Distribuidor", "Ativo", 5900, "Coleta no Seller", "Xitou", "Gravatai", "RS", "www.ferramentasmax.com.br"),
 ("Distribuidora Farmasul", "Distribuidor", "Ativo", 15400, "Coleta no Seller", "Loja propria", "Sao Jose", "SC", "www.farmasul.com.br"),
 ("Moveis Serra Sul", "Indústria / Fabricante", "Ativo", 3400, "Coleta no Seller", "Loja propria, Xitou", "Bento Goncalves", "RS", "www.moveisserrasul.com.br"),
 ("Ceramica Paranaense", "Indústria / Fabricante", "Inativo", 1800, "Coleta no Seller", "Compria", "Ponta Grossa", "PR", "www.ceramicaparanaense.com.br"),
 ("Confeccoes Vale do Itajai", "Indústria / Fabricante", "Ativo", 4700, "Coleta no Seller", "Loja propria", "Brusque", "SC", "www.valedoitajai.ind.br"),
 ("Joao Pedro Nogueira", "Pessoa Física (C2C)", "Ativo", 30, "Coleta no DropOff", "Venda de Etiqueta", "Curitiba", "PR", ""),
 ("Marilia Fontes Ateliê", "Pessoa Física (C2C)", "Ativo", 45, "Coleta no DropOff", "Venda de Etiqueta", "Torres", "RS", ""),
 ("Studio Aurora Papelaria", "Pessoa Física (C2C)", "Em Homologação", 20, "Coleta no DropOff", "Venda de Etiqueta", "Itajai", "SC", ""),
]

def cnpj(i):
    a = 20 + (i % 70); b = (i*271) % 1000; c = (i*733) % 1000; d = (i*97) % 100
    return f"{a:02d}.{b:03d}.{c:03d}/0001-{d:02d}"

first_names = ["Carlos","Fernanda","Rafael","Juliana","Bruno","Camila","Diego","Patricia","Thiago","Aline","Marcos","Leticia","Rodrigo","Bianca","Gustavo","Renata"]
last_names = ["Silva","Souza","Oliveira","Pereira","Costa","Almeida","Ribeiro","Carvalho","Gomes","Martins","Rocha","Barbosa","Teixeira","Moraes"]

acc_rows = []
con_rows = []
agr_rows = []
plan = []  # (cnpj, status, vol, since)
for i, s in enumerate(shippers, start=1):
    name, seg, status, vol, pickup, mkts, city, uf, site = s
    is_pf = seg == "Pessoa Física (C2C)"
    doc = "" if is_pf else cnpj(i)
    since = ""
    if status in ("Ativo", "Inativo"):
        y = random.randint(2019, 2024); m = random.randint(1,12); d = random.randint(1,28)
        since = f"{y}-{m:02d}-{d:02d}"
    acc_rows.append({
        "Name": name, "RecordTypeId": RT_SHIPPER,
        "LT_Shipper_Segment__c": seg, "LT_Shipper_Status__c": status,
        "LT_Pickup_Type__c": pickup, "LT_Monthly_Volume_Estimate__c": vol,
        "LT_Origin_Marketplaces__c": mkts, "LT_Shipper_Since__c": since,
        "LT_CNPJ__c": doc,
        "LT_Commercial_Rep__c": REP_ID if status == "Ativo" else "",
        "OwnerId": REP_ID,
        "Phone": f"(4{random.randint(1,9)}) 3{random.randint(100,999)}-{random.randint(1000,9999)}",
        "Website": site,
        "BillingCity": city, "BillingState": uf, "BillingCountry": "Brasil",
        "Industry": "Transportation",
        "Description": f"Embarcador {seg} atendido pela LogiTrack. Canais: {mkts}.",
    })
    plan.append((doc if doc else name, status, vol, since, name))
    # contacts
    ncon = 0 if is_pf else 2
    roles = ["Comercial", "Financeiro", "Operacional / Logistica", "Diretoria"]
    for c in range(ncon):
        fn = random.choice(first_names); ln = random.choice(last_names)
        con_rows.append({
            "FirstName": fn, "LastName": ln,
            "Account.LT_CNPJ__c": doc,
            "LT_Contact_Role__c": roles[c % len(roles)],
            "Email": f"{fn.lower()}.{ln.lower()}@{(site or 'cliente').replace('www.','')}".replace(" ",""),
            "Phone": f"(4{random.randint(1,9)}) 9{random.randint(1000,9999)}-{random.randint(1000,9999)}",
            "Title": roles[c % len(roles)],
        })
    # agreement for active shippers
    if status == "Ativo" and not is_pf:
        ppp = round(random.uniform(4.5, 12.0), 2)
        st = since or "2022-01-01"
        agr_rows.append({
            "LT_Shipper__r.LT_CNPJ__c": doc,
            "LT_Agreement_Status__c": "Vigente",
            "LT_Start_Date__c": st,
            "LT_End_Date__c": "",
            "LT_Price_Per_Package__c": ppp,
            "LT_Minimum_Monthly_Volume__c": int(vol * 0.7),
            "LT_Payment_Term_Days__c": random.choice([15, 30, 45]),
            "LT_SLA_Target__c": round(random.choice([0.90, 0.92, 0.95, 0.97]), 2),
            "LT_Agreement_Commercial_Rep__c": REP_ID,
        })

def write(fn, rows):
    keys = list({k for r in rows for k in r})
    # keep a stable order: first row's keys then extras
    keys = list(rows[0].keys()) + [k for k in keys if k not in rows[0]]
    with open(os.path.join(OUT, fn), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in keys})

write("shippers.csv", acc_rows)
write("shipper_contacts.csv", con_rows)
write("shipper_agreements.csv", agr_rows)

import json
json.dump(plan, open(os.path.join(OUT, "billing_plan.json"), "w"))
print(f"shippers={len(acc_rows)} contacts={len(con_rows)} agreements={len(agr_rows)}")

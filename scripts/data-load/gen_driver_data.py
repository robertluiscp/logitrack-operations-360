#!/usr/bin/env python3
import csv, random, datetime, os
random.seed(23)
OUT = os.path.dirname(os.path.abspath(__file__))
RAFAEL = "005g8000009K1pBAAS"
TODAY = datetime.date(2026, 9, 6)

RT = {
 "TAC": "012.SET.TAC", "MEI": "012.SET.MEI", "ETC": "012.SET.ETC",
 "Coleta": "012.SET.COL", "MR": "012.SET.MR",
}
import sys
# args: TAC MEI ETC Coleta MR record type ids
for i, k in enumerate(["TAC", "MEI", "ETC", "Coleta", "MR"]):
    RT[k] = sys.argv[i + 1]

BASES = ["CWB 02-PR", "ARP-PR", "CAC-PR", "ALM-PR", "CIC-PR", "CLB-PR", "CPM-PR", "LDB-PR", "PGZ-PR", "PNG-PR",
         "F ARP-PR", "F CWB-PR", "F LOD-PR", "F MGR-PR",
         "BNU-SC", "BIG-SC", "CCM-SC", "JOI-SC", "ITJ-SC", "LGS-SC", "TUB-SC", "SJE-SC",
         "F JOI-SC", "F BLU-SC", "F CHA-SC",
         "POA-RS", "CXJ-RS", "GRV-RS", "NHG-RS", "PEL-RS", "SCU-RS", "STR-RS",
         "F POA-RS", "F CNS-RS", "F PET-RS"]

FIRST = ["Adriano", "Everson", "Gustavo", "Rudinei", "Marcelo", "Anderson", "Cleiton", "Fabio", "Jonas",
         "Leandro", "Mauricio", "Rogerio", "Sidnei", "Valdir", "Wagner", "Alex", "Bruno", "Cesar",
         "Diego", "Edson", "Fernando", "Gilberto", "Hugo", "Ivan", "Jefferson", "Kleber", "Luciano",
         "Marcos", "Nelson", "Otavio", "Paulo", "Rafael", "Sergio", "Tiago", "Vinicius", "Willian",
         "Juliana", "Fernanda", "Patricia", "Camila", "Aline", "Sandra"]
LAST = ["Souza", "Costa", "Oliveira", "Santos", "Pereira", "Lima", "Ferreira", "Alves", "Ribeiro",
        "Carvalho", "Gomes", "Martins", "Rocha", "Nascimento", "Araujo", "Barbosa", "Cardoso",
        "Correia", "Cunha", "Dias", "Fernandes", "Freitas", "Machado", "Moraes", "Nunes", "Pinto",
        "Ramos", "Teixeira", "Vieira", "Moreira", "da Silva", "de Andrade", "Bittencourt"]

def cpf(i):
    return f"{100+i:03d}.{(i*37)%1000:03d}.{(i*71)%1000:03d}-{(i*13)%100:02d}"
def cnpj(i):
    return f"{30+(i%60):02d}.{(i*211)%1000:03d}.{(i*577)%1000:03d}/0001-{(i*29)%100:02d}"

CNH_CAT = {"TAC": ["B", "AB", "C"], "MEI": ["A", "AB", "B"], "ETC": ["C", "D", "E"],
           "Coleta": ["B", "AB", "C"], "MR": ["C", "D", "E"]}

PLAN = [("TAC", 12), ("MEI", 10), ("ETC", 5), ("Coleta", 9), ("MR", 5)]

drivers = []   # (row, ext_cpf, category, status, base)
i = 0
etc_cpfs = []
for cat, n in PLAN:
    for _ in range(n):
        i += 1
        name = f"{random.choice(FIRST)} {random.choice(LAST)}"
        doc = cpf(i)
        base = random.choice(BASES)
        # status mix
        r = random.random()
        if r < 0.72:
            status = "Ativo"
        elif r < 0.82:
            status = "Documentacao Pendente"
        elif r < 0.9:
            status = "Em Cadastro"
        elif r < 0.96:
            status = "Suspenso"
        else:
            status = "Inativo"
        # CNH expiration
        rr = random.random()
        if rr < 0.08:
            cnh_exp = TODAY - datetime.timedelta(days=random.randint(5, 400))   # vencida
            if status == "Ativo":
                status = "Suspenso"   # cannot be active with expired CNH
        elif rr < 0.22:
            cnh_exp = TODAY + datetime.timedelta(days=random.randint(3, 29))     # a vencer
        else:
            cnh_exp = TODAY + datetime.timedelta(days=random.randint(60, 1800))
        onb = ""
        if status in ("Ativo",):
            onb = (TODAY - datetime.timedelta(days=random.randint(60, 1400))).isoformat()
        row = {
            "Name": name, "RecordTypeId": RT[cat],
            "LT_CPF__c": doc,
            "LT_CNPJ__c": cnpj(i) if cat in ("MEI", "ETC") else "",
            "LT_CNH_Number__c": f"{random.randint(10**10, 10**11-1)}",
            "LT_CNH_Category__c": random.choice(CNH_CAT[cat]),
            "LT_CNH_Expiration__c": cnh_exp.isoformat(),
            "LT_Home_Base__r.Unit_Code__c": base,
            "LT_Driver_Status__c": status,
            "LT_Onboarding_Date__c": onb,
            "LT_Phone__c": f"(4{random.randint(1,9)}) 9{random.randint(1000,9999)}-{random.randint(1000,9999)}",
            "LT_PIX_Key__c": doc if random.random() < 0.6 else f"{random.choice(FIRST).lower()}.{random.choice(LAST).split()[-1].lower()}@email.com",
            "OwnerId": RAFAEL,
        }
        drivers.append((row, doc, cat, status, base))
        if cat == "ETC":
            etc_cpfs.append(doc)

# assign some auxiliaries to ETC leads (Coleta / MEI aux under ETC)
for row, doc, cat, status, base in drivers:
    if cat in ("MEI", "Coleta") and etc_cpfs and random.random() < 0.25:
        row["LT_Lead_Driver__r.LT_CPF__c"] = random.choice(etc_cpfs)

keys = list(drivers[0][0].keys()) + ["LT_Lead_Driver__r.LT_CPF__c"]
with open(f"{OUT}/drivers.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=keys)
    w.writeheader()
    for row, *_ in drivers:
        w.writerow({k: row.get(k, "") for k in keys})

# ---------------- vehicles ----------------
VTYPE = {"TAC": ["Fiorino / Furgao Pequeno", "Carro de Passeio"], "MEI": ["Moto", "Carro de Passeio", "Bicicleta / Eletrica"],
         "ETC": ["Van", "VUC", "Caminhao 3/4"], "Coleta": ["Fiorino / Furgao Pequeno", "Van", "VUC"],
         "MR": ["VUC", "Caminhao 3/4", "Caminhao Toco"]}
CAP = {"Moto": 60, "Bicicleta / Eletrica": 30, "Carro de Passeio": 120, "Fiorino / Furgao Pequeno": 350,
       "Van": 900, "VUC": 1600, "Caminhao 3/4": 2400, "Caminhao Toco": 3000}
BRANDS = {"Moto": ["Honda CG 160", "Yamaha Factor 150"], "Bicicleta / Eletrica": ["Caloi E-Vibe", "Sense Impulse"],
          "Carro de Passeio": ["VW Gol", "Fiat Argo", "Chevrolet Onix"], "Fiorino / Furgao Pequeno": ["Fiat Fiorino", "VW Saveiro"],
          "Van": ["Renault Master", "Mercedes Sprinter", "Fiat Ducato"], "VUC": ["Hyundai HR", "Iveco Daily", "JAC T6"],
          "Caminhao 3/4": ["VW Delivery 6.160", "Mercedes Accelo 815"], "Caminhao Toco": ["VW Constellation 17.190", "Volvo VM 220"]}

def plate(i):
    L = "ABCDEFGHJKLMNPRSTUVWXYZ"
    if i % 2 == 0:  # Mercosul
        return f"{random.choice(L)}{random.choice(L)}{random.choice(L)}{random.randint(0,9)}{random.choice(L)}{random.randint(0,9)}{random.randint(0,9)}"
    return f"{random.choice(L)}{random.choice(L)}{random.choice(L)}{random.randint(1000,9999)}"

veh = []
vi = 0
for row, doc, cat, status, base in drivers:
    if status in ("Ativo", "Suspenso", "Documentacao Pendente") and random.random() < 0.82:
        vi += 1
        vt = random.choice(VTYPE[cat])
        yr = random.randint(2012, 2025)
        rr = random.random()
        crlv = (TODAY + datetime.timedelta(days=random.randint(-60, 400))).isoformat()
        vstatus = "Ativo" if status == "Ativo" else random.choice(["Ativo", "Em Manutencao", "Inativo"])
        veh.append({
            "LT_Plate__c": plate(vi),
            "LT_Vehicle_Type__c": vt,
            "LT_Brand_Model__c": random.choice(BRANDS[vt]),
            "LT_Model_Year__c": yr,
            "LT_Cargo_Capacity_M3__c": round(CAP[vt] / 250.0, 2),
            "LT_Cargo_Capacity_Packages__c": CAP[vt] + random.randint(-40, 40) if vt not in ("Moto", "Bicicleta / Eletrica") else min(80, CAP[vt]),
            "LT_Owner_Type__c": random.choice(["Proprio do Motorista", "Alugado", "Da Empresa", "Do Parceiro Operacional"]),
            "LT_Driver__r.LT_CPF__c": doc,
            "LT_CRLV_Expiration__c": crlv,
            "LT_Insurance_Expiration__c": (TODAY + datetime.timedelta(days=random.randint(-30, 500))).isoformat() if random.random() < 0.7 else "",
            "LT_Vehicle_Status__c": vstatus,
            "OwnerId": RAFAEL,
        })
with open(f"{OUT}/vehicles.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(veh[0].keys()))
    w.writeheader(); w.writerows(veh)

# ---------------- documents ----------------
docs = []
DTYPES_BASE = ["CNH", "CPF", "Comprovante de Residencia"]
for row, doc, cat, status, base in drivers:
    types = list(DTYPES_BASE)
    if cat in ("MEI", "ETC"):
        types.append("Contrato MEI (CCMEI)")
    if cat in ("ETC", "MR"):
        types.append("RNTRC / ANTT")
    if cat in ("TAC", "ETC", "MR"):
        types.append("Curso MOPP")
    for dt in types:
        exp = ""
        if dt == "CNH":
            exp = row["LT_CNH_Expiration__c"]
        elif dt in ("Contrato MEI (CCMEI)", "RNTRC / ANTT", "Curso MOPP"):
            exp = (TODAY + datetime.timedelta(days=random.randint(-90, 900))).isoformat()
        verified = status in ("Ativo", "Suspenso") or random.random() < 0.3
        docs.append({
            "LT_Driver__r.LT_CPF__c": doc,
            "LT_Document_Type__c": dt,
            "LT_Document_Number__c": f"{random.randint(10**6, 10**9)}",
            "LT_Issue_Date__c": (TODAY - datetime.timedelta(days=random.randint(120, 2500))).isoformat(),
            "LT_Expiration_Date__c": exp,
            "LT_Verified__c": str(verified).lower(),
            "LT_Verified_By__c": RAFAEL if verified else "",
            "LT_Verification_Date__c": (TODAY - datetime.timedelta(days=random.randint(1, 200))).isoformat() if verified else "",
        })
with open(f"{OUT}/driver_documents.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(docs[0].keys()))
    w.writeheader(); w.writerows(docs)

print(f"drivers={len(drivers)} vehicles={len(veh)} documents={len(docs)}")

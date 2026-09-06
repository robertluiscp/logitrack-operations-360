#!/usr/bin/env python3
import re, csv, random, unicodedata

random.seed(42)
SRC = r"C:\Users\Robert Luis\Downloads\Bases e Cidades.txt"
OUT = r"C:\Users\ROBERT~1\AppData\Local\Temp\claude\C--Users-Robert-Luis-Desktop-LogiTrack-SFDX\9f02e204-5a31-476e-ba33-4a01f545d640\scratchpad"

CITY_FIX = {
    "balneario camboriu": "Balneário Camboriú",
    "araucaria": "Araucária",
    "foz do iguacu": "Foz do Iguaçu",
    "frederico westephalen": "Frederico Westphalen",
    "dois vizinhos": "Dois Vizinhos",
    "itajai": "Itajaí",
    "jandaia": "Jandaia do Sul",
    "jaragua do sul": "Jaraguá do Sul",
    "pereci novo": "Pareci Novo",
    "paranavai": "Paranavaí",
    "sao matheus do sul": "São Mateus do Sul",
    "xenxere": "Xanxerê",
    "imbutuba": "Imbituba",
    "florianopolis": "Florianópolis",
    "santa rita": "Santa Rita",
    "cruz alta": "Cruz Alta",
}

SMALL = {"do","da","de","dos","das","e"}

def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def title_pt(s):
    words = s.split()
    out = []
    for i, w in enumerate(words):
        lw = w.lower()
        if i > 0 and lw in SMALL:
            out.append(lw)
        else:
            out.append(lw[:1].upper() + lw[1:])
    return ' '.join(out)

def clean_city(raw):
    key = strip_accents(raw).lower().strip()
    key = re.sub(r'\s+', ' ', key)
    if key in CITY_FIX:
        return CITY_FIX[key]
    return title_pt(re.sub(r'\s+', ' ', raw.strip()))

rows = []
seen = set()
with open(SRC, encoding='utf-8') as f:
    for ln in f:
        ln = ln.rstrip('\n')
        if not ln.strip():
            continue
        # drop leading line number if the Read tool style leaked in (it won't from raw file)
        m = re.match(r'^(?P<code>.+?)\s*-\s*(?P<uf>PR|SC|RS)\b[\s]+(?P<city>.+)$', ln)
        if not m:
            # special rows without -UF (e.g. "PR SJS\tSao Jose dos Pinhais")
            print("SKIP (no -UF):", repr(ln))
            continue
        codepart = re.sub(r'\s+', ' ', m.group('code').strip())
        uf = m.group('uf')
        city = clean_city(m.group('city'))
        code = f"{codepart}-{uf}"
        if code in seen:
            print("DUP:", code)
            continue
        seen.add(code)
        is_fr = strip_accents(code).upper().startswith("F ")
        rows.append({"code": code, "uf": uf, "city": city, "fr": is_fr, "codepart": codepart})

# Exclude the CD that appears in the file
rows = [r for r in rows if r["code"] not in ("PR SJS",)]

print(f"\nTotal bases: {len(rows)}")
fr = [r for r in rows if r["fr"]]
own = [r for r in rows if not r["fr"]]
print(f"Franqueadas: {len(fr)}  Próprias: {len(own)}")
for uf in ("PR","SC","RS"):
    print(f"  {uf}: {sum(1 for r in rows if r['uf']==uf)}")

CD = {"PR": "PR SJS", "SC": "SC BNU", "RS": "RS NSR"}

def cnpj(i):
    a = 10 + (i % 90)
    b = (i * 137) % 1000
    c = (i * 911) % 1000
    d = (i * 53) % 100
    return f"{a:02d}.{b:03d}.{c:03d}/0001-{d:02d}"

# franchise partner accounts
with open(f"{OUT}/franchise_partners.csv", "w", newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(["Name","RecordTypeId","LT_Operating_Partner_Type__c","LT_CNPJ__c","LT_Partner_Status__c","Type","Description"])
    for i, r in enumerate(fr, start=1):
        name = f"Franquia {r['city']} ({r['codepart']})"
        w.writerow([name, "012g8000002pYbBAAU", "Franqueado", cnpj(i), "Ativo", "Franquia",
                    f"Parceiro operacional responsável pela base franqueada {r['code']} em {r['city']}/{r['uf']}."])

# bases
with open(f"{OUT}/bases.csv", "w", newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(["Unit_Code__c","Name","Unit_Type__c","Unit_Status__c","Operating_Model__c",
                "State__c","City__c","Operation_Start_Date__c","Daily_Operational_Capacity__c",
                "Parent_Unit__r.Unit_Code__c","Operating_Partner__r.LT_CNPJ__c"])
    fr_idx = 0
    for r in rows:
        yr = random.randint(2018, 2024); mo = random.randint(1,12); da = random.randint(1,28)
        start = f"{yr}-{mo:02d}-{da:02d}"
        if r["fr"]:
            fr_idx += 1
            model = "Franqueada"
            partner = cnpj(fr_idx)
            cap = random.choice([600, 800, 1000, 1200, 1500, 2000])
            nm = f"Base Franqueada {r['city']} ({r['codepart']})"
        else:
            model = "Própria"
            partner = ""
            cap = random.choice([1500, 2500, 3500, 5000, 7500, 10000])
            nm = f"Base {r['city']} ({r['codepart']})"
        w.writerow([r["code"], nm, "Base de Entrega", "Ativa", model, r["uf"], r["city"],
                    start, cap, CD[r["uf"]], partner])

print("\nWrote franchise_partners.csv and bases.csv")

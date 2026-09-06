#!/usr/bin/env python3
"""Modulo O: Data Security - OWD restrita + sharing rules (owner e criteria based)."""
import os, re
ROOT = r"C:\Users\Robert Luis\Desktop\LogiTrack-SFDX\force-app\main\default"

def w(path, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8", newline="\n").write(body.rstrip() + "\n")

# ---------------------------------------------------------------
# 1. PUBLIC GROUPS (destino das sharing rules)
# ---------------------------------------------------------------
def group(name, label, desc, bosses=True):
    # membros sao adicionados via Apex (GroupMember) - o tipo Group nao versiona membership
    w(os.path.join(ROOT, "groups", f"{name}.group-meta.xml"),
f"""<?xml version="1.0" encoding="UTF-8"?>
<Group xmlns="http://soap.sforce.com/2006/04/metadata">
    <description>{desc}</description>
    <doesIncludeBosses>{str(bosses).lower()}</doesIncludeBosses>
    <name>{label}</name>
</Group>""")

group("LT_Financeiro", "LT Financeiro",
      "Time do financeiro: analistas, coordenacao e diretoria financeira.")
group("LT_Prevencao_Perdas", "LT Prevencao de Perdas",
      "Time de prevencao de perdas: SAC, coordenacao de qualidade e cadastro (penalizacoes).")
group("LT_Operacao_Sul", "LT Operacao Sul",
      "Time da operacao da regional Sul: gerencia regional, coordenacao de CD, supervisao de base e analistas.")

# ---------------------------------------------------------------
# 2. OWD - apertar sharingModel dos objetos sensiveis
#    (feito editando o .object-meta.xml de cada objeto)
# ---------------------------------------------------------------
OWD = {
    "LT_Payment_Request__c": "Private",
    "LT_Driver_Penalty__c": "Private",
    "LT_Loss_Claim__c": "Read",
    "LT_Expense__c": "Read",
}
for obj, model in OWD.items():
    p = os.path.join(ROOT, "objects", obj, f"{obj}.object-meta.xml")
    t = open(p, encoding="utf-8").read()
    t = re.sub(r"<sharingModel>[^<]+</sharingModel>", f"<sharingModel>{model}</sharingModel>", t, count=1)
    # objetos Private/Read precisam de external sharing model tambem em alguns orgs; deixa igual
    w(p, t)
    print(f"OWD {obj} -> {model}")

# ---------------------------------------------------------------
# 3. SHARING RULES
# ---------------------------------------------------------------
def sharing_rules(obj, owner_rules=None, criteria_rules=None):
    blocks = []
    for r in (criteria_rules or []):
        name, label, access, group_name, items = r
        crit = "\n".join(
f"""        <criteriaItems>
            <field>{f}</field>
            <operation>{op}</operation>
            <value>{v}</value>
        </criteriaItems>""" for f, op, v in items)
        blocks.append(f"""    <sharingCriteriaRules>
        <fullName>{name}</fullName>
        <accessLevel>{access}</accessLevel>
        <description>{label}</description>
        <label>{label}</label>
        <sharedTo>
            <group>{group_name}</group>
        </sharedTo>
{crit}
    </sharingCriteriaRules>""")
    for r in (owner_rules or []):
        name, label, access, group_name, _ = r
        blocks.append(f"""    <sharingOwnerRules>
        <fullName>{name}</fullName>
        <accessLevel>{access}</accessLevel>
        <description>{label}</description>
        <label>{label}</label>
        <sharedTo>
            <group>{group_name}</group>
        </sharedTo>
        <sharedFrom>
            <allInternalUsers></allInternalUsers>
        </sharedFrom>
    </sharingOwnerRules>""")
    w(os.path.join(ROOT, "sharingRules", f"{obj}.sharingRules-meta.xml"),
f"""<?xml version="1.0" encoding="UTF-8"?>
<SharingRules xmlns="http://soap.sforce.com/2006/04/metadata">
{chr(10).join(blocks)}
</SharingRules>""")

sharing_rules("LT_Payment_Request__c",
    owner_rules=[
        ("Share_Payment_Requests_With_Finance", "Compartilha todas as solicitacoes de pagamento com o time do Financeiro",
         "Edit", "LT_Financeiro", "AllInternalUsers"),
    ],
    criteria_rules=[
        ("Share_Urgent_Payments_With_Ops", "Solicitacoes urgentes visiveis para a operacao da regional Sul",
         "Read", "LT_Operacao_Sul", [("LT_Priority__c", "equals", "Urgente")]),
    ])

sharing_rules("LT_Driver_Penalty__c",
    owner_rules=[
        ("Share_Penalties_With_Loss_Prevention", "Compartilha as penalizacoes de motorista com a Prevencao de Perdas",
         "Edit", "LT_Prevencao_Perdas", "AllInternalUsers"),
    ],
    criteria_rules=[
        ("Share_Contested_Penalties_With_Ops", "Penalizacoes em contestacao visiveis para a operacao (analise)",
         "Edit", "LT_Operacao_Sul", [("LT_Status__c", "equals", "Em Contestacao")]),
    ])

sharing_rules("LT_Loss_Claim__c",
    criteria_rules=[
        ("Share_Driver_Loss_With_Loss_Prevention", "Extravios com responsabilidade do motorista visiveis para a Prevencao de Perdas",
         "Edit", "LT_Prevencao_Perdas", [("LT_Responsibility__c", "equals", "Motorista")]),
        ("Share_Reimbursed_Loss_With_Finance", "Extravios ressarcidos visiveis para o Financeiro (conciliacao)",
         "Read", "LT_Financeiro", [("LT_Status__c", "equals", "Ressarcido")]),
    ])

sharing_rules("LT_Expense__c",
    owner_rules=[
        ("Share_Expenses_With_Finance", "Compartilha as despesas com o time do Financeiro",
         "Edit", "LT_Financeiro", "AllInternalUsers"),
    ])

print("Modulo O: grupos, OWD e sharing rules gerados.")

#!/usr/bin/env python3
"""Modulo R: Salesforce Mobile - global actions, form factors, compact layouts mobile."""
import os, re
ROOT = r"C:\Users\Robert Luis\Desktop\LogiTrack-SFDX\force-app\main\default"

def w(path, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8", newline="\n").write(body.rstrip() + "\n")

# ---------------------------------------------------------------
# 1. GLOBAL QUICK ACTIONS (barra de acoes do app mobile + publisher)
# ---------------------------------------------------------------
def qa_global_create(name, label, target, fields, desc):
    cols = ""
    half = (len(fields) + 1) // 2
    for group in (fields[:half], fields[half:]):
        items = "".join(f"""
            <quickActionLayoutItems>
                <emptySpace>false</emptySpace>
                <field>{f}</field>
                <uiBehavior>{beh}</uiBehavior>
            </quickActionLayoutItems>""" for f, beh in group)
        cols += f"        <quickActionLayoutColumns>{items}\n        </quickActionLayoutColumns>\n"
    w(os.path.join(ROOT, "quickActions", f"{name}.quickAction-meta.xml"),
f"""<?xml version="1.0" encoding="UTF-8"?>
<QuickAction xmlns="http://soap.sforce.com/2006/04/metadata">
    <description>{desc}</description>
    <label>{label}</label>
    <optionsCreateFeedItem>false</optionsCreateFeedItem>
    <quickActionLayout>
        <layoutSectionStyle>TwoColumnsLeftToRight</layoutSectionStyle>
{cols}    </quickActionLayout>
    <targetObject>{target}</targetObject>
    <type>Create</type>
</QuickAction>""")

def qa_global_flow(name, label, flow_dev, desc):
    w(os.path.join(ROOT, "quickActions", f"{name}.quickAction-meta.xml"),
f"""<?xml version="1.0" encoding="UTF-8"?>
<QuickAction xmlns="http://soap.sforce.com/2006/04/metadata">
    <description>{desc}</description>
    <flowDefinition>{flow_dev}</flowDefinition>
    <label>{label}</label>
    <optionsCreateFeedItem>false</optionsCreateFeedItem>
    <type>Flow</type>
</QuickAction>""")

qa_global_create("LT_New_Payment_Request", "Nova solicitacao de pagamento", "LT_Payment_Request__c",
    [("LT_Request_Type__c", "Edit"), ("LT_Amount__c", "Required"), ("LT_Due_Date__c", "Required"),
     ("LT_Payee_Name__c", "Required"), ("LT_Cost_Center__c", "Edit"), ("LT_Description__c", "Edit")],
    "Cria uma solicitacao de pagamento direto pela barra de acoes (util no mobile).")

qa_global_create("LT_New_Incident", "Registrar ocorrencia operacional", "LT_Operational_Incident__c",
    [("LT_Incident_Type__c", "Edit"), ("LT_Priority__c", "Edit"), ("LT_Detected_Date__c", "Required"),
     ("LT_Shipment__c", "Edit"), ("LT_Owner_Unit__c", "Edit"), ("LT_Description__c", "Edit")],
    "Abre uma ocorrencia operacional pela barra de acoes global (util para a operacao em campo).")

qa_global_flow("LT_Consultar_CEP_Action", "Consultar CEP", "LT_Consultar_CEP",
    "Abre o fluxo de consulta de endereco por CEP (ViaCEP).")

# ---------------------------------------------------------------
# 2. GLOBAL LAYOUT - adicionar as global actions na quickActionList
# ---------------------------------------------------------------
gl = os.path.join(ROOT, "layouts", "Global-Global Layout.layout-meta.xml")
t = open(gl, encoding="utf-8").read()
new_items = "".join(f"""
        <quickActionListItems>
            <quickActionName>{a}</quickActionName>
        </quickActionListItems>""" for a in ["LT_New_Payment_Request", "LT_New_Incident", "LT_Consultar_CEP_Action"]
    if f"<quickActionName>{a}</quickActionName>" not in t)
if new_items:
    t = t.replace("    </quickActionList>", new_items + "\n    </quickActionList>", 1)
    w(gl, t)
    print("Global Layout: +3 global actions")

# ---------------------------------------------------------------
# 3. FORM FACTORS - garantir Small em todos os apps LogiTrack
# ---------------------------------------------------------------
for app in ["LogiTrack_Executivo"]:
    p = os.path.join(ROOT, "applications", f"{app}.app-meta.xml")
    t = open(p, encoding="utf-8").read()
    if "<formFactors>Small</formFactors>" not in t:
        t = t.replace("    <formFactors>Large</formFactors>\n",
                      "    <formFactors>Large</formFactors>\n    <formFactors>Small</formFactors>\n", 1)
        w(p, t)
        print(f"{app}: +formFactor Small")

print("Modulo R gerado.")

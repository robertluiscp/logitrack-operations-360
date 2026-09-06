#!/usr/bin/env python3
"""Modulo N: vitorias rapidas - matching/duplicate rules, weblinks, quick actions,
picklists dependentes."""
import os, re
ROOT = r"C:\Users\Robert Luis\Desktop\LogiTrack-SFDX\force-app\main\default"

def w(path, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8", newline="\n").write(body.rstrip() + "\n")

# ======================================================================
# N4 - MATCHING RULES + DUPLICATE RULES
# ======================================================================
w(os.path.join(ROOT, "matchingRules", "Account.matchingRule-meta.xml"), """<?xml version="1.0" encoding="UTF-8"?>
<MatchingRules xmlns="http://soap.sforce.com/2006/04/metadata">
    <matchingRules>
        <fullName>LT_Account_By_CNPJ</fullName>
        <description>Identifica contas (embarcadores / parceiros) com o mesmo CNPJ.</description>
        <label>Conta por CNPJ</label>
        <matchingRuleItems>
            <blankValueBehavior>MatchBlanks</blankValueBehavior>
            <fieldName>LT_CNPJ__c</fieldName>
            <matchingMethod>Exact</matchingMethod>
        </matchingRuleItems>
        <ruleStatus>Active</ruleStatus>
    </matchingRules>
</MatchingRules>""")

w(os.path.join(ROOT, "matchingRules", "LT_Driver__c.matchingRule-meta.xml"), """<?xml version="1.0" encoding="UTF-8"?>
<MatchingRules xmlns="http://soap.sforce.com/2006/04/metadata">
    <matchingRules>
        <fullName>LT_Driver_By_CPF</fullName>
        <description>Identifica motoristas com o mesmo CPF.</description>
        <label>Motorista por CPF</label>
        <matchingRuleItems>
            <blankValueBehavior>MatchBlanks</blankValueBehavior>
            <fieldName>LT_CPF__c</fieldName>
            <matchingMethod>Exact</matchingMethod>
        </matchingRuleItems>
        <ruleStatus>Active</ruleStatus>
    </matchingRules>
    <matchingRules>
        <fullName>LT_Driver_By_CNPJ</fullName>
        <description>Identifica motoristas PJ (MEI/ETC) com o mesmo CNPJ.</description>
        <label>Motorista por CNPJ</label>
        <matchingRuleItems>
            <blankValueBehavior>MatchBlanks</blankValueBehavior>
            <fieldName>LT_CNPJ__c</fieldName>
            <matchingMethod>Exact</matchingMethod>
        </matchingRuleItems>
        <ruleStatus>Active</ruleStatus>
    </matchingRules>
</MatchingRules>""")

w(os.path.join(ROOT, "matchingRules", "LT_Vehicle__c.matchingRule-meta.xml"), """<?xml version="1.0" encoding="UTF-8"?>
<MatchingRules xmlns="http://soap.sforce.com/2006/04/metadata">
    <matchingRules>
        <fullName>LT_Vehicle_By_Plate</fullName>
        <description>Identifica veiculos com a mesma placa.</description>
        <label>Veiculo por Placa</label>
        <matchingRuleItems>
            <blankValueBehavior>NullNotAllowed</blankValueBehavior>
            <fieldName>LT_Plate__c</fieldName>
            <matchingMethod>Exact</matchingMethod>
        </matchingRuleItems>
        <ruleStatus>Active</ruleStatus>
    </matchingRules>
</MatchingRules>""")

def dup_rule(obj, name, label, desc, match_rule, action_insert, action_update, sort):
    # operations blocks only allowed when action is NOT Block
    ops = ""
    if action_insert != "Block":
        ops += "\n".join(f"    <operationsOnInsert>{o}</operationsOnInsert>" for o in ("Alert", "Report")) + "\n"
    if action_update != "Block":
        ops += "\n".join(f"    <operationsOnUpdate>{o}</operationsOnUpdate>" for o in ("Alert", "Report")) + "\n"
    w(os.path.join(ROOT, "duplicateRules", f"{obj}.{name}.duplicateRule-meta.xml"),
f"""<?xml version="1.0" encoding="UTF-8"?>
<DuplicateRule xmlns="http://soap.sforce.com/2006/04/metadata">
    <actionOnInsert>{action_insert}</actionOnInsert>
    <actionOnUpdate>{action_update}</actionOnUpdate>
    <alertText>{desc}</alertText>
    <description>{desc}</description>
    <duplicateRuleMatchRules>
        <matchRuleSObjectType>{obj}</matchRuleSObjectType>
        <matchingRule>{match_rule}</matchingRule>
    </duplicateRuleMatchRules>
    <isActive>true</isActive>
    <masterLabel>{label}</masterLabel>
{ops}    <securityOption>EnforceSharingRules</securityOption>
    <sortOrder>{sort}</sortOrder>
</DuplicateRule>""")

# Account ja tem a regra padrao no sortOrder 1 -> customizada = 2
dup_rule("Account", "LT_Account_By_CNPJ_Rule", "Conta duplicada por CNPJ",
         "Ja existe uma conta com este CNPJ.", "LT_Account_By_CNPJ", "Allow", "Allow", 2)
# LT_Driver__c / LT_Vehicle__c nao tem regra padrao -> customizada = 1
dup_rule("LT_Driver__c", "LT_Driver_By_CPF_Rule", "Motorista duplicado por CPF",
         "Ja existe um motorista com este CPF.", "LT_Driver_By_CPF", "Allow", "Allow", 1)
dup_rule("LT_Driver__c", "LT_Driver_By_CNPJ_Rule", "Motorista duplicado por CNPJ",
         "Ja existe um motorista PJ com este CNPJ.", "LT_Driver_By_CNPJ", "Allow", "Allow", 2)
dup_rule("LT_Vehicle__c", "LT_Vehicle_By_Plate_Rule", "Veiculo duplicado por placa",
         "Ja existe um veiculo com esta placa.", "LT_Vehicle_By_Plate", "Block", "Allow", 1)

# ======================================================================
# N2 - CUSTOM BUTTONS & LINKS (webLinks)
# ======================================================================
def weblink(obj, name, label, url, desc, display="newWindow"):
    w(os.path.join(ROOT, "objects", obj, "webLinks", f"{name}.webLink-meta.xml"),
f"""<?xml version="1.0" encoding="UTF-8"?>
<WebLink xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>{name}</fullName>
    <availability>online</availability>
    <description>{desc}</description>
    <displayType>button</displayType>
    <encodingKey>UTF-8</encodingKey>
    <hasMenubar>false</hasMenubar>
    <hasScrollbars>true</hasScrollbars>
    <hasToolbar>false</hasToolbar>
    <height>600</height>
    <isResizable>true</isResizable>
    <linkType>url</linkType>
    <masterLabel>{label}</masterLabel>
    <openType>{display}</openType>
    <position>none</position>
    <protected>false</protected>
    <showsLocation>false</showsLocation>
    <showsStatus>false</showsStatus>
    <url>{url}</url>
    <width>800</width>
</WebLink>""")

weblink("LT_Shipment__c", "Rastrear_no_Site", "Rastrear no site",
        "https://rastreio.logitrack360.example/br?codigo={!LT_Shipment__c.LT_Tracking_Code__c}",
        "Abre a pagina publica de rastreamento da remessa (ambiente de demonstracao).")
weblink("LT_Shipment__c", "Ver_Destino_no_Mapa", "Ver destino no mapa",
        "https://www.google.com/maps/search/?api=1&amp;query={!LT_Shipment__c.LT_Dest_Street__c}, {!LT_Shipment__c.LT_Dest_City__c} - {!LT_Shipment__c.LT_Dest_State__c}",
        "Abre o Google Maps no endereco de destino da remessa.")
weblink("LT_Driver__c", "Falar_no_WhatsApp", "Falar no WhatsApp",
        "https://wa.me/55{!SUBSTITUTE(SUBSTITUTE(SUBSTITUTE(SUBSTITUTE(LT_Driver__c.LT_Phone__c,\" \",\"\"),\"-\",\"\"),\"(\",\"\"),\")\",\"\")}",
        "Abre uma conversa no WhatsApp com o telefone do motorista.")
weblink("LT_Manifest__c", "Imprimir_Romaneio", "Imprimir romaneio",
        "/apex/nao_configurado?id={!LT_Manifest__c.Id}",
        "Placeholder para a pagina de impressao do romaneio (a implementar).")

# ======================================================================
# N3 - QUICK ACTIONS
# ======================================================================
def _qa_cols(fields):
    half = (len(fields) + 1) // 2
    cols = [fields[:half], fields[half:]]
    out = ""
    for col in cols:
        items = "".join(f"""
            <quickActionLayoutItems>
                <emptySpace>false</emptySpace>
                <field>{f}</field>
                <uiBehavior>{beh}</uiBehavior>
            </quickActionLayoutItems>""" for f, beh in col)
        out += f"        <quickActionLayoutColumns>{items}\n        </quickActionLayoutColumns>\n"
    return out

def qa_create(obj, name, label, target, parent_field, fields, desc):
    fp = f"\n    <targetParentField>{parent_field}</targetParentField>" if parent_field else ""
    w(os.path.join(ROOT, "quickActions", f"{obj}.{name}.quickAction-meta.xml"),
f"""<?xml version="1.0" encoding="UTF-8"?>
<QuickAction xmlns="http://soap.sforce.com/2006/04/metadata">
    <description>{desc}</description>
    <label>{label}</label>
    <optionsCreateFeedItem>false</optionsCreateFeedItem>
    <quickActionLayout>
        <layoutSectionStyle>TwoColumnsLeftToRight</layoutSectionStyle>
{_qa_cols(fields)}    </quickActionLayout>
    <targetObject>{target}</targetObject>{fp}
    <type>Create</type>
</QuickAction>""")

def qa_update(obj, name, label, fields, desc):
    w(os.path.join(ROOT, "quickActions", f"{obj}.{name}.quickAction-meta.xml"),
f"""<?xml version="1.0" encoding="UTF-8"?>
<QuickAction xmlns="http://soap.sforce.com/2006/04/metadata">
    <description>{desc}</description>
    <label>{label}</label>
    <optionsCreateFeedItem>false</optionsCreateFeedItem>
    <quickActionLayout>
        <layoutSectionStyle>TwoColumnsLeftToRight</layoutSectionStyle>
{_qa_cols(fields)}    </quickActionLayout>
    <targetObject>{obj}</targetObject>
    <type>Update</type>
</QuickAction>""")

qa_create("LT_Shipment__c", "Registrar_Ocorrencia", "Registrar ocorrencia",
          "LT_Operational_Incident__c", "LT_Shipment__c",
          [("LT_Incident_Type__c", "Edit"), ("LT_Priority__c", "Edit"),
           ("LT_Detected_Date__c", "Required"), ("LT_Description__c", "Edit")],
          "Abre uma ocorrencia operacional ja vinculada a esta remessa.")

qa_create("LT_Route__c", "Nova_Tentativa", "Nova tentativa de entrega",
          "LT_Delivery_Attempt__c", "LT_Route__c",
          [("LT_Shipment__c", "Required"), ("LT_Result__c", "Edit"),
           ("LT_Attempt_DateTime__c", "Edit"), ("LT_Notes__c", "Edit")],
          "Registra uma tentativa de entrega a partir da rota.")

qa_create("Case", "Abrir_Extravio", "Abrir extravio",
          "LT_Loss_Claim__c", "LT_Case__c",
          [("LT_Shipment__c", "Required"), ("LT_Loss_Reason__c", "Edit"),
           ("LT_Responsibility__c", "Edit"), ("LT_Detected_Date__c", "Required")],
          "Abre um extravio a partir do chamado do SAC.")

qa_create("LT_Driver__c", "Registrar_Penalizacao", "Registrar penalizacao",
          "LT_Driver_Penalty__c", "LT_Driver__c",
          [("LT_Penalty_Type__c", "Edit"), ("LT_Origin__c", "Edit"),
           ("LT_Reference_Date__c", "Required"), ("LT_Description__c", "Edit")],
          "Aplica uma penalizacao ao motorista.")

qa_update("LT_Loss_Claim__c", "Marcar_Ressarcido", "Marcar como ressarcido",
          [("LT_Status__c", "Required"), ("LT_Reimbursement_Value__c", "Required"),
           ("LT_Reimbursement_Date__c", "Required"), ("LT_Resolution_Notes__c", "Edit")],
          "Registra o ressarcimento do extravio ao embarcador.")

# ======================================================================
# N5 - PICKLISTS DEPENDENTES (field dependencies)
# ======================================================================
# 5a: LT_Root_Cause__c (Ocorrencia) controlado por LT_Incident_Type__c
ROOT_CAUSE_MAP = {
    "Retido com Motorista": ["Postura do Motorista", "Fora da Area de Cobertura", "Endereco Incorreto", "Outro"],
    "Retido na Base": ["Falha de Triagem", "Falha Sistemica", "Endereco Incorreto", "Outro"],
    "Sem Movimentacao": ["Falha de Triagem", "Falha Sistemica", "Fora da Area de Cobertura", "Outro"],
    "Suspeita de Extravio": ["Extravio Interno", "Falha de Triagem", "Outro"],
    "Avaria em Transporte": ["Avaria", "Postura do Motorista", "Outro"],
    "Entrada no Galpao sem Expedicao": ["Falha de Triagem", "Falha Sistemica", "Outro"],
}
ALL_RC = ["Endereco Incorreto", "Cliente Ausente", "Falha de Triagem", "Extravio Interno",
          "Avaria", "Falha Sistemica", "Postura do Motorista", "Fora da Area de Cobertura", "Outro"]
CTRL_RC = list(ROOT_CAUSE_MAP.keys())

def value_settings(all_values, ctrl_values, mapping):
    out = []
    for v in all_values:
        allowed = [c for c in ctrl_values if v in mapping.get(c, [])]
        if not allowed:
            continue
        cfv = "\n".join(f"        <controllingFieldValue>{c}</controllingFieldValue>" for c in allowed)
        out.append(f"""    <valueSettings>
{cfv}
        <valueName>{v}</valueName>
    </valueSettings>""")
    return "\n".join(out)

rc_vs = value_settings(ALL_RC, CTRL_RC, ROOT_CAUSE_MAP)
rc_defs = "\n".join(f"""            <value>
                <fullName>{v}</fullName>
                <default>false</default>
                <label>{v}</label>
            </value>""" for v in ALL_RC)
w(os.path.join(ROOT, "objects", "LT_Operational_Incident__c", "fields", "LT_Root_Cause__c.field-meta.xml"),
f"""<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>LT_Root_Cause__c</fullName>
    <description>Causa raiz identificada, dependente do Tipo de Ocorrencia.</description>
    <label>Causa Raiz</label>
    <required>false</required>
    <trackHistory>false</trackHistory>
    <trackFeedHistory>false</trackFeedHistory>
    <type>Picklist</type>
    <valueSet>
        <controllingField>LT_Incident_Type__c</controllingField>
        <restricted>true</restricted>
        <valueSetDefinition>
            <sorted>false</sorted>
{rc_defs}
        </valueSetDefinition>
{rc_vs}
    </valueSet>
</CustomField>""")

# 5b: novo campo LT_Loss_Sub_Reason__c (Extravio) controlado por LT_Loss_Reason__c
SUB_MAP = {
    "PNR - Paguei Nao Recebi": ["Fraude do Destinatario", "Falha na Comprovacao", "Entrega em Endereco Errado"],
    "Assinado Nao Recebido": ["Assinatura de Terceiro", "Portaria / Recepcao", "Falha na Comprovacao"],
    "Avaria na Entrega": ["Manuseio do Motorista", "Embalagem Insuficiente", "Produto Fragil"],
    "Avaria em Transporte": ["Acidente de Veiculo", "Carga Mal Acomodada", "Umidade / Chuva"],
    "Retido +10 dias": ["Sem Tentativa de Contato", "Endereco Nao Localizado", "Recusa do Cliente"],
    "Sem Movimentacao +10 dias": ["Perda no Galpao", "Erro de Bipagem", "Sem Rota Atribuida"],
    "Roubo / Furto de Carga": ["Roubo em Rota", "Furto no Galpao", "Desvio Interno"],
    "Sinistro (Acidente)": ["Colisao", "Incendio", "Alagamento"],
    "Endereco Inexistente": ["CEP Invalido", "Numero Inexistente", "Cliente Mudou"],
    "Outro": ["Outro"],
}
SUB_VALUES = sorted({s for lst in SUB_MAP.values() for s in lst})
CTRL_SUB = list(SUB_MAP.keys())
sub_vs = value_settings(SUB_VALUES, CTRL_SUB, SUB_MAP)
sub_defs = "\n".join(f"""            <value>
                <fullName>{v}</fullName>
                <default>false</default>
                <label>{v}</label>
            </value>""" for v in SUB_VALUES)
w(os.path.join(ROOT, "objects", "LT_Loss_Claim__c", "fields", "LT_Loss_Sub_Reason__c.field-meta.xml"),
f"""<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>LT_Loss_Sub_Reason__c</fullName>
    <description>Sub-motivo do extravio, dependente do Motivo do Extravio.</description>
    <label>Sub-motivo do Extravio</label>
    <required>false</required>
    <trackHistory>false</trackHistory>
    <trackFeedHistory>false</trackFeedHistory>
    <type>Picklist</type>
    <valueSet>
        <controllingField>LT_Loss_Reason__c</controllingField>
        <restricted>true</restricted>
        <valueSetDefinition>
            <sorted>false</sorted>
{sub_defs}
        </valueSetDefinition>
{sub_vs}
    </valueSet>
</CustomField>""")

print("Modulo N: matching rules, duplicate rules, weblinks, quick actions, picklists dependentes gerados.")

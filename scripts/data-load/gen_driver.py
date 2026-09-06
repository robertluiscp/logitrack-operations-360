#!/usr/bin/env python3
import os
ROOT = r"C:\Users\Robert Luis\Desktop\LogiTrack-SFDX\force-app\main\default"
D = os.path.join(ROOT, "objects", "LT_Driver__c")
for sub in ("fields", "validationRules", "recordTypes", "compactLayouts", "listViews"):
    os.makedirs(os.path.join(D, sub), exist_ok=True)

def wf(name, xml):
    open(os.path.join(D, "fields", f"{name}.field-meta.xml"), "w", encoding="utf-8").write(xml.strip() + "\n")

def wv(name, desc, formula, msg, field=None):
    fld = f"\n    <errorDisplayField>{field}</errorDisplayField>" if field else ""
    open(os.path.join(D, "validationRules", f"{name}.validationRule-meta.xml"), "w", encoding="utf-8").write(
f"""<?xml version="1.0" encoding="UTF-8"?>
<ValidationRule xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>{name}</fullName>
    <active>true</active>
    <description>{desc}</description>
    <errorConditionFormula>{formula}</errorConditionFormula>{fld}
    <errorMessage>{msg}</errorMessage>
</ValidationRule>
""")

def picklist(api, label, desc, helptext, values, default=None, track=True):
    vs = "\n".join(
f"""            <value>
                <fullName>{v}</fullName>
                <default>{'true' if v == default else 'false'}</default>
                <label>{v}</label>
            </value>""" for v in values)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>{api}</fullName>
    <description>{desc}</description>
    <inlineHelpText>{helptext}</inlineHelpText>
    <label>{label}</label>
    <required>false</required>
    <trackHistory>{str(track).lower()}</trackHistory>
    <trackFeedHistory>false</trackFeedHistory>
    <type>Picklist</type>
    <valueSet>
        <restricted>true</restricted>
        <valueSetDefinition>
            <sorted>false</sorted>
{vs}
        </valueSetDefinition>
    </valueSet>
</CustomField>"""

def textf(api, label, desc, length, helptext="", unique=False, extid=False, track=True):
    u = f"\n    <unique>{str(unique).lower()}</unique>"
    e = f"\n    <externalId>{str(extid).lower()}</externalId>" if extid else ""
    c = "\n    <caseSensitive>false</caseSensitive>" if unique else ""
    h = f"\n    <inlineHelpText>{helptext}</inlineHelpText>" if helptext else ""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>{api}</fullName>
    <description>{desc}</description>{e}{h}
    <label>{label}</label>
    <length>{length}</length>
    <required>false</required>
    <trackHistory>{str(track).lower()}</trackHistory>
    <trackFeedHistory>false</trackFeedHistory>
    <type>Text</type>{u}{c}
</CustomField>"""

def formula(api, label, desc, ftype, expr, blanks="BlankAsZero", extra=""):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>{api}</fullName>
    <description>{desc}</description>
    <label>{label}</label>
    <formula>{expr}</formula>
    <formulaTreatBlanksAs>{blanks}</formulaTreatBlanksAs>{extra}
    <type>{ftype}</type>
</CustomField>"""

# ---------- identity ----------
wf("LT_CPF__c", textf("LT_CPF__c", "CPF", "Cadastro de Pessoa Fisica do motorista.", 14,
   "Informe o CPF no formato 000.000.000-00.", unique=True, extid=True))
wf("LT_CNPJ__c", textf("LT_CNPJ__c", "CNPJ", "CNPJ do motorista (obrigatorio para MEI e ETC).", 18,
   "Informe o CNPJ no formato 00.000.000/0000-00. Obrigatorio para MEI e ETC.", unique=False))
wf("LT_Phone__c", """<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>LT_Phone__c</fullName>
    <description>Telefone de contato do motorista.</description>
    <label>Telefone</label>
    <required>false</required>
    <trackHistory>false</trackHistory>
    <type>Phone</type>
</CustomField>""")
wf("LT_PIX_Key__c", textf("LT_PIX_Key__c", "Chave PIX", "Chave PIX para pagamento de fretes e romaneios.", 80, track=False))

# ---------- CNH ----------
wf("LT_CNH_Number__c", textf("LT_CNH_Number__c", "Numero da CNH", "Numero de registro da Carteira Nacional de Habilitacao.", 15))
wf("LT_CNH_Category__c", picklist("LT_CNH_Category__c", "Categoria da CNH",
   "Categoria da habilitacao do motorista.", "Selecione a categoria da CNH.",
   ["A", "B", "AB", "C", "D", "E", "AC", "AD", "AE"]))
wf("LT_CNH_Expiration__c", """<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>LT_CNH_Expiration__c</fullName>
    <description>Data de validade da CNH. Motorista com CNH vencida nao pode ser ativado.</description>
    <label>Validade da CNH</label>
    <required>false</required>
    <trackHistory>true</trackHistory>
    <type>Date</type>
</CustomField>""")
wf("LT_CNH_Status__c", formula("LT_CNH_Status__c", "Situacao da CNH",
   "Situacao calculada da CNH conforme a data de validade.", "Text",
   'IF(ISBLANK(LT_CNH_Expiration__c), "Sem CNH cadastrada", '
   'IF(LT_CNH_Expiration__c &lt; TODAY(), "Vencida", '
   'IF(LT_CNH_Expiration__c &lt;= TODAY() + 30, "A vencer (30 dias)", "Vigente")))'))

# ---------- classification (RT-derived formulas) ----------
RT = "RecordType.DeveloperName"

def rt_case(pairs, default):
    """nested IF over RecordType.DeveloperName (text - CASE not allowed on text)"""
    expr = default
    for k, v in reversed(pairs):
        expr = f'IF({RT} = "{k}", {v}, {expr})'
    return expr

wf("LT_Category_Code__c", formula("LT_Category_Code__c", "Sigla da Categoria",
   "Sigla da categoria do motorista derivada do Record Type.", "Text",
   rt_case([("LT_TAC", '"TAC"'), ("LT_MEI", '"MEI"'), ("LT_ETC", '"ETC"'), ("LT_MR", '"MR"'), ("LT_Coleta", '"Coleta"')], '""')))
wf("LT_Driver_Code__c", formula("LT_Driver_Code__c", "Identificacao do Motorista",
   "Identificacao usada na operacao: sigla da categoria + nome (ex.: TAC ADRIANO SOUZA).", "Text",
   f'IF(AND(LEN(LT_Category_Code__c) &gt; 0, LT_Category_Code__c &lt;&gt; "Coleta"), LT_Category_Code__c &amp; " " &amp; UPPER(Name), UPPER(Name))'))
wf("LT_Payment_Model__c", formula("LT_Payment_Model__c", "Modelo de Pagamento",
   "Coleta (First Mile) e Mini Transferencia sao pagos por Romaneio; demais categorias por Frete.", "Text",
   f'IF(OR({RT} = "LT_Coleta", {RT} = "LT_MR"), "Romaneio (por pacote)", "Frete (por rota)")'))
wf("LT_Min_Packages_Per_Trip__c", formula("LT_Min_Packages_Per_Trip__c", "Minimo de Pacotes por Frete",
   "Quantidade minima de pacotes por frete conforme a categoria (0 = sem minimo).", "Number",
   rt_case([("LT_TAC", "100"), ("LT_ETC", "300"), ("LT_MR", "300")], "0"),
   extra="\n    <precision>6</precision>\n    <scale>0</scale>"))
wf("LT_Max_Packages_Per_Trip__c", formula("LT_Max_Packages_Per_Trip__c", "Maximo de Pacotes por Frete",
   "Quantidade maxima de pacotes por frete conforme a categoria (0 = sem maximo).", "Number",
   rt_case([("LT_MEI", "80"), ("LT_ETC", "3000"), ("LT_MR", "3000")], "0"),
   extra="\n    <precision>6</precision>\n    <scale>0</scale>"))
wf("LT_Vehicle_Requirement__c", formula("LT_Vehicle_Requirement__c", "Exigencia de Veiculo",
   "Tipo de veiculo exigido pela categoria do motorista.", "Text",
   rt_case([
     ("LT_TAC", '"Veiculo com porta-malas amplo (Fiorino, sedan grande, station wagon)"'),
     ("LT_MEI", '"Qualquer veiculo (moto, carro, bicicleta) - ate 80 pacotes"'),
     ("LT_ETC", '"Veiculo grande: Van, VUC ou caminhao - 300 a 3.000 pacotes/dia"'),
     ("LT_Coleta", '"Veiculo compativel com o volume do roteiro de coleta"'),
     ("LT_MR", '"Veiculo grande para transferencia - 300 a 3.000 pacotes"'),
   ], '""')))

# ---------- relationships ----------
wf("LT_Home_Base__c", """<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>LT_Home_Base__c</fullName>
    <description>Base de entrega ou centro de distribuicao ao qual o motorista esta vinculado.</description>
    <inlineHelpText>Unidade logistica onde o motorista faz a triagem e retirada dos pacotes.</inlineHelpText>
    <label>Base Vinculada</label>
    <referenceTo>LT_Logistics_Unit__c</referenceTo>
    <relationshipLabel>Motoristas</relationshipLabel>
    <relationshipName>LT_Drivers</relationshipName>
    <required>false</required>
    <trackHistory>true</trackHistory>
    <type>Lookup</type>
    <lookupFilter>
        <active>true</active>
        <errorMessage>Vincule o motorista a uma Base de Entrega ou Centro de Distribuicao ativo.</errorMessage>
        <filterItems>
            <field>LT_Logistics_Unit__c.Unit_Status__c</field>
            <operation>equals</operation>
            <value>Ativa</value>
        </filterItems>
        <filterItems>
            <field>LT_Logistics_Unit__c.Unit_Type__c</field>
            <operation>notEqual</operation>
            <value>Regional</value>
        </filterItems>
        <isOptional>false</isOptional>
    </lookupFilter>
</CustomField>""")

wf("LT_Operating_Partner__c", """<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>LT_Operating_Partner__c</fullName>
    <description>Parceiro operacional (franquia) responsavel pelo motorista, quando ele opera por uma base franqueada.</description>
    <label>Parceiro Operacional</label>
    <referenceTo>Account</referenceTo>
    <relationshipLabel>Motoristas</relationshipLabel>
    <relationshipName>LT_Drivers</relationshipName>
    <required>false</required>
    <trackHistory>false</trackHistory>
    <type>Lookup</type>
    <lookupFilter>
        <active>true</active>
        <errorMessage>Selecione uma conta do tipo Parceiro Operacional.</errorMessage>
        <filterItems>
            <field>Account.RecordType.DeveloperName</field>
            <operation>equals</operation>
            <value>LT_Operating_Partner</value>
        </filterItems>
        <isOptional>false</isOptional>
    </lookupFilter>
</CustomField>""")

wf("LT_Lead_Driver__c", """<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>LT_Lead_Driver__c</fullName>
    <description>Motorista ETC principal ao qual este motorista auxiliar esta subordinado nas entregas.</description>
    <inlineHelpText>Preencha apenas para motoristas auxiliares que acompanham um ETC principal.</inlineHelpText>
    <label>Motorista Principal (ETC)</label>
    <referenceTo>LT_Driver__c</referenceTo>
    <relationshipLabel>Motoristas Auxiliares</relationshipLabel>
    <relationshipName>LT_Sub_Drivers</relationshipName>
    <required>false</required>
    <trackHistory>false</trackHistory>
    <type>Lookup</type>
    <lookupFilter>
        <active>true</active>
        <errorMessage>O Motorista Principal deve ser um motorista da categoria ETC.</errorMessage>
        <filterItems>
            <field>LT_Driver__c.RecordType.DeveloperName</field>
            <operation>equals</operation>
            <value>LT_ETC</value>
        </filterItems>
        <isOptional>false</isOptional>
    </lookupFilter>
</CustomField>""")

# ---------- status / lifecycle ----------
wf("LT_Driver_Status__c", picklist("LT_Driver_Status__c", "Status do Motorista",
   "Situacao cadastral e operacional do motorista.", "Somente motoristas Ativos podem receber rotas e romaneios.",
   ["Em Cadastro", "Documentacao Pendente", "Ativo", "Suspenso", "Inativo", "Desligado"], default="Em Cadastro"))
wf("LT_Onboarding_Date__c", """<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>LT_Onboarding_Date__c</fullName>
    <description>Data em que o motorista foi ativado e comecou a operar.</description>
    <label>Data de Ativacao</label>
    <required>false</required>
    <trackHistory>true</trackHistory>
    <type>Date</type>
</CustomField>""")
wf("LT_Termination_Date__c", """<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>LT_Termination_Date__c</fullName>
    <description>Data de desligamento do motorista.</description>
    <label>Data de Desligamento</label>
    <required>false</required>
    <trackHistory>true</trackHistory>
    <type>Date</type>
</CustomField>""")
wf("LT_Notes__c", """<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>LT_Notes__c</fullName>
    <description>Observacoes gerais sobre o motorista.</description>
    <label>Observacoes</label>
    <length>32768</length>
    <required>false</required>
    <trackHistory>false</trackHistory>
    <type>LongTextArea</type>
    <visibleLines>4</visibleLines>
</CustomField>""")

# document roll-up helpers live on the document object; roll-ups here:
wf("LT_Pending_Documents__c", """<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>LT_Pending_Documents__c</fullName>
    <description>Quantidade de documentos do motorista ainda nao verificados.</description>
    <label>Documentos Pendentes</label>
    <summaryForeignKey>LT_Driver_Document__c.LT_Driver__c</summaryForeignKey>
    <summaryOperation>count</summaryOperation>
    <summaryFilterItems>
        <field>LT_Driver_Document__c.LT_Verified__c</field>
        <operation>equals</operation>
        <value>false</value>
    </summaryFilterItems>
    <type>Summary</type>
</CustomField>""")

# ---------- record types ----------
RTS = [
 ("LT_TAC", "TAC", "Motorista TAC (Transportador Autonomo de Cargas). Exige veiculo com porta-malas amplo. Minimo de 100 pacotes por frete."),
 ("LT_MEI", "MEI", "Motorista MEI. Possui CNPJ. Qualquer tipo de veiculo. Maximo de 80 pacotes por frete."),
 ("LT_ETC", "ETC", "Motorista ETC (Empresa de Transporte de Cargas). Veiculo grande. 300 a 3.000 pacotes/dia. Pode ter motoristas auxiliares."),
 ("LT_Coleta", "Coleta (First Mile)", "Motorista de coleta / First Mile. Pago via Romaneio pela quantidade de pacotes coletados."),
 ("LT_MR", "Mini Transferencia (MR)", "Motorista de Mini Transferencia. Leva cargas para cidades distantes (mais de 60 km da base). Pago via Romaneio."),
]
for dev, label, desc in RTS:
    open(os.path.join(D, "recordTypes", f"{dev}.recordType-meta.xml"), "w", encoding="utf-8").write(
f"""<?xml version="1.0" encoding="UTF-8"?>
<RecordType xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>{dev}</fullName>
    <active>true</active>
    <compactLayoutAssignment>LT_Driver_Highlights</compactLayoutAssignment>
    <description>{desc}</description>
    <label>{label}</label>
</RecordType>
""")

# ---------- validation rules ----------
wv("LT_Driver_Validate_CPF_Format",
   "Valida a mascara do CPF (000.000.000-00).",
   'AND(NOT(ISBLANK(LT_CPF__c)), NOT(REGEX(LT_CPF__c, "^[0-9]{3}[.][0-9]{3}[.][0-9]{3}-[0-9]{2}$")))',
   "Informe o CPF no formato 000.000.000-00.", "LT_CPF__c")
wv("LT_Driver_Validate_CNPJ_Format",
   "Valida a mascara do CNPJ (00.000.000/0000-00).",
   'AND(NOT(ISBLANK(LT_CNPJ__c)), NOT(REGEX(LT_CNPJ__c, "^[0-9]{2}[.][0-9]{3}[.][0-9]{3}/[0-9]{4}-[0-9]{2}$")))',
   "Informe o CNPJ no formato 00.000.000/0000-00.", "LT_CNPJ__c")
wv("LT_Driver_MEI_ETC_Require_CNPJ",
   "Motoristas MEI e ETC precisam ter CNPJ cadastrado.",
   f'AND(OR({RT} = "LT_MEI", {RT} = "LT_ETC"), ISBLANK(LT_CNPJ__c))',
   "Motoristas MEI e ETC precisam ter o CNPJ cadastrado.", "LT_CNPJ__c")
wv("LT_Driver_Active_Requires_CNH",
   "Motorista Ativo precisa da CNH completa (numero, categoria e validade).",
   'AND(ISPICKVAL(LT_Driver_Status__c, "Ativo"), OR(ISBLANK(LT_CNH_Number__c), ISBLANK(TEXT(LT_CNH_Category__c)), ISBLANK(LT_CNH_Expiration__c)))',
   "Para ativar o motorista informe numero, categoria e validade da CNH.")
wv("LT_Driver_Block_Activation_Expired_CNH",
   "Nao permite ativar motorista com CNH vencida.",
   'AND(ISPICKVAL(LT_Driver_Status__c, "Ativo"), NOT(ISBLANK(LT_CNH_Expiration__c)), LT_CNH_Expiration__c &lt; TODAY())',
   "A CNH do motorista esta vencida. Regularize antes de ativar.", "LT_CNH_Expiration__c")
wv("LT_Driver_Active_Requires_Base",
   "Motorista Ativo precisa estar vinculado a uma base.",
   'AND(ISPICKVAL(LT_Driver_Status__c, "Ativo"), ISBLANK(LT_Home_Base__c))',
   "Vincule o motorista a uma base antes de ativar.", "LT_Home_Base__c")
wv("LT_Driver_Active_Needs_Onboard_Dt",
   "Motorista Ativo precisa da data de ativacao preenchida.",
   'AND(ISPICKVAL(LT_Driver_Status__c, "Ativo"), ISBLANK(LT_Onboarding_Date__c))',
   "Informe a Data de Ativacao ao ativar o motorista.", "LT_Onboarding_Date__c")
wv("LT_Driver_Lead_Not_Self",
   "O motorista nao pode ser o proprio motorista principal.",
   'LT_Lead_Driver__c = Id',
   "Um motorista nao pode ser o proprio Motorista Principal.", "LT_Lead_Driver__c")
wv("LT_Driver_Terminated_Requires_Date",
   "Motorista Desligado precisa da data de desligamento.",
   'AND(ISPICKVAL(LT_Driver_Status__c, "Desligado"), ISBLANK(LT_Termination_Date__c))',
   "Informe a Data de Desligamento.", "LT_Termination_Date__c")
wv("LT_Driver_Lead_Only_Auxiliary",
   "Motorista com Motorista Principal nao pode ele mesmo ser ETC.",
   f'AND(NOT(ISBLANK(LT_Lead_Driver__c)), {RT} = "LT_ETC")',
   "Um motorista ETC nao pode estar subordinado a outro motorista principal.", "LT_Lead_Driver__c")

# ---------- compact layout ----------
open(os.path.join(D, "compactLayouts", "LT_Driver_Highlights.compactLayout-meta.xml"), "w", encoding="utf-8").write(
"""<?xml version="1.0" encoding="UTF-8"?>
<CompactLayout xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>LT_Driver_Highlights</fullName>
    <fields>LT_Driver_Code__c</fields>
    <fields>LT_Driver_Status__c</fields>
    <fields>LT_Category_Code__c</fields>
    <fields>LT_Home_Base__c</fields>
    <fields>LT_CNH_Status__c</fields>
    <fields>LT_Phone__c</fields>
    <label>Motorista - Destaques</label>
</CompactLayout>
""")

# ---------- list views ----------
def lv(name, label, cols, filters=""):
    fcols = "\n".join(f"    <columns>{c}</columns>" for c in cols)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<ListView xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>{name}</fullName>
{fcols}
    <filterScope>Everything</filterScope>
{filters}    <label>{label}</label>
</ListView>
"""
lvdir = os.path.join(D, "listViews")
open(os.path.join(lvdir, "All.listView-meta.xml"), "w", encoding="utf-8").write(
   lv("All", "Todos", ["LT_Driver_Code__c", "LT_Category_Code__c", "LT_Driver_Status__c", "LT_Home_Base__c", "LT_CNH_Status__c", "LT_Phone__c"]))
open(os.path.join(lvdir, "Ativos.listView-meta.xml"), "w", encoding="utf-8").write(
   lv("Ativos", "Motoristas Ativos", ["LT_Driver_Code__c", "LT_Category_Code__c", "LT_Home_Base__c", "LT_CNH_Status__c", "LT_Payment_Model__c", "LT_Phone__c"],
      "    <filters>\n        <field>LT_Driver_Status__c</field>\n        <operation>equals</operation>\n        <value>Ativo</value>\n    </filters>\n"))
open(os.path.join(lvdir, "CNH_Pendente.listView-meta.xml"), "w", encoding="utf-8").write(
   lv("CNH_Pendente", "CNH Vencida ou a Vencer", ["LT_Driver_Code__c", "LT_Category_Code__c", "LT_Driver_Status__c", "LT_CNH_Expiration__c", "LT_CNH_Status__c", "LT_Home_Base__c"],
      "    <filters>\n        <field>LT_CNH_Status__c</field>\n        <operation>contains</operation>\n        <value>Vencida,A vencer</value>\n    </filters>\n"))

print("LT_Driver__c:", len(os.listdir(os.path.join(D, "fields"))), "fields,",
      len(os.listdir(os.path.join(D, "validationRules"))), "VRs,",
      len(os.listdir(os.path.join(D, "recordTypes"))), "RTs")

#!/usr/bin/env python3
import os
ROOT = r"C:\Users\Robert Luis\Desktop\LogiTrack-SFDX\force-app\main\default"

def setup(obj):
    base = os.path.join(ROOT, "objects", obj)
    for sub in ("fields", "validationRules", "compactLayouts", "listViews"):
        os.makedirs(os.path.join(base, sub), exist_ok=True)
    return base

def wf(base, name, xml):
    open(os.path.join(base, "fields", f"{name}.field-meta.xml"), "w", encoding="utf-8").write(xml.strip() + "\n")

def wv(base, name, desc, formula, msg, field=None):
    fld = f"\n    <errorDisplayField>{field}</errorDisplayField>" if field else ""
    open(os.path.join(base, "validationRules", f"{name}.validationRule-meta.xml"), "w", encoding="utf-8").write(
f"""<?xml version="1.0" encoding="UTF-8"?>
<ValidationRule xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>{name}</fullName>
    <active>true</active>
    <description>{desc}</description>
    <errorConditionFormula>{formula}</errorConditionFormula>{fld}
    <errorMessage>{msg}</errorMessage>
</ValidationRule>
""")

def picklist(api, label, desc, values, default=None, helptext="", track=True):
    vs = "\n".join(
f"""            <value>
                <fullName>{v}</fullName>
                <default>{'true' if v == default else 'false'}</default>
                <label>{v}</label>
            </value>""" for v in values)
    h = f"\n    <inlineHelpText>{helptext}</inlineHelpText>" if helptext else ""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>{api}</fullName>
    <description>{desc}</description>{h}
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

def simple(api, label, desc, ftype, **kw):
    extra = ""
    if ftype in ("Number", "Currency", "Percent"):
        extra = f"\n    <precision>{kw.get('precision',10)}</precision>\n    <scale>{kw.get('scale',0)}</scale>"
    if ftype == "Text":
        extra = f"\n    <length>{kw.get('length',80)}</length>\n    <unique>{str(kw.get('unique',False)).lower()}</unique>"
        if kw.get("extid"):
            extra += "\n    <externalId>true</externalId>"
        if kw.get("unique"):
            extra += "\n    <caseSensitive>false</caseSensitive>"
    h = f"\n    <inlineHelpText>{kw['help']}</inlineHelpText>" if kw.get("help") else ""
    req = f"\n    <required>{str(kw.get('required',False)).lower()}</required>"
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>{api}</fullName>
    <description>{desc}</description>{h}
    <label>{label}</label>{req}
    <trackHistory>{str(kw.get('track',True)).lower()}</trackHistory>
    <trackFeedHistory>false</trackFeedHistory>
    <type>{ftype}</type>{extra}
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

def lookup(api, label, desc, ref, rel_label, rel_name, lf=None, help="", track=True):
    filt = ""
    if lf:
        items = "\n".join(
f"""        <filterItems>
            <field>{f}</field>
            <operation>{op}</operation>
            <value>{v}</value>
        </filterItems>""" for f, op, v in lf["items"])
        filt = f"""
    <lookupFilter>
        <active>true</active>
        <errorMessage>{lf['msg']}</errorMessage>
{items}
        <isOptional>{str(lf.get('optional', False)).lower()}</isOptional>
    </lookupFilter>"""
    h = f"\n    <inlineHelpText>{help}</inlineHelpText>" if help else ""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>{api}</fullName>
    <description>{desc}</description>{h}
    <label>{label}</label>
    <referenceTo>{ref}</referenceTo>
    <relationshipLabel>{rel_label}</relationshipLabel>
    <relationshipName>{rel_name}</relationshipName>
    <required>false</required>
    <trackHistory>{str(track).lower()}</trackHistory>
    <type>Lookup</type>{filt}
</CustomField>"""

# ===================== LT_Vehicle__c =====================
V = setup("LT_Vehicle__c")
wf(V, "LT_Plate__c", simple("LT_Plate__c", "Placa", "Placa do veiculo (padrao antigo AAA0000 ou Mercosul AAA0A00).", "Text",
   length=8, unique=True, extid=True, required=False, help="Informe a placa sem tracos, ex.: ABC1D23 ou ABC1234."))
wf(V, "LT_Vehicle_Type__c", picklist("LT_Vehicle_Type__c", "Tipo de Veiculo",
   "Categoria fisica do veiculo.",
   ["Bicicleta / Eletrica", "Moto", "Carro de Passeio", "Fiorino / Furgao Pequeno", "Van", "VUC", "Caminhao 3/4", "Caminhao Toco"],
   helptext="Motos e bicicletas ficam limitadas a 80 pacotes."))
wf(V, "LT_Brand_Model__c", simple("LT_Brand_Model__c", "Marca / Modelo", "Marca e modelo do veiculo.", "Text", length=80))
wf(V, "LT_Model_Year__c", simple("LT_Model_Year__c", "Ano do Modelo", "Ano de fabricacao/modelo do veiculo.", "Number", precision=4, scale=0))
wf(V, "LT_Cargo_Capacity_M3__c", simple("LT_Cargo_Capacity_M3__c", "Capacidade de Carga (m3)", "Volume util de carga em metros cubicos.", "Number", precision=6, scale=2))
wf(V, "LT_Cargo_Capacity_Packages__c", simple("LT_Cargo_Capacity_Packages__c", "Capacidade de Carga (pacotes)", "Quantidade maxima de pacotes que o veiculo comporta por viagem.", "Number", precision=6, scale=0))
wf(V, "LT_Owner_Type__c", picklist("LT_Owner_Type__c", "Propriedade",
   "Quem e o proprietario do veiculo.",
   ["Proprio do Motorista", "Alugado", "Da Empresa", "Do Parceiro Operacional"]))
wf(V, "LT_Driver__c", lookup("LT_Driver__c", "Motorista", "Motorista que opera este veiculo.",
   "LT_Driver__c", "Veiculos", "LT_Vehicles"))
wf(V, "LT_CRLV_Expiration__c", simple("LT_CRLV_Expiration__c", "Vencimento do Licenciamento (CRLV)", "Data de vencimento do licenciamento anual do veiculo.", "Date"))
wf(V, "LT_Insurance_Expiration__c", simple("LT_Insurance_Expiration__c", "Vencimento do Seguro", "Data de vencimento da apolice de seguro do veiculo.", "Date"))
wf(V, "LT_Vehicle_Status__c", picklist("LT_Vehicle_Status__c", "Status do Veiculo",
   "Situacao operacional do veiculo.",
   ["Ativo", "Em Manutencao", "Inativo", "Bloqueado"], default="Ativo",
   helptext="Somente veiculos Ativos podem ser usados em rotas."))
wf(V, "LT_Document_Status__c", formula("LT_Document_Status__c", "Situacao Documental",
   "Situacao dos documentos do veiculo (CRLV e seguro).", "Text",
   'IF(OR(AND(NOT(ISBLANK(LT_CRLV_Expiration__c)), LT_CRLV_Expiration__c &lt; TODAY()), AND(NOT(ISBLANK(LT_Insurance_Expiration__c)), LT_Insurance_Expiration__c &lt; TODAY())), "Documentacao Vencida", '
   'IF(OR(AND(NOT(ISBLANK(LT_CRLV_Expiration__c)), LT_CRLV_Expiration__c &lt;= TODAY() + 30), AND(NOT(ISBLANK(LT_Insurance_Expiration__c)), LT_Insurance_Expiration__c &lt;= TODAY() + 30)), "A Regularizar (30 dias)", "Regular"))'))

wv(V, "LT_Vehicle_Validate_Plate",
   "Valida a placa nos padroes antigo (AAA0000) ou Mercosul (AAA0A00).",
   'AND(NOT(ISBLANK(LT_Plate__c)), NOT(OR(REGEX(UPPER(LT_Plate__c), "^[A-Z]{3}[0-9]{4}$"), REGEX(UPPER(LT_Plate__c), "^[A-Z]{3}[0-9][A-Z][0-9]{2}$"))))',
   "Placa invalida. Use o padrao AAA0000 (antigo) ou AAA0A00 (Mercosul), sem tracos.", "LT_Plate__c")
wv(V, "LT_Vehicle_Active_Requires_CRLV",
   "Veiculo Ativo precisa de licenciamento (CRLV) valido.",
   'AND(ISPICKVAL(LT_Vehicle_Status__c, "Ativo"), OR(ISBLANK(LT_CRLV_Expiration__c), LT_CRLV_Expiration__c &lt; TODAY()))',
   "Veiculo Ativo precisa de licenciamento (CRLV) dentro da validade.", "LT_CRLV_Expiration__c")
wv(V, "LT_Vehicle_Year_Range",
   "Ano do modelo fora da faixa aceitavel.",
   'AND(NOT(ISBLANK(LT_Model_Year__c)), OR(LT_Model_Year__c &lt; 1990, LT_Model_Year__c &gt; YEAR(TODAY()) + 1))',
   "Informe um Ano do Modelo entre 1990 e o proximo ano.", "LT_Model_Year__c")
wv(V, "LT_Vehicle_Capacity_Positive",
   "Capacidades do veiculo nao podem ser negativas.",
   'OR(LT_Cargo_Capacity_M3__c &lt; 0, LT_Cargo_Capacity_Packages__c &lt; 0)',
   "As capacidades de carga nao podem ser negativas.")
wv(V, "LT_Vehicle_Two_Wheel_Limit",
   "Motos e bicicletas ficam limitadas a 80 pacotes.",
   'AND(OR(ISPICKVAL(LT_Vehicle_Type__c, "Moto"), ISPICKVAL(LT_Vehicle_Type__c, "Bicicleta / Eletrica")), LT_Cargo_Capacity_Packages__c &gt; 80)',
   "Motos e bicicletas nao podem ter capacidade acima de 80 pacotes.", "LT_Cargo_Capacity_Packages__c")

open(os.path.join(V, "compactLayouts", "LT_Vehicle_Summary.compactLayout-meta.xml"), "w", encoding="utf-8").write(
"""<?xml version="1.0" encoding="UTF-8"?>
<CompactLayout xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>LT_Vehicle_Summary</fullName>
    <fields>LT_Plate__c</fields>
    <fields>LT_Vehicle_Type__c</fields>
    <fields>LT_Vehicle_Status__c</fields>
    <fields>LT_Driver__c</fields>
    <fields>LT_Document_Status__c</fields>
    <label>Veiculo - Resumo</label>
</CompactLayout>
""")
open(os.path.join(V, "listViews", "All.listView-meta.xml"), "w", encoding="utf-8").write(
"""<?xml version="1.0" encoding="UTF-8"?>
<ListView xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>All</fullName>
    <columns>LT_Plate__c</columns>
    <columns>LT_Vehicle_Type__c</columns>
    <columns>LT_Brand_Model__c</columns>
    <columns>LT_Vehicle_Status__c</columns>
    <columns>LT_Driver__c</columns>
    <columns>LT_Document_Status__c</columns>
    <filterScope>Everything</filterScope>
    <label>Todos</label>
</ListView>
""")
open(os.path.join(V, "listViews", "Doc_Vencida.listView-meta.xml"), "w", encoding="utf-8").write(
"""<?xml version="1.0" encoding="UTF-8"?>
<ListView xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>Doc_Vencida</fullName>
    <columns>LT_Plate__c</columns>
    <columns>LT_Vehicle_Type__c</columns>
    <columns>LT_Vehicle_Status__c</columns>
    <columns>LT_CRLV_Expiration__c</columns>
    <columns>LT_Insurance_Expiration__c</columns>
    <columns>LT_Document_Status__c</columns>
    <filterScope>Everything</filterScope>
    <filters>
        <field>LT_Document_Status__c</field>
        <operation>notEqual</operation>
        <value>Regular</value>
    </filters>
    <label>Documentacao Pendente</label>
</ListView>
""")

open(os.path.join(ROOT, "objects", "LT_Vehicle__c", "LT_Vehicle__c.object-meta.xml"), "w", encoding="utf-8").write(
"""<?xml version="1.0" encoding="UTF-8"?>
<CustomObject xmlns="http://soap.sforce.com/2006/04/metadata">
    <allowInChatterGroups>false</allowInChatterGroups>
    <compactLayoutAssignment>LT_Vehicle_Summary</compactLayoutAssignment>
    <deploymentStatus>Deployed</deploymentStatus>
    <description>Veiculo utilizado por um motorista da malha LogiTrack.</description>
    <enableActivities>true</enableActivities>
    <enableBulkApi>true</enableBulkApi>
    <enableHistory>true</enableHistory>
    <enableReports>true</enableReports>
    <enableSearch>true</enableSearch>
    <enableSharing>true</enableSharing>
    <enableStreamingApi>true</enableStreamingApi>
    <label>Veiculo</label>
    <nameField>
        <displayFormat>VEIC-{00000}</displayFormat>
        <label>Codigo do Veiculo</label>
        <type>AutoNumber</type>
    </nameField>
    <pluralLabel>Veiculos</pluralLabel>
    <sharingModel>ReadWrite</sharingModel>
    <visibility>Public</visibility>
</CustomObject>
""")

# ===================== LT_Driver_Document__c =====================
DD = setup("LT_Driver_Document__c")
wf(DD, "LT_Driver__c", """<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>LT_Driver__c</fullName>
    <description>Motorista dono deste documento.</description>
    <label>Motorista</label>
    <referenceTo>LT_Driver__c</referenceTo>
    <relationshipLabel>Documentos</relationshipLabel>
    <relationshipName>LT_Documents</relationshipName>
    <relationshipOrder>0</relationshipOrder>
    <reparentableMasterDetail>false</reparentableMasterDetail>
    <type>MasterDetail</type>
    <writeRequiresMasterRead>false</writeRequiresMasterRead>
</CustomField>""")
wf(DD, "LT_Document_Type__c", picklist("LT_Document_Type__c", "Tipo de Documento",
   "Tipo do documento apresentado pelo motorista.",
   ["CNH", "CPF", "Comprovante de Residencia", "Contrato MEI (CCMEI)", "Contrato de Prestacao de Servicos",
    "RNTRC / ANTT", "Certidao Negativa", "Curso MOPP", "Antecedentes Criminais", "Outro"]))
wf(DD, "LT_Document_Number__c", simple("LT_Document_Number__c", "Numero do Documento", "Numero de identificacao do documento.", "Text", length=60, track=False))
wf(DD, "LT_Issue_Date__c", simple("LT_Issue_Date__c", "Data de Emissao", "Data de emissao do documento.", "Date", track=False))
wf(DD, "LT_Expiration_Date__c", simple("LT_Expiration_Date__c", "Data de Validade", "Data de validade do documento (deixe em branco se nao expira).", "Date"))
wf(DD, "LT_Situation__c", formula("LT_Situation__c", "Situacao",
   "Situacao do documento conforme a data de validade.", "Text",
   'IF(ISBLANK(LT_Expiration_Date__c), "Sem Validade", '
   'IF(LT_Expiration_Date__c &lt; TODAY(), "Vencido", '
   'IF(LT_Expiration_Date__c &lt;= TODAY() + 30, "A Vencer", "Vigente")))'))
wf(DD, "LT_Verified__c", """<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>LT_Verified__c</fullName>
    <description>Indica se o documento foi conferido pela equipe de Cadastro.</description>
    <label>Verificado</label>
    <defaultValue>false</defaultValue>
    <type>Checkbox</type>
</CustomField>""")
wf(DD, "LT_Verified_By__c", lookup("LT_Verified_By__c", "Verificado Por", "Usuario da equipe de Cadastro que conferiu o documento.",
   "User", "Documentos Verificados", "LT_Verified_Documents", track=False))
wf(DD, "LT_Verification_Date__c", simple("LT_Verification_Date__c", "Data da Verificacao", "Data em que o documento foi conferido.", "Date", track=False))
wf(DD, "LT_File_Link__c", """<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>LT_File_Link__c</fullName>
    <description>Link para o arquivo digitalizado do documento.</description>
    <label>Link do Arquivo</label>
    <required>false</required>
    <type>Url</type>
</CustomField>""")

wv(DD, "LT_Doc_Expiration_After_Issue",
   "A data de validade nao pode ser anterior a data de emissao.",
   'AND(NOT(ISBLANK(LT_Issue_Date__c)), NOT(ISBLANK(LT_Expiration_Date__c)), LT_Expiration_Date__c &lt; LT_Issue_Date__c)',
   "A Data de Validade nao pode ser anterior a Data de Emissao.", "LT_Expiration_Date__c")
wv(DD, "LT_Doc_Verified_Requires_Data",
   "Documento verificado exige responsavel e data da verificacao.",
   'AND(LT_Verified__c, OR(ISBLANK(LT_Verified_By__c), ISBLANK(LT_Verification_Date__c)))',
   "Ao marcar como Verificado informe quem verificou e a data.", "LT_Verified_By__c")

open(os.path.join(DD, "compactLayouts", "LT_Driver_Document_Summary.compactLayout-meta.xml"), "w", encoding="utf-8").write(
"""<?xml version="1.0" encoding="UTF-8"?>
<CompactLayout xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>LT_Driver_Document_Summary</fullName>
    <fields>LT_Document_Type__c</fields>
    <fields>LT_Driver__c</fields>
    <fields>LT_Situation__c</fields>
    <fields>LT_Expiration_Date__c</fields>
    <fields>LT_Verified__c</fields>
    <label>Documento - Resumo</label>
</CompactLayout>
""")
open(os.path.join(DD, "listViews", "All.listView-meta.xml"), "w", encoding="utf-8").write(
"""<?xml version="1.0" encoding="UTF-8"?>
<ListView xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>All</fullName>
    <columns>NAME</columns>
    <columns>LT_Driver__c</columns>
    <columns>LT_Document_Type__c</columns>
    <columns>LT_Situation__c</columns>
    <columns>LT_Expiration_Date__c</columns>
    <columns>LT_Verified__c</columns>
    <filterScope>Everything</filterScope>
    <label>Todos</label>
</ListView>
""")

open(os.path.join(ROOT, "objects", "LT_Driver_Document__c", "LT_Driver_Document__c.object-meta.xml"), "w", encoding="utf-8").write(
"""<?xml version="1.0" encoding="UTF-8"?>
<CustomObject xmlns="http://soap.sforce.com/2006/04/metadata">
    <allowInChatterGroups>false</allowInChatterGroups>
    <compactLayoutAssignment>LT_Driver_Document_Summary</compactLayoutAssignment>
    <deploymentStatus>Deployed</deploymentStatus>
    <description>Documento apresentado por um motorista durante o cadastro. Detail de Motorista.</description>
    <enableActivities>false</enableActivities>
    <enableBulkApi>true</enableBulkApi>
    <enableHistory>true</enableHistory>
    <enableReports>true</enableReports>
    <enableSearch>true</enableSearch>
    <enableStreamingApi>true</enableStreamingApi>
    <label>Documento do Motorista</label>
    <nameField>
        <displayFormat>DOC-{00000}</displayFormat>
        <label>Codigo do Documento</label>
        <type>AutoNumber</type>
    </nameField>
    <pluralLabel>Documentos do Motorista</pluralLabel>
    <sharingModel>ControlledByParent</sharingModel>
    <visibility>Public</visibility>
</CustomObject>
""")

print("Vehicle fields:", len(os.listdir(os.path.join(V, "fields"))))
print("Document fields:", len(os.listdir(os.path.join(DD, "fields"))))

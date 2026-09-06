#!/usr/bin/env python3
import os
ROOT = r"C:\Users\Robert Luis\Desktop\LogiTrack-SFDX\force-app\main\default"

# ---- simple layouts for Vehicle & Document ----
def layout(path, sections):
    secs = ""
    for label, style, cols in sections:
        colblocks = ""
        for col in cols:
            items = "".join(f"""
            <layoutItems>
                <behavior>{beh}</behavior>
                <field>{fld}</field>
            </layoutItems>""" for beh, fld in col)
            colblocks += f"""
        <layoutColumns>{items}
        </layoutColumns>"""
        secs += f"""
    <layoutSections>
        <customLabel>true</customLabel>
        <detailHeading>true</detailHeading>
        <editHeading>true</editHeading>
        <label>{label}</label>{colblocks}
        <style>{style}</style>
    </layoutSections>"""
    open(path, "w", encoding="utf-8").write(
f"""<?xml version="1.0" encoding="UTF-8"?>
<Layout xmlns="http://soap.sforce.com/2006/04/metadata">{secs}
    <showEmailCheckbox>false</showEmailCheckbox>
    <showHighlightsPanel>true</showHighlightsPanel>
    <showInteractionLogPanel>false</showInteractionLogPanel>
    <showRunAssignmentRulesCheckbox>false</showRunAssignmentRulesCheckbox>
    <showSubmitAndAttachButton>false</showSubmitAndAttachButton>
</Layout>
""")

layout(os.path.join(ROOT, "layouts", "LT_Vehicle__c-Veiculo Layout.layout-meta.xml"), [
  ("Identificacao do Veiculo", "TwoColumnsLeftToRight",
   [[("Edit", "LT_Plate__c"), ("Edit", "LT_Vehicle_Type__c")],
    [("Edit", "LT_Brand_Model__c"), ("Edit", "LT_Model_Year__c"), ("Edit", "LT_Vehicle_Status__c"), ("Edit", "OwnerId")]]),
  ("Capacidade e Vinculo", "TwoColumnsLeftToRight",
   [[("Edit", "LT_Cargo_Capacity_M3__c"), ("Edit", "LT_Cargo_Capacity_Packages__c")],
    [("Edit", "LT_Driver__c"), ("Edit", "LT_Owner_Type__c")]]),
  ("Documentacao", "TwoColumnsLeftToRight",
   [[("Edit", "LT_CRLV_Expiration__c"), ("Edit", "LT_Insurance_Expiration__c")],
    [("Readonly", "LT_Document_Status__c")]]),
])

layout(os.path.join(ROOT, "layouts", "LT_Driver_Document__c-Documento do Motorista Layout.layout-meta.xml"), [
  ("Documento", "TwoColumnsLeftToRight",
   [[("Required", "LT_Driver__c"), ("Edit", "LT_Document_Type__c"), ("Edit", "LT_Document_Number__c")],
    [("Edit", "LT_Issue_Date__c"), ("Edit", "LT_Expiration_Date__c"), ("Readonly", "LT_Situation__c")]]),
  ("Verificacao", "TwoColumnsLeftToRight",
   [[("Edit", "LT_Verified__c"), ("Edit", "LT_Verified_By__c")],
    [("Edit", "LT_Verification_Date__c"), ("Edit", "LT_File_Link__c")]]),
])

# ---- permission set LT_Cadastro ----
def fp(field, e):
    return f"""    <fieldPermissions>
        <editable>{str(e).lower()}</editable>
        <field>{field}</field>
        <readable>true</readable>
    </fieldPermissions>
"""
def op(obj, c, e, d, r=True):
    return f"""    <objectPermissions>
        <allowCreate>{str(c).lower()}</allowCreate>
        <allowDelete>{str(d).lower()}</allowDelete>
        <allowEdit>{str(e).lower()}</allowEdit>
        <allowRead>{str(r).lower()}</allowRead>
        <modifyAllRecords>false</modifyAllRecords>
        <object>{obj}</object>
        <viewAllFields>false</viewAllFields>
        <viewAllRecords>false</viewAllRecords>
    </objectPermissions>
"""
def tab(t):
    return f"""    <tabSettings>
        <tab>{t}</tab>
        <visibility>Visible</visibility>
    </tabSettings>
"""

# editable driver fields (skip required Name; skip formulas)
drv_fields = [
 ("LT_Driver__c.LT_CPF__c", True), ("LT_Driver__c.LT_CNPJ__c", True),
 ("LT_Driver__c.LT_Phone__c", True), ("LT_Driver__c.LT_PIX_Key__c", True),
 ("LT_Driver__c.LT_CNH_Number__c", True), ("LT_Driver__c.LT_CNH_Category__c", True),
 ("LT_Driver__c.LT_CNH_Expiration__c", True), ("LT_Driver__c.LT_CNH_Status__c", False),
 ("LT_Driver__c.LT_Category_Code__c", False), ("LT_Driver__c.LT_Driver_Code__c", False),
 ("LT_Driver__c.LT_Payment_Model__c", False), ("LT_Driver__c.LT_Min_Packages_Per_Trip__c", False),
 ("LT_Driver__c.LT_Max_Packages_Per_Trip__c", False), ("LT_Driver__c.LT_Vehicle_Requirement__c", False),
 ("LT_Driver__c.LT_Home_Base__c", True), ("LT_Driver__c.LT_Operating_Partner__c", True),
 ("LT_Driver__c.LT_Lead_Driver__c", True), ("LT_Driver__c.LT_Driver_Status__c", True),
 ("LT_Driver__c.LT_Onboarding_Date__c", True), ("LT_Driver__c.LT_Termination_Date__c", True),
 ("LT_Driver__c.LT_Notes__c", True),
 ("LT_Driver__c.LT_Pending_Documents__c", False),
]
veh_fields = [
 ("LT_Vehicle__c.LT_Plate__c", True), ("LT_Vehicle__c.LT_Vehicle_Type__c", True),
 ("LT_Vehicle__c.LT_Brand_Model__c", True), ("LT_Vehicle__c.LT_Model_Year__c", True),
 ("LT_Vehicle__c.LT_Cargo_Capacity_M3__c", True), ("LT_Vehicle__c.LT_Cargo_Capacity_Packages__c", True),
 ("LT_Vehicle__c.LT_Owner_Type__c", True), ("LT_Vehicle__c.LT_Driver__c", True),
 ("LT_Vehicle__c.LT_CRLV_Expiration__c", True), ("LT_Vehicle__c.LT_Insurance_Expiration__c", True),
 ("LT_Vehicle__c.LT_Vehicle_Status__c", True), ("LT_Vehicle__c.LT_Document_Status__c", False),
]
doc_fields = [
 ("LT_Driver_Document__c.LT_Document_Type__c", True), ("LT_Driver_Document__c.LT_Document_Number__c", True),
 ("LT_Driver_Document__c.LT_Issue_Date__c", True), ("LT_Driver_Document__c.LT_Expiration_Date__c", True),
 ("LT_Driver_Document__c.LT_Situation__c", False), ("LT_Driver_Document__c.LT_Verified__c", True), ("LT_Driver_Document__c.LT_Verified_By__c", True),
 ("LT_Driver_Document__c.LT_Verification_Date__c", True), ("LT_Driver_Document__c.LT_File_Link__c", True),
]

rtvis = "".join(f"""    <recordTypeVisibilities>
        <recordType>LT_Driver__c.{rt}</recordType>
        <visible>true</visible>
    </recordTypeVisibilities>
""" for rt in ["LT_TAC", "LT_MEI", "LT_ETC", "LT_Coleta", "LT_MR"])

ps = ['<?xml version="1.0" encoding="UTF-8"?>', '<PermissionSet xmlns="http://soap.sforce.com/2006/04/metadata">']
ps.append('    <description>Equipe de Cadastro: cria e mantem motoristas, veiculos e documentacao. Acesso de leitura as unidades logisticas e parceiros.</description>')
ps.append('    <hasActivationRequired>false</hasActivationRequired>')
ps.append('    <label>LT - Cadastro de Motoristas</label>')
for f, e in drv_fields + veh_fields + doc_fields:
    ps.append(fp(f, e).rstrip("\n"))
ps.append('    <applicationVisibilities>\n        <application>LogiTrack_Cadastro</application>\n        <visible>true</visible>\n    </applicationVisibilities>')
ps.append('    <applicationVisibilities>\n        <application>LogiTrack_Operations_360</application>\n        <visible>true</visible>\n    </applicationVisibilities>')
ps.append(rtvis.rstrip("\n"))
ps.append(op("LT_Driver__c", True, True, False).rstrip("\n"))
ps.append(op("LT_Vehicle__c", True, True, False).rstrip("\n"))
ps.append(op("LT_Driver_Document__c", True, True, True).rstrip("\n"))
ps.append(op("LT_Logistics_Unit__c", False, False, False).rstrip("\n"))
ps.append(op("Account", False, False, False).rstrip("\n"))
for t in ["LT_Driver__c", "LT_Vehicle__c", "LT_Driver_Document__c", "LT_Logistics_Unit__c"]:
    ps.append(tab(t).rstrip("\n"))
ps.append('</PermissionSet>')
open(os.path.join(ROOT, "permissionsets", "LT_Cadastro.permissionset-meta.xml"), "w", encoding="utf-8").write("\n".join(ps) + "\n")

# ---- app ----
open(os.path.join(ROOT, "applications", "LogiTrack_Cadastro.app-meta.xml"), "w", encoding="utf-8").write(
"""<?xml version="1.0" encoding="UTF-8"?>
<CustomApplication xmlns="http://soap.sforce.com/2006/04/metadata">
    <brand>
        <headerColor>#5B3A8C</headerColor>
        <shouldOverrideOrgTheme>false</shouldOverrideOrgTheme>
    </brand>
    <description>Aplicativo da equipe de Cadastro da LogiTrack: motoristas, veiculos e documentacao.</description>
    <formFactors>Large</formFactors>
    <formFactors>Small</formFactors>
    <isNavAutoTempTabsDisabled>false</isNavAutoTempTabsDisabled>
    <isNavPersonalizationDisabled>false</isNavPersonalizationDisabled>
    <isNavTabPersistenceDisabled>false</isNavTabPersistenceDisabled>
    <label>LogiTrack Cadastro</label>
    <navType>Standard</navType>
    <tabs>standard-home</tabs>
    <tabs>LT_Driver__c</tabs>
    <tabs>LT_Vehicle__c</tabs>
    <tabs>LT_Driver_Document__c</tabs>
    <tabs>LT_Logistics_Unit__c</tabs>
    <tabs>standard-report</tabs>
    <tabs>standard-Dashboard</tabs>
    <uiType>Lightning</uiType>
</CustomApplication>
""")

print("C security + layouts + app written")

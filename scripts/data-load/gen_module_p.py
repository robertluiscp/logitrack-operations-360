#!/usr/bin/env python3
"""Modulo P: Lightning Record Pages (Dynamic Forms) para os objetos-bandeira."""
import os, uuid
ROOT = r"C:\Users\Robert Luis\Desktop\LogiTrack-SFDX\force-app\main\default"
FP = os.path.join(ROOT, "flexipages")

def w(path, body):
    open(path, "w", encoding="utf-8", newline="\n").write(body.rstrip() + "\n")

def fid():
    return "Facet-" + str(uuid.uuid4())

def field_instance(api, behavior="none"):
    ident = "Record" + api.replace("__c", "_c").replace(".", "") + "Field"
    return f"""            <fieldInstance>
                <fieldInstanceProperties>
                    <name>uiBehavior</name>
                    <value>{behavior}</value>
                </fieldInstanceProperties>
                <fieldItem>Record.{api}</fieldItem>
                <identifier>{ident}</identifier>
            </fieldInstance>"""

def region_facet(name, items):
    body = "\n".join(f"        <itemInstances>\n{it}\n        </itemInstances>" for it in items)
    return f"""    <flexiPageRegions>
{body}
        <name>{name}</name>
        <type>Facet</type>
    </flexiPageRegions>"""

def column_comp(facet_name, ident):
    return f"""            <componentInstance>
                <componentInstanceProperties>
                    <name>body</name>
                    <value>{facet_name}</value>
                </componentInstanceProperties>
                <componentName>flexipage:column</componentName>
                <identifier>{ident}</identifier>
            </componentInstance>"""

def field_section_comp(cols_facet, label, ident):
    return f"""            <componentInstance>
                <componentInstanceProperties>
                    <name>columns</name>
                    <value>{cols_facet}</value>
                </componentInstanceProperties>
                <componentInstanceProperties>
                    <name>horizontalAlignment</name>
                    <value>false</value>
                </componentInstanceProperties>
                <componentInstanceProperties>
                    <name>label</name>
                    <value>{label}</value>
                </componentInstanceProperties>
                <componentName>flexipage:fieldSection</componentName>
                <identifier>{ident}</identifier>
            </componentInstance>"""

def record_page(dev_name, label, sobject, sections, related_lists):
    regions = []
    # header
    regions.append("""    <flexiPageRegions>
        <itemInstances>
            <componentInstance>
                <componentInstanceProperties>
                    <name>numVisibleActions</name>
                    <value>4</value>
                </componentInstanceProperties>
                <componentName>force:highlightsPanel</componentName>
                <identifier>force_highlightsPanel</identifier>
            </componentInstance>
        </itemInstances>
        <name>header</name>
        <type>Region</type>
    </flexiPageRegions>""")
    # related list container facet
    regions.append("""    <flexiPageRegions>
        <itemInstances>
            <componentInstance>
                <componentInstanceProperties>
                    <name>relatedListComponentOverride</name>
                    <value>NONE</value>
                </componentInstanceProperties>
                <componentInstanceProperties>
                    <name>rowsToDisplay</name>
                    <value>10</value>
                </componentInstanceProperties>
                <componentName>force:relatedListContainer</componentName>
                <identifier>force_relatedListContainer</identifier>
            </componentInstance>
        </itemInstances>
        <name>relatedTabContent</name>
        <type>Facet</type>
    </flexiPageRegions>""")

    section_comps = []
    n = 0
    for sec_label, fields in sections:
        n += 1
        half = (len(fields) + 1) // 2
        left, right = fields[:half], fields[half:]
        f_left, f_right, f_cols = fid(), fid(), fid()
        regions.append(region_facet(f_left, [field_instance(a, b) for a, b in left]))
        regions.append(region_facet(f_right, [field_instance(a, b) for a, b in right]) if right else region_facet(f_right, [field_instance(left[0][0], left[0][1])]))
        regions.append(region_facet(f_cols, [column_comp(f_left, f"col_{n}_1"), column_comp(f_right, f"col_{n}_2")]))
        section_comps.append(field_section_comp(f_cols, sec_label, f"fieldSection_{n}"))

    # system info section
    f_sys_l, f_sys_r, f_sys_c = fid(), fid(), fid()
    regions.append(region_facet(f_sys_l, [field_instance("CreatedById", "readonly")]))
    regions.append(region_facet(f_sys_r, [field_instance("LastModifiedById", "readonly")]))
    regions.append(region_facet(f_sys_c, [column_comp(f_sys_l, "col_sys_1"), column_comp(f_sys_r, "col_sys_2")]))
    section_comps.append(field_section_comp(f_sys_c, "@@@SFDCSystem_InformationSFDC@@@", "fieldSection_sys"))

    regions.append("""    <flexiPageRegions>
""" + "\n".join(f"        <itemInstances>\n{c}\n        </itemInstances>" for c in section_comps) + """
        <name>detailTabContent</name>
        <type>Facet</type>
    </flexiPageRegions>""")

    # main tabs (detail + related)
    regions.append("""    <flexiPageRegions>
        <itemInstances>
            <componentInstance>
                <componentInstanceProperties>
                    <name>body</name>
                    <value>relatedTabContent</value>
                </componentInstanceProperties>
                <componentInstanceProperties>
                    <name>title</name>
                    <value>Standard.Tab.relatedLists</value>
                </componentInstanceProperties>
                <componentName>flexipage:tab</componentName>
                <identifier>relatedListsTab</identifier>
            </componentInstance>
        </itemInstances>
        <itemInstances>
            <componentInstance>
                <componentInstanceProperties>
                    <name>active</name>
                    <value>true</value>
                </componentInstanceProperties>
                <componentInstanceProperties>
                    <name>body</name>
                    <value>detailTabContent</value>
                </componentInstanceProperties>
                <componentInstanceProperties>
                    <name>title</name>
                    <value>Standard.Tab.detail</value>
                </componentInstanceProperties>
                <componentName>flexipage:tab</componentName>
                <identifier>detailTab</identifier>
            </componentInstance>
        </itemInstances>
        <name>maintabs</name>
        <type>Facet</type>
    </flexiPageRegions>""")

    regions.append("""    <flexiPageRegions>
        <itemInstances>
            <componentInstance>
                <componentInstanceProperties>
                    <name>tabs</name>
                    <value>maintabs</value>
                </componentInstanceProperties>
                <componentName>flexipage:tabset</componentName>
                <identifier>flexipage_tabset</identifier>
            </componentInstance>
        </itemInstances>
        <name>main</name>
        <type>Region</type>
    </flexiPageRegions>""")

    regions.append("""    <flexiPageRegions>
        <itemInstances>
            <componentInstance>
                <componentInstanceProperties>
                    <name>showLegacyActivityComposer</name>
                    <value>false</value>
                </componentInstanceProperties>
                <componentName>runtime_sales_activities:activityPanel</componentName>
                <identifier>runtime_sales_activities_activityPanel</identifier>
            </componentInstance>
        </itemInstances>
        <name>sidebar</name>
        <type>Region</type>
    </flexiPageRegions>""")

    body = f"""<?xml version="1.0" encoding="UTF-8"?>
<FlexiPage xmlns="http://soap.sforce.com/2006/04/metadata">
{chr(10).join(regions)}
    <masterLabel>{label}</masterLabel>
    <sobjectType>{sobject}</sobjectType>
    <template>
        <name>flexipage:recordHomeTemplateDesktop</name>
    </template>
    <type>RecordPage</type>
</FlexiPage>"""
    w(os.path.join(FP, f"{dev_name}.flexipage-meta.xml"), body)


# E = Edit, R = readonly, N = none
def F(*items):
    return [(a, b) for a, b in items]

record_page("LT_Payment_Request_Record_Page", "Solicitacao de Pagamento - Record Page", "LT_Payment_Request__c", [
    ("Solicitacao", F(("Name","none"),("LT_Request_Type__c","none"),("LT_Status__c","none"),("LT_Priority__c","none"),
                      ("LT_Amount__c","required"),("LT_Approval_Level__c","readonly"),("LT_Cost_Center__c","none"),
                      ("LT_Request_Date__c","required"),("LT_Due_Date__c","required"))),
    ("Favorecido", F(("LT_Payee_Name__c","required"),("LT_Payee_Document__c","none"),("LT_Payment_Method__c","none"),
                     ("LT_Payee_Pix_Key__c","none"),("LT_Bank_Details__c","none"),("LT_Invoice_Number__c","none"))),
    ("Vinculos", F(("LT_Shipper__c","none"),("LT_Driver__c","none"),("LT_Manifest__c","none"),
                   ("LT_Base__c","none"),("LT_Loss_Claim__c","none"),("LT_Requested_By__c","none"))),
    ("Aprovacao e Pagamento", F(("LT_Approved_By__c","readonly"),("LT_Approval_Date__c","readonly"),
                                ("LT_Amount_Paid__c","readonly"),("LT_Balance__c","readonly"),
                                ("LT_Fully_Paid__c","readonly"),("LT_Is_Overdue__c","readonly"),
                                ("LT_Days_To_Due__c","readonly"),("LT_Last_Payment_Date__c","readonly"))),
    ("Justificativa", F(("LT_Description__c","none"),("LT_Rejection_Reason__c","none"))),
], ["LT_Payment__c.LT_Payment_Request__c", "LT_Expense__c.LT_Payment_Request__c"])

record_page("LT_Shipment_Record_Page", "Remessa - Record Page", "LT_Shipment__c", [
    ("Remessa", F(("Name","none"),("LT_Tracking_Code__c","none"),("LT_Status__c","none"),("LT_Shipper__c","none"),
                  ("LT_Package_Type__c","none"),("LT_Collection_Type__c","none"),("LT_Weight_Kg__c","none"),
                  ("LT_Declared_Value__c","none"))),
    ("Origem e Destino", F(("LT_Origin_Marketplace__c","none"),("LT_Origin_Pickup_Point__c","none"),
                           ("LT_Destination_CD__c","none"),("LT_Delivery_Base__c","none"),
                           ("LT_Dest_Street__c","none"),("LT_Dest_District__c","none"),("LT_Dest_City__c","none"),
                           ("LT_Dest_State__c","none"),("LT_Dest_ZIP__c","none"))),
    ("Rastreamento", F(("LT_Last_Event_Date__c","readonly"),("LT_Is_Delivered__c","readonly"),
                       ("LT_Is_Late__c","readonly"),("LT_Delivered_Date__c","readonly"),
                       ("LT_Days_In_Transit__c","readonly"),("LT_Hours_Without_Movement__c","readonly"),
                       ("LT_Delivery_Attempts__c","readonly"))),
], ["LT_Tracking_Event__c.LT_Shipment__c"])

record_page("LT_Loss_Claim_Record_Page", "Extravio - Record Page", "LT_Loss_Claim__c", [
    ("Extravio", F(("Name","none"),("LT_Shipment__c","required"),("LT_Loss_Reason__c","none"),
                   ("LT_Loss_Sub_Reason__c","none"),("LT_Status__c","none"),("LT_Detected_Date__c","required"))),
    ("Responsabilidade", F(("LT_Responsibility__c","none"),("LT_Responsible_Driver__c","none"),
                           ("LT_Responsible_Base__c","none"),("LT_Case__c","none"),("LT_Operational_Incident__c","none"))),
    ("Valores", F(("LT_Declared_Value__c","none"),("LT_Reimbursement_Value__c","none"),
                  ("LT_Driver_Charge_Value__c","none"),("LT_Net_Company_Cost__c","readonly"),
                  ("LT_Generates_Penalty__c","readonly"),("LT_Approved_By__c","none"),
                  ("LT_Approval_Date__c","none"),("LT_Reimbursement_Date__c","none"))),
    ("Encerramento", F(("LT_Description__c","none"),("LT_Resolution_Notes__c","none"))),
], ["LT_Driver_Penalty__c.LT_Loss_Claim__c"])

record_page("LT_Driver_Record_Page", "Motorista - Record Page", "LT_Driver__c", [
    ("Motorista", F(("Name","none"),("LT_Driver_Code__c","none"),("LT_Driver_Status__c","none"),
                    ("LT_Category_Code__c","readonly"),("LT_Home_Base__c","none"),("LT_Operating_Partner__c","none"),
                    ("LT_Phone__c","none"),("LT_PIX_Key__c","none"))),
    ("Documentos", F(("LT_CPF__c","none"),("LT_CNPJ__c","none"),("LT_CNH_Number__c","none"),
                     ("LT_CNH_Category__c","none"),("LT_CNH_Expiration__c","none"),("LT_CNH_Status__c","readonly"))),
    ("Regras da Categoria", F(("LT_Payment_Model__c","readonly"),("LT_Min_Packages_Per_Trip__c","readonly"),
                              ("LT_Max_Packages_Per_Trip__c","readonly"),("LT_Vehicle_Requirement__c","readonly"),
                              ("LT_Pending_Documents__c","readonly"))),
], ["LT_Vehicle__c.LT_Driver__c", "LT_Driver_Document__c.LT_Driver__c", "LT_Manifest__c.LT_Driver__c", "LT_Driver_Penalty__c.LT_Driver__c"])

record_page("LT_Operational_Incident_Record_Page", "Ocorrencia Operacional - Record Page", "LT_Operational_Incident__c", [
    ("Ocorrencia", F(("Name","none"),("LT_Incident_Type__c","none"),("LT_Root_Cause__c","none"),("LT_Status__c","none"),
                     ("LT_Priority__c","none"),("LT_Shipment__c","none"),("LT_Owner_Unit__c","none"),
                     ("LT_Responsible_Driver__c","none"))),
    ("Prazos", F(("LT_Detected_Date__c","none"),("LT_Resolution_Deadline__c","readonly"),("LT_Days_Open__c","readonly"),
                 ("LT_Aging_Bucket__c","readonly"),("LT_Is_Open__c","readonly"),("LT_Is_Overdue__c","readonly"),
                 ("LT_Escalated__c","readonly"),("LT_Escalation_Date__c","readonly"))),
    ("Resolucao", F(("LT_Assigned_To__c","none"),("LT_Resolution_Type__c","none"),("LT_Resolved_Date__c","none"),
                    ("LT_Description__c","none"),("LT_Resolution_Notes__c","none"))),
], [])

record_page("LT_Route_Record_Page", "Rota - Record Page", "LT_Route__c", [
    ("Rota", F(("Name","none"),("LT_Route_Date__c","none"),("LT_Route_Type__c","none"),("LT_Status__c","none"),
               ("LT_Driver__c","none"),("LT_Vehicle__c","none"),("LT_Base__c","none"),("LT_Target_City__c","none"))),
    ("Carga", F(("LT_Planned_Packages__c","none"),("LT_Loaded_Packages__c","none"),("LT_Driver_Max_Packages__c","readonly"),
                ("LT_Distance_Km__c","none"),("LT_MR_Eligible__c","readonly"))),
    ("Resultado", F(("LT_Attempts_Count__c","readonly"),("LT_Delivered_Count__c","readonly"),
                    ("LT_Success_Rate__c","readonly"),("LT_Departure_Time__c","none"),("LT_Return_Time__c","none"),
                    ("LT_Notes__c","none"))),
], ["LT_Delivery_Attempt__c.LT_Route__c"])

print("Modulo P: record pages geradas ->", len([f for f in os.listdir(FP) if f.endswith('_Record_Page.flexipage-meta.xml')]))

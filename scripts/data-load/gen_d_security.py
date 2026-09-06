#!/usr/bin/env python3
import os
ROOT = r"C:\Users\Robert Luis\Desktop\LogiTrack-SFDX\force-app\main\default"

def fp(field, e):
    return f"""    <fieldPermissions>
        <editable>{str(e).lower()}</editable>
        <field>{field}</field>
        <readable>true</readable>
    </fieldPermissions>"""

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
    </objectPermissions>"""

def tab(t):
    return f"""    <tabSettings>
        <tab>{t}</tab>
        <visibility>Visible</visibility>
    </tabSettings>"""

# Shipment editable fields (skip required Name/tracking/shipper/recipient/city/zip/sla, skip formulas & rollups)
ship_edit = ["LT_Origin_Marketplace__c", "LT_Collection_Type__c", "LT_Package_Type__c",
   "LT_Sender_Name__c", "LT_Recipient_Phone__c", "LT_Dest_Street__c", "LT_Dest_District__c",
   "LT_Dest_State__c", "LT_Weight_Kg__c", "LT_Declared_Value__c", "LT_Origin_Pickup_Point__c",
   "LT_Destination_CD__c", "LT_Delivery_Base__c", "LT_Last_Mile_Driver__c", "LT_Status__c",
   "LT_Current_Holder__c", "LT_Posted_Date__c", "LT_Collected_Date__c", "LT_Delivered_Date__c",
   "LT_Delivery_Attempts__c", "LT_Value_Reimbursed__c"]
ship_read = ["LT_Event_Count__c", "LT_Last_Event_Date__c", "LT_Is_Delivered__c", "LT_Is_Terminal__c",
   "LT_On_Time__c", "LT_Is_Late__c", "LT_Days_In_Transit__c", "LT_Hours_Without_Movement__c"]
evt_edit = ["LT_Event_Type__c", "LT_Unit__c", "LT_Driver__c", "LT_Location_City__c",
   "LT_Responsible_User__c", "LT_Notes__c"]

lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<PermissionSet xmlns="http://soap.sforce.com/2006/04/metadata">']
lines.append('    <description>Operacao: registra e acompanha remessas e eventos de rastreamento; leitura de motoristas, unidades e embarcadores.</description>')
lines.append('    <hasActivationRequired>false</hasActivationRequired>')
lines.append('    <label>LT - Operacao (Remessas)</label>')
for f in ship_edit:
    lines.append(fp(f"LT_Shipment__c.{f}", True))
for f in ship_read:
    lines.append(fp(f"LT_Shipment__c.{f}", False))
for f in evt_edit:
    lines.append(fp(f"LT_Tracking_Event__c.{f}", True))
lines.append("""    <applicationVisibilities>
        <application>LogiTrack_Operations_360</application>
        <visible>true</visible>
    </applicationVisibilities>""")
lines.append(op("LT_Shipment__c", True, True, False))
lines.append(op("LT_Tracking_Event__c", True, True, True))
lines.append(op("LT_Driver__c", False, False, False))
lines.append(op("LT_Logistics_Unit__c", False, False, False))
lines.append(op("Account", False, False, False))
for t in ["LT_Shipment__c", "LT_Tracking_Event__c", "LT_Logistics_Unit__c", "Operational_Indicator__c"]:
    lines.append(tab(t))
lines.append('</PermissionSet>')
open(os.path.join(ROOT, "permissionsets", "LT_Operations.permissionset-meta.xml"), "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")

# ---- update LogiTrack_Operations_360 app: add tabs ----
p = os.path.join(ROOT, "applications", "LogiTrack_Operations_360.app-meta.xml")
t = open(p, encoding="utf-8").read()
if "<tabs>LT_Shipment__c</tabs>" not in t:
    t = t.replace("    <tabs>Operational_Indicator__c</tabs>\n",
                  "    <tabs>Operational_Indicator__c</tabs>\n    <tabs>LT_Shipment__c</tabs>\n    <tabs>LT_Tracking_Event__c</tabs>\n    <tabs>LT_Driver__c</tabs>\n    <tabs>LT_Vehicle__c</tabs>\n")
open(p, "w", encoding="utf-8", newline="\n").write(t)
print("LT_Operations permset + app updated")

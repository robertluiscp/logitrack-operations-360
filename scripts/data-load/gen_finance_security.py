#!/usr/bin/env python3
import os
ROOT = r"C:\Users\Robert Luis\Desktop\LogiTrack-SFDX\force-app\main\default"

def fp(f, e): return f'    <fieldPermissions>\n        <editable>{str(e).lower()}</editable>\n        <field>{f}</field>\n        <readable>true</readable>\n    </fieldPermissions>'
def op(o, c, e, d): return f'    <objectPermissions>\n        <allowCreate>{str(c).lower()}</allowCreate>\n        <allowDelete>{str(d).lower()}</allowDelete>\n        <allowEdit>{str(e).lower()}</allowEdit>\n        <allowRead>true</allowRead>\n        <modifyAllRecords>false</modifyAllRecords>\n        <object>{o}</object>\n        <viewAllFields>false</viewAllFields>\n        <viewAllRecords>false</viewAllRecords>\n    </objectPermissions>'
def tab(t): return f'    <tabSettings>\n        <tab>{t}</tab>\n        <visibility>Visible</visibility>\n    </tabSettings>'
def app(a): return f'    <applicationVisibilities>\n        <application>{a}</application>\n        <visible>true</visible>\n    </applicationVisibilities>'

# NOTE: required fields (LT_Amount__c, LT_Request_Date__c, LT_Due_Date__c, LT_Payee_Name__c on PR;
# LT_Amount__c, LT_Payment_Date__c on PAY; LT_Amount__c, LT_Expense_Date__c, LT_Competency_Month__c on EXP)
# are omitted: Salesforce rejects FLS entries for universally-required fields.
pr_e = ["LT_Request_Type__c", "LT_Status__c", "LT_Priority__c", "LT_Cost_Center__c", "LT_Payment_Method__c",
  "LT_Shipper__c", "LT_Driver__c", "LT_Manifest__c", "LT_Base__c", "LT_Loss_Claim__c", "LT_Requested_By__c",
  "LT_Approved_By__c", "LT_Approval_Date__c",
  "LT_Payee_Document__c", "LT_Payee_Pix_Key__c", "LT_Bank_Details__c",
  "LT_Invoice_Number__c", "LT_Recurring__c", "LT_Description__c", "LT_Rejection_Reason__c"]
pr_r = ["LT_Amount_Paid__c", "LT_Payment_Count__c", "LT_Last_Payment_Date__c", "LT_Approval_Level__c",
  "LT_Balance__c", "LT_Fully_Paid__c", "LT_Days_To_Due__c", "LT_Is_Overdue__c", "LT_Status_Text__c"]
pay_e = ["LT_Status__c", "LT_Payment_Method__c", "LT_Bank_Account__c",
  "LT_Transaction_Id__c", "LT_Paid_By__c", "LT_Fee_Amount__c", "LT_Reconciled__c", "LT_Reconciliation_Date__c", "LT_Notes__c"]
pay_r = ["LT_Total_Disbursed__c"]
exp_e = ["LT_Expense_Category__c", "LT_Status__c", "LT_Cost_Center__c", "LT_Base__c",
  "LT_Payment_Request__c", "LT_Supplier__c", "LT_Invoice_Number__c",
  "LT_Recurring__c", "LT_Pass_Through__c", "LT_Description__c"]
exp_r = ["LT_Is_Paid__c"]

L = ['<?xml version="1.0" encoding="UTF-8"?>', '<PermissionSet xmlns="http://soap.sforce.com/2006/04/metadata">']
L.append('    <description>Financeiro: solicitacoes de pagamento, aprovacao por alcada, pagamentos e despesas por centro de custo.</description>')
L.append('    <hasActivationRequired>false</hasActivationRequired>')
L.append('    <label>LT - Financeiro</label>')
for f in pr_e: L.append(fp(f"LT_Payment_Request__c.{f}", True))
for f in pr_r: L.append(fp(f"LT_Payment_Request__c.{f}", False))
for f in pay_e: L.append(fp(f"LT_Payment__c.{f}", True))
for f in pay_r: L.append(fp(f"LT_Payment__c.{f}", False))
for f in exp_e: L.append(fp(f"LT_Expense__c.{f}", True))
for f in exp_r: L.append(fp(f"LT_Expense__c.{f}", False))
L.append(app("LogiTrack_Financeiro"))
L.append(app("LogiTrack_Operations_360"))
L.append(op("LT_Payment_Request__c", True, True, True))
L.append(op("LT_Payment__c", True, True, True))
L.append(op("LT_Expense__c", True, True, True))
L.append(op("Account", False, False, False))
L.append(op("LT_Driver__c", False, False, False))
L.append(op("LT_Manifest__c", False, False, False))
L.append(op("LT_Logistics_Unit__c", False, False, False))
L.append(op("LT_Loss_Claim__c", False, True, False))
for t in ["LT_Payment_Request__c", "LT_Payment__c", "LT_Expense__c"]:
    L.append(tab(t))
L.append('</PermissionSet>')
open(os.path.join(ROOT, "permissionsets", "LT_Finance.permissionset-meta.xml"), "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
print("LT_Finance permission set written:", len(pr_e) + len(pr_r) + len(pay_e) + len(pay_r) + len(exp_e) + len(exp_r), "field grants")

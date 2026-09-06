#!/usr/bin/env python3
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from metahelp import *

ROOT = r"C:\Users\Robert Luis\Desktop\LogiTrack-SFDX\force-app\main\default"
PR = os.path.join(ROOT, "objects", "LT_Payment_Request__c")
PAY = os.path.join(ROOT, "objects", "LT_Payment__c")
EXP = os.path.join(ROOT, "objects", "LT_Expense__c")
for b in (PR, PAY, EXP):
    ensure(b)

# shared picklist value sets
REQ_TYPE = ["Pagamento a Embarcador (Ressarcimento)", "Pagamento a Motorista (Romaneio)",
            "Folha de Pagamento (Funcionarios)", "Insumos para Base/Escritorio",
            "Verba para Viagem/Projeto", "Abertura de Galpao/Nova Base",
            "Reembolso de Despesa", "Fornecedor / Prestador de Servico", "Outro"]
COST_CENTER = ["Operacao - Ultima Milha", "Operacao - Primeira Milha", "Comercial",
               "Cadastro / Frota", "SAC", "Administrativo / RH", "Financeiro",
               "Expansao / Novas Bases", "Diretoria"]
PAY_METHOD = ["PIX", "TED / Transferencia", "Boleto", "Cartao Corporativo", "Dinheiro (Caixa)"]
PR_STATUS = ["Rascunho", "Em Aprovacao", "Aprovada", "Reprovada", "Paga", "Cancelada"]
PRIORITY = ["Baixa", "Normal", "Alta", "Urgente"]

# ==================== LT_Payment_Request__c ====================
wf(PR, "LT_Request_Type__c", picklist("LT_Request_Type__c", "Tipo de Solicitacao",
   "Natureza do pagamento solicitado.", REQ_TYPE, track=False))
wf(PR, "LT_Status__c", picklist("LT_Status__c", "Status",
   "Etapa da solicitacao: rascunho, aprovacao, pagamento.", PR_STATUS, default="Rascunho"))
wf(PR, "LT_Priority__c", picklist("LT_Priority__c", "Prioridade",
   "Urgencia do pagamento.", PRIORITY, default="Normal", track=False))
wf(PR, "LT_Cost_Center__c", picklist("LT_Cost_Center__c", "Centro de Custo",
   "Area a que a despesa e alocada.", COST_CENTER, track=False))
wf(PR, "LT_Payment_Method__c", picklist("LT_Payment_Method__c", "Forma de Pagamento",
   "Meio pelo qual o pagamento sera efetuado.", PAY_METHOD, default="PIX", track=False))

wf(PR, "LT_Shipper__c", lookup("LT_Shipper__c", "Embarcador", "Embarcador beneficiario do pagamento.",
   "Account", "Solicitacoes de Pagamento", "LT_Payment_Requests", lf_optional=True, track=False))
wf(PR, "LT_Driver__c", lookup("LT_Driver__c", "Motorista", "Motorista beneficiario do pagamento.",
   "LT_Driver__c", "Solicitacoes de Pagamento", "LT_Payment_Requests", lf_optional=True, track=False))
wf(PR, "LT_Manifest__c", lookup("LT_Manifest__c", "Romaneio", "Romaneio que originou o pagamento ao motorista.",
   "LT_Manifest__c", "Solicitacoes de Pagamento", "LT_Payment_Requests", lf_optional=True, track=False))
wf(PR, "LT_Base__c", lookup("LT_Base__c", "Base / Unidade", "Base ou unidade relacionada ao pagamento.",
   "LT_Logistics_Unit__c", "Solicitacoes de Pagamento", "LT_Payment_Requests", lf_optional=True, track=False))
wf(PR, "LT_Loss_Claim__c", lookup("LT_Loss_Claim__c", "Extravio", "Extravio cujo ressarcimento gera este pagamento.",
   "LT_Loss_Claim__c", "Solicitacoes de Pagamento", "LT_Payment_Requests", lf_optional=True, track=False))
wf(PR, "LT_Requested_By__c", lookup("LT_Requested_By__c", "Solicitado Por", "Usuario que abriu a solicitacao.",
   "User", "Solicitacoes de Pagamento Abertas", "LT_Opened_Payment_Requests", lf_optional=True, track=False))
wf(PR, "LT_Approved_By__c", lookup("LT_Approved_By__c", "Aprovado Por", "Usuario que aprovou a solicitacao.",
   "User", "Solicitacoes de Pagamento Aprovadas", "LT_Approved_Payment_Requests", lf_optional=True, track=False))

wf(PR, "LT_Amount__c", field("LT_Amount__c", "Valor Solicitado", "Valor total solicitado.", "Currency",
   required=True, precision=14, scale=2))
wf(PR, "LT_Request_Date__c", field("LT_Request_Date__c", "Data da Solicitacao", "Data de abertura da solicitacao.",
   "Date", required=True, default="TODAY()"))
wf(PR, "LT_Due_Date__c", field("LT_Due_Date__c", "Data de Vencimento", "Data limite para o pagamento.",
   "Date", required=True))
wf(PR, "LT_Approval_Date__c", field("LT_Approval_Date__c", "Data de Aprovacao", "Data em que a solicitacao foi aprovada.",
   "Date", track=False))
wf(PR, "LT_Payee_Name__c", field("LT_Payee_Name__c", "Favorecido", "Nome do favorecido do pagamento.", "Text",
   length=120, required=True, track=False))
wf(PR, "LT_Payee_Document__c", field("LT_Payee_Document__c", "CPF/CNPJ do Favorecido", "Documento do favorecido.",
   "Text", length=20, track=False))
wf(PR, "LT_Payee_Pix_Key__c", field("LT_Payee_Pix_Key__c", "Chave PIX", "Chave PIX do favorecido.", "Text",
   length=80, track=False))
wf(PR, "LT_Bank_Details__c", field("LT_Bank_Details__c", "Dados Bancarios", "Banco, agencia e conta do favorecido.",
   "Text", length=140, track=False))
wf(PR, "LT_Invoice_Number__c", field("LT_Invoice_Number__c", "Nota Fiscal / Documento", "Numero da NF ou documento de suporte.",
   "Text", length=40, track=False))
wf(PR, "LT_Recurring__c", field("LT_Recurring__c", "Recorrente", "Pagamento que se repete todo mes.", "Checkbox",
   default="false", track=False))
wf(PR, "LT_Description__c", field("LT_Description__c", "Justificativa", "Justificativa e detalhamento da solicitacao.",
   "LongTextArea", length=8000, lines=4, track=False))
wf(PR, "LT_Rejection_Reason__c", field("LT_Rejection_Reason__c", "Motivo da Reprovacao", "Motivo informado na reprovacao.",
   "LongTextArea", length=4000, lines=3, track=False))

# roll-ups from LT_Payment__c (MD child)
wf(PR, "LT_Amount_Paid__c", rollup("LT_Amount_Paid__c", "Valor Pago",
   "Soma dos pagamentos confirmados desta solicitacao.", "LT_Payment__c", "LT_Payment_Request__c",
   "Sum", "LT_Amount__c", filters=[("LT_Status__c", "equals", "Confirmado")]))
wf(PR, "LT_Payment_Count__c", rollup("LT_Payment_Count__c", "Qtd. Pagamentos",
   "Numero de pagamentos lancados para esta solicitacao.", "LT_Payment__c", "LT_Payment_Request__c", "Count"))
wf(PR, "LT_Last_Payment_Date__c", rollup("LT_Last_Payment_Date__c", "Ultimo Pagamento",
   "Data do pagamento mais recente.", "LT_Payment__c", "LT_Payment_Request__c", "Max", "LT_Payment_Date__c"))

# formula fields
wf(PR, "LT_Approval_Level__c", formula("LT_Approval_Level__c", "Alcada de Aprovacao",
   "Nivel de alcada exigido pelo valor solicitado.", "Text",
   'IF(BLANKVALUE(LT_Amount__c, 0) &gt;= 10000, "Diretoria", IF(BLANKVALUE(LT_Amount__c, 0) &gt;= 2000, "Gerencia", "Coordenacao"))',
   blanks="BlankAsZero"))
wf(PR, "LT_Balance__c", formula("LT_Balance__c", "Saldo a Pagar",
   "Valor solicitado menos o valor ja pago.", "Currency",
   'BLANKVALUE(LT_Amount__c, 0) - BLANKVALUE(LT_Amount_Paid__c, 0)', precision=16, scale=2))
wf(PR, "LT_Fully_Paid__c", formula("LT_Fully_Paid__c", "Quitada",
   "Verdadeiro quando o valor pago cobre o valor solicitado.", "Checkbox",
   'AND(BLANKVALUE(LT_Amount__c, 0) &gt; 0, BLANKVALUE(LT_Amount_Paid__c, 0) &gt;= LT_Amount__c)'))
wf(PR, "LT_Days_To_Due__c", formula("LT_Days_To_Due__c", "Dias ate o Vencimento",
   "Dias entre hoje e o vencimento (negativo quando vencido).", "Number",
   'IF(ISBLANK(LT_Due_Date__c), NULL, LT_Due_Date__c - TODAY())', precision=6, scale=0))
wf(PR, "LT_Is_Overdue__c", formula("LT_Is_Overdue__c", "Vencida",
   "Solicitacao em aberto com vencimento no passado.", "Checkbox",
   'AND(NOT(ISPICKVAL(LT_Status__c, "Paga")), NOT(ISPICKVAL(LT_Status__c, "Reprovada")), NOT(ISPICKVAL(LT_Status__c, "Cancelada")), NOT(ISBLANK(LT_Due_Date__c)), LT_Due_Date__c &lt; TODAY())'))
wf(PR, "LT_Status_Text__c", formula("LT_Status_Text__c", "Status (Texto)",
   "Valor textual do status, para uso em automacoes.", "Text", 'TEXT(LT_Status__c)'))

# validation rules
wv(PR, "LT_PR_Amount_Positive", "O valor solicitado deve ser maior que zero.",
   'BLANKVALUE(LT_Amount__c, 0) &lt;= 0', "Informe um valor solicitado maior que zero.", "LT_Amount__c")
wv(PR, "LT_PR_Due_Not_Before_Request", "O vencimento nao pode ser anterior a data da solicitacao.",
   'AND(NOT(ISBLANK(LT_Due_Date__c)), NOT(ISBLANK(LT_Request_Date__c)), LT_Due_Date__c &lt; LT_Request_Date__c)',
   "A data de vencimento nao pode ser anterior a data da solicitacao.", "LT_Due_Date__c")
wv(PR, "LT_PR_Justification_Required", "Solicitacoes exigem justificativa antes de sair do rascunho.",
   'AND(NOT(ISPICKVAL(LT_Status__c, "Rascunho")), ISBLANK(LT_Description__c))',
   "Preencha a justificativa antes de submeter a solicitacao.", "LT_Description__c")
wv(PR, "LT_PR_Approved_Requires_Date", "Solicitacao aprovada ou paga exige data de aprovacao.",
   'AND(OR(ISPICKVAL(LT_Status__c, "Aprovada"), ISPICKVAL(LT_Status__c, "Paga")), ISBLANK(LT_Approval_Date__c))',
   "Informe a data de aprovacao.", "LT_Approval_Date__c")
wv(PR, "LT_PR_Rejected_Requires_Reason", "Solicitacao reprovada exige o motivo da reprovacao.",
   'AND(ISPICKVAL(LT_Status__c, "Reprovada"), ISBLANK(LT_Rejection_Reason__c), NOT(ISCHANGED(LT_Status__c)))',
   "Informe o motivo da reprovacao.", "LT_Rejection_Reason__c")
wv(PR, "LT_PR_Driver_Type_Requires_Driver", "Pagamento a motorista exige o motorista e o romaneio.",
   'AND(ISPICKVAL(LT_Request_Type__c, "Pagamento a Motorista (Romaneio)"), OR(ISBLANK(LT_Driver__c), ISBLANK(LT_Manifest__c)))',
   "Informe o motorista e o romaneio para pagamentos a motorista.", "LT_Driver__c")
wv(PR, "LT_PR_Shipper_Type_Requires_Shipper", "Ressarcimento a embarcador exige o embarcador.",
   'AND(ISPICKVAL(LT_Request_Type__c, "Pagamento a Embarcador (Ressarcimento)"), ISBLANK(LT_Shipper__c))',
   "Informe o embarcador para pagamentos de ressarcimento.", "LT_Shipper__c")
wv(PR, "LT_PR_Paid_Not_Over_Requested", "O valor pago nao pode exceder o valor solicitado.",
   'AND(NOT(ISBLANK(LT_Amount_Paid__c)), NOT(ISBLANK(LT_Amount__c)), LT_Amount_Paid__c &gt; LT_Amount__c)',
   "O total pago ultrapassa o valor solicitado. Ajuste a solicitacao ou os pagamentos.", "LT_Amount__c")

open(os.path.join(PR, "compactLayouts", "LT_Payment_Request_Summary.compactLayout-meta.xml"), "w", encoding="utf-8", newline="\n").write(
   compact("LT_Payment_Request_Summary", "Solicitacao - Resumo",
           ["Name", "LT_Request_Type__c", "LT_Payee_Name__c", "LT_Amount__c", "LT_Status__c", "LT_Due_Date__c"]))
for n, l, cols, fil in [
  ("All", "Todas", ["NAME", "LT_Request_Type__c", "LT_Payee_Name__c", "LT_Amount__c", "LT_Status__c", "LT_Cost_Center__c", "LT_Due_Date__c"], None),
  ("Em_Aprovacao", "Aguardando Aprovacao", ["NAME", "LT_Request_Type__c", "LT_Payee_Name__c", "LT_Amount__c", "LT_Approval_Level__c", "LT_Priority__c", "LT_Due_Date__c"],
   [("LT_Status__c", "equals", "Em Aprovacao")]),
  ("A_Pagar", "Aprovadas a Pagar", ["NAME", "LT_Payee_Name__c", "LT_Amount__c", "LT_Amount_Paid__c", "LT_Balance__c", "LT_Due_Date__c"],
   [("LT_Status__c", "equals", "Aprovada")]),
  ("Vencidas", "Vencidas", ["NAME", "LT_Payee_Name__c", "LT_Amount__c", "LT_Status__c", "LT_Due_Date__c", "LT_Days_To_Due__c"],
   [("LT_Is_Overdue__c", "equals", "1")]),
]:
    open(os.path.join(PR, "listViews", f"{n}.listView-meta.xml"), "w", encoding="utf-8", newline="\n").write(listview(n, l, cols, fil))

wobj(PR, "LT_Payment_Request__c", "Solicitacao de Pagamento", "Solicitacoes de Pagamento",
     "Codigo da Solicitacao", "AutoNumber", "SOL-{000000}", compact="LT_Payment_Request_Summary")

# ==================== LT_Payment__c (MD child of LT_Payment_Request__c) ====================
PAY_STATUS = ["Agendado", "Processando", "Confirmado", "Falhou", "Estornado"]
BANK_ACCOUNT = ["Conta Corrente - Itau", "Conta Corrente - Bradesco", "Conta Pagamentos - Nubank PJ", "Caixa / Fundo Fixo"]

open(os.path.join(PAY, "fields", "LT_Payment_Request__c.field-meta.xml"), "w", encoding="utf-8", newline="\n").write(
   mdfield("LT_Payment_Request__c", "Solicitacao de Pagamento", "Solicitacao que autoriza este pagamento.",
           "LT_Payment_Request__c", "Pagamentos", "LT_Payments").strip() + "\n")
wf(PAY, "LT_Amount__c", field("LT_Amount__c", "Valor Pago", "Valor efetivamente pago nesta transacao.", "Currency",
   required=True, precision=14, scale=2))
wf(PAY, "LT_Payment_Date__c", field("LT_Payment_Date__c", "Data do Pagamento", "Data em que o pagamento foi efetuado.",
   "Date", required=True))
wf(PAY, "LT_Status__c", picklist("LT_Status__c", "Status", "Situacao da transacao de pagamento.", PAY_STATUS, default="Agendado"))
wf(PAY, "LT_Payment_Method__c", picklist("LT_Payment_Method__c", "Forma de Pagamento", "Meio usado nesta transacao.",
   PAY_METHOD, default="PIX", track=False))
wf(PAY, "LT_Bank_Account__c", picklist("LT_Bank_Account__c", "Conta de Origem", "Conta bancaria de onde saiu o recurso.",
   BANK_ACCOUNT, track=False))
wf(PAY, "LT_Transaction_Id__c", field("LT_Transaction_Id__c", "ID da Transacao", "Identificador do comprovante bancario.",
   "Text", length=60, track=False))
wf(PAY, "LT_Paid_By__c", lookup("LT_Paid_By__c", "Pago Por", "Usuario que executou o pagamento.",
   "User", "Pagamentos Executados", "LT_Executed_Payments", lf_optional=True, track=False))
wf(PAY, "LT_Fee_Amount__c", field("LT_Fee_Amount__c", "Tarifa Bancaria", "Tarifa cobrada pelo banco na transacao.",
   "Currency", precision=10, scale=2, track=False))
wf(PAY, "LT_Reconciled__c", field("LT_Reconciled__c", "Conciliado", "Pagamento conferido contra o extrato bancario.",
   "Checkbox", default="false"))
wf(PAY, "LT_Reconciliation_Date__c", field("LT_Reconciliation_Date__c", "Data da Conciliacao", "Data da conciliacao bancaria.",
   "Date", track=False))
wf(PAY, "LT_Notes__c", field("LT_Notes__c", "Observacoes", "Observacoes sobre o pagamento.", "LongTextArea",
   length=4000, lines=3, track=False))
wf(PAY, "LT_Total_Disbursed__c", formula("LT_Total_Disbursed__c", "Total Desembolsado",
   "Valor pago somado a tarifa bancaria.", "Currency",
   'BLANKVALUE(LT_Amount__c, 0) + BLANKVALUE(LT_Fee_Amount__c, 0)', precision=16, scale=2))

wv(PAY, "LT_PAY_Amount_Positive", "O valor pago deve ser maior que zero.",
   'BLANKVALUE(LT_Amount__c, 0) &lt;= 0', "Informe um valor pago maior que zero.", "LT_Amount__c")
wv(PAY, "LT_PAY_Confirmed_Requires_Txn", "Pagamento confirmado exige o ID da transacao.",
   'AND(ISPICKVAL(LT_Status__c, "Confirmado"), ISBLANK(LT_Transaction_Id__c))',
   "Informe o ID da transacao ao confirmar o pagamento.", "LT_Transaction_Id__c")
wv(PAY, "LT_PAY_Reconciled_Requires_Date", "Pagamento conciliado exige a data da conciliacao.",
   'AND(LT_Reconciled__c, ISBLANK(LT_Reconciliation_Date__c))',
   "Informe a data da conciliacao.", "LT_Reconciliation_Date__c")
wv(PAY, "LT_PAY_Reversed_Not_Reconciled", "Pagamento estornado nao pode estar conciliado.",
   'AND(ISPICKVAL(LT_Status__c, "Estornado"), LT_Reconciled__c)',
   "Um pagamento estornado nao pode ficar marcado como conciliado.", "LT_Reconciled__c")

open(os.path.join(PAY, "compactLayouts", "LT_Payment_Summary.compactLayout-meta.xml"), "w", encoding="utf-8", newline="\n").write(
   compact("LT_Payment_Summary", "Pagamento - Resumo",
           ["Name", "LT_Payment_Request__c", "LT_Amount__c", "LT_Status__c", "LT_Payment_Date__c", "LT_Payment_Method__c"]))
for n, l, cols, fil in [
  ("All", "Todos", ["NAME", "LT_Payment_Request__c", "LT_Amount__c", "LT_Status__c", "LT_Payment_Method__c", "LT_Payment_Date__c"], None),
  ("A_Conciliar", "A Conciliar", ["NAME", "LT_Amount__c", "LT_Bank_Account__c", "LT_Payment_Date__c", "LT_Transaction_Id__c"],
   [("LT_Status__c", "equals", "Confirmado"), ("LT_Reconciled__c", "equals", "0")]),
]:
    open(os.path.join(PAY, "listViews", f"{n}.listView-meta.xml"), "w", encoding="utf-8", newline="\n").write(
        listview(n, l, cols, fil))

wobj(PAY, "LT_Payment__c", "Pagamento", "Pagamentos", "Codigo do Pagamento", "AutoNumber", "PAG-{000000}",
     compact="LT_Payment_Summary", mdchild=True)

# ==================== LT_Expense__c ====================
EXP_CATEGORY = ["Combustivel", "Manutencao de Veiculos", "Aluguel de Base/Galpao",
                "Energia / Agua / Internet", "Material de Embalagem", "Equipamentos / EPI",
                "Folha / Encargos", "Frete / Transferencia (SC/MR)", "Ressarcimento a Embarcador",
                "Penalizacao / Multa", "Viagem / Diaria", "Servicos de Terceiros", "Outras Despesas"]
EXP_STATUS = ["Prevista", "Realizada", "Paga", "Cancelada"]

wf(EXP, "LT_Expense_Category__c", picklist("LT_Expense_Category__c", "Categoria da Despesa",
   "Natureza contabil da despesa.", EXP_CATEGORY, track=False))
wf(EXP, "LT_Status__c", picklist("LT_Status__c", "Status", "Situacao da despesa no periodo.", EXP_STATUS, default="Prevista"))
wf(EXP, "LT_Cost_Center__c", picklist("LT_Cost_Center__c", "Centro de Custo", "Area a que a despesa e alocada.",
   COST_CENTER, track=False))
wf(EXP, "LT_Amount__c", field("LT_Amount__c", "Valor", "Valor da despesa.", "Currency", required=True, precision=14, scale=2))
wf(EXP, "LT_Expense_Date__c", field("LT_Expense_Date__c", "Data da Despesa", "Data de realizacao da despesa.", "Date", required=True))
wf(EXP, "LT_Competency_Month__c", field("LT_Competency_Month__c", "Mes de Competencia",
   "Mes contabil no formato AAAA-MM.", "Text", length=7, required=True, track=False,
   help="Use o formato AAAA-MM, por exemplo 2026-08."))
wf(EXP, "LT_Base__c", lookup("LT_Base__c", "Base / Unidade", "Base ou unidade que incorreu na despesa.",
   "LT_Logistics_Unit__c", "Despesas", "LT_Expenses", lf_optional=True, track=False))
wf(EXP, "LT_Payment_Request__c", lookup("LT_Payment_Request__c", "Solicitacao de Pagamento",
   "Solicitacao de pagamento que cobre esta despesa.", "LT_Payment_Request__c", "Despesas", "LT_Expenses",
   lf_optional=True, track=False))
wf(EXP, "LT_Supplier__c", field("LT_Supplier__c", "Fornecedor", "Fornecedor ou prestador da despesa.", "Text",
   length=120, track=False))
wf(EXP, "LT_Invoice_Number__c", field("LT_Invoice_Number__c", "Nota Fiscal", "Numero da nota fiscal.", "Text",
   length=40, track=False))
wf(EXP, "LT_Recurring__c", field("LT_Recurring__c", "Recorrente", "Despesa que se repete todo mes.", "Checkbox",
   default="false", track=False))
wf(EXP, "LT_Pass_Through__c", field("LT_Pass_Through__c", "Repasse a Motorista",
   "Despesa que e apenas repasse de valores a motoristas (frete de ultima milha).", "Checkbox",
   default="false", track=False))
wf(EXP, "LT_Description__c", field("LT_Description__c", "Descricao", "Detalhamento da despesa.", "LongTextArea",
   length=8000, lines=3, track=False))
wf(EXP, "LT_Is_Paid__c", formula("LT_Is_Paid__c", "Paga",
   "Verdadeiro quando a despesa ja foi paga.", "Checkbox", 'ISPICKVAL(LT_Status__c, "Paga")'))

wv(EXP, "LT_EXP_Amount_Positive", "O valor da despesa deve ser maior que zero.",
   'BLANKVALUE(LT_Amount__c, 0) &lt;= 0', "Informe um valor de despesa maior que zero.", "LT_Amount__c")
wv(EXP, "LT_EXP_Competency_Format", "O mes de competencia deve estar no formato AAAA-MM.",
   'NOT(REGEX(LT_Competency_Month__c, "[0-9]{4}-(0[1-9]|1[0-2])"))',
   "Use o formato AAAA-MM no mes de competencia (ex.: 2026-08).", "LT_Competency_Month__c")
wv(EXP, "LT_EXP_Paid_Requires_Support", "Despesa paga exige nota fiscal ou solicitacao de pagamento.",
   'AND(ISPICKVAL(LT_Status__c, "Paga"), ISBLANK(LT_Invoice_Number__c), ISBLANK(LT_Payment_Request__c))',
   "Vincule uma nota fiscal ou uma solicitacao de pagamento para marcar a despesa como paga.", "LT_Status__c")

open(os.path.join(EXP, "compactLayouts", "LT_Expense_Summary.compactLayout-meta.xml"), "w", encoding="utf-8", newline="\n").write(
   compact("LT_Expense_Summary", "Despesa - Resumo",
           ["Name", "LT_Expense_Category__c", "LT_Amount__c", "LT_Status__c", "LT_Competency_Month__c", "LT_Cost_Center__c"]))
for n, l, cols, fil in [
  ("All", "Todas", ["NAME", "LT_Expense_Category__c", "LT_Amount__c", "LT_Status__c", "LT_Cost_Center__c", "LT_Competency_Month__c", "LT_Expense_Date__c"], None),
  ("Previstas", "Previstas", ["NAME", "LT_Expense_Category__c", "LT_Amount__c", "LT_Cost_Center__c", "LT_Expense_Date__c"],
   [("LT_Status__c", "equals", "Prevista")]),
  ("Por_Base", "Com Base Definida", ["NAME", "LT_Base__c", "LT_Expense_Category__c", "LT_Amount__c", "LT_Status__c", "LT_Competency_Month__c"],
   [("LT_Base__c", "notEqual", "")]),
]:
    open(os.path.join(EXP, "listViews", f"{n}.listView-meta.xml"), "w", encoding="utf-8", newline="\n").write(listview(n, l, cols, fil))

wobj(EXP, "LT_Expense__c", "Despesa", "Despesas", "Codigo da Despesa", "AutoNumber", "DES-{000000}",
     compact="LT_Expense_Summary")

# ==================== layouts ====================
simple_layout(os.path.join(ROOT, "layouts", "LT_Payment_Request__c-Solicitacao de Pagamento Layout.layout-meta.xml"), [
  ("Solicitacao", "TwoColumnsLeftToRight", [
    [("Readonly", "Name"), ("Edit", "LT_Request_Type__c"), ("Edit", "LT_Status__c"), ("Edit", "LT_Priority__c"), ("Edit", "LT_Cost_Center__c")],
    [("Required", "LT_Amount__c"), ("Required", "LT_Request_Date__c"), ("Required", "LT_Due_Date__c"), ("Readonly", "LT_Approval_Level__c"), ("Edit", "LT_Recurring__c")]]),
  ("Favorecido", "TwoColumnsLeftToRight", [
    [("Required", "LT_Payee_Name__c"), ("Edit", "LT_Payee_Document__c"), ("Edit", "LT_Payment_Method__c")],
    [("Edit", "LT_Payee_Pix_Key__c"), ("Edit", "LT_Bank_Details__c"), ("Edit", "LT_Invoice_Number__c")]]),
  ("Vinculos", "TwoColumnsLeftToRight", [
    [("Edit", "LT_Shipper__c"), ("Edit", "LT_Driver__c"), ("Edit", "LT_Manifest__c")],
    [("Edit", "LT_Base__c"), ("Edit", "LT_Loss_Claim__c"), ("Edit", "LT_Requested_By__c")]]),
  ("Aprovacao e Pagamento", "TwoColumnsLeftToRight", [
    [("Readonly", "LT_Approved_By__c"), ("Readonly", "LT_Approval_Date__c"), ("Readonly", "LT_Amount_Paid__c"), ("Readonly", "LT_Balance__c")],
    [("Readonly", "LT_Payment_Count__c"), ("Readonly", "LT_Last_Payment_Date__c"), ("Readonly", "LT_Fully_Paid__c"), ("Readonly", "LT_Is_Overdue__c"), ("Readonly", "LT_Days_To_Due__c")]]),
  ("Justificativa", "OneColumn", [[("Edit", "LT_Description__c"), ("Edit", "LT_Rejection_Reason__c")]]),
], related=["LT_Payment__c.LT_Payment_Request__c", "LT_Expense__c.LT_Payment_Request__c", "RelatedHistoryList"])

simple_layout(os.path.join(ROOT, "layouts", "LT_Payment__c-Pagamento Layout.layout-meta.xml"), [
  ("Pagamento", "TwoColumnsLeftToRight", [
    [("Readonly", "Name"), ("Required", "LT_Payment_Request__c"), ("Required", "LT_Amount__c"), ("Required", "LT_Payment_Date__c"), ("Edit", "LT_Status__c")],
    [("Edit", "LT_Payment_Method__c"), ("Edit", "LT_Bank_Account__c"), ("Edit", "LT_Fee_Amount__c"), ("Readonly", "LT_Total_Disbursed__c"), ("Edit", "LT_Paid_By__c")]]),
  ("Comprovacao e Conciliacao", "TwoColumnsLeftToRight", [
    [("Edit", "LT_Transaction_Id__c"), ("Edit", "LT_Reconciled__c")],
    [("Edit", "LT_Reconciliation_Date__c"), ("Edit", "LT_Notes__c")]]),
])

simple_layout(os.path.join(ROOT, "layouts", "LT_Expense__c-Despesa Layout.layout-meta.xml"), [
  ("Despesa", "TwoColumnsLeftToRight", [
    [("Readonly", "Name"), ("Edit", "LT_Expense_Category__c"), ("Edit", "LT_Status__c"), ("Edit", "LT_Cost_Center__c")],
    [("Required", "LT_Amount__c"), ("Required", "LT_Expense_Date__c"), ("Required", "LT_Competency_Month__c"), ("Edit", "LT_Recurring__c"), ("Edit", "LT_Pass_Through__c")]]),
  ("Origem", "TwoColumnsLeftToRight", [
    [("Edit", "LT_Base__c"), ("Edit", "LT_Payment_Request__c")],
    [("Edit", "LT_Supplier__c"), ("Edit", "LT_Invoice_Number__c"), ("Readonly", "LT_Is_Paid__c")]]),
  ("Descricao", "OneColumn", [[("Edit", "LT_Description__c")]]),
])

# ==================== tabs ====================
for t, motif in [("LT_Payment_Request__c", "Custom19: Bank"), ("LT_Payment__c", "Custom22: Currency"),
                 ("LT_Expense__c", "Custom25: Coins")]:
    open(os.path.join(ROOT, "tabs", f"{t}.tab-meta.xml"), "w", encoding="utf-8", newline="\n").write(
f"""<?xml version="1.0" encoding="UTF-8"?>
<CustomTab xmlns="http://soap.sforce.com/2006/04/metadata">
    <customObject>true</customObject>
    <motif>{motif}</motif>
</CustomTab>
""")

# ==================== app ====================
open(os.path.join(ROOT, "applications", "LogiTrack_Financeiro.app-meta.xml"), "w", encoding="utf-8", newline="\n").write(
"""<?xml version="1.0" encoding="UTF-8"?>
<CustomApplication xmlns="http://soap.sforce.com/2006/04/metadata">
    <brand>
        <headerColor>#1B5E20</headerColor>
        <shouldOverrideOrgTheme>false</shouldOverrideOrgTheme>
    </brand>
    <description>Aplicativo Financeiro da LogiTrack: solicitacoes de pagamento, aprovacoes por alcada, pagamentos e despesas por centro de custo.</description>
    <formFactors>Large</formFactors>
    <formFactors>Small</formFactors>
    <isNavAutoTempTabsDisabled>false</isNavAutoTempTabsDisabled>
    <isNavPersonalizationDisabled>false</isNavPersonalizationDisabled>
    <isNavTabPersistenceDisabled>false</isNavTabPersistenceDisabled>
    <label>LogiTrack Financeiro</label>
    <navType>Standard</navType>
    <tabs>standard-home</tabs>
    <tabs>LT_Payment_Request__c</tabs>
    <tabs>LT_Payment__c</tabs>
    <tabs>LT_Expense__c</tabs>
    <tabs>LT_Manifest__c</tabs>
    <tabs>LT_Loss_Claim__c</tabs>
    <tabs>standard-report</tabs>
    <tabs>standard-Dashboard</tabs>
    <uiType>Lightning</uiType>
</CustomApplication>
""")

# add finance tabs to Operations 360
p = os.path.join(ROOT, "applications", "LogiTrack_Operations_360.app-meta.xml")
t = open(p, encoding="utf-8").read()
if "<tabs>LT_Payment_Request__c</tabs>" not in t:
    t = t.replace("    <tabs>LT_Driver_Penalty__c</tabs>\n",
                  "    <tabs>LT_Driver_Penalty__c</tabs>\n    <tabs>LT_Payment_Request__c</tabs>\n    <tabs>LT_Expense__c</tabs>\n", 1)
    open(p, "w", encoding="utf-8", newline="\n").write(t)

print("Finance metadata generated.")
print("PR fields:", len(os.listdir(os.path.join(PR, "fields"))))
print("PAY fields:", len(os.listdir(os.path.join(PAY, "fields"))))
print("EXP fields:", len(os.listdir(os.path.join(EXP, "fields"))))

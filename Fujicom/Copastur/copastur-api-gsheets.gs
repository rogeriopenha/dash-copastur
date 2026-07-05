function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('Copastur API')
    .addItem('1. Configurar Sheet1 (painel)', 'SETUP_SHEET1')
    .addSeparator()
    .addItem('2. Listar Empresas', 'LIST_COMPANIES')
    .addItem('3. Listar Centros de Custo', 'LIST_COST_CENTERS')
    .addItem('4. Listar Pedidos', 'LIST_ORDERS')
    .addItem('5. Consultar Pedido', 'GET_ORDER')
    .addItem('6. Pedidos Completos (GetOrderV2)', 'GET_FULL_ORDER')
    .addItem('7. Listar Aprovações', 'LIST_APPROVALS')
    .addItem('8. Fluxo de Aprovação', 'LIST_APPROVAL_FLOWS')
    .addItem('9. Listar Orçamentos', 'LIST_BUDGETS')
    .addItem('10. Listar Cartões', 'LIST_CARDS')
    .addItem('11. Listar Usuários', 'LIST_USERS')
    .addItem('12. Consultar Usuário', 'GET_USER')
    .addItem('13. Cadastrar Usuário', 'CREATE_USER')
    .addItem('14. Excluir Usuário', 'DELETE_USER')
    .addItem('15. Aprovar Pedido', 'ACCEPT_ORDER')
    .addItem('16. Reprovar Pedido', 'DECLINE_ORDER')
    .addItem('17. Pagar OS', 'PAY_ORDER')
    .addItem('18. Comentar OS', 'FOLLOWUP_ORDER')
    .addItem('19. Listar Comentários OS', 'LIST_ORDER_FOLLOWUPS')
    .addItem('20. Consultar Usuário (Matrícula)', 'GET_USER_BY_REGISTRATION')
    .addItem('21. Health Check', 'HEALTH_CHECK')
    .addItem('22. Listar Pedidos Completos (Período)', 'LIST_FULL_ORDERS')
    .addSeparator()
    .addItem('Status da Conexão', 'STATUS_CONEXAO')
    .addItem('Forçar reautenticação', 'FORCE_REAUTH')
    .addItem('Limpar abas geradas', 'CLEAR_SHEETS')
    .addToUi();
}

function SETUP_SHEET1() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName('Sheet1');
  if (!sheet) {
    sheet = ss.insertSheet('Sheet1');
  }
  sheet.clearContents();

  const azulEscuro = '#1a5276';
  const azulMedio = '#2e86c1';
  const azulClaro = '#d4e6f1';
  const azulFundo = '#eaf2f8';
  const branco = '#ffffff';

  sheet.getRange('A1').setValue('COPASTUR API - Painel de Controle')
    .setFontSize(16).setFontWeight('bold')
    .setBackground(azulEscuro).setFontColor(branco);
  sheet.getRange('A1:B1').merge();

  sheet.getRange('A3').setValue('CONFIGURAÇÕES DE ACESSO')
    .setFontWeight('bold').setFontSize(12)
    .setBackground(azulMedio).setFontColor(branco);
  sheet.getRange('A3:B3').merge();

  sheet.getRange('A4').setValue('Usuário').setBackground(azulFundo);
  sheet.getRange('B4').setValue('fujicom').setBackground(azulFundo);
  sheet.getRange('A5').setValue('Senha').setBackground(azulFundo);
  sheet.getRange('B5').setValue('S3lZohQedysA').setBackground(azulFundo);
  sheet.getRange('A6').setValue('URL Base').setBackground(azulFundo);
  sheet.getRange('B6').setValue('https://api.copastur.com.br/api-company').setBackground(azulFundo);

  sheet.getRange('A8').setValue('PARÂMETROS DAS REQUISIÇÕES')
    .setFontWeight('bold').setFontSize(12)
    .setBackground(azulMedio).setFontColor(branco);
  sheet.getRange('A8:B8').merge();

  const secoes = [
    [10, 'LISTAR EMPRESAS', 11, ['(sem parâmetros necessários)']],
    [13, 'LISTAR CENTROS DE CUSTO', 14, ['companyCode (Cód. Empresa)', 'active (true/false)']],
    [17, 'LISTAR PEDIDOS', 18, ['request_date_start (Data Início YYYY-MM-DD)', 'request_date_end (Data Fim YYYY-MM-DD)', 'request_status (Status Viagem)', 'expense_status (Status Despesa)', 'date_type (Tipo Data)', 'advancePaymentStatus (Status Adto.)']],
    [25, 'CONSULTAR PEDIDO', 26, ['osNumber (Nº do Pedido)']],
    [28, 'LISTAR APROVAÇÕES', 29, ['loginEmployee', 'costCenterCode', 'companyCode']],
    [33, 'FLUXO DE APROVAÇÃO', 34, ['loginApprover', 'startDate (YYYY-MM-DD)', 'endDate (YYYY-MM-DD)']],
    [38, 'LISTAR ORÇAMENTOS', 39, ['CompanyCode', 'CostCenterCode', 'Date (YYYY-MM-DD)']],
    [43, 'LISTAR CARTÕES', 44, ['initialDate (YYYY-MM-DD)', 'finalDate (YYYY-MM-DD)', 'flag (Bandeira)', 'login']],
    [49, 'LISTAR USUÁRIOS', 50, ['companyCode (Cód. Empresa)', 'costCenterCode (Cód. CC)', 'name (Nome)']],
    [54, 'CONSULTAR USUÁRIO', 55, ['login (Login)']],
    [57, 'CONSULTAR USUÁRIO (MATRÍCULA)', 58, ['registration (Matrícula)']],
    [60, 'EXCLUIR USUÁRIO', 61, ['login (Login)']],
    [63, 'APROVAR PEDIDO', 64, ['order (Nº Pedido)', 'loginApprover (Login Aprovador)']],
    [67, 'REPROVAR PEDIDO', 68, ['order (Nº Pedido)', 'loginApprover (Login Aprovador)', 'reason (Motivo)']],
    [72, 'PAGAR OS', 73, ['osNumber (Nº OS)', 'amount (Valor)']],
    [76, 'COMENTAR OS', 77, ['osNumber (Nº OS)', 'comments (Comentário)']],
    [79, 'LISTAR COMENTÁRIOS OS', 80, ['osNumber (Nº OS)']],
  ];

  secoes.forEach(([headerRow, titulo, paramStart, params]) => {
    sheet.getRange('A' + headerRow).setValue(titulo)
      .setFontWeight('bold').setBackground(azulClaro);
    sheet.getRange('B' + headerRow).setBackground(azulClaro);
    params.forEach((p, i) => {
      sheet.getRange('A' + (paramStart + i)).setValue(p).setBackground(azulFundo);
      sheet.getRange('B' + (paramStart + i)).setBackground(azulFundo);
    });
  });

  const fimSecoes = 82;
  const instrucaoRow = fimSecoes + 2;
  sheet.getRange('A' + instrucaoRow).setValue('INSTRUÇÕES')
    .setFontWeight('bold').setFontSize(12)
    .setBackground(azulMedio).setFontColor(branco);
  sheet.getRange('A' + instrucaoRow + ':B' + instrucaoRow).merge();

  const instrRow = instrucaoRow + 1;
  sheet.getRange('A' + instrRow).setValue(
    '1. Preencha as credenciais de acesso nas células B4:B6.\n' +
    '2. Preencha os parâmetros desejados ao lado de cada função.\n' +
    '3. Use o menu Extensões > Copastur API para executar cada ação.\n' +
    '4. Cada ação criará ou atualizará uma aba com os resultados.\n' +
    '5. Use "Forçar reautenticação" se o token expirar.\n' +
    '6. Use "Limpar abas geradas" para remover todas as abas criadas (exceto Sheet1).\n' +
    '7. Se nada acontecer ao executar uma ação, verifique o erro exibido e tente "Forçar reautenticação".'
  ).setFontSize(10).setBackground(azulFundo);
  sheet.getRange('A' + instrRow).setWrap(true);
  sheet.getRange('A' + instrRow + ':B' + instrRow).merge();

  sheet.getRange('A1').setFontColor(branco);
  sheet.getRange('A3').setFontColor(branco);
  sheet.getRange('A8').setFontColor(branco);

  sheet.setColumnWidth(1, 280);
  sheet.setColumnWidth(2, 400);

  SpreadsheetApp.getUi().alert(
    'Sheet1 configurada com tema azul!\n\n' +
    'Preencha os campos e use o menu Copastur API.'
  );
}

function getConfig_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('Sheet1');
  const padrao = {
    BASE_URL: 'https://api.copastur.com.br/api-company',
    USERNAME: 'fujicomhomolog@copastur.com.br',
    PASSWORD: '^Oe#w#bil4A$50A',
    TOKEN_KEY: 'COPASTUR_TOKEN',
    EXPIRY_KEY: 'COPASTUR_TOKEN_EXPIRY',
    AUTH_TIME_KEY: 'COPASTUR_AUTH_TIME'
  };
  if (!sheet) return padrao;
  return {
    BASE_URL: sheet.getRange('B6').getValue() || padrao.BASE_URL,
    USERNAME: sheet.getRange('B4').getValue() || padrao.USERNAME,
    PASSWORD: sheet.getRange('B5').getValue() || padrao.PASSWORD,
    TOKEN_KEY: padrao.TOKEN_KEY,
    EXPIRY_KEY: padrao.EXPIRY_KEY,
    AUTH_TIME_KEY: padrao.AUTH_TIME_KEY
  };
}

function getParam_(row) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('Sheet1');
  if (!sheet) return '';
  const val = sheet.getRange('B' + row).getValue();
  if (val === null || val === undefined) return '';
  if (val instanceof Date) {
    const d = val;
    const ano = d.getFullYear();
    const mes = String(d.getMonth() + 1).padStart(2, '0');
    const dia = String(d.getDate()).padStart(2, '0');
    return ano + '-' + mes + '-' + dia;
  }
  return String(val).trim();
}

function authenticate() {
  const cfg = getConfig_();
  const props = PropertiesService.getScriptProperties();
  const token = props.getProperty(cfg.TOKEN_KEY);
  const expiry = props.getProperty(cfg.EXPIRY_KEY);

  if (token && expiry && new Date() < new Date(expiry)) {
    return token;
  }

  const payload = {
    username: cfg.USERNAME,
    password: cfg.PASSWORD
  };

  const options = {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };

  const response = JSON.parse(
    UrlFetchApp.fetch(cfg.BASE_URL + '/v2/api/Authentication/Authenticate', options)
  );

  if (!response.success) {
    throw new Error('Falha na autenticação: ' + JSON.stringify(response.message));
  }

  const tokenData = response.data;
  props.setProperty(cfg.TOKEN_KEY, tokenData.access_token);
  props.setProperty(cfg.EXPIRY_KEY, tokenData.expirationToken);
  props.setProperty(cfg.AUTH_TIME_KEY, new Date().toISOString());

  return tokenData.access_token;
}

function conexaoStatus_() {
  const cfg = getConfig_();
  const props = PropertiesService.getScriptProperties();
  const token = props.getProperty(cfg.TOKEN_KEY);
  const expiry = props.getProperty(cfg.EXPIRY_KEY);
  const authTime = props.getProperty(cfg.AUTH_TIME_KEY);

  if (!token || !expiry) {
    return { conectado: false, mensagem: 'Nenhuma conexão ativa. Execute uma ação para autenticar.' };
  }

  const agora = new Date();
  const expira = new Date(expiry);
  const conectado = agora < expira;

  const fmt = d =>
    d.toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo', dateStyle: 'short', timeStyle: 'medium' });

  let mensagem = '';
  if (conectado) {
    mensagem = 'Conectado desde ' + fmt(new Date(authTime)) + '\nExpira às ' + fmt(expira);
  } else {
    mensagem = 'Token expirou em ' + fmt(expira) + '. Reautentique.';
  }

  return { conectado, mensagem };
}

function STATUS_CONEXAO() {
  const status = conexaoStatus_();
  SpreadsheetApp.getUi().alert('Status da Conexão', status.mensagem, SpreadsheetApp.getUi().ButtonSet.OK);
}

function apiGet(endpoint) {
  const cfg = getConfig_();
  const token = authenticate();
  const options = {
    method: 'get',
    headers: {
      Authorization: 'Bearer ' + token,
      accept: 'application/json'
    },
    muteHttpExceptions: true,
    timeout: 300000
  };

  const response = JSON.parse(
    UrlFetchApp.fetch(cfg.BASE_URL + endpoint, options)
  );

  if (!response.success) {
    throw new Error('Erro na consulta: ' + JSON.stringify(response.message));
  }

  return response;
}

function apiGetWithParams(endpoint, params) {
  const cfg = getConfig_();
  const token = authenticate();
  const qs = Object.entries(params)
    .filter(([_, v]) => v !== undefined && v !== null && v !== '')
    .map(([k, v]) => encodeURIComponent(k) + '=' + encodeURIComponent(v))
    .join('&');

  const url = cfg.BASE_URL + endpoint + (qs ? '?' + qs : '');
  const options = {
    method: 'get',
    headers: {
      Authorization: 'Bearer ' + token,
      accept: 'application/json'
    },
    muteHttpExceptions: true,
    timeout: 300000
  };

  const url = cfg.BASE_URL + endpoint + (qs ? '?' + qs : '');
  const response = JSON.parse(UrlFetchApp.fetch(url, options));
  if (!response.success) {
    throw new Error('Erro na consulta: ' + JSON.stringify(response.message));
  }
  return response;
}

function arrayToSheet_(data, sheetName) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(sheetName);
  if (!sheet) {
    sheet = ss.insertSheet(sheetName);
  }
  sheet.clearContents();

  if (!data || data.length === 0) {
    sheet.getRange(1, 1).setValue('Nenhum dado encontrado');
    return;
  }

  const headers = Object.keys(data[0]);
  const rows = data.map(obj => headers.map(h => {
    const val = obj[h];
    return val !== null && val !== undefined ? val : '';
  }));

  sheet.getRange(1, 1, 1, headers.length).setValues([headers]).setFontWeight('bold');
  if (rows.length > 0) {
    sheet.getRange(2, 1, rows.length, headers.length).setValues(rows);
  }
  sheet.autoResizeColumns(1, headers.length);
}

function formatOrders_(orders) {
  return orders.map(o => ({
    'Nº Pedido': o.osNumber || o.requestNumber || '',
    'ID Solicitação': o.requestId || '',
    'Status Viagem': o.tripStatus || '',
    'Status Despesa': o.expenseStatus || '',
    'Status Adiantamento': o.advancePaymentStatus || '',
    'Data Alteração': o.changeDate || ''
  }));
}

function formatOrderDetail_(order) {
  return [{
    'Nº Pedido': order.orderNumber || '',
    'Solicitante': order.requester || '',
    'Email Solicitante': order.requesterEmail || '',
    'Login Solicitante': order.requesterLogin || '',
    'Status Viagem': order.statusTravel || '',
    'Status Despesa': order.statusExpense || '',
    'Data Pedido': order.dateOrder || '',
    'Data Criação': order.dateCreated || '',
    'Viajante': order.traveler || '',
    'Motivo': order.reason || '',
    'Centro Custo': order.centerCostDescription || '',
    'Código CC': order.centerCostCode || '',
    'Empresa': order.companyName || '',
    'Código Empresa': order.companyCode || '',
    'Aprovador': order.approver || '',
    'Atendente': order.atending || '',
    'Agência': order.agency || '',
    'Total': order.total || '',
    'Observação': order.remarks || ''
  }];
}

function formatBudgetList_(budgets) {
  return budgets.map(b => ({
    'ID': b.id || '',
    'Código CC': b.costCenterCode || '',
    'Descrição CC': b.costCenterDescription || '',
    'Conta Contábil': b.ledgerAccountDescription || '',
    'Valor Orçado': b.budgetedValue || '',
    'Valor Gasto': b.spentValue || '',
    'Saldo': b.balanceValue || '',
    'Data': b.date || '',
    'Ativo': b.active || '',
    'Observação': b.observation || ''
  }));
}

function FORCE_REAUTH() {
  const props = PropertiesService.getScriptProperties();
  props.deleteProperty('COPASTUR_TOKEN');
  props.deleteProperty('COPASTUR_TOKEN_EXPIRY');
  props.deleteProperty('COPASTUR_AUTH_TIME');
  SpreadsheetApp.getUi().alert('Token removido. A próxima chamada renovará a autenticação.');
}

function LIST_COMPANIES() {
  try {
    const res = apiGet('/v2/api/Companies/ListCompanies');
    const data = res.data || [];
    arrayToSheet_(data, 'Empresas');
    const st = conexaoStatus_();
    SpreadsheetApp.getUi().alert(st.mensagem + '\n\nOK - ' + data.length + ' empresas encontradas.');
  } catch (e) {
    SpreadsheetApp.getUi().alert('ERRO ao listar empresas:\n' + e.message);
  }
}

function LIST_COST_CENTERS() {
  try {
    const params = {};
    const companyCode = getParam_(14);
    const active = getParam_(15);
    if (companyCode) params.companyCode = companyCode;
    if (active) params.active = active;
    const res = apiGetWithParams('/v2/api/CostCenters/ListCostCenters', params);
    const data = res.data || [];
    const formatted = data.map(c => ({
      'Código': c.code || '',
      'Descrição': c.description || '',
      'Empresa': c.company || '',
      'Ativo': c.active || ''
    }));
    arrayToSheet_(formatted, 'CentrosCusto');
    const st = conexaoStatus_();
    SpreadsheetApp.getUi().alert(st.mensagem + '\n\nOK - ' + data.length + ' centros de custo encontrados.');
  } catch (e) {
    SpreadsheetApp.getUi().alert('ERRO ao listar centros de custo:\n' + e.message);
  }
}

function LIST_ORDERS() {
  try {
    const params = {};
    const startDate = getParam_(18);
    const endDate = getParam_(19);
    const reqStatus = getParam_(20);
    const expStatus = getParam_(21);
    const dateType = getParam_(22);
    const advStatus = getParam_(23);
    if (startDate) params.request_date_start = startDate;
    if (endDate) params.request_date_end = endDate;
    if (reqStatus) params.request_status = reqStatus;
    if (expStatus) params.expense_status = expStatus;
    if (dateType) params.date_type = dateType;
    if (advStatus) params.advancePaymentStatus = advStatus;
    const res = apiGetWithParams('/v2/api/Order/List', params);
    const data = res.data || [];
    const formatted = formatOrders_(data);
    arrayToSheet_(formatted, 'Pedidos');
    const st = conexaoStatus_();
    SpreadsheetApp.getUi().alert(st.mensagem + '\n\nOK - ' + data.length + ' pedidos encontrados.');
  } catch (e) {
    SpreadsheetApp.getUi().alert('ERRO ao listar pedidos:\n' + e.message);
  }
}

function LIST_FULL_ORDERS() {
  try {
    const params = {};
    const startDate = getParam_(18);
    const endDate = getParam_(19);
    const reqStatus = getParam_(20);
    const expStatus = getParam_(21);
    const dateType = getParam_(22);
    const advStatus = getParam_(23);
    if (startDate) params.request_date_start = startDate;
    if (endDate) params.request_date_end = endDate;
    if (reqStatus) params.request_status = reqStatus;
    if (expStatus) params.expense_status = expStatus;
    if (dateType) params.date_type = dateType;
    if (advStatus) params.advancePaymentStatus = advStatus;
    const res = apiGetWithParams('/v2/api/Order/List', params);
    const orders = res.data || [];
    if (orders.length === 0) {
      SpreadsheetApp.getUi().alert('Nenhum pedido encontrado no período.');
      return;
    }
    var orderNumbers = [];
    for (var i = 0; i < orders.length; i++) {
      var num = orders[i].osNumber || orders[i].requestNumber || '';
      if (num) orderNumbers.push(num);
    }
    var ui = SpreadsheetApp.getUi();
    var confirm = ui.alert(
      'Listar Pedidos Completos',
      'Serão processados ' + orderNumbers.length + ' pedidos.\nIsso pode levar vários minutos.\nContinuar?',
      ui.ButtonSet.YES_NO
    );
    if (confirm !== ui.Button.YES) return;

    var allPedidos = [];
    var allAereos = [];
    var allHoteis = [];
    var allCarros = [];
    var allOutrosServicos = [];
    var allServicos = [];
    var allTransporte = [];
    var allReembolsos = [];
    var allAdiantamentos = [];
    var allViajantes = [];
    var allAprovadores = [];
    var allResumo = [];
    var allRateio = [];
    var allStatusDespesa = [];
    var allFollowUp = [];

    var errors = [];
    for (var j = 0; j < orderNumbers.length; j++) {
      try {
        var num = orderNumbers[j];
        var res2 = apiGet('/v2/api/Order/GetOrderV2?osNumber=' + encodeURIComponent(num));
        var d = res2.data;
        if (!d) continue;

        allPedidos.push({
          'Nº Pedido': d.orderNumber || '',
          'Nº Pedido Root': d.orderNumberRoot || '',
          'Solicitante': d.requester || '',
          'Email Solicitante': d.requesterEmail || '',
          'Login Solicitante': d.requesterLogin || '',
          'Status Viagem': d.statusTravel || '',
          'Status Despesa': d.statusExpense || '',
          'Data Pedido': d.dateOrder || '',
          'Data Criação': d.dateCreated || '',
          'Data Emissão': d.issuedDate || '',
          'Data Cotação': d.dateQuotation || '',
          'Data Escolha': d.dateChoice || '',
          'Data Aprov. Custo': d.dateApprovalCost || '',
          'Data Vencimento': d.dateExpiration || '',
          'Data Aprov. Reembolso': d.dateApprovedRefund || '',
          'Data Pgto Reembolso': d.datePaidRefund || '',
          'Data Pgto Adiantamento': d.datePaidAdvance || '',
          'Data Conferência Reembolso': d.conferenceRefundDate || '',
          'Data Cancelamento': d.dateCancel || '',
          'Viajante': d.traveler || '',
          'Motivo': d.reason || '',
          'Tipo Viagem': d.typeTravel || '',
          'Centro Custo': d.centerCostDescription || '',
          'Código CC': d.centerCostCode || '',
          'Empresa': d.companyName || '',
          'Código Empresa': d.companyCode || '',
          'Aprovador': d.approver || '',
          'Atendente': d.atending || '',
          'Email Atendente': d.atendingEmail || '',
          'Emitente': d.issuer || '',
          'Email Emitente': d.issuerEmail || '',
          'Agência': d.agency || '',
          'Nº Autorização': d.authorizationNumber || '',
          'Total': d.total || '',
          'Observação': d.remarks || '',
          'Self Ticket': d.selfTicket || '',
          'Self Book': d.selfBook || '',
          'URL Cliente': d.urlClient || '',
          'Reemissão': d.isReissue || '',
          'Fechamento Cartão': d.isCardExpenseClosing || '',
          'Data Início Viagem': d.dateStartTravel || '',
          'Data Fim Viagem': d.dateEndTravel || ''
        });

        if (d.airs && d.airs.length > 0) {
          for (var a = 0; a < d.airs.length; a++) {
            var air = d.airs[a];
            allAereos.push({
              'Nº Pedido': num,
              'Companhia': air.ciaName || '',
              'Nr Voo': air.flyNumber || '',
              'Origem': (air.cityDeparture || '') + ' (' + (air.iataDeparture || '') + ')',
              'Destino': (air.cityArrival || '') + ' (' + (air.iataArrival || '') + ')',
              'Partida': air.departureDate || '',
              'Chegada': air.arrivalDate || '',
              'Tarifa': air.fare || '',
              'Taxas': air.tax || '',
              'Total': air.totalFare || '',
              'Moeda': air.currency || '',
              'Localizador': air.pnr || '',
              'eTicket': air.eticket || '',
              'Classe': air.class || '',
              'Cabine': air.cabin || '',
              'Status': air.status || '',
              'Fornecedor': air.supplier || '',
              'Conexões': air.connections || '',
              'Paradas': air.stops || '',
              'Origem País': air.countryDeparture || '',
              'Destino País': air.countryArrival || '',
              'ID Cotação': air.quotationId || ''
            });
          }
        }

        if (d.hotels && d.hotels.length > 0) {
          for (var h = 0; h < d.hotels.length; h++) {
            var hot = d.hotels[h];
            allHoteis.push({
              'Nº Pedido': num,
              'Hotel': hot.name || '',
              'Cidade': hot.city || '',
              'Estado': hot.state || '',
              'Endereço': hot.address || '',
              'CheckIn': hot.checkinDate || '',
              'CheckOut': hot.checkoutDate || '',
              'Suplementar': hot.additionalFare || '',
              'Desconto': hot.discountFare || '',
              'Tarifa': hot.fare || '',
              'Taxas': hot.tax || '',
              'Total': hot.totalFare || '',
              'Moeda': hot.currency || '',
              'Tipo Quarto': hot.roomType || '',
              'Tipo Cama': hot.bedType || '',
              'Tipo Cobrança': hot.billingType || '',
              'Diárias': hot.amountDialy || '',
              'Fornecedor': hot.supplier || '',
              'Voucher': hot.voucher || '',
              'Data Cancelamento': hot.dateCancel || '',
              'Categoria': hot.category || '',
              'Nº Autorização': hot.authorizationNumber || '',
              'Online': hot.online || '',
              'Data Criação': hot.dateCreated || ''
            });
          }
        }

        if (d.cars && d.cars.length > 0) {
          for (var c = 0; c < d.cars.length; c++) {
            var car = d.cars[c];
            allCarros.push({
              'Nº Pedido': num,
              'Locadora': car.supplier || '',
              'Categoria': car.category || '',
              'Veículo': car.vehicle || '',
              'Cambio': car.gearbox || '',
              'Ar Condicionado': car.hasAirConditional || '',
              'Motorista': car.hasDriver || '',
              'GPS': car.hasGPS || '',
              'Retirada': car.localCheckin || '',
              'Devolução': car.localCheckout || '',
              'Data Retirada': car.checkinDate || '',
              'Data Devolução': car.checkoutDate || '',
              'Tarifa': car.fare || '',
              'Suplementar': car.additionalFare || '',
              'Desconto': car.discountFare || '',
              'Taxas': car.tax || '',
              'Total': car.totalFare || '',
              'Moeda': car.currency || '',
              'Diárias': car.dailyQuantity || '',
              'Voucher': car.voucher || '',
              'Data Cancelamento': car.cancelDate || '',
              'Nº Autorização': car.authorizationNumber || '',
              'Data Criação': car.dateCreated || ''
            });
          }
        }

        if (d.miscellaneous && d.miscellaneous.length > 0) {
          for (var m = 0; m < d.miscellaneous.length; m++) {
            var mis = d.miscellaneous[m];
            allOutrosServicos.push({
              'Nº Pedido': num,
              'Origem': mis.departure || '',
              'Destino': mis.arrival || '',
              'Data Partida': mis.departureDate || '',
              'Data Chegada': mis.arrivalDate || '',
              'Fornecedor': mis.supplier || '',
              'Total': mis.totalFare || ''
            });
          }
        }

        if (d.services && d.services.length > 0) {
          for (var s = 0; s < d.services.length; s++) {
            var svc = d.services[s];
            allServicos.push({
              'Nº Pedido': num,
              'Descrição': svc.description || '',
              'Tipo Serviço': svc.typeService || '',
              'Fornecedor': svc.supplier || '',
              'Data Início': svc.startDate || '',
              'Data Fim': svc.endDate || '',
              'Data Vencimento': svc.expirationDate || '',
              'Quantidade': svc.quantity || '',
              'Tarifa': svc.fare || '',
              'Taxas': svc.tax || '',
              'Total': svc.totalFare || '',
              'Voucher': svc.voucher || '',
              'Data Voucher': svc.dateVoucher || '',
              'Observação': svc.remarks || '',
              'ID Cotação': svc.quotationId || '',
              'Nº Autorização': svc.authorizationNumber || '',
              'Data Cancelamento': svc.dateCanceled || '',
              'Data Emissão': svc.issuedDate || '',
              'Data Criação': svc.dateCreated || ''
            });
          }
        }

        if (d.transport && d.transport.length > 0) {
          for (var t = 0; t < d.transport.length; t++) {
            var trp = d.transport[t];
            allTransporte.push({
              'Nº Pedido': num,
              'Cia': trp.cia || '',
              'Assento': trp.seat || '',
              'Origem': trp.departure || '',
              'Terminal Origem': trp.terminalDeparture || '',
              'Destino': trp.arrival || '',
              'Terminal Destino': trp.terminalArrival || '',
              'Data Partida': trp.dateDeparture || '',
              'Data Chegada': trp.dateArrival || '',
              'Tipo Serviço': trp.serviceType || '',
              'Tarifa': trp.fare || '',
              'Suplementar': trp.additionalFare || '',
              'Desconto': trp.discountFare || '',
              'Total': trp.totalFare || '',
              'Voucher': trp.voucher || '',
              'Data Voucher': trp.dateVoucher || '',
              'Observação': trp.remarks || '',
              'ID Cotação': trp.quotationId || '',
              'Data Inclusão': trp.dateIncluded || '',
              'Data Atualização': trp.dateUpdated || '',
              'Data Vencimento': trp.dateExpired || '',
              'Data Cancelamento': trp.dateCanceled || ''
            });
          }
        }

        if (d.refunds && d.refunds.length > 0) {
          for (var r = 0; r < d.refunds.length; r++) {
            var ref = d.refunds[r];
            allReembolsos.push({
              'Nº Pedido': num,
              'Despesa': ref.expense || '',
              'Descrição': ref.descriptiveExpense || '',
              'Categoria': ref.category || '',
              'Conta': ref.account || '',
              'Moeda': ref.currency || '',
              'Código Moeda': ref.currencyCode || '',
              'Cotação': ref.exchange || '',
              'Quantidade': ref.quantity || '',
              'Preço': ref.price || '',
              'Valor': ref.amount || '',
              'Valor Total': ref.totalAmount || '',
              'Valor Taxa': ref.taxAmount || '',
              '% Taxa': ref.taxPercent || '',
              'Valor Ref.': ref.referAmount || '',
              'Moeda Ref.': ref.referCurrency || '',
              'Cotação Ref.': ref.referExchange || '',
              'Histórico': ref.history || '',
              'Centro Custo': ref.costCenterDescription || '',
              'Código CC': ref.costCenterCode || '',
              'Conta Bancária': ref.bankAccount || '',
              'Comprovante': ref.proofPayment || '',
              'URL Nota': ref.invoicheImagemURL || '',
              'Observação': ref.observation || '',
              'Tipo Pagamento': ref.typePaymentName || '',
              'Data Criação': ref.dateCreated || '',
              'Data Pagamento': ref.datePaid || '',
              'Data Início': ref.dateStart || '',
              'Data Fim': ref.dateEnd || '',
              'Data Modificação': ref.dateModified || '',
              'Ativo': ref.isActive || '',
              'Aprovado': ref.isApproved || '',
              'Reembolso': ref.isRefund || '',
              'Verificado': ref.isVerified || ''
            });
          }
        }

        if (d.advances && d.advances.length > 0) {
          for (var ad = 0; ad < d.advances.length; ad++) {
            var adv = d.advances[ad];
            allAdiantamentos.push({
              'Nº Pedido': num,
              'Despesa': adv.expense || '',
              'Moeda': adv.currency || '',
              'Código Moeda': adv.currencyCode || '',
              'Cotação': adv.exchange || '',
              'Moeda Original': adv.coin || '',
              'Código Bacen': adv.bacenCode || '',
              'Quantidade': adv.quantity || '',
              'Preço': adv.price || '',
              'Valor Total': adv.totalAmount || '',
              'Tipo Pagamento': adv.typePaymentName || '',
              'Motivo Viagem': adv.reasonTravelling || '',
              'Cidade Origem': adv.cityOrigin || '',
              'Cidade Partida': adv.departureCity || '',
              'Cidade Destino': adv.arrivalCity || '',
              'País Partida': adv.departureCountry || '',
              'País Destino': adv.arrivalCountry || '',
              'Comentários': adv.comments || '',
              'Data Criação': adv.dateCreated || '',
              'Data Pagamento': adv.datePaid || '',
              'Data Início': adv.dateStart || '',
              'Data Fim': adv.dateEnd || '',
              'Data Modificação': adv.dateModified || ''
            });
          }
        }

        if (d.travelers && d.travelers.length > 0) {
          for (var v = 0; v < d.travelers.length; v++) {
            var tvl = d.travelers[v];
            allViajantes.push({
              'Nº Pedido': num,
              'Nome': tvl.fullName || '',
              'Login': tvl.login || '',
              'Email': tvl.email || '',
              'Matrícula': tvl.registration || '',
              'Telefone': tvl.phone || '',
              'Celular': tvl.celularPhone || '',
              'Cargo': tvl.position || '',
              'VIP': tvl.vip || '',
              'Estado': tvl.state || ''
            });
          }
        }

        if (d.approvers && d.approvers.length > 0) {
          for (var ap = 0; ap < d.approvers.length; ap++) {
            var apr = d.approvers[ap];
            allAprovadores.push({
              'Nº Pedido': num,
              'Nome': apr.fullName || '',
              'Login': apr.login || '',
              'Email': apr.email || '',
              'Matrícula': apr.registration || '',
              'Data Aprovação': apr.approvalDate || ''
            });
          }
        }

        if (d.summary && d.summary.length > 0) {
          for (var sm = 0; sm < d.summary.length; sm++) {
            var sum = d.summary[sm];
            allResumo.push({
              'Nº Pedido': num,
              'Tipo': sum.Tipo || '',
              'Moeda': sum.currency || '',
              'Valor Maior': sum.ValorMaior || '',
              'Valor Menor': sum.ValorMenor || '',
              'Valor Médio': sum.ValorMedio || '',
              'Valor Total': sum.ValorTotal || '',
              'Quantidade': sum.Quantidade || '',
              'Bilhete': sum.Bilhete || '',
              'Localizador': sum.Localizador || '',
              'Voucher': sum.voucher || '',
              'Selecionado': sum.Selecionado || '',
              'ID Cotação': sum.CotacaoId || ''
            });
          }
        }

        if (d.apportionment && d.apportionment.length > 0) {
          for (var ar = 0; ar < d.apportionment.length; ar++) {
            var app = d.apportionment[ar];
            allRateio.push({
              'Nº Pedido': num,
              'Empresa': app.company || '',
              'Código Empresa': app.companyCode || '',
              '%': app.percent || '',
              'Conta Contábil Cód.': app.contaContabilCod || '',
              'Conta Contábil Desc.': app.contaContabilDesc || '',
              'Projeto Cód.': app.projectCod || '',
              'Projeto Desc.': app.projectDesc || '',
              'Observação': app.observation || ''
            });
          }
        }

        if (d.expenseStatus && d.expenseStatus.length > 0) {
          for (var es = 0; es < d.expenseStatus.length; es++) {
            var st = d.expenseStatus[es];
            allStatusDespesa.push({
              'Nº Pedido': num,
              'Status': st.status_name || '',
              'Código': st.status_code || '',
              'Data': st.status_date || ''
            });
          }
        }

        if (d.followUP && d.followUP.length > 0) {
          for (var fu = 0; fu < d.followUP.length; fu++) {
            var fup = d.followUP[fu];
            allFollowUp.push({
              'Nº Pedido': num,
              'Mensagem': fup.message || '',
              'Enviado Por': fup.sentBy || '',
              'Destinatários': fup.recipients || '',
              'Data Inclusão': fup.inclusionDate || ''
            });
          }
        }
      } catch (e) {
        errors.push(num + ': ' + e.message);
      }
    }

    var sheetName = 'Pedidos_' + startDate + '_' + endDate;
    arrayToSheet_(allPedidos, sheetName);
    if (allAereos.length > 0) arrayToSheet_(allAereos, 'Aereos_' + startDate + '_' + endDate);
    if (allHoteis.length > 0) arrayToSheet_(allHoteis, 'Hoteis_' + startDate + '_' + endDate);
    if (allCarros.length > 0) arrayToSheet_(allCarros, 'Carros_' + startDate + '_' + endDate);
    if (allOutrosServicos.length > 0) arrayToSheet_(allOutrosServicos, 'OutrosServicos_' + startDate + '_' + endDate);
    if (allServicos.length > 0) arrayToSheet_(allServicos, 'Servicos_' + startDate + '_' + endDate);
    if (allTransporte.length > 0) arrayToSheet_(allTransporte, 'Transporte_' + startDate + '_' + endDate);
    if (allReembolsos.length > 0) arrayToSheet_(allReembolsos, 'Reembolsos_' + startDate + '_' + endDate);
    if (allAdiantamentos.length > 0) arrayToSheet_(allAdiantamentos, 'Adiantamentos_' + startDate + '_' + endDate);
    if (allViajantes.length > 0) arrayToSheet_(allViajantes, 'Viajantes_' + startDate + '_' + endDate);
    if (allAprovadores.length > 0) arrayToSheet_(allAprovadores, 'Aprovadores_' + startDate + '_' + endDate);
    if (allResumo.length > 0) arrayToSheet_(allResumo, 'ResumoCotacoes_' + startDate + '_' + endDate);
    if (allRateio.length > 0) arrayToSheet_(allRateio, 'Rateio_' + startDate + '_' + endDate);
    if (allStatusDespesa.length > 0) arrayToSheet_(allStatusDespesa, 'StatusDespesa_' + startDate + '_' + endDate);
    if (allFollowUp.length > 0) arrayToSheet_(allFollowUp, 'FollowUp_' + startDate + '_' + endDate);

    var msg = 'OK - ' + orderNumbers.length + ' pedidos processados.\nAbas criadas:\n';
    msg += '- Pedidos_' + startDate + '_' + endDate + ' (' + allPedidos.length + ' linhas)\n';
    msg += allAereos.length > 0 ? '- Aereos (' + allAereos.length + ' linhas)\n' : '';
    msg += allHoteis.length > 0 ? '- Hoteis (' + allHoteis.length + ' linhas)\n' : '';
    msg += allCarros.length > 0 ? '- Carros (' + allCarros.length + ' linhas)\n' : '';
    msg += allOutrosServicos.length > 0 ? '- OutrosServicos (' + allOutrosServicos.length + ' linhas)\n' : '';
    msg += allServicos.length > 0 ? '- Servicos (' + allServicos.length + ' linhas)\n' : '';
    msg += allTransporte.length > 0 ? '- Transporte (' + allTransporte.length + ' linhas)\n' : '';
    msg += allReembolsos.length > 0 ? '- Reembolsos (' + allReembolsos.length + ' linhas)\n' : '';
    msg += allAdiantamentos.length > 0 ? '- Adiantamentos (' + allAdiantamentos.length + ' linhas)\n' : '';
    msg += allViajantes.length > 0 ? '- Viajantes (' + allViajantes.length + ' linhas)\n' : '';
    msg += allAprovadores.length > 0 ? '- Aprovadores (' + allAprovadores.length + ' linhas)\n' : '';
    msg += allResumo.length > 0 ? '- ResumoCotacoes (' + allResumo.length + ' linhas)\n' : '';
    msg += allRateio.length > 0 ? '- Rateio (' + allRateio.length + ' linhas)\n' : '';
    msg += allStatusDespesa.length > 0 ? '- StatusDespesa (' + allStatusDespesa.length + ' linhas)\n' : '';
    msg += allFollowUp.length > 0 ? '- FollowUp (' + allFollowUp.length + ' linhas)\n' : '';
    if (errors.length > 0) {
      msg += '\nErros:\n' + errors.join('\n');
    }
    SpreadsheetApp.getUi().alert(msg);
  } catch (e) {
    SpreadsheetApp.getUi().alert('ERRO ao listar pedidos completos:\n' + e.message);
  }
}

function GET_ORDER() {
  try {
    const orderNumber = getParam_(26);
    if (!orderNumber) {
      SpreadsheetApp.getUi().alert('Informe o Nº do Pedido na célula B26.');
      return;
    }
    const res = apiGet('/v2/api/Order/GetOrderV2?osNumber=' + encodeURIComponent(orderNumber));
    const data = res.data;
    if (!data) {
      SpreadsheetApp.getUi().alert('Pedido não encontrado.');
      return;
    }
    const formatted = formatOrderDetail_(data);
    arrayToSheet_(formatted, 'Pedido_' + orderNumber);
    const st = conexaoStatus_();
    SpreadsheetApp.getUi().alert(st.mensagem + '\n\nOK - Pedido ' + orderNumber + ' carregado.');
  } catch (e) {
    SpreadsheetApp.getUi().alert('ERRO ao consultar pedido:\n' + e.message);
  }
}

function GET_FULL_ORDER() {
  try {
    const orderNumber = getParam_(26);
    if (!orderNumber) {
      SpreadsheetApp.getUi().alert('Informe o Nº do Pedido na célula B26.');
      return;
    }
    const res = apiGet('/v2/api/Order/GetOrderV2?osNumber=' + encodeURIComponent(orderNumber));
    const data = res.data;
    if (!data) {
      SpreadsheetApp.getUi().alert('Pedido não encontrado.');
      return;
    }
    var sheets = [];
    var cabecalho = [{
      'Nº Pedido': data.orderNumber || '',
      'Nº Pedido Root': data.orderNumberRoot || '',
      'Solicitante': data.requester || '',
      'Email Solicitante': data.requesterEmail || '',
      'Login Solicitante': data.requesterLogin || '',
      'Status Viagem': data.statusTravel || '',
      'Status Despesa': data.statusExpense || '',
      'Data Pedido': data.dateOrder || '',
      'Data Criação': data.dateCreated || '',
      'Data Emissão': data.issuedDate || '',
      'Data Cotação': data.dateQuotation || '',
      'Data Escolha': data.dateChoice || '',
      'Data Aprov. Custo': data.dateApprovalCost || '',
      'Data Vencimento': data.dateExpiration || '',
      'Data Aprov. Reembolso': data.dateApprovedRefund || '',
      'Data Pgto Reembolso': data.datePaidRefund || '',
      'Data Pgto Adiantamento': data.datePaidAdvance || '',
      'Data Conferência Reembolso': data.conferenceRefundDate || '',
      'Data Cancelamento': data.dateCancel || '',
      'Viajante': data.traveler || '',
      'Motivo': data.reason || '',
      'Tipo Viagem': data.typeTravel || '',
      'Centro Custo': data.centerCostDescription || '',
      'Código CC': data.centerCostCode || '',
      'Empresa': data.companyName || '',
      'Código Empresa': data.companyCode || '',
      'Aprovador': data.approver || '',
      'Atendente': data.atending || '',
      'Email Atendente': data.atendingEmail || '',
      'Emitente': data.issuer || '',
      'Email Emitente': data.issuerEmail || '',
      'Agência': data.agency || '',
      'Nº Autorização': data.authorizationNumber || '',
      'Total': data.total || '',
      'Observação': data.remarks || '',
      'Self Ticket': data.selfTicket || '',
      'Self Book': data.selfBook || '',
      'URL Cliente': data.urlClient || '',
      'Reemissão': data.isReissue || '',
      'Fechamento Cartão': data.isCardExpenseClosing || '',
      'Data Início Viagem': data.dateStartTravel || '',
      'Data Fim Viagem': data.dateEndTravel || ''
    }];
    arrayToSheet_(cabecalho, 'Pedido_' + orderNumber);
    sheets.push('Pedido_' + orderNumber);

    var sheetName;
    var mapFunc;

    // Aéreos
    if (data.airs && data.airs.length > 0) {
      sheetName = 'Aereos_' + orderNumber;
      mapFunc = function(a) { return {
        'Nº Pedido': orderNumber,
        'Companhia': a.ciaName || '',
        'Nr Voo': a.flyNumber || '',
        'Origem': (a.cityDeparture || '') + ' (' + (a.iataDeparture || '') + ')',
        'Destino': (a.cityArrival || '') + ' (' + (a.iataArrival || '') + ')',
        'Partida': a.departureDate || '',
        'Chegada': a.arrivalDate || '',
        'Tarifa': a.fare || '',
        'Taxas': a.tax || '',
        'Total': a.totalFare || '',
        'Moeda': a.currency || '',
        'Localizador': a.pnr || '',
        'eTicket': a.eticket || '',
        'Classe': a.class || '',
        'Cabine': a.cabin || '',
        'Status': a.status || '',
        'Fornecedor': a.supplier || '',
        'Conexões': a.connections || '',
        'Paradas': a.stops || '',
        'Origem País': a.countryDeparture || '',
        'Destino País': a.countryArrival || '',
        'ID Cotação': a.quotationId || ''
      }; };
      arrayToSheet_(data.airs.map(mapFunc), sheetName);
      sheets.push(sheetName);
    }

    // Hoteis
    if (data.hotels && data.hotels.length > 0) {
      sheetName = 'Hoteis_' + orderNumber;
      mapFunc = function(h) { return {
        'Nº Pedido': orderNumber,
        'Hotel': h.name || '',
        'Cidade': h.city || '',
        'Estado': h.state || '',
        'Endereço': h.address || '',
        'CheckIn': h.checkinDate || '',
        'CheckOut': h.checkoutDate || '',
        'Suplementar': h.additionalFare || '',
        'Desconto': h.discountFare || '',
        'Tarifa': h.fare || '',
        'Taxas': h.tax || '',
        'Total': h.totalFare || '',
        'Moeda': h.currency || '',
        'Tipo Quarto': h.roomType || '',
        'Tipo Cama': h.bedType || '',
        'Tipo Cobrança': h.billingType || '',
        'Diárias': h.amountDialy || '',
        'Fornecedor': h.supplier || '',
        'Voucher': h.voucher || '',
        'Data Cancelamento': h.dateCancel || '',
        'Categoria': h.category || '',
        'Nº Autorização': h.authorizationNumber || '',
        'Online': h.online || '',
        'Data Criação': h.dateCreated || ''
      }; };
      arrayToSheet_(data.hotels.map(mapFunc), sheetName);
      sheets.push(sheetName);
    }

    // Carros
    if (data.cars && data.cars.length > 0) {
      sheetName = 'Carros_' + orderNumber;
      mapFunc = function(c) { return {
        'Nº Pedido': orderNumber,
        'Locadora': c.supplier || '',
        'Categoria': c.category || '',
        'Veículo': c.vehicle || '',
        'Cambio': c.gearbox || '',
        'Ar Condicionado': c.hasAirConditional || '',
        'Motorista': c.hasDriver || '',
        'GPS': c.hasGPS || '',
        'Retirada': c.localCheckin || '',
        'Devolução': c.localCheckout || '',
        'Data Retirada': c.checkinDate || '',
        'Data Devolução': c.checkoutDate || '',
        'Tarifa': c.fare || '',
        'Suplementar': c.additionalFare || '',
        'Desconto': c.discountFare || '',
        'Taxas': c.tax || '',
        'Total': c.totalFare || '',
        'Moeda': c.currency || '',
        'Diárias': c.dailyQuantity || '',
        'Voucher': c.voucher || '',
        'Data Cancelamento': c.cancelDate || '',
        'Nº Autorização': c.authorizationNumber || '',
        'Data Criação': c.dateCreated || ''
      }; };
      arrayToSheet_(data.cars.map(mapFunc), sheetName);
      sheets.push(sheetName);
    }

    // Outros Serviços (Miscellaneous)
    if (data.miscellaneous && data.miscellaneous.length > 0) {
      sheetName = 'OutrosServicos_' + orderNumber;
      mapFunc = function(m) { return {
        'Nº Pedido': orderNumber,
        'Origem': m.departure || '',
        'Destino': m.arrival || '',
        'Data Partida': m.departureDate || '',
        'Data Chegada': m.arrivalDate || '',
        'Fornecedor': m.supplier || '',
        'Total': m.totalFare || ''
      }; };
      arrayToSheet_(data.miscellaneous.map(mapFunc), sheetName);
      sheets.push(sheetName);
    }

    // Serviços
    if (data.services && data.services.length > 0) {
      sheetName = 'Servicos_' + orderNumber;
      mapFunc = function(s) { return {
        'Nº Pedido': orderNumber,
        'Descrição': s.description || '',
        'Tipo Serviço': s.typeService || '',
        'Fornecedor': s.supplier || '',
        'Data Início': s.startDate || '',
        'Data Fim': s.endDate || '',
        'Data Vencimento': s.expirationDate || '',
        'Quantidade': s.quantity || '',
        'Tarifa': s.fare || '',
        'Taxas': s.tax || '',
        'Total': s.totalFare || '',
        'Voucher': s.voucher || '',
        'Data Voucher': s.dateVoucher || '',
        'Observação': s.remarks || '',
        'ID Cotação': s.quotationId || '',
        'Nº Autorização': s.authorizationNumber || '',
        'Data Cancelamento': s.dateCanceled || '',
        'Data Emissão': s.issuedDate || '',
        'Data Criação': s.dateCreated || ''
      }; };
      arrayToSheet_(data.services.map(mapFunc), sheetName);
      sheets.push(sheetName);
    }

    // Transporte
    if (data.transport && data.transport.length > 0) {
      sheetName = 'Transporte_' + orderNumber;
      mapFunc = function(t) { return {
        'Nº Pedido': orderNumber,
        'Cia': t.cia || '',
        'Assento': t.seat || '',
        'Origem': t.departure || '',
        'Terminal Origem': t.terminalDeparture || '',
        'Destino': t.arrival || '',
        'Terminal Destino': t.terminalArrival || '',
        'Data Partida': t.dateDeparture || '',
        'Data Chegada': t.dateArrival || '',
        'Tipo Serviço': t.serviceType || '',
        'Tarifa': t.fare || '',
        'Suplementar': t.additionalFare || '',
        'Desconto': t.discountFare || '',
        'Total': t.totalFare || '',
        'Voucher': t.voucher || '',
        'Data Voucher': t.dateVoucher || '',
        'Observação': t.remarks || '',
        'ID Cotação': t.quotationId || '',
        'Data Inclusão': t.dateIncluded || '',
        'Data Atualização': t.dateUpdated || '',
        'Data Vencimento': t.dateExpired || '',
        'Data Cancelamento': t.dateCanceled || ''
      }; };
      arrayToSheet_(data.transport.map(mapFunc), sheetName);
      sheets.push(sheetName);
    }

    // Reembolsos (refunds)
    if (data.refunds && data.refunds.length > 0) {
      sheetName = 'Reembolsos_' + orderNumber;
      mapFunc = function(r) { return {
        'Nº Pedido': orderNumber,
        'Despesa': r.expense || '',
        'Descrição': r.descriptiveExpense || '',
        'Categoria': r.category || '',
        'Conta': r.account || '',
        'Moeda': r.currency || '',
        'Código Moeda': r.currencyCode || '',
        'Cotação': r.exchange || '',
        'Quantidade': r.quantity || '',
        'Preço': r.price || '',
        'Valor': r.amount || '',
        'Valor Total': r.totalAmount || '',
        'Valor Taxa': r.taxAmount || '',
        '% Taxa': r.taxPercent || '',
        'Valor Ref.': r.referAmount || '',
        'Moeda Ref.': r.referCurrency || '',
        'Cotação Ref.': r.referExchange || '',
        'Histórico': r.history || '',
        'Centro Custo': r.costCenterDescription || '',
        'Código CC': r.costCenterCode || '',
        'Conta Bancária': r.bankAccount || '',
        'Comprovante': r.proofPayment || '',
        'URL Nota': r.invoicheImagemURL || '',
        'Observação': r.observation || '',
        'Tipo Pagamento': r.typePaymentName || '',
        'Data Criação': r.dateCreated || '',
        'Data Pagamento': r.datePaid || '',
        'Data Início': r.dateStart || '',
        'Data Fim': r.dateEnd || '',
        'Data Modificação': r.dateModified || '',
        'Ativo': r.isActive || '',
        'Aprovado': r.isApproved || '',
        'Reembolso': r.isRefund || '',
        'Verificado': r.isVerified || ''
      }; };
      arrayToSheet_(data.refunds.map(mapFunc), sheetName);
      sheets.push(sheetName);
    }

    // Adiantamentos
    if (data.advances && data.advances.length > 0) {
      sheetName = 'Adiantamentos_' + orderNumber;
      mapFunc = function(a) { return {
        'Nº Pedido': orderNumber,
        'Despesa': a.expense || '',
        'Moeda': a.currency || '',
        'Código Moeda': a.currencyCode || '',
        'Cotação': a.exchange || '',
        'Moeda Original': a.coin || '',
        'Código Bacen': a.bacenCode || '',
        'Quantidade': a.quantity || '',
        'Preço': a.price || '',
        'Valor Total': a.totalAmount || '',
        'Tipo Pagamento': a.typePaymentName || '',
        'Motivo Viagem': a.reasonTravelling || '',
        'Cidade Origem': a.cityOrigin || '',
        'Cidade Partida': a.departureCity || '',
        'Cidade Destino': a.arrivalCity || '',
        'País Partida': a.departureCountry || '',
        'País Destino': a.arrivalCountry || '',
        'Comentários': a.comments || '',
        'Data Criação': a.dateCreated || '',
        'Data Pagamento': a.datePaid || '',
        'Data Início': a.dateStart || '',
        'Data Fim': a.dateEnd || '',
        'Data Modificação': a.dateModified || ''
      }; };
      arrayToSheet_(data.advances.map(mapFunc), sheetName);
      sheets.push(sheetName);
    }

    // Viajantes
    if (data.travelers && data.travelers.length > 0) {
      sheetName = 'Viajantes_' + orderNumber;
      mapFunc = function(v) { return {
        'Nº Pedido': orderNumber,
        'Nome': v.fullName || '',
        'Login': v.login || '',
        'Email': v.email || '',
        'Matrícula': v.registration || '',
        'Telefone': v.phone || '',
        'Celular': v.celularPhone || '',
        'Cargo': v.position || '',
        'VIP': v.vip || '',
        'Estado': v.state || ''
      }; };
      arrayToSheet_(data.travelers.map(mapFunc), sheetName);
      sheets.push(sheetName);
    }

    // Aprovadores
    if (data.approvers && data.approvers.length > 0) {
      sheetName = 'Aprovadores_' + orderNumber;
      mapFunc = function(ap) { return {
        'Nº Pedido': orderNumber,
        'Nome': ap.fullName || '',
        'Login': ap.login || '',
        'Email': ap.email || '',
        'Matrícula': ap.registration || '',
        'Data Aprovação': ap.approvalDate || ''
      }; };
      arrayToSheet_(data.approvers.map(mapFunc), sheetName);
      sheets.push(sheetName);
    }

    // Resumo Cotações
    if (data.summary && data.summary.length > 0) {
      sheetName = 'ResumoCotacoes_' + orderNumber;
      mapFunc = function(sm) { return {
        'Nº Pedido': orderNumber,
        'Tipo': sm.Tipo || '',
        'Moeda': sm.currency || '',
        'Valor Maior': sm.ValorMaior || '',
        'Valor Menor': sm.ValorMenor || '',
        'Valor Médio': sm.ValorMedio || '',
        'Valor Total': sm.ValorTotal || '',
        'Quantidade': sm.Quantidade || '',
        'Bilhete': sm.Bilhete || '',
        'Localizador': sm.Localizador || '',
        'Voucher': sm.voucher || '',
        'Selecionado': sm.Selecionado || '',
        'ID Cotação': sm.CotacaoId || ''
      }; };
      arrayToSheet_(data.summary.map(mapFunc), sheetName);
      sheets.push(sheetName);
    }

    // Rateio (apportionment)
    if (data.apportionment && data.apportionment.length > 0) {
      sheetName = 'Rateio_' + orderNumber;
      mapFunc = function(ap) { return {
        'Nº Pedido': orderNumber,
        'Empresa': ap.company || '',
        'Código Empresa': ap.companyCode || '',
        '%': ap.percent || '',
        'Conta Contábil Cód.': ap.contaContabilCod || '',
        'Conta Contábil Desc.': ap.contaContabilDesc || '',
        'Projeto Cód.': ap.projectCod || '',
        'Projeto Desc.': ap.projectDesc || '',
        'Observação': ap.observation || ''
      }; };
      arrayToSheet_(data.apportionment.map(mapFunc), sheetName);
      sheets.push(sheetName);
    }

    // Status Despesa
    if (data.expenseStatus && data.expenseStatus.length > 0) {
      sheetName = 'StatusDespesa_' + orderNumber;
      mapFunc = function(es) { return {
        'Nº Pedido': orderNumber,
        'Status': es.status_name || '',
        'Código': es.status_code || '',
        'Data': es.status_date || ''
      }; };
      arrayToSheet_(data.expenseStatus.map(mapFunc), sheetName);
      sheets.push(sheetName);
    }

    // Follow-up
    if (data.followUP && data.followUP.length > 0) {
      sheetName = 'FollowUp_' + orderNumber;
      mapFunc = function(fu) { return {
        'Nº Pedido': orderNumber,
        'Mensagem': fu.message || '',
        'Enviado Por': fu.sentBy || '',
        'Destinatários': fu.recipients || '',
        'Data Inclusão': fu.inclusionDate || ''
      }; };
      arrayToSheet_(data.followUP.map(mapFunc), sheetName);
      sheets.push(sheetName);
    }

    var st = conexaoStatus_();
    SpreadsheetApp.getUi().alert(st.mensagem + '\n\nOK - Pedido ' + orderNumber + ' carregado.\nAbas criadas: ' + sheets.join(', '));
  } catch (e) {
    SpreadsheetApp.getUi().alert('ERRO ao consultar pedido completo:\n' + e.message);
  }
}

function GET_FULL_ORDER_BY_NUMBER_(orderNumber) {
  const res = apiGet('/v2/api/Order/GetOrderV2?osNumber=' + encodeURIComponent(orderNumber));
  const data = res.data;
  if (!data) return;
  var cabecalho = [{
    'Nº Pedido': data.orderNumber || '',
    'Nº Pedido Root': data.orderNumberRoot || '',
    'Solicitante': data.requester || '',
    'Email Solicitante': data.requesterEmail || '',
    'Login Solicitante': data.requesterLogin || '',
    'Status Viagem': data.statusTravel || '',
    'Status Despesa': data.statusExpense || '',
    'Data Pedido': data.dateOrder || '',
    'Data Criação': data.dateCreated || '',
    'Data Emissão': data.issuedDate || '',
    'Data Cotação': data.dateQuotation || '',
    'Data Escolha': data.dateChoice || '',
    'Data Aprov. Custo': data.dateApprovalCost || '',
    'Data Vencimento': data.dateExpiration || '',
    'Data Aprov. Reembolso': data.dateApprovedRefund || '',
    'Data Pgto Reembolso': data.datePaidRefund || '',
    'Data Pgto Adiantamento': data.datePaidAdvance || '',
    'Data Conferência Reembolso': data.conferenceRefundDate || '',
    'Data Cancelamento': data.dateCancel || '',
    'Viajante': data.traveler || '',
    'Motivo': data.reason || '',
    'Tipo Viagem': data.typeTravel || '',
    'Centro Custo': data.centerCostDescription || '',
    'Código CC': data.centerCostCode || '',
    'Empresa': data.companyName || '',
    'Código Empresa': data.companyCode || '',
    'Aprovador': data.approver || '',
    'Atendente': data.atending || '',
    'Email Atendente': data.atendingEmail || '',
    'Emitente': data.issuer || '',
    'Email Emitente': data.issuerEmail || '',
    'Agência': data.agency || '',
    'Nº Autorização': data.authorizationNumber || '',
    'Total': data.total || '',
    'Observação': data.remarks || '',
    'Self Ticket': data.selfTicket || '',
    'Self Book': data.selfBook || '',
    'URL Cliente': data.urlClient || '',
    'Reemissão': data.isReissue || '',
    'Fechamento Cartão': data.isCardExpenseClosing || '',
    'Data Início Viagem': data.dateStartTravel || '',
    'Data Fim Viagem': data.dateEndTravel || ''
  }];
  arrayToSheet_(cabecalho, 'Pedido_' + orderNumber);
  var sheetName;
  var mapFunc;
  if (data.airs && data.airs.length > 0) {
    sheetName = 'Aereos_' + orderNumber;
    mapFunc = function(a) { return {
      'Nº Pedido': orderNumber,
      'Companhia': a.ciaName || '',
      'Nr Voo': a.flyNumber || '',
      'Origem': (a.cityDeparture || '') + ' (' + (a.iataDeparture || '') + ')',
      'Destino': (a.cityArrival || '') + ' (' + (a.iataArrival || '') + ')',
      'Partida': a.departureDate || '',
      'Chegada': a.arrivalDate || '',
      'Tarifa': a.fare || '',
      'Taxas': a.tax || '',
      'Total': a.totalFare || '',
      'Moeda': a.currency || '',
      'Localizador': a.pnr || '',
      'eTicket': a.eticket || '',
      'Classe': a.class || '',
      'Cabine': a.cabin || '',
      'Status': a.status || '',
      'Fornecedor': a.supplier || '',
      'Conexões': a.connections || '',
      'Paradas': a.stops || '',
      'Origem País': a.countryDeparture || '',
      'Destino País': a.countryArrival || '',
      'ID Cotação': a.quotationId || ''
    }; };
    arrayToSheet_(data.airs.map(mapFunc), sheetName);
  }
  if (data.hotels && data.hotels.length > 0) {
    sheetName = 'Hoteis_' + orderNumber;
    mapFunc = function(h) { return {
      'Nº Pedido': orderNumber,
      'Hotel': h.name || '',
      'Cidade': h.city || '',
      'Estado': h.state || '',
      'Endereço': h.address || '',
      'CheckIn': h.checkinDate || '',
      'CheckOut': h.checkoutDate || '',
      'Suplementar': h.additionalFare || '',
      'Desconto': h.discountFare || '',
      'Tarifa': h.fare || '',
      'Taxas': h.tax || '',
      'Total': h.totalFare || '',
      'Moeda': h.currency || '',
      'Tipo Quarto': h.roomType || '',
      'Tipo Cama': h.bedType || '',
      'Tipo Cobrança': h.billingType || '',
      'Diárias': h.amountDialy || '',
      'Fornecedor': h.supplier || '',
      'Voucher': h.voucher || '',
      'Data Cancelamento': h.dateCancel || '',
      'Categoria': h.category || '',
      'Nº Autorização': h.authorizationNumber || '',
      'Online': h.online || '',
      'Data Criação': h.dateCreated || ''
    }; };
    arrayToSheet_(data.hotels.map(mapFunc), sheetName);
  }
  if (data.cars && data.cars.length > 0) {
    sheetName = 'Carros_' + orderNumber;
    mapFunc = function(c) { return {
      'Nº Pedido': orderNumber,
      'Locadora': c.supplier || '',
      'Categoria': c.category || '',
      'Veículo': c.vehicle || '',
      'Cambio': c.gearbox || '',
      'Ar Condicionado': c.hasAirConditional || '',
      'Motorista': c.hasDriver || '',
      'GPS': c.hasGPS || '',
      'Retirada': c.localCheckin || '',
      'Devolução': c.localCheckout || '',
      'Data Retirada': c.checkinDate || '',
      'Data Devolução': c.checkoutDate || '',
      'Tarifa': c.fare || '',
      'Suplementar': c.additionalFare || '',
      'Desconto': c.discountFare || '',
      'Taxas': c.tax || '',
      'Total': c.totalFare || '',
      'Moeda': c.currency || '',
      'Diárias': c.dailyQuantity || '',
      'Voucher': c.voucher || '',
      'Data Cancelamento': c.cancelDate || '',
      'Nº Autorização': c.authorizationNumber || '',
      'Data Criação': c.dateCreated || ''
    }; };
    arrayToSheet_(data.cars.map(mapFunc), sheetName);
  }
  if (data.miscellaneous && data.miscellaneous.length > 0) {
    sheetName = 'OutrosServicos_' + orderNumber;
    mapFunc = function(m) { return {
      'Nº Pedido': orderNumber,
      'Origem': m.departure || '',
      'Destino': m.arrival || '',
      'Data Partida': m.departureDate || '',
      'Data Chegada': m.arrivalDate || '',
      'Fornecedor': m.supplier || '',
      'Total': m.totalFare || ''
    }; };
    arrayToSheet_(data.miscellaneous.map(mapFunc), sheetName);
  }
  if (data.services && data.services.length > 0) {
    sheetName = 'Servicos_' + orderNumber;
    mapFunc = function(s) { return {
      'Nº Pedido': orderNumber,
      'Descrição': s.description || '',
      'Tipo Serviço': s.typeService || '',
      'Fornecedor': s.supplier || '',
      'Data Início': s.startDate || '',
      'Data Fim': s.endDate || '',
      'Data Vencimento': s.expirationDate || '',
      'Quantidade': s.quantity || '',
      'Tarifa': s.fare || '',
      'Taxas': s.tax || '',
      'Total': s.totalFare || '',
      'Voucher': s.voucher || '',
      'Data Voucher': s.dateVoucher || '',
      'Observação': s.remarks || '',
      'ID Cotação': s.quotationId || '',
      'Nº Autorização': s.authorizationNumber || '',
      'Data Cancelamento': s.dateCanceled || '',
      'Data Emissão': s.issuedDate || '',
      'Data Criação': s.dateCreated || ''
    }; };
    arrayToSheet_(data.services.map(mapFunc), sheetName);
  }
  if (data.transport && data.transport.length > 0) {
    sheetName = 'Transporte_' + orderNumber;
    mapFunc = function(t) { return {
      'Nº Pedido': orderNumber,
      'Cia': t.cia || '',
      'Assento': t.seat || '',
      'Origem': t.departure || '',
      'Terminal Origem': t.terminalDeparture || '',
      'Destino': t.arrival || '',
      'Terminal Destino': t.terminalArrival || '',
      'Data Partida': t.dateDeparture || '',
      'Data Chegada': t.dateArrival || '',
      'Tipo Serviço': t.serviceType || '',
      'Tarifa': t.fare || '',
      'Suplementar': t.additionalFare || '',
      'Desconto': t.discountFare || '',
      'Total': t.totalFare || '',
      'Voucher': t.voucher || '',
      'Data Voucher': t.dateVoucher || '',
      'Observação': t.remarks || '',
      'ID Cotação': t.quotationId || '',
      'Data Inclusão': t.dateIncluded || '',
      'Data Atualização': t.dateUpdated || '',
      'Data Vencimento': t.dateExpired || '',
      'Data Cancelamento': t.dateCanceled || ''
    }; };
    arrayToSheet_(data.transport.map(mapFunc), sheetName);
  }
  if (data.refunds && data.refunds.length > 0) {
    sheetName = 'Reembolsos_' + orderNumber;
    mapFunc = function(r) { return {
      'Nº Pedido': orderNumber,
      'Despesa': r.expense || '',
      'Descrição': r.descriptiveExpense || '',
      'Categoria': r.category || '',
      'Conta': r.account || '',
      'Moeda': r.currency || '',
      'Código Moeda': r.currencyCode || '',
      'Cotação': r.exchange || '',
      'Quantidade': r.quantity || '',
      'Preço': r.price || '',
      'Valor': r.amount || '',
      'Valor Total': r.totalAmount || '',
      'Valor Taxa': r.taxAmount || '',
      '% Taxa': r.taxPercent || '',
      'Valor Ref.': r.referAmount || '',
      'Moeda Ref.': r.referCurrency || '',
      'Cotação Ref.': r.referExchange || '',
      'Histórico': r.history || '',
      'Centro Custo': r.costCenterDescription || '',
      'Código CC': r.costCenterCode || '',
      'Conta Bancária': r.bankAccount || '',
      'Comprovante': r.proofPayment || '',
      'URL Nota': r.invoicheImagemURL || '',
      'Observação': r.observation || '',
      'Tipo Pagamento': r.typePaymentName || '',
      'Data Criação': r.dateCreated || '',
      'Data Pagamento': r.datePaid || '',
      'Data Início': r.dateStart || '',
      'Data Fim': r.dateEnd || '',
      'Data Modificação': r.dateModified || '',
      'Ativo': r.isActive || '',
      'Aprovado': r.isApproved || '',
      'Reembolso': r.isRefund || '',
      'Verificado': r.isVerified || ''
    }; };
    arrayToSheet_(data.refunds.map(mapFunc), sheetName);
  }
  if (data.advances && data.advances.length > 0) {
    sheetName = 'Adiantamentos_' + orderNumber;
    mapFunc = function(a) { return {
      'Nº Pedido': orderNumber,
      'Despesa': a.expense || '',
      'Moeda': a.currency || '',
      'Código Moeda': a.currencyCode || '',
      'Cotação': a.exchange || '',
      'Moeda Original': a.coin || '',
      'Código Bacen': a.bacenCode || '',
      'Quantidade': a.quantity || '',
      'Preço': a.price || '',
      'Valor Total': a.totalAmount || '',
      'Tipo Pagamento': a.typePaymentName || '',
      'Motivo Viagem': a.reasonTravelling || '',
      'Cidade Origem': a.cityOrigin || '',
      'Cidade Partida': a.departureCity || '',
      'Cidade Destino': a.arrivalCity || '',
      'País Partida': a.departureCountry || '',
      'País Destino': a.arrivalCountry || '',
      'Comentários': a.comments || '',
      'Data Criação': a.dateCreated || '',
      'Data Pagamento': a.datePaid || '',
      'Data Início': a.dateStart || '',
      'Data Fim': a.dateEnd || '',
      'Data Modificação': a.dateModified || ''
    }; };
    arrayToSheet_(data.advances.map(mapFunc), sheetName);
  }
  if (data.travelers && data.travelers.length > 0) {
    sheetName = 'Viajantes_' + orderNumber;
    mapFunc = function(v) { return {
      'Nº Pedido': orderNumber,
      'Nome': v.fullName || '',
      'Login': v.login || '',
      'Email': v.email || '',
      'Matrícula': v.registration || '',
      'Telefone': v.phone || '',
      'Celular': v.celularPhone || '',
      'Cargo': v.position || '',
      'VIP': v.vip || '',
      'Estado': v.state || ''
    }; };
    arrayToSheet_(data.travelers.map(mapFunc), sheetName);
  }
  if (data.approvers && data.approvers.length > 0) {
    sheetName = 'Aprovadores_' + orderNumber;
    mapFunc = function(ap) { return {
      'Nº Pedido': orderNumber,
      'Nome': ap.fullName || '',
      'Login': ap.login || '',
      'Email': ap.email || '',
      'Matrícula': ap.registration || '',
      'Data Aprovação': ap.approvalDate || ''
    }; };
    arrayToSheet_(data.approvers.map(mapFunc), sheetName);
  }
  if (data.summary && data.summary.length > 0) {
    sheetName = 'ResumoCotacoes_' + orderNumber;
    mapFunc = function(sm) { return {
      'Nº Pedido': orderNumber,
      'Tipo': sm.Tipo || '',
      'Moeda': sm.currency || '',
      'Valor Maior': sm.ValorMaior || '',
      'Valor Menor': sm.ValorMenor || '',
      'Valor Médio': sm.ValorMedio || '',
      'Valor Total': sm.ValorTotal || '',
      'Quantidade': sm.Quantidade || '',
      'Bilhete': sm.Bilhete || '',
      'Localizador': sm.Localizador || '',
      'Voucher': sm.voucher || '',
      'Selecionado': sm.Selecionado || '',
      'ID Cotação': sm.CotacaoId || ''
    }; };
    arrayToSheet_(data.summary.map(mapFunc), sheetName);
  }
  if (data.apportionment && data.apportionment.length > 0) {
    sheetName = 'Rateio_' + orderNumber;
    mapFunc = function(ap) { return {
      'Nº Pedido': orderNumber,
      'Empresa': ap.company || '',
      'Código Empresa': ap.companyCode || '',
      '%': ap.percent || '',
      'Conta Contábil Cód.': ap.contaContabilCod || '',
      'Conta Contábil Desc.': ap.contaContabilDesc || '',
      'Projeto Cód.': ap.projectCod || '',
      'Projeto Desc.': ap.projectDesc || '',
      'Observação': ap.observation || ''
    }; };
    arrayToSheet_(data.apportionment.map(mapFunc), sheetName);
  }
  if (data.expenseStatus && data.expenseStatus.length > 0) {
    sheetName = 'StatusDespesa_' + orderNumber;
    mapFunc = function(es) { return {
      'Nº Pedido': orderNumber,
      'Status': es.status_name || '',
      'Código': es.status_code || '',
      'Data': es.status_date || ''
    }; };
    arrayToSheet_(data.expenseStatus.map(mapFunc), sheetName);
  }
  if (data.followUP && data.followUP.length > 0) {
    sheetName = 'FollowUp_' + orderNumber;
    mapFunc = function(fu) { return {
      'Nº Pedido': orderNumber,
      'Mensagem': fu.message || '',
      'Enviado Por': fu.sentBy || '',
      'Destinatários': fu.recipients || '',
      'Data Inclusão': fu.inclusionDate || ''
    }; };
    arrayToSheet_(data.followUP.map(mapFunc), sheetName);
  }
}

function LIST_APPROVALS() {
  try {
    const params = {};
    const loginEmployee = getParam_(29);
    const costCenterCode = getParam_(30);
    const companyCode = getParam_(31);
    if (loginEmployee) params.loginEmployee = loginEmployee;
    if (costCenterCode) params.costCenterCode = costCenterCode;
    if (companyCode) params.companyCode = companyCode;
    const res = apiGetWithParams('/v2/api/Approvals', params);
    const data = res.data || [];
    const formatted = data.map(a => ({
      'ID': a.id || '',
      'Login': a.employeeLogin || '',
      'Código CC': a.costCenterCode || '',
      'Nível': a.level || '',
      'Tipo': a.type || ''
    }));
    arrayToSheet_(formatted, 'Aprovacoes');
    const st = conexaoStatus_();
    SpreadsheetApp.getUi().alert(st.mensagem + '\n\nOK - ' + data.length + ' aprovações encontradas.');
  } catch (e) {
    SpreadsheetApp.getUi().alert('ERRO ao listar aprovações:\n' + e.message);
  }
}

function LIST_APPROVAL_FLOWS() {
  try {
    const params = {};
    const loginApprover = getParam_(34);
    const startDate = getParam_(35);
    const endDate = getParam_(36);
    if (loginApprover) params.loginApprover = loginApprover;
    if (startDate) params.startDate = startDate;
    if (endDate) params.endDate = endDate;
    const res = apiGetWithParams('/v2/api/ApprovalFlow/ListOrdersApproval', params);
    const data = res.data || [];
    const formatted = formatOrders_(data);
    arrayToSheet_(formatted, 'FluxoAprovacao');
    const st = conexaoStatus_();
    SpreadsheetApp.getUi().alert(st.mensagem + '\n\nOK - ' + data.length + ' pedidos pendentes de aprovação.');
  } catch (e) {
    SpreadsheetApp.getUi().alert('ERRO no fluxo de aprovação:\n' + e.message);
  }
}

function LIST_BUDGETS() {
  try {
    const params = {};
    const companyCode = getParam_(39);
    const costCenterCode = getParam_(40);
    const date = getParam_(41);
    if (companyCode) params.CompanyCode = companyCode;
    if (costCenterCode) params.CostCenterCode = costCenterCode;
    if (date) params.Date = date;
    const res = apiGetWithParams('/v2/api/Budget/List', params);
    const data = res.data || [];
    const formatted = formatBudgetList_(data);
    arrayToSheet_(formatted, 'Orcamentos');
    const st = conexaoStatus_();
    SpreadsheetApp.getUi().alert(st.mensagem + '\n\nOK - ' + data.length + ' orçamentos encontrados.');
  } catch (e) {
    SpreadsheetApp.getUi().alert('ERRO ao listar orçamentos:\n' + e.message);
  }
}

function LIST_CARDS() {
  try {
    const params = {};
    const initialDate = getParam_(44);
    const finalDate = getParam_(45);
    const flag = getParam_(46);
    const login = getParam_(47);
    if (initialDate) params.initialDate = initialDate;
    if (finalDate) params.finalDate = finalDate;
    if (flag) params.flag = flag;
    if (login) params.login = login;
    const res = apiGetWithParams('/v2/api/Card/List', params);
    const data = res.data || [];
    const formatted = data.map(c => ({
      'ID': c.id || '',
      'Número': c.cardNumber || '',
      'Bandeira': c.flag || '',
      'Titular': c.holderName || '',
      'Validade': c.expirationDate || '',
      'Ativo': c.active || '',
      'Limite': c.limit || ''
    }));
    arrayToSheet_(formatted, 'Cartoes');
    const st = conexaoStatus_();
    SpreadsheetApp.getUi().alert(st.mensagem + '\n\nOK - ' + data.length + ' cartões encontrados.');
  } catch (e) {
    SpreadsheetApp.getUi().alert('ERRO ao listar cartões:\n' + e.message);
  }
}

function apiPost(endpoint, body) {
  const cfg = getConfig_();
  const token = authenticate();
  const options = {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(body),
    headers: {
      Authorization: 'Bearer ' + token,
      accept: 'application/json'
    },
    muteHttpExceptions: true
  };

  const response = JSON.parse(UrlFetchApp.fetch(cfg.BASE_URL + endpoint, options));
  if (!response.success) {
    throw new Error('Erro na operação: ' + JSON.stringify(response.message));
  }
  return response;
}

function apiPostForm(endpoint, params) {
  const cfg = getConfig_();
  const token = authenticate();
  const qs = Object.entries(params)
    .filter(([_, v]) => v !== undefined && v !== null && v !== '')
    .map(([k, v]) => encodeURIComponent(k) + '=' + encodeURIComponent(v))
    .join('&');

  const url = cfg.BASE_URL + endpoint + (qs ? '?' + qs : '');
  const options = {
    method: 'post',
    headers: {
      Authorization: 'Bearer ' + token,
      accept: 'application/json'
    },
    muteHttpExceptions: true
  };

  const response = JSON.parse(UrlFetchApp.fetch(url, options));
  if (!response.success) {
    throw new Error('Erro na operação: ' + JSON.stringify(response.message));
  }
  return response;
}

function LIST_USERS() {
  try {
    const params = {};
    const companyCode = getParam_(50);
    const costCenterCode = getParam_(51);
    const name = getParam_(52);
    if (companyCode) params.companyCode = companyCode;
    if (costCenterCode) params.costCenterCode = costCenterCode;
    if (name) params.name = name;
    const res = apiGetWithParams('/v2/api/Users/ListUsers', params);
    const data = res.data || [];
    const formatted = data.map(u => ({
      'Login': u.login || '',
      'Nome': u.fullName || '',
      'Matrícula': u.registration || '',
      'Empresa': u.companyName || '',
      'Cód. Empresa': u.companyCode || '',
      'Cód. CC': u.costCenterCode || '',
      'Email': u.email || '',
      'Sexo': u.gender || '',
      'Telefone': u.phone || '',
      'Celular': u.cellPhone || '',
      'Cargo': u.office || '',
      'Departamento': u.department || '',
      'Data Nascimento': u.birthDate || '',
      'Data Admissão': u.admissionDate || '',
      'Ativo': u.active || ''
    }));
    arrayToSheet_(formatted, 'Usuarios');
    const st = conexaoStatus_();
    SpreadsheetApp.getUi().alert(st.mensagem + '\n\nOK - ' + data.length + ' usuários encontrados.');
  } catch (e) {
    SpreadsheetApp.getUi().alert('ERRO ao listar usuários:\n' + e.message);
  }
}

function GET_USER() {
  try {
    const login = getParam_(55);
    if (!login) {
      SpreadsheetApp.getUi().alert('Informe o Login na célula B55.');
      return;
    }
    const res = apiGetWithParams('/v2/api/Users', { login: login });
    const data = res.data;
    if (!data) {
      SpreadsheetApp.getUi().alert('Usuário não encontrado.');
      return;
    }
    const formatted = [{
      'Login': data.login || '',
      'Nome': data.fullName || '',
      'Matrícula': data.registration || '',
      'Empresa': data.companyName || '',
      'Cód. Empresa': data.companyCode || '',
      'Cód. CC': data.costCenterCode || '',
      'Email': data.email || '',
      'Sexo': data.gender || '',
      'Telefone': data.phone || '',
      'Celular': data.cellPhone || '',
      'Cargo': data.office || '',
      'Departamento': data.department || '',
      'Data Nascimento': data.birthDate || '',
      'Data Admissão': data.admissionDate || '',
      'Ativo': data.active || ''
    }];
    arrayToSheet_(formatted, 'Usuario_' + login);
    const st = conexaoStatus_();
    SpreadsheetApp.getUi().alert(st.mensagem + '\n\nOK - Usuário ' + login + ' carregado.');
  } catch (e) {
    SpreadsheetApp.getUi().alert('ERRO ao consultar usuário:\n' + e.message);
  }
}

function CREATE_USER() {
  try {
    const login = getParam_(55);
    if (!login) {
      SpreadsheetApp.getUi().alert('Informe o Login na célula B55.');
      return;
    }
    const body = {
      login: login,
      fullName: getParam_(84) || undefined,
      firstName: getParam_(85) || undefined,
      lastName: getParam_(86) || undefined,
      gender: getParam_(87) || undefined,
      costCenterCode: getParam_(88) || undefined,
      companyCode: getParam_(89) || undefined,
      registration: getParam_(58) || undefined,
      email: getParam_(90) || undefined,
      phone: getParam_(91) || undefined,
      cellPhone: getParam_(92) || undefined,
      office: getParam_(93) || undefined,
      department: getParam_(94) || undefined,
      birthDate: getParam_(95) || undefined,
      admissionDate: getParam_(96) || undefined
    };
    const res = apiPost('/v2/api/Users', body);
    const st = conexaoStatus_();
    SpreadsheetApp.getUi().alert(st.mensagem + '\n\nOK - Usuário ' + login + ' cadastrado/editado.');
  } catch (e) {
    SpreadsheetApp.getUi().alert('ERRO ao cadastrar usuário:\n' + e.message);
  }
}

function DELETE_USER() {
  try {
    const login = getParam_(61);
    if (!login) {
      SpreadsheetApp.getUi().alert('Informe o Login na célula B61.');
      return;
    }
    const res = apiGetWithParams('/v2/api/Users', { login: login });
    const data = res.data;
    if (data) {
      const ui = SpreadsheetApp.getUi();
      const confirm = ui.alert('Excluir Usuário', 'Tem certeza que deseja excluir o usuário ' + login + '?', ui.ButtonSet.YES_NO);
      if (confirm !== ui.Button.YES) return;
    }
    const cfg = getConfig_();
    const token = authenticate();
    const options = {
      method: 'delete',
      headers: {
        Authorization: 'Bearer ' + token,
        accept: 'application/json'
      },
      muteHttpExceptions: true
    };
    const response = JSON.parse(UrlFetchApp.fetch(cfg.BASE_URL + '/v2/api/Users?login=' + encodeURIComponent(login), options));
    if (!response.success) {
      throw new Error(JSON.stringify(response.message));
    }
    const st = conexaoStatus_();
    SpreadsheetApp.getUi().alert(st.mensagem + '\n\nOK - Usuário ' + login + ' excluído.');
  } catch (e) {
    SpreadsheetApp.getUi().alert('ERRO ao excluir usuário:\n' + e.message);
  }
}

function ACCEPT_ORDER() {
  try {
    const order = getParam_(64);
    const loginApprover = getParam_(65);
    if (!order || !loginApprover) {
      SpreadsheetApp.getUi().alert('Informe o Nº do Pedido (B64) e o Login do Aprovador (B65).');
      return;
    }
    const params = { order: order, loginApprover: loginApprover };
    const res = apiPostForm('/v2/api/ApprovalFlow/AcceptOrder', params);
    const st = conexaoStatus_();
    SpreadsheetApp.getUi().alert(st.mensagem + '\n\nOK - Pedido ' + order + ' aprovado.');
  } catch (e) {
    SpreadsheetApp.getUi().alert('ERRO ao aprovar pedido:\n' + e.message);
  }
}

function DECLINE_ORDER() {
  try {
    const order = getParam_(68);
    const loginApprover = getParam_(69);
    const reason = getParam_(70);
    if (!order || !loginApprover || !reason) {
      SpreadsheetApp.getUi().alert('Informe o Nº do Pedido (B68), Login (B69) e Motivo (B70).');
      return;
    }
    const params = { order: order, loginApprover: loginApprover, reason: reason };
    const res = apiPostForm('/v2/api/ApprovalFlow/DeclineOrder', params);
    const st = conexaoStatus_();
    SpreadsheetApp.getUi().alert(st.mensagem + '\n\nOK - Pedido ' + order + ' reprovado.');
  } catch (e) {
    SpreadsheetApp.getUi().alert('ERRO ao reprovar pedido:\n' + e.message);
  }
}

function PAY_ORDER() {
  try {
    const osNumber = getParam_(73);
    const amount = getParam_(74);
    if (!osNumber || !amount) {
      SpreadsheetApp.getUi().alert('Informe o Nº da OS (B73) e o Valor (B74).');
      return;
    }
    const body = {
      osNumber: osNumber,
      amount: parseFloat(amount.replace(',', '.'))
    };
    const res = apiPost('/v2/api/Order/Pay', body);
    const st = conexaoStatus_();
    SpreadsheetApp.getUi().alert(st.mensagem + '\n\nOK - Pagamento da OS ' + osNumber + ' registrado.');
  } catch (e) {
    SpreadsheetApp.getUi().alert('ERRO ao pagar OS:\n' + e.message);
  }
}

function FOLLOWUP_ORDER() {
  try {
    const osNumber = getParam_(77);
    const comments = getParam_(78);
    if (!osNumber || !comments) {
      SpreadsheetApp.getUi().alert('Informe o Nº da OS (B77) e o Comentário (B78).');
      return;
    }
    const body = {
      osNumber: osNumber,
      comments: comments
    };
    const res = apiPost('/v2/api/Order/FollowUp', body);
    const st = conexaoStatus_();
    SpreadsheetApp.getUi().alert(st.mensagem + '\n\nOK - Comentário adicionado à OS ' + osNumber + '.');
  } catch (e) {
    SpreadsheetApp.getUi().alert('ERRO ao comentar OS:\n' + e.message);
  }
}

function LIST_ORDER_FOLLOWUPS() {
  try {
    const osNumber = getParam_(80);
    if (!osNumber) {
      SpreadsheetApp.getUi().alert('Informe o Nº da OS na célula B80.');
      return;
    }
    const res = apiGetWithParams('/v2/api/Order/FollowUP', { osNumber: osNumber });
    const data = res.data || [];
    const formatted = data.map(f => ({
      'Nº OS': f.osNumber || '',
      'Data': f.date || '',
      'Usuário': f.user || '',
      'Comentário': f.comments || '',
      'Tipo': f.type || ''
    }));
    arrayToSheet_(formatted, 'Comentarios_' + osNumber);
    const st = conexaoStatus_();
    SpreadsheetApp.getUi().alert(st.mensagem + '\n\nOK - ' + data.length + ' comentários encontrados.');
  } catch (e) {
    SpreadsheetApp.getUi().alert('ERRO ao listar comentários:\n' + e.message);
  }
}

function GET_USER_BY_REGISTRATION() {
  try {
    const registration = getParam_(58);
    if (!registration) {
      SpreadsheetApp.getUi().alert('Informe a Matrícula na célula B58.');
      return;
    }
    const res = apiGetWithParams('/v2/api/Users/GetUserByRegistration', { registration: registration });
    const data = res.data;
    if (!data) {
      SpreadsheetApp.getUi().alert('Usuário não encontrado.');
      return;
    }
    const formatted = [{
      'Login': data.login || '',
      'Nome': data.fullName || '',
      'Matrícula': data.registration || '',
      'Empresa': data.companyName || '',
      'Cód. Empresa': data.companyCode || '',
      'Cód. CC': data.costCenterCode || '',
      'Email': data.email || '',
      'Sexo': data.gender || '',
      'Telefone': data.phone || '',
      'Celular': data.cellPhone || '',
      'Cargo': data.office || '',
      'Departamento': data.department || '',
      'Data Nascimento': data.birthDate || '',
      'Data Admissão': data.admissionDate || '',
      'Ativo': data.active || ''
    }];
    arrayToSheet_(formatted, 'UsuarioMat_' + registration);
    const st = conexaoStatus_();
    SpreadsheetApp.getUi().alert(st.mensagem + '\n\nOK - Usuário matrícula ' + registration + ' carregado.');
  } catch (e) {
    SpreadsheetApp.getUi().alert('ERRO ao consultar usuário por matrícula:\n' + e.message);
  }
}

function HEALTH_CHECK() {
  try {
    const res = apiGet('/v2/api/HealthChecks');
    var st = conexaoStatus_();
    SpreadsheetApp.getUi().alert(st.mensagem + '\n\nHealthCheck: ' + JSON.stringify(res.data));
  } catch (e) {
    SpreadsheetApp.getUi().alert('ERRO no health check:\n' + e.message);
  }
}

function CLEAR_SHEETS() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheets = ss.getSheets();
  sheets.forEach(s => {
    if (s.getName() !== 'Sheet1') {
      ss.deleteSheet(s);
    }
  });
  SpreadsheetApp.getUi().alert('Abas removidas (exceto Sheet1).');
}

function onOpen() {
  try {
    SpreadsheetApp.getUi()
      .createMenu('COPASTUR BI')
      .addItem('Configurar Painel', 'SETUP_PAINEL')
      .addSeparator()
      .addItem('Executar (Data Informada)', 'RUN_MANUAL')
      .addItem('Executar (Última Execução)', 'RUN_INCREMENTAL')
      .addSeparator()
      .addItem('Diagnosticar Auto-Execução', 'TEST_AUTO')
      .addSeparator()
      .addItem('Ativar Auto-Execução (5h-00h)', 'INSTALL_TRIGGER')
      .addItem('Desativar Auto-Execução', 'REMOVE_TRIGGER')
      .addItem('Status da Conexão', 'STATUS_CONEXAO')
      .addToUi();
  } catch (e) {
    console.log('onOpen: ' + e.message);
  }
}

function SETUP_PAINEL() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName('Painel');
  if (!sheet) {
    sheet = ss.insertSheet('Painel', 0);
  }
  const cfg = getConfig_();
  sheet.clearContents();
  var dados = [
    ['COPASTUR BI - Painel de Controle', '', '', ''],
    ['', '', '', ''],
    ['Configuração de Acesso', '', '', ''],
    ['Usuário', cfg.USERNAME, '', ''],
    ['Senha', cfg.PASSWORD, '', ''],
    ['Base URL', cfg.BASE_URL, '', ''],
    ['', '', '', ''],
    ['Execução Manual', '', '', ''],
    ['Data Início', '', '', ''],
    ['Data Fim', '', '', ''],
    ['', '', '', ''],
    ['Auto-Execução', '', '', ''],
    ['Ativar Auto', false, '', ''],
    ['Última Execução', '', '', ''],
    ['', '', '', ''],
    ['Status', '', '', '']
  ];
  var r = sheet.getRange(1, 1, dados.length, 4);
  r.setValues(dados);
  sheet.getRange(1, 1, 1, 4).merge().setFontWeight('bold').setFontSize(14);
  sheet.getRange(3, 1, 1, 4).merge().setFontWeight('bold').setFontSize(11);
  sheet.getRange(8, 1, 1, 4).merge().setFontWeight('bold').setFontSize(11);
  sheet.getRange(12, 1, 1, 4).merge().setFontWeight('bold').setFontSize(11);
  sheet.getRange('C13').insertCheckboxes();
  sheet.getRange('B4').setFontWeight('bold');
  sheet.getRange('B5').setFontWeight('bold');
  sheet.getRange('B6').setFontWeight('bold');
  sheet.getRange('B9').setFontWeight('bold');
  sheet.getRange('B10').setFontWeight('bold');
  sheet.autoResizeColumns(1, 4);

  var lastRun = PropertiesService.getScriptProperties().getProperty('BI_LAST_RUN');
  if (lastRun) {
    sheet.getRange('C14').setValue(lastRun);
  }

  sheet.getRange('C16').setFormula('=IF(C13,"Auto-Execução Ativa (5h-00h)","Auto-Execução Desativada")');
  sheet.getRange('C16').setBackground('#FFF3CD');
  sheet.getRange('C17').setValue('Último resultado: ---');
  sheet.getRange('C17').setBackground('#F5F5F5');
  sheet.getRange('C14').setBackground('#E8F5E9');

  sheet.getRange('A20').setValue('Total de Pedidos Internalizados').setFontWeight('bold');
  sheet.getRange('B20').setValue(0).setBackground('#E8F5E9').setFontWeight('bold');
  sheet.getRange('C20').setValue(0).setBackground('#E8F5E9').setFontWeight('bold');
  sheet.getRange('A20').setFontWeight('bold');
  sheet.getRange('B19').setValue('Total Geral');
  sheet.getRange('C19').setValue('Hoje');
  sheet.getRange('B19').setFontWeight('bold');
  sheet.getRange('C19').setFontWeight('bold');
  sheet.getRange('B19').setBackground('#D6E4F0');
  sheet.getRange('C19').setBackground('#D6E4F0');

  updateContadoresPainel_();
  SpreadsheetApp.getUi().alert('Painel configurado na aba "Painel".\n\nPreencha os dados de acesso e período, depois use o menu.');
}

function getConfig_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('Painel');
  const padrao = {
    BASE_URL: 'https://api.copastur.com.br/api-company',
    USERNAME: 'fujicomhomolog@copastur.com.br',
    PASSWORD: '^Oe#w#bil4A$50A',
    TOKEN_KEY: 'COPASTUR_BI_TOKEN',
    EXPIRY_KEY: 'COPASTUR_BI_TOKEN_EXPIRY',
    AUTH_TIME_KEY: 'COPASTUR_BI_AUTH_TIME'
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

function authenticate() {
  const cfg = getConfig_();
  const props = PropertiesService.getScriptProperties();
  const token = props.getProperty(cfg.TOKEN_KEY);
  const expiry = props.getProperty(cfg.EXPIRY_KEY);
  if (token && expiry && new Date() < new Date(expiry)) {
    return token;
  }
  const payload = { username: cfg.USERNAME, password: cfg.PASSWORD };
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
    return { conectado: false, mensagem: 'Nenhuma conexão ativa.' };
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
    headers: { Authorization: 'Bearer ' + token, accept: 'application/json' },
    muteHttpExceptions: true,
    timeout: 300000
  };
  const response = JSON.parse(UrlFetchApp.fetch(cfg.BASE_URL + endpoint, options));
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
    headers: { Authorization: 'Bearer ' + token, accept: 'application/json' },
    muteHttpExceptions: true,
    timeout: 300000
  };
  const response = JSON.parse(UrlFetchApp.fetch(url, options));
  if (!response.success) {
    throw new Error('Erro na consulta: ' + JSON.stringify(response.message));
  }
  return response;
}

function appendToSheet_(data, sheetName) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(sheetName);
  if (!sheet) {
    sheet = ss.insertSheet(sheetName);
  }
  if (!data || data.length === 0) return 0;
  var added = 0;
  if (sheet.getLastRow() === 0) {
    var headers = Object.keys(data[0]);
    var rows = data.map(obj => headers.map(h => {
      var val = obj[h];
      return val !== null && val !== undefined ? val : '';
    }));
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]).setFontWeight('bold');
    sheet.getRange(2, 1, rows.length, headers.length).setValues(rows);
    added = rows.length;
  } else {
    var existingHeaders = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
    var existingData = sheet.getRange(2, 1, sheet.getLastRow() - 1, sheet.getLastColumn()).getValues();
    var existingKeys = {};
    for (var e = 0; e < existingData.length; e++) {
      existingKeys[String(existingData[e][0])] = true;
    }
    var newRows = [];
    for (var d = 0; d < data.length; d++) {
      var key = String(data[d][existingHeaders[0]] || '');
      if (!existingKeys[key]) {
        newRows.push(existingHeaders.map(function(h) {
          var val = data[d][h];
          return val !== null && val !== undefined ? val : '';
        }));
        existingKeys[key] = true;
      }
    }
    if (newRows.length > 0) {
      sheet.getRange(sheet.getLastRow() + 1, 1, newRows.length, existingHeaders.length).setValues(newRows);
      added = newRows.length;
    }
  }
  if (added > 0) SpreadsheetApp.flush();
  return added;
}

function getCellDate_(row) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('Painel');
  if (!sheet) return '';
  var val = sheet.getRange('B' + row).getValue();
  if (!val) return '';
  if (val instanceof Date) {
    var d = val;
    var ano = d.getFullYear();
    var mes = String(d.getMonth() + 1).padStart(2, '0');
    var dia = String(d.getDate()).padStart(2, '0');
    return ano + '-' + mes + '-' + dia;
  }
  return String(val).trim();
}

function isAutoEnabled_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('Painel');
  if (!sheet) return false;
  return sheet.getRange('C13').isChecked();
}

function updateLastRun_() {
  var agora = new Date();
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var tz = ss.getSpreadsheetTimeZone();
  var fmt = Utilities.formatDate(agora, tz, 'dd/MM/yyyy HH:mm:ss');
  PropertiesService.getScriptProperties().setProperty('BI_LAST_RUN', fmt);
  PropertiesService.getScriptProperties().setProperty('BI_LAST_RUN_ISO', agora.toISOString());
  const sheet = ss.getSheetByName('Painel');
  if (sheet) {
    sheet.getRange('C14').setValue(fmt);
  }
}

function getLastRunISO_() {
  return PropertiesService.getScriptProperties().getProperty('BI_LAST_RUN_ISO') || '';
}

function getExistingOrderNumbers_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('Pedidos');
  if (!sheet || sheet.getLastRow() < 2) return {};
  var data = sheet.getRange(2, 1, sheet.getLastRow() - 1, 1).getValues();
  var map = {};
  for (var i = 0; i < data.length; i++) {
    map[String(data[i][0])] = true;
  }
  return map;
}

function processOrders_BY_PERIOD_(startDate, endDate) {
  var params = { request_date_start: startDate, request_date_end: endDate };
  var res = apiGetWithParams('/v2/api/Order/List', params);
  var orders = res.data || [];
  if (orders.length === 0) return 0;

  var existingOrders = getExistingOrderNumbers_();
  var orderNumbers = [];
  for (var i = 0; i < orders.length; i++) {
    var num = orders[i].osNumber || orders[i].requestNumber || '';
    if (num && !existingOrders[num]) orderNumbers.push(num);
  }
  if (orderNumbers.length === 0) return 0;

  var pedidosData = [];
  var aereosData = [];
  var hoteisData = [];
  var carrosData = [];
  var outrosData = [];
  var servicosData = [];
  var transportData = [];
  var reembolsosData = [];
  var adiantamentosData = [];
  var viajantesData = [];
  var aprovadoresData = [];
  var resumoData = [];
  var rateioData = [];
  var statusData = [];
  var followUpData = [];

  for (var j = 0; j < orderNumbers.length; j++) {
    try {
      var num = orderNumbers[j];
      var res2 = apiGet('/v2/api/Order/GetOrderV2?osNumber=' + encodeURIComponent(num));
      var d = res2.data;
      if (!d) continue;

      pedidosData.push({
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
          aereosData.push({
            'Nº Pedido': num, 'Companhia': air.ciaName || '', 'Nr Voo': air.flyNumber || '',
            'Origem': (air.cityDeparture || '') + ' (' + (air.iataDeparture || '') + ')',
            'Destino': (air.cityArrival || '') + ' (' + (air.iataArrival || '') + ')',
            'Partida': air.departureDate || '', 'Chegada': air.arrivalDate || '',
            'Tarifa': air.fare || '', 'Taxas': air.tax || '', 'Total': air.totalFare || '',
            'Moeda': air.currency || '', 'Localizador': air.pnr || '', 'eTicket': air.eticket || '',
            'Classe': air.class || '', 'Cabine': air.cabin || '', 'Status': air.status || '',
            'Fornecedor': air.supplier || '', 'Conexões': air.connections || '', 'Paradas': air.stops || '',
            'Origem País': air.countryDeparture || '', 'Destino País': air.countryArrival || '',
            'ID Cotação': air.quotationId || ''
          });
        }
      }

      if (d.hotels && d.hotels.length > 0) {
        for (var h = 0; h < d.hotels.length; h++) {
          var hot = d.hotels[h];
          hoteisData.push({
            'Nº Pedido': num, 'Hotel': hot.name || '', 'Cidade': hot.city || '',
            'Estado': hot.state || '', 'Endereço': hot.address || '',
            'CheckIn': hot.checkinDate || '', 'CheckOut': hot.checkoutDate || '',
            'Suplementar': hot.additionalFare || '', 'Desconto': hot.discountFare || '',
            'Tarifa': hot.fare || '', 'Taxas': hot.tax || '', 'Total': hot.totalFare || '',
            'Moeda': hot.currency || '', 'Tipo Quarto': hot.roomType || '', 'Tipo Cama': hot.bedType || '',
            'Tipo Cobrança': hot.billingType || '', 'Diárias': hot.amountDialy || '',
            'Fornecedor': hot.supplier || '', 'Voucher': hot.voucher || '',
            'Data Cancelamento': hot.dateCancel || '', 'Categoria': hot.category || '',
            'Nº Autorização': hot.authorizationNumber || '', 'Online': hot.online || '',
            'Data Criação': hot.dateCreated || ''
          });
        }
      }

      if (d.cars && d.cars.length > 0) {
        for (var c = 0; c < d.cars.length; c++) {
          var car = d.cars[c];
          carrosData.push({
            'Nº Pedido': num, 'Locadora': car.supplier || '', 'Categoria': car.category || '',
            'Veículo': car.vehicle || '', 'Cambio': car.gearbox || '',
            'Ar Condicionado': car.hasAirConditional || '', 'Motorista': car.hasDriver || '',
            'GPS': car.hasGPS || '', 'Retirada': car.localCheckin || '', 'Devolução': car.localCheckout || '',
            'Data Retirada': car.checkinDate || '', 'Data Devolução': car.checkoutDate || '',
            'Tarifa': car.fare || '', 'Suplementar': car.additionalFare || '', 'Desconto': car.discountFare || '',
            'Taxas': car.tax || '', 'Total': car.totalFare || '', 'Moeda': car.currency || '',
            'Diárias': car.dailyQuantity || '', 'Voucher': car.voucher || '',
            'Data Cancelamento': car.cancelDate || '', 'Nº Autorização': car.authorizationNumber || '',
            'Data Criação': car.dateCreated || ''
          });
        }
      }

      if (d.miscellaneous && d.miscellaneous.length > 0) {
        for (var m = 0; m < d.miscellaneous.length; m++) {
          var mis = d.miscellaneous[m];
          outrosData.push({
            'Nº Pedido': num, 'Origem': mis.departure || '', 'Destino': mis.arrival || '',
            'Data Partida': mis.departureDate || '', 'Data Chegada': mis.arrivalDate || '',
            'Fornecedor': mis.supplier || '', 'Total': mis.totalFare || ''
          });
        }
      }

      if (d.services && d.services.length > 0) {
        for (var s = 0; s < d.services.length; s++) {
          var svc = d.services[s];
          servicosData.push({
            'Nº Pedido': num, 'Descrição': svc.description || '', 'Tipo Serviço': svc.typeService || '',
            'Fornecedor': svc.supplier || '', 'Data Início': svc.startDate || '',
            'Data Fim': svc.endDate || '', 'Data Vencimento': svc.expirationDate || '',
            'Quantidade': svc.quantity || '', 'Tarifa': svc.fare || '', 'Taxas': svc.tax || '',
            'Total': svc.totalFare || '', 'Voucher': svc.voucher || '', 'Data Voucher': svc.dateVoucher || '',
            'Observação': svc.remarks || '', 'ID Cotação': svc.quotationId || '',
            'Nº Autorização': svc.authorizationNumber || '', 'Data Cancelamento': svc.dateCanceled || '',
            'Data Emissão': svc.issuedDate || '', 'Data Criação': svc.dateCreated || ''
          });
        }
      }

      if (d.transport && d.transport.length > 0) {
        for (var t = 0; t < d.transport.length; t++) {
          var trp = d.transport[t];
          transportData.push({
            'Nº Pedido': num, 'Cia': trp.cia || '', 'Assento': trp.seat || '',
            'Origem': trp.departure || '', 'Terminal Origem': trp.terminalDeparture || '',
            'Destino': trp.arrival || '', 'Terminal Destino': trp.terminalArrival || '',
            'Data Partida': trp.dateDeparture || '', 'Data Chegada': trp.dateArrival || '',
            'Tipo Serviço': trp.serviceType || '', 'Tarifa': trp.fare || '',
            'Suplementar': trp.additionalFare || '', 'Desconto': trp.discountFare || '',
            'Total': trp.totalFare || '', 'Voucher': trp.voucher || '', 'Data Voucher': trp.dateVoucher || '',
            'Observação': trp.remarks || '', 'ID Cotação': trp.quotationId || '',
            'Data Inclusão': trp.dateIncluded || '', 'Data Atualização': trp.dateUpdated || '',
            'Data Vencimento': trp.dateExpired || '', 'Data Cancelamento': trp.dateCanceled || ''
          });
        }
      }

      if (d.refunds && d.refunds.length > 0) {
        for (var r = 0; r < d.refunds.length; r++) {
          var ref = d.refunds[r];
          reembolsosData.push({
            'Nº Pedido': num, 'Despesa': ref.expense || '', 'Descrição': ref.descriptiveExpense || '',
            'Categoria': ref.category || '', 'Conta': ref.account || '',
            'Moeda': ref.currency || '', 'Código Moeda': ref.currencyCode || '',
            'Cotação': ref.exchange || '', 'Quantidade': ref.quantity || '',
            'Preço': ref.price || '', 'Valor': ref.amount || '', 'Valor Total': ref.totalAmount || '',
            'Valor Taxa': ref.taxAmount || '', '% Taxa': ref.taxPercent || '',
            'Valor Ref.': ref.referAmount || '', 'Moeda Ref.': ref.referCurrency || '',
            'Cotação Ref.': ref.referExchange || '', 'Histórico': ref.history || '',
            'Centro Custo': ref.costCenterDescription || '', 'Código CC': ref.costCenterCode || '',
            'Conta Bancária': ref.bankAccount || '', 'Comprovante': ref.proofPayment || '',
            'URL Nota': ref.invoicheImagemURL || '', 'Observação': ref.observation || '',
            'Tipo Pagamento': ref.typePaymentName || '', 'Data Criação': ref.dateCreated || '',
            'Data Pagamento': ref.datePaid || '', 'Data Início': ref.dateStart || '',
            'Data Fim': ref.dateEnd || '', 'Data Modificação': ref.dateModified || '',
            'Ativo': ref.isActive || '', 'Aprovado': ref.isApproved || '',
            'Reembolso': ref.isRefund || '', 'Verificado': ref.isVerified || ''
          });
        }
      }

      if (d.advances && d.advances.length > 0) {
        for (var ad = 0; ad < d.advances.length; ad++) {
          var adv = d.advances[ad];
          adiantamentosData.push({
            'Nº Pedido': num, 'Despesa': adv.expense || '',
            'Moeda': adv.currency || '', 'Código Moeda': adv.currencyCode || '',
            'Cotação': adv.exchange || '', 'Moeda Original': adv.coin || '',
            'Código Bacen': adv.bacenCode || '', 'Quantidade': adv.quantity || '',
            'Preço': adv.price || '', 'Valor Total': adv.totalAmount || '',
            'Tipo Pagamento': adv.typePaymentName || '', 'Motivo Viagem': adv.reasonTravelling || '',
            'Cidade Origem': adv.cityOrigin || '', 'Cidade Partida': adv.departureCity || '',
            'Cidade Destino': adv.arrivalCity || '', 'País Partida': adv.departureCountry || '',
            'País Destino': adv.arrivalCountry || '', 'Comentários': adv.comments || '',
            'Data Criação': adv.dateCreated || '', 'Data Pagamento': adv.datePaid || '',
            'Data Início': adv.dateStart || '', 'Data Fim': adv.dateEnd || '',
            'Data Modificação': adv.dateModified || ''
          });
        }
      }

      if (d.travelers && d.travelers.length > 0) {
        for (var v = 0; v < d.travelers.length; v++) {
          var tvl = d.travelers[v];
          viajantesData.push({
            'Nº Pedido': num, 'Nome': tvl.fullName || '', 'Login': tvl.login || '',
            'Email': tvl.email || '', 'Matrícula': tvl.registration || '',
            'Telefone': tvl.phone || '', 'Celular': tvl.celularPhone || '',
            'Cargo': tvl.position || '', 'VIP': tvl.vip || '', 'Estado': tvl.state || ''
          });
        }
      }

      if (d.approvers && d.approvers.length > 0) {
        for (var ap = 0; ap < d.approvers.length; ap++) {
          var apr = d.approvers[ap];
          aprovadoresData.push({
            'Nº Pedido': num, 'Nome': apr.fullName || '', 'Login': apr.login || '',
            'Email': apr.email || '', 'Matrícula': apr.registration || '',
            'Data Aprovação': apr.approvalDate || ''
          });
        }
      }

      if (d.summary && d.summary.length > 0) {
        for (var sm = 0; sm < d.summary.length; sm++) {
          var sum = d.summary[sm];
          resumoData.push({
            'Nº Pedido': num, 'Tipo': sum.Tipo || '', 'Moeda': sum.currency || '',
            'Valor Maior': sum.ValorMaior || '', 'Valor Menor': sum.ValorMenor || '',
            'Valor Médio': sum.ValorMedio || '', 'Valor Total': sum.ValorTotal || '',
            'Quantidade': sum.Quantidade || '', 'Bilhete': sum.Bilhete || '',
            'Localizador': sum.Localizador || '', 'Voucher': sum.voucher || '',
            'Selecionado': sum.Selecionado || '', 'ID Cotação': sum.CotacaoId || ''
          });
        }
      }

      if (d.apportionment && d.apportionment.length > 0) {
        for (var ar = 0; ar < d.apportionment.length; ar++) {
          var app = d.apportionment[ar];
          rateioData.push({
            'Nº Pedido': num, 'Empresa': app.company || '', 'Código Empresa': app.companyCode || '',
            '%': app.percent || '', 'Conta Contábil Cód.': app.contaContabilCod || '',
            'Conta Contábil Desc.': app.contaContabilDesc || '', 'Projeto Cód.': app.projectCod || '',
            'Projeto Desc.': app.projectDesc || '', 'Observação': app.observation || ''
          });
        }
      }

      if (d.expenseStatus && d.expenseStatus.length > 0) {
        for (var es = 0; es < d.expenseStatus.length; es++) {
          var st = d.expenseStatus[es];
          statusData.push({
            'Nº Pedido': num, 'Status': st.status_name || '', 'Código': st.status_code || '',
            'Data': st.status_date || ''
          });
        }
      }

      if (d.followUP && d.followUP.length > 0) {
        for (var fu = 0; fu < d.followUP.length; fu++) {
          var fup = d.followUP[fu];
          followUpData.push({
            'Nº Pedido': num, 'Mensagem': fup.message || '', 'Enviado Por': fup.sentBy || '',
            'Destinatários': fup.recipients || '', 'Data Inclusão': fup.inclusionDate || ''
          });
        }
      }
    } catch (e) {
      console.log('Erro pedido ' + num + ': ' + e.message);
    }
  }

  if (pedidosData.length === 0) return 0;

  var colInt = garantirColunaInternalizacao_();
  var totalLinhas = 0;
  var addPed = appendToSheet_(pedidosData, 'Pedidos');
  if (addPed > 0 && colInt > 0) {
    var pedSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Pedidos');
    var tz = SpreadsheetApp.getActiveSpreadsheet().getSpreadsheetTimeZone();
    var agoraInt = new Date();
    var dataHora = Utilities.formatDate(agoraInt, tz, 'yyyy-MM-dd HH:mm:ss');
    var startRow = pedSheet.getLastRow() - addPed + 1;
    var rangeDate = pedSheet.getRange(startRow, colInt, addPed, 1);
    rangeDate.setValue(dataHora);
    SpreadsheetApp.flush();
  }
  totalLinhas += addPed;
  if (aereosData.length > 0) appendToSheet_(aereosData, 'Aereos');
  if (hoteisData.length > 0) appendToSheet_(hoteisData, 'Hoteis');
  if (carrosData.length > 0) appendToSheet_(carrosData, 'Carros');
  if (outrosData.length > 0) appendToSheet_(outrosData, 'OutrosServicos');
  if (servicosData.length > 0) appendToSheet_(servicosData, 'Servicos');
  if (transportData.length > 0) appendToSheet_(transportData, 'Transporte');
  if (reembolsosData.length > 0) appendToSheet_(reembolsosData, 'Reembolsos');
  if (adiantamentosData.length > 0) appendToSheet_(adiantamentosData, 'Adiantamentos');
  if (viajantesData.length > 0) appendToSheet_(viajantesData, 'Viajantes');
  if (aprovadoresData.length > 0) appendToSheet_(aprovadoresData, 'Aprovadores');
  if (resumoData.length > 0) appendToSheet_(resumoData, 'ResumoCotacoes');
  if (rateioData.length > 0) appendToSheet_(rateioData, 'Rateio');
  if (statusData.length > 0) appendToSheet_(statusData, 'StatusDespesa');
  if (followUpData.length > 0) appendToSheet_(followUpData, 'FollowUp');

  return pedidosData.length;
}

function registrarInternalizacao_(qtdNovos) {
  var props = PropertiesService.getScriptProperties();
  var HOJE_KEY = 'BI_CONT_HOJE';
  var HOJE_DATA_KEY = 'BI_CONT_HOJE_DATA';
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var tz = ss.getSpreadsheetTimeZone();
  var hojeStr = Utilities.formatDate(new Date(), tz, 'yyyy-MM-dd');
  var hojeData = props.getProperty(HOJE_DATA_KEY);
  if (hojeData === hojeStr) {
    var cont = parseInt(props.getProperty(HOJE_KEY) || '0', 10);
    props.setProperty(HOJE_KEY, String(cont + qtdNovos));
  } else {
    props.setProperty(HOJE_DATA_KEY, hojeStr);
    props.setProperty(HOJE_KEY, String(qtdNovos));
  }
}

function updateContadoresPainel_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('Painel');
  if (!sheet) return;
  var pedSheet = ss.getSheetByName('Pedidos');
  var total = 0;
  var hoje = 0;
  if (pedSheet && pedSheet.getLastRow() > 1) {
    total = pedSheet.getLastRow() - 1;
  }
  var props = PropertiesService.getScriptProperties();
  var HOJE_KEY = 'BI_CONT_HOJE';
  var HOJE_DATA_KEY = 'BI_CONT_HOJE_DATA';
  var tz = ss.getSpreadsheetTimeZone();
  var hojeStr = Utilities.formatDate(new Date(), tz, 'yyyy-MM-dd');
  if (props.getProperty(HOJE_DATA_KEY) === hojeStr) {
    hoje = parseInt(props.getProperty(HOJE_KEY) || '0', 10);
  }
  sheet.getRange('B20').setValue(total);
  sheet.getRange('C20').setValue(hoje);
}

function garantirColunaInternalizacao_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('Pedidos');
  if (!sheet) return -1;
  var headers = sheet.getLastRow() > 0 ? sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0] : [];
  for (var i = 0; i < headers.length; i++) {
    if (headers[i] === 'Data Internalização') return i + 1;
  }
  var colIdx = sheet.getLastColumn() + 1;
  sheet.getRange(1, colIdx).setValue('Data Internalização').setFontWeight('bold');
  if (sheet.getLastRow() > 1) {
    sheet.getRange(2, colIdx, sheet.getLastRow() - 1, 1).setValue('');
  }
  SpreadsheetApp.flush();
  return colIdx;
}

function RUN_MANUAL() {
  try {
    var startDate = getCellDate_(9);
    var endDate = getCellDate_(10);
    if (!startDate || !endDate) {
      SpreadsheetApp.getUi().alert('Preencha a Data Início (B9) e Data Fim (B10) no Painel.');
      return;
    }
    SpreadsheetApp.getUi().alert(
      'Executando consulta de ' + startDate + ' a ' + endDate + '...\nIsso pode levar alguns minutos.'
    );
    var novos = processOrders_BY_PERIOD_(startDate, endDate);
    registrarInternalizacao_(novos);
    updateLastRun_();
    updateContadoresPainel_();
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Painel');
    var tz = SpreadsheetApp.getActiveSpreadsheet().getSpreadsheetTimeZone();
    if (sheet) sheet.getRange('C17').setValue('Manual: ' + novos + ' novos pedidos em ' + Utilities.formatDate(new Date(), tz, 'dd/MM/yyyy HH:mm:ss'));
    SpreadsheetApp.getUi().alert('Concluído!\n\nNovos pedidos adicionados: ' + novos + '\n\nAbas incrementadas: Pedidos, Aereos, Hoteis, Carros, OutrosServicos, Servicos, Transporte, Reembolsos, Adiantamentos, Viajantes, Aprovadores, ResumoCotacoes, Rateio, StatusDespesa, FollowUp');
  } catch (e) {
    SpreadsheetApp.getUi().alert('ERRO: ' + e.message);
  }
}

function RUN_INCREMENTAL() {
  try {
    var lastRun = getLastRunISO_();
    if (!lastRun) {
      SpreadsheetApp.getUi().alert('Nenhuma execução anterior encontrada. Use "Executar (Data Informada)" primeiro.');
      return;
    }
    var agora = new Date();
    var fmtAgora = agora.toISOString();
    var startDate = lastRun.substring(0, 10);
    var endDate = fmtAgora.substring(0, 10);
    SpreadsheetApp.getUi().alert(
      'Executando consulta incremental de ' + startDate + ' a ' + endDate + '...'
    );
    var novos = processOrders_BY_PERIOD_(startDate, endDate);
    registrarInternalizacao_(novos);
    updateLastRun_();
    updateContadoresPainel_();
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Painel');
    var tz = SpreadsheetApp.getActiveSpreadsheet().getSpreadsheetTimeZone();
    if (sheet) sheet.getRange('C17').setValue('Incremental: ' + novos + ' novos pedidos em ' + Utilities.formatDate(new Date(), tz, 'dd/MM/yyyy HH:mm:ss'));
    SpreadsheetApp.getUi().alert('Concluído!\n\nNovos pedidos adicionados: ' + novos);
  } catch (e) {
    SpreadsheetApp.getUi().alert('ERRO: ' + e.message);
  }
}

function AUTO_EXECUTE() {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    if (!isAutoEnabled_()) return;
    var tz = ss.getSpreadsheetTimeZone();
    var agora = new Date();
    var hora = parseInt(Utilities.formatDate(agora, tz, 'HH'), 10);
    if (hora < 5) return;
    var fmtAgora = agora.toISOString();
    var startDate, endDate = fmtAgora.substring(0, 10);
    var lastRun = getLastRunISO_();
    if (lastRun) {
      startDate = lastRun.substring(0, 10);
    } else {
      var doisDias = new Date(agora);
      doisDias.setDate(doisDias.getDate() - 2);
      startDate = doisDias.toISOString().substring(0, 10);
    }
    var novos = processOrders_BY_PERIOD_(startDate, endDate);
    registrarInternalizacao_(novos);
    updateLastRun_();
    updateContadoresPainel_();
    var sheet = ss.getSheetByName('Painel');
    if (sheet) {
      sheet.getRange('C17').setValue('Auto: ' + novos + ' novos pedidos em ' + Utilities.formatDate(agora, tz, 'dd/MM/yyyy HH:mm:ss'));
    }
  } catch (e) {
    console.log('AUTO_EXECUTE erro: ' + e.message);
    try {
      var sheet2 = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Painel');
      if (sheet2) sheet2.getRange('C17').setValue('ERRO: ' + e.message);
    } catch (f) {}
  }
}


function INSTALL_TRIGGER() {
  var ui = SpreadsheetApp.getUi();
  var existing = ScriptApp.getProjectTriggers();
  for (var i = 0; i < existing.length; i++) {
    if (existing[i].getHandlerFunction() === 'AUTO_EXECUTE') {
      ui.alert('Auto-Execução já está ativada.');
      return;
    }
  }
  ScriptApp.newTrigger('AUTO_EXECUTE')
    .timeBased()
    .everyMinutes(30)
    .create();
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('Painel');
  if (sheet) sheet.getRange('C13').check();
  ui.alert('Auto-Execução ativada!\n\nO script será executado automaticamente a cada 30 minutos, entre 05:00 e 00:00.\n\nUse "Desativar Auto-Execução" para parar.');
}

function REMOVE_TRIGGER() {
  var existing = ScriptApp.getProjectTriggers();
  for (var i = 0; i < existing.length; i++) {
    if (existing[i].getHandlerFunction() === 'AUTO_EXECUTE') {
      ScriptApp.deleteTrigger(existing[i]);
    }
  }
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('Painel');
  if (sheet) sheet.getRange('C13').uncheck();
  SpreadsheetApp.getUi().alert('Auto-Execução desativada.');
}

function FORCE_REAUTH() {
  const cfg = getConfig_();
  const props = PropertiesService.getScriptProperties();
  props.deleteProperty(cfg.TOKEN_KEY);
  props.deleteProperty(cfg.EXPIRY_KEY);
  props.deleteProperty(cfg.AUTH_TIME_KEY);
  SpreadsheetApp.getUi().alert('Token removido. A próxima execução reautenticará automaticamente.');
}

function TEST_AUTO() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('Painel');
  var msgs = [];
  msgs.push('Data/hora servidor: ' + new Date().toString());
  msgs.push('Fuso planilha: ' + ss.getSpreadsheetTimeZone());
  var tz = ss.getSpreadsheetTimeZone();
  var agora = new Date();
  msgs.push('Hora local: ' + Utilities.formatDate(agora, tz, 'HH:mm:ss'));
  msgs.push('Auto habilitado: ' + (sheet ? sheet.getRange('C13').isChecked() : 'Painel não encontrado'));
  var triggers = ScriptApp.getProjectTriggers();
  msgs.push('Triggers ativos: ' + triggers.length);
  for (var i = 0; i < triggers.length; i++) {
    msgs.push('  - ' + triggers[i].getHandlerFunction() + ' (' + triggers[i].getTriggerSource() + ')');
  }
  var statusAtual = sheet ? sheet.getRange('C17').getValue() : '';
  msgs.push('Status C17: ' + (statusAtual || '(vazio)'));
  msgs.push('');
  if (sheet) {
    sheet.getRange('C17').setValue('Teste: OK em ' + Utilities.formatDate(agora, tz, 'dd/MM/yyyy HH:mm:ss'));
    msgs.push('C17 atualizado com sucesso!');
  }
  SpreadsheetApp.getUi().alert('Diagnóstico Auto-Execução:\n\n' + msgs.join('\n'));
}

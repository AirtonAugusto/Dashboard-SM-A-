/**
 * Backend do painel "Programação de Atividades SM&A" — Google Apps Script.
 *
 * Isso roda dentro do Google Sheets (Extensões > Apps Script), publicado
 * como "Web App". O painel HTML (GitHub Pages) chama essa URL para:
 *   - ler todas as atividades (GET);
 *   - concluir, justificar, adicionar atividade nova (backlog) ou
 *     registrar atividade extra por proatividade (POST).
 *
 * A planilha Google precisa ter duas abas:
 *   "Atividades" — uma linha de cabeçalho (ver COLS abaixo) + uma linha
 *                  por atividade.
 *   "Log"        — cabeçalho: Timestamp | Ação | ID | Responsável | Detalhe
 *                  (append-only, histórico de tudo que foi feito por aqui).
 *
 * Nada disso mexe na sua planilha Excel diretamente — a sincronização de
 * volta pro Excel é feita pelo script local `sync_sheets_to_excel.py`
 * (um clique, como o `atualizar_painel.bat` já existente).
 */

var SHEET_ATIVIDADES = 'Atividades';
var SHEET_LOG = 'Log';

// Ordem das colunas na aba "Atividades". Se um dia precisar adicionar uma
// coluna nova, só acrescentar aqui no fim e também no cabeçalho da planilha.
var COLS = [
  'id', 'desc', 'local', 'ini', 'fim', 'horas', 'situacao', 'status',
  'obs', 'resp', 'justificativa', 'origem', 'dataExecucao',
  'criadoEm', 'atualizadoEm'
];

function getSheet_(nome) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(nome);
  if (!sh) throw new Error('Aba "' + nome + '" não encontrada na planilha.');
  return sh;
}

function hojeIso_() {
  return Utilities.formatDate(new Date(), Session.getScriptTimeZone() || 'America/Sao_Paulo', 'yyyy-MM-dd');
}

function agoraIso_() {
  return new Date().toISOString();
}

// ---------- leitura ----------

function listarAtividades_() {
  var sh = getSheet_(SHEET_ATIVIDADES);
  var values = sh.getDataRange().getValues();
  if (values.length < 2) return [];
  var headers = values[0].map(function (h) { return String(h).trim(); });
  var idx = {};
  headers.forEach(function (h, i) { idx[h] = i; });

  var out = [];
  for (var r = 1; r < values.length; r++) {
    var row = values[r];
    if (row.every(function (c) { return c === '' || c === null; })) continue;
    var obj = {};
    COLS.forEach(function (c) {
      var v = idx[c] !== undefined ? row[idx[c]] : '';
      if (v instanceof Date) {
        v = Utilities.formatDate(v, Session.getScriptTimeZone() || 'America/Sao_Paulo', 'yyyy-MM-dd');
      }
      obj[c] = (v === null || v === undefined) ? '' : v;
    });
    if (obj.horas === '') obj.horas = 0;
    out.push(obj);
  }
  return out;
}

function proximoId_(atividades) {
  var maxId = 0;
  atividades.forEach(function (a) {
    var n = Number(a.id);
    if (!isNaN(n) && n > maxId) maxId = n;
  });
  return maxId + 1;
}

function registrarLog_(acao, id, responsavel, detalhe) {
  var sh = getSheet_(SHEET_LOG);
  sh.appendRow([new Date(), acao, id, responsavel || '', detalhe || '']);
}

// ---------- escrita ----------

function encontrarLinhaPorId_(sh, id) {
  var values = sh.getDataRange().getValues();
  var headers = values[0].map(function (h) { return String(h).trim(); });
  var idxId = headers.indexOf('id');
  for (var r = 1; r < values.length; r++) {
    if (String(values[r][idxId]) === String(id)) {
      return { linha: r + 1, headers: headers };
    }
  }
  return null;
}

function setCelula_(sh, linha, headers, coluna, valor) {
  var idx = headers.indexOf(coluna);
  if (idx === -1) return;
  sh.getRange(linha, idx + 1).setValue(valor);
}

function acaoConcluir_(p) {
  var sh = getSheet_(SHEET_ATIVIDADES);
  var achado = encontrarLinhaPorId_(sh, p.id);
  if (!achado) throw new Error('Atividade ' + p.id + ' não encontrada.');
  var dataExec = p.dataExecucao || hojeIso_();
  setCelula_(sh, achado.linha, achado.headers, 'status', 'concluído');
  setCelula_(sh, achado.linha, achado.headers, 'situacao', 'Concluído');
  setCelula_(sh, achado.linha, achado.headers, 'resp', p.responsavel || '');
  setCelula_(sh, achado.linha, achado.headers, 'dataExecucao', dataExec);
  setCelula_(sh, achado.linha, achado.headers, 'atualizadoEm', agoraIso_());
  if (p.horasRealizadas) setCelula_(sh, achado.linha, achado.headers, 'horas', Number(p.horasRealizadas));
  registrarLog_('concluir', p.id, p.responsavel, 'Concluída em ' + dataExec);
}

function acaoJustificar_(p) {
  var sh = getSheet_(SHEET_ATIVIDADES);
  var achado = encontrarLinhaPorId_(sh, p.id);
  if (!achado) throw new Error('Atividade ' + p.id + ' não encontrada.');
  setCelula_(sh, achado.linha, achado.headers, 'justificativa', p.justificativa || '');
  setCelula_(sh, achado.linha, achado.headers, 'resp', p.responsavel || '');
  setCelula_(sh, achado.linha, achado.headers, 'dataExecucao', p.dataExecucao || hojeIso_());
  setCelula_(sh, achado.linha, achado.headers, 'atualizadoEm', agoraIso_());
  registrarLog_('justificar', p.id, p.responsavel, p.justificativa || '');
}

function acaoNovaAtividade_(p) {
  var sh = getSheet_(SHEET_ATIVIDADES);
  var atividades = listarAtividades_();
  var novoId = proximoId_(atividades);
  var linha = [];
  var map = {
    id: novoId,
    desc: p.desc || '',
    local: p.local || '',
    ini: '',          // sem data => entra no backlog, como as demais linhas sem data
    fim: '',
    horas: Number(p.horas) || 0,
    situacao: 'A Programar',
    status: 'pendente',
    obs: p.obs || '',
    resp: p.responsavel || '',
    justificativa: '',
    origem: 'backlog_colaborador',
    dataExecucao: '',
    criadoEm: agoraIso_(),
    atualizadoEm: agoraIso_()
  };
  COLS.forEach(function (c) { linha.push(map[c]); });
  sh.appendRow(linha);
  registrarLog_('nova_atividade', novoId, p.responsavel, p.desc || '');
  return novoId;
}

function acaoAtividadeAdicional_(p) {
  var sh = getSheet_(SHEET_ATIVIDADES);
  var atividades = listarAtividades_();
  var novoId = proximoId_(atividades);
  var dataExec = p.dataExecucao || hojeIso_();
  var linha = [];
  var map = {
    id: novoId,
    desc: p.desc || '',
    local: p.local || '',
    ini: dataExec,     // já nasce com data = dia da execução (fora do planejamento original)
    fim: dataExec,
    horas: Number(p.horas) || 0,
    situacao: 'Concluído',
    status: 'concluído',
    obs: p.obs || '',
    resp: p.responsavel || '',
    justificativa: '',
    origem: 'adicional',
    dataExecucao: dataExec,
    criadoEm: agoraIso_(),
    atualizadoEm: agoraIso_()
  };
  COLS.forEach(function (c) { linha.push(map[c]); });
  sh.appendRow(linha);
  registrarLog_('atividade_adicional', novoId, p.responsavel, p.desc || '');
  return novoId;
}

// ---------- roteamento HTTP ----------

function jsonOut_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function doGet(e) {
  try {
    var acao = (e.parameter.action || 'listar');
    if (acao === 'listar') {
      return jsonOut_({ ok: true, acts: listarAtividades_() });
    }
    return jsonOut_({ ok: false, erro: 'Ação GET desconhecida: ' + acao });
  } catch (err) {
    return jsonOut_({ ok: false, erro: String(err) });
  }
}

// O painel manda o POST com o corpo em texto puro (não JSON no header
// Content-Type) de propósito: isso evita que o navegador precise de um
// preflight OPTIONS, que o Apps Script Web App não sabe responder. O
// conteúdo em si continua sendo um JSON normal, só o content-type
// declarado que é "text/plain".
function doPost(e) {
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(10000);
  } catch (err) {
    return jsonOut_({ ok: false, erro: 'Sistema ocupado, tente de novo em alguns segundos.' });
  }
  try {
    var p = JSON.parse(e.postData.contents);
    var acao = p.acao;
    var novoId;
    switch (acao) {
      case 'concluir':
        acaoConcluir_(p);
        return jsonOut_({ ok: true });
      case 'justificar':
        acaoJustificar_(p);
        return jsonOut_({ ok: true });
      case 'nova_atividade':
        novoId = acaoNovaAtividade_(p);
        return jsonOut_({ ok: true, id: novoId });
      case 'atividade_adicional':
        novoId = acaoAtividadeAdicional_(p);
        return jsonOut_({ ok: true, id: novoId });
      default:
        return jsonOut_({ ok: false, erro: 'Ação POST desconhecida: ' + acao });
    }
  } catch (err) {
    return jsonOut_({ ok: false, erro: String(err) });
  } finally {
    lock.releaseLock();
  }
}

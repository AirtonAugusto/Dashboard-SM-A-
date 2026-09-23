// Endereço da API (backend/). Ajuste para o domínio real quando publicar.
const API_BASE = "http://localhost:8000";

function getToken() {
  return sessionStorage.getItem("sma_token");
}

function getRole() {
  return sessionStorage.getItem("sma_role");
}

async function apiFetch(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const resp = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (resp.status === 401) {
    sessionStorage.clear();
    window.location.href = "login.html";
    return null;
  }
  if (!resp.ok) {
    const erro = await resp.json().catch(() => ({}));
    throw new Error(erro.detail || `Erro ${resp.status}`);
  }
  return resp.status === 204 ? null : resp.json();
}

// Chame no topo de cada página protegida. Isto é só conveniência de UX
// (esconder telas de quem não devia vê-las) — a permissão de verdade é
// sempre reforçada pela API, nunca só aqui no frontend.
function exigirLogin(roleEsperada) {
  const role = getRole();
  if (!getToken() || !role) {
    window.location.href = "login.html";
    return;
  }
  if (roleEsperada && role !== roleEsperada) {
    window.location.href = role === "GESTOR" ? "gestor.html" : "colaborador.html";
  }
}

function sair() {
  sessionStorage.clear();
  window.location.href = "login.html";
}

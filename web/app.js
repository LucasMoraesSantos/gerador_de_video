const API_BASE = '/api';

async function api(url, method = 'GET', body) {
  const resp = await fetch(`${API_BASE}${url}`, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!resp.ok) throw new Error(await resp.text());
  return resp.json();
}

function formToJson(form) {
  const data = Object.fromEntries(new FormData(form).entries());
  for (const k of Object.keys(data)) {
    if (data[k] !== '' && !isNaN(data[k])) data[k] = Number(data[k]);
  }
  return data;
}

async function refreshChannels() {
  const rows = await api('/channels');
  document.getElementById('channels').textContent = JSON.stringify(rows, null, 2);
}
async function refreshScripts() {
  const rows = await api('/scripts');
  document.getElementById('scripts').textContent = JSON.stringify(rows, null, 2);
}
async function refreshPublish() {
  const rows = await api('/publish-jobs');
  document.getElementById('publish').textContent = JSON.stringify(rows, null, 2);
}

document.getElementById('channelForm').onsubmit = async (e) => {
  e.preventDefault();
  await api('/channels', 'POST', formToJson(e.target));
  await refreshChannels();
};

document.getElementById('analyzeForm').onsubmit = async (e) => {
  e.preventDefault();
  await api('/analyze', 'POST', formToJson(e.target));
  alert('Análise concluída.');
};

document.getElementById('rankingForm').onsubmit = async (e) => {
  e.preventDefault();
  const { niche } = formToJson(e.target);
  const rows = await api(`/ranking/${encodeURIComponent(niche)}`);
  document.getElementById('ranking').textContent = JSON.stringify(rows, null, 2);
};

document.getElementById('scriptForm').onsubmit = async (e) => {
  e.preventDefault();
  await api('/script', 'POST', formToJson(e.target));
  await refreshScripts();
};

document.getElementById('approveForm').onsubmit = async (e) => {
  e.preventDefault();
  await api('/approve', 'POST', formToJson(e.target));
  await refreshScripts();
};

document.getElementById('scheduleForm').onsubmit = async (e) => {
  e.preventDefault();
  const payload = formToJson(e.target);
  payload.scheduled_at = new Date(payload.scheduled_at).toISOString();
  await api('/schedule', 'POST', payload);
  await refreshPublish();
};

document.getElementById('refreshScripts').onclick = refreshScripts;
document.getElementById('refreshPublish').onclick = refreshPublish;

refreshChannels();
refreshScripts();
refreshPublish();

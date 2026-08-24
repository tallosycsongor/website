const $ = (selector) => document.querySelector(selector);
const escapeHtml = (value) => String(value).replace(/[&<>'"]/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));

async function api(path, options = {}) {
  const response = await fetch(path, {headers: {'Content-Type': 'application/json'}, ...options});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Ismeretlen hiba történt.');
  return data;
}

function message(text, error = false) {
  $('#message').textContent = text;
  $('#message').className = error ? 'error' : '';
}

async function init() {
  try {
    const {config} = await api('/api/status');
    $('#root').value = config.root || '';
    await history();
  } catch (error) { message(error.message, true); }
}

$('#save').addEventListener('click', async () => {
  try {
    const {config} = await api('/api/config', {method: 'POST', body: JSON.stringify({root: $('#root').value})});
    $('#root').value = config.root;
    message('A kezelt mappa mentve. Most elindíthatod az átvizsgálást.');
  } catch (error) { message(error.message, true); }
});

$('#scan').addEventListener('click', scan);
async function scan() {
  const button = $('#scan'); button.disabled = true; message('Átvizsgálás folyamatban…');
  try {
    const {files} = await api('/api/scan');
    const suggestions = files.filter(file => file.needsChange);
    $('#docCount').textContent = files.filter(file => file.kind === 'document').length;
    $('#imageCount').textContent = files.filter(file => file.kind === 'image').length;
    $('#duplicateCount').textContent = files.filter(file => file.duplicateOf).length;
    $('#suggestionCount').textContent = suggestions.length;
    $('#files').innerHTML = suggestions.length ? suggestions.map(fileCard).join('') : '<div class="empty">Nincs alkalmazandó rendszerezési javaslat.</div>';
    message(`${files.length} támogatott fájl átvizsgálva. Semmi nem változott meg.`);
  } catch (error) { message(error.message, true); }
  finally { button.disabled = false; }
}

function fileCard(file) {
  return `<article class="file"><div><span class="type">${file.kind === 'image' ? 'KÉP' : escapeHtml(file.category.toUpperCase())}</span><h3>${escapeHtml(file.name)}</h3><div class="path">${escapeHtml(file.path)}</div>${file.duplicateOf ? `<div class="duplicate">Lehetséges másolat: ${escapeHtml(file.duplicateOf)}</div>` : ''}</div><div><div class="arrow">Javasolt hely ↘</div><h3>${escapeHtml(file.suggestedPath)}</h3><div class="path">Az eredeti tartalom változatlan marad.</div></div><button class="apply" data-source="${escapeHtml(file.path)}" data-target="${escapeHtml(file.suggestedPath)}">Alkalmazás</button></article>`;
}

$('#files').addEventListener('click', async event => {
  const button = event.target.closest('.apply'); if (!button) return;
  button.disabled = true;
  try {
    await api('/api/apply', {method: 'POST', body: JSON.stringify({source: button.dataset.source, target: button.dataset.target})});
    button.closest('.file').remove();
    $('#suggestionCount').textContent = Math.max(0, Number($('#suggestionCount').textContent) - 1);
    message('A javaslat alkalmazva. Az Előzmények lapról visszavonható.'); await history();
  } catch (error) { button.disabled = false; message(error.message, true); }
});

async function history() {
  const {operations} = await api('/api/history');
  $('#operations').innerHTML = operations.length ? operations.map(op => `<article class="file"><div><span class="type">${op.status === 'applied' ? 'ALKALMAZVA' : 'VISSZAÁLLÍTVA'}</span><h3>${escapeHtml(op.original_path)}</h3><div class="path">${escapeHtml(op.created_at)}</div></div><div><div class="arrow">${op.status === 'applied' ? 'Áthelyezve ide ↘' : 'Korábbi cél'}</div><h3>${escapeHtml(op.current_path)}</h3></div><div class="history-actions">${op.status === 'applied' ? `<button class="undo" data-id="${op.id}">Visszavonás</button>` : '<span class="undone">Visszavonva</span>'}</div></article>`).join('') : '<div class="empty">Még nincs végrehajtott művelet.</div>';
}

$('#operations').addEventListener('click', async event => {
  const button = event.target.closest('.undo'); if (!button) return;
  button.disabled = true;
  try { await api('/api/undo', {method: 'POST', body: JSON.stringify({id: button.dataset.id})}); message('Az eredeti fájlnév és hely visszaállítva.'); await history(); }
  catch (error) { button.disabled = false; message(error.message, true); }
});

document.querySelectorAll('.tab').forEach(tab => tab.addEventListener('click', () => {
  document.querySelectorAll('.tab,.view').forEach(item => item.classList.remove('active'));
  tab.classList.add('active'); $(`#${tab.dataset.view}`).classList.add('active');
}));

init();

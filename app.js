const tabs = document.querySelectorAll('.tab');
const panes = {
  current: document.getElementById('tab-current'),
  project: document.getElementById('tab-project'),
  mission: document.getElementById('tab-mission'),
};

for (const t of tabs) {
  t.addEventListener('click', () => {
    const key = t.dataset.tab;
    tabs.forEach(x => {
      x.classList.toggle('active', x === t);
      x.setAttribute('aria-selected', x === t ? 'true' : 'false');
    });
    Object.entries(panes).forEach(([k, el]) => {
      const active = k === key;
      if (!el) return;
      el.classList.toggle('active', active);
      el.setAttribute('aria-hidden', active ? 'false' : 'true');
    });
  });
}

// Todo checkbox persistence (browser localStorage)
const STORAGE_KEY = 'commandDeck.todoState.v1';
let todoState = {};
try {
  todoState = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
} catch {
  todoState = {};
}

document.querySelectorAll('.todo-check').forEach((cb) => {
  const id = cb.dataset.todoId;
  if (!id) return;
  if (Object.prototype.hasOwnProperty.call(todoState, id)) {
    cb.checked = !!todoState[id];
  }
  cb.addEventListener('change', () => {
    todoState[id] = cb.checked;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(todoState));
  });
});

document.getElementById('demoBtn')?.addEventListener('click', () => {
  const out = document.getElementById('demoOut');
  if (!out) return;
  out.textContent = '⚠️ Alert simulated: Discord listener latency exceeded 30s. Recommendation: restart gateway + check CPU top processes.';
  out.style.color = '#f5b82e';
});

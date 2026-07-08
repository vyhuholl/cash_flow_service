// Home page: load the filtered records list, render the table, paginate, and
// wire per-row edit/delete. All data comes from the JSON API via window.api.
(function () {
  'use strict';

  const filters = document.getElementById('filters');
  const body = document.getElementById('records-body');
  const countEl = document.getElementById('records-count');
  const prevBtn = document.getElementById('prev-page');
  const nextBtn = document.getElementById('next-page');
  const FILTER_NAMES = [
    'date_from',
    'date_to',
    'status',
    'type',
    'category',
    'subcategory',
  ];

  let prevUrl = null;
  let nextUrl = null;

  function field(name) {
    return filters.querySelector('[name="' + name + '"]');
  }

  function cell(text, className) {
    const td = document.createElement('td');
    td.textContent = text === null || text === undefined ? '' : String(text);
    if (className) {
      td.className = className;
    }
    return td;
  }

  function fillSelect(name, items) {
    const select = field(name);
    items.forEach((item) => {
      const option = document.createElement('option');
      option.value = item.id;
      option.textContent = item.name;
      select.appendChild(option);
    });
  }

  async function loadFilterOptions() {
    const [statuses, types, categories, subcategories] = await Promise.all([
      api.get('/api/statuses/'),
      api.get('/api/types/'),
      api.get('/api/categories/'),
      api.get('/api/subcategories/'),
    ]);
    fillSelect('status', statuses.results);
    fillSelect('type', types.results);
    fillSelect('category', categories.results);
    fillSelect('subcategory', subcategories.results);
  }

  function currentUrl() {
    const params = new URLSearchParams();
    FILTER_NAMES.forEach((name) => {
      const value = field(name).value;
      if (value) {
        params.append(name, value);
      }
    });
    const query = params.toString();
    return '/api/records/' + (query ? '?' + query : '');
  }

  function renderRows(records) {
    body.replaceChildren();
    if (records.length === 0) {
      const tr = document.createElement('tr');
      const td = cell('Нет записей', 'text-center text-muted');
      td.colSpan = 8;
      tr.appendChild(td);
      body.appendChild(tr);
      return;
    }
    records.forEach((record) => {
      const tr = document.createElement('tr');
      tr.appendChild(cell(record.created_date));
      tr.appendChild(cell(record.status_name || '—'));
      tr.appendChild(cell(record.type_name));
      tr.appendChild(cell(record.category_name));
      tr.appendChild(cell(record.subcategory_name));
      tr.appendChild(cell(record.amount, 'text-end'));
      tr.appendChild(cell(record.comment));

      const actions = document.createElement('td');
      actions.className = 'text-nowrap';
      const edit = document.createElement('a');
      edit.className = 'btn btn-sm btn-outline-secondary me-1';
      edit.href = '/records/' + record.id + '/edit';
      edit.textContent = 'Изменить';
      const del = document.createElement('button');
      del.type = 'button';
      del.className = 'btn btn-sm btn-outline-danger';
      del.textContent = 'Удалить';
      del.addEventListener('click', () => deleteRecord(record));
      actions.append(edit, del);
      tr.appendChild(actions);
      body.appendChild(tr);
    });
  }

  async function load(url) {
    try {
      const data = await api.get(url || currentUrl());
      renderRows(data.results);
      prevUrl = data.previous;
      nextUrl = data.next;
      prevBtn.disabled = !prevUrl;
      nextBtn.disabled = !nextUrl;
      countEl.textContent = 'Всего записей: ' + data.count;
    } catch (err) {
      api.showAlert('Не удалось загрузить записи.');
    }
  }

  async function deleteRecord(record) {
    const label = record.created_date + ' — ' + record.amount + ' ₽';
    if (!window.confirm('Удалить запись «' + label + '»?')) {
      return;
    }
    try {
      await api.del('/api/records/' + record.id + '/');
      load();
    } catch (err) {
      api.showAlert('Не удалось удалить запись.');
    }
  }

  filters.addEventListener('submit', (event) => {
    event.preventDefault();
    load();
  });
  document.getElementById('clear-filters').addEventListener('click', () => {
    filters.reset();
    load();
  });
  prevBtn.addEventListener('click', () => {
    if (prevUrl) {
      load(prevUrl);
    }
  });
  nextBtn.addEventListener('click', () => {
    if (nextUrl) {
      load(nextUrl);
    }
  });

  loadFilterOptions().catch(() =>
    api.showAlert('Не удалось загрузить справочники для фильтров.')
  );
  load();
})();

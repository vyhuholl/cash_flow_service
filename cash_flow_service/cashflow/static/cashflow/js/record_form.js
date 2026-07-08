// Record create/edit form: cascading Type→Category→Subcategory selects,
// edit-mode prefill, client-side validation mirroring the server rules, and
// submit with inline mapping of DRF field errors / 409 conflicts.
(function () {
  'use strict';

  const form = document.getElementById('record-form');
  const config = JSON.parse(
    document.getElementById('form-config').textContent
  );
  const recordId = config.recordId;

  const statusSel = form.querySelector('[name="status"]');
  const typeSel = form.querySelector('[name="type"]');
  const catSel = form.querySelector('[name="category"]');
  const subSel = form.querySelector('[name="subcategory"]');
  const amountInput = form.querySelector('[name="amount"]');

  // Monotonic tokens so a slow response for an old parent value can't clobber
  // the options for the parent the user has since selected.
  let catToken = 0;
  let subToken = 0;

  function setOptions(select, items, placeholder) {
    select.replaceChildren();
    const blank = document.createElement('option');
    blank.value = '';
    blank.textContent = placeholder;
    select.appendChild(blank);
    items.forEach((item) => {
      const option = document.createElement('option');
      option.value = item.id;
      option.textContent = item.name;
      select.appendChild(option);
    });
  }

  async function loadCategories(typeId, selected) {
    const token = ++catToken;
    if (!typeId) {
      setOptions(catSel, [], '—');
      catSel.disabled = true;
      return;
    }
    const data = await api.get('/api/categories/?type=' + typeId);
    if (token !== catToken) {
      return; // a newer type was selected while this was in flight
    }
    setOptions(catSel, data.results, '— выберите —');
    catSel.disabled = false;
    if (selected) {
      catSel.value = String(selected);
    }
  }

  async function loadSubcategories(categoryId, selected) {
    const token = ++subToken;
    if (!categoryId) {
      setOptions(subSel, [], '—');
      subSel.disabled = true;
      return;
    }
    const data = await api.get('/api/subcategories/?category=' + categoryId);
    if (token !== subToken) {
      return;
    }
    setOptions(subSel, data.results, '— выберите —');
    subSel.disabled = false;
    if (selected) {
      subSel.value = String(selected);
    }
  }

  typeSel.addEventListener('change', async () => {
    // Parent changed: clear both descendants, then repopulate categories.
    catSel.value = '';
    subSel.value = '';
    await loadSubcategories('', null);
    await loadCategories(typeSel.value, null);
  });
  catSel.addEventListener('change', async () => {
    subSel.value = '';
    await loadSubcategories(catSel.value, null);
  });

  function setError(name, message) {
    const el = form.querySelector('[name="' + name + '"]');
    el.classList.add('is-invalid');
    const feedback = el.parentElement.querySelector('.invalid-feedback');
    if (feedback) {
      feedback.textContent = message;
    }
  }

  function clearErrors() {
    form
      .querySelectorAll('.is-invalid')
      .forEach((el) => el.classList.remove('is-invalid'));
    form
      .querySelectorAll('.invalid-feedback')
      .forEach((el) => (el.textContent = ''));
  }

  // The cascade guarantees category∈type and subcategory∈category (you can
  // only pick from the fetched options), so the client checks reduce to
  // required fields + a positive amount. The server stays the source of truth.
  function validate() {
    clearErrors();
    let ok = true;
    if (!typeSel.value) {
      setError('type', 'Выберите тип.');
      ok = false;
    }
    if (!catSel.value) {
      setError('category', 'Выберите категорию.');
      ok = false;
    }
    if (!subSel.value) {
      setError('subcategory', 'Выберите подкатегорию.');
      ok = false;
    }
    const amount = amountInput.value;
    if (!amount) {
      setError('amount', 'Укажите сумму.');
      ok = false;
    } else if (Number(amount) <= 0) {
      setError('amount', 'Сумма должна быть больше нуля.');
      ok = false;
    }
    return ok;
  }

  function buildPayload() {
    const payload = {
      type: Number(typeSel.value),
      category: Number(catSel.value),
      subcategory: Number(subSel.value),
      amount: amountInput.value,
      comment: form.querySelector('[name="comment"]').value,
      status: statusSel.value ? Number(statusSel.value) : null,
    };
    const date = form.querySelector('[name="created_date"]').value;
    if (date) {
      payload.created_date = date;
    }
    return payload;
  }

  function applyServerErrors(data) {
    if (!data || typeof data !== 'object') {
      api.showAlert('Не удалось сохранить запись.');
      return;
    }
    const nonField = [];
    Object.keys(data).forEach((fieldName) => {
      const value = data[fieldName];
      const message = Array.isArray(value) ? value.join(' ') : String(value);
      if (form.querySelector('[name="' + fieldName + '"]')) {
        setError(fieldName, message);
      } else {
        nonField.push(message);
      }
    });
    if (nonField.length) {
      api.showAlert(nonField.join(' '));
    }
  }

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!validate()) {
      return;
    }
    const payload = buildPayload();
    try {
      if (recordId) {
        await api.patch('/api/records/' + recordId + '/', payload);
      } else {
        await api.post('/api/records/', payload);
      }
      window.location.href = '/';
    } catch (err) {
      if (err.status === 400 || err.status === 409) {
        applyServerErrors(err.data);
      } else {
        api.showAlert('Не удалось сохранить запись.');
      }
    }
  });

  async function init() {
    const [statuses, types] = await Promise.all([
      api.get('/api/statuses/'),
      api.get('/api/types/'),
    ]);
    setOptions(statusSel, statuses.results, '— не выбран —');
    setOptions(typeSel, types.results, '— выберите —');

    if (!recordId) {
      return;
    }
    document.getElementById('form-title').textContent = 'Изменить запись';
    const record = await api.get('/api/records/' + recordId + '/');
    form.querySelector('[name="created_date"]').value =
      record.created_date || '';
    statusSel.value = record.status ? String(record.status) : '';
    amountInput.value = record.amount;
    form.querySelector('[name="comment"]').value = record.comment || '';
    typeSel.value = String(record.type);
    await loadCategories(record.type, record.category);
    await loadSubcategories(record.category, record.subcategory);
  }

  init().catch(() => api.showAlert('Не удалось загрузить форму записи.'));
})();

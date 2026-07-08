// Reference management page: one CRUD controller per dictionary section.
// Categories and subcategories carry a parent selector (type / category).
// Blocked deletions (HTTP 409) surface as a dismissible alert.
(function () {
  'use strict';

  function formatErrors(data) {
    if (!data) {
      return 'Не удалось сохранить запись.';
    }
    if (typeof data === 'string') {
      return data;
    }
    const messages = [];
    Object.keys(data).forEach((key) => {
      const value = data[key];
      messages.push(Array.isArray(value) ? value.join(' ') : String(value));
    });
    return messages.join(' ');
  }

  class DictSection {
    constructor(el) {
      this.name = el.dataset.dict; // e.g. 'statuses'
      this.endpoint = '/api/' + this.name + '/';
      this.parentField = el.dataset.parent || null; // 'type' | 'category'
      this.parentEndpoint = el.dataset.parentEndpoint || null;
      this.list = el.querySelector('.dict-list');
      this.form = el.querySelector('.dict-form');
      this.parentSelect = el.querySelector('.dict-parent');
      this.cancelBtn = el.querySelector('.dict-cancel');
      // `form.name` / `form.id` resolve to the form's own attributes, not the
      // inputs — select the fields explicitly.
      this.idInput = this.form.querySelector('[name="id"]');
      this.nameInput = this.form.querySelector('[name="name"]');

      this.form.addEventListener('submit', (event) => this.onSubmit(event));
      if (this.cancelBtn) {
        this.cancelBtn.addEventListener('click', () => this.resetForm());
      }
    }

    async init() {
      if (this.parentEndpoint) {
        await this.loadParents();
      }
      await this.reload();
    }

    async loadParents() {
      const data = await api.get('/api/' + this.parentEndpoint + '/');
      data.results.forEach((item) => {
        const option = document.createElement('option');
        option.value = item.id;
        option.textContent = item.name;
        this.parentSelect.appendChild(option);
      });
    }

    async reload() {
      const data = await api.get(this.endpoint);
      this.render(data.results);
    }

    render(items) {
      this.list.replaceChildren();
      items.forEach((item) => {
        const tr = document.createElement('tr');

        const nameTd = document.createElement('td');
        nameTd.textContent = item.name;
        tr.appendChild(nameTd);

        if (this.parentField) {
          const parentTd = document.createElement('td');
          parentTd.className = 'text-muted';
          parentTd.textContent = item[this.parentField + '_name'] || '';
          tr.appendChild(parentTd);
        }

        const actionsTd = document.createElement('td');
        actionsTd.className = 'text-end text-nowrap';
        const edit = document.createElement('button');
        edit.type = 'button';
        edit.className = 'btn btn-sm btn-outline-primary me-1';
        edit.textContent = 'Изменить';
        edit.addEventListener('click', () => this.startEdit(item));
        const del = document.createElement('button');
        del.type = 'button';
        del.className = 'btn btn-sm btn-danger';
        del.textContent = 'Удалить';
        del.addEventListener('click', () => this.remove(item));
        actionsTd.append(edit, del);
        tr.appendChild(actionsTd);

        this.list.appendChild(tr);
      });
    }

    startEdit(item) {
      this.idInput.value = item.id;
      this.nameInput.value = item.name;
      if (this.parentField) {
        this.parentSelect.value = String(item[this.parentField]);
      }
      if (this.cancelBtn) {
        this.cancelBtn.classList.remove('d-none');
      }
      this.nameInput.focus();
    }

    resetForm() {
      this.form.reset();
      this.idInput.value = '';
      if (this.cancelBtn) {
        this.cancelBtn.classList.add('d-none');
      }
    }

    buildPayload() {
      const payload = { name: this.nameInput.value.trim() };
      if (this.parentField) {
        payload[this.parentField] = this.parentSelect.value
          ? Number(this.parentSelect.value)
          : null;
      }
      return payload;
    }

    async onSubmit(event) {
      event.preventDefault();
      const id = this.idInput.value;
      const payload = this.buildPayload();
      try {
        if (id) {
          await api.patch(this.endpoint + id + '/', payload);
        } else {
          await api.post(this.endpoint, payload);
        }
        this.resetForm();
        await this.reload();
      } catch (err) {
        if (err.status === 400) {
          api.showAlert(formatErrors(err.data));
        } else {
          api.showAlert('Не удалось сохранить запись справочника.');
        }
      }
    }

    async remove(item) {
      if (!window.confirm('Удалить «' + item.name + '»?')) {
        return;
      }
      try {
        await api.del(this.endpoint + item.id + '/');
        await this.reload();
      } catch (err) {
        if (err.status === 409) {
          const detail =
            err.data && err.data.detail
              ? err.data.detail
              : 'Запись используется и не может быть удалена.';
          api.showAlert(detail, 'warning');
        } else {
          api.showAlert('Не удалось удалить запись.');
        }
      }
    }
  }

  document.querySelectorAll('[data-dict]').forEach((el) => {
    const section = new DictSection(el);
    section
      .init()
      .catch(() => api.showAlert('Не удалось загрузить справочник.'));
  });
})();

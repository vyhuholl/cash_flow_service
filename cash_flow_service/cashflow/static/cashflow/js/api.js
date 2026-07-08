// Shared frontend helpers: a CSRF-aware fetch wrapper over the JSON API and a
// dismissible-alert renderer. Exposed as `window.api` for the per-page scripts.
(function () {
  'use strict';

  function getCookie(name) {
    const match = document.cookie.match(
      new RegExp('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)')
    );
    return match ? decodeURIComponent(match[2]) : null;
  }

  const SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS'];

  // Perform a request and return parsed JSON (or null for empty bodies).
  // On a non-2xx response, throw an Error carrying `.status` and `.data` so
  // callers can map DRF field errors / 409 conflicts back to the UI.
  async function request(method, url, body) {
    const options = { method: method, headers: {} };
    if (!SAFE_METHODS.includes(method)) {
      options.headers['X-CSRFToken'] = getCookie('csrftoken');
    }
    if (body !== undefined && body !== null) {
      options.headers['Content-Type'] = 'application/json';
      options.body = JSON.stringify(body);
    }
    const response = await fetch(url, options);
    const text = await response.text();
    let data = null;
    if (text) {
      try {
        data = JSON.parse(text);
      } catch (err) {
        data = text;
      }
    }
    if (!response.ok) {
      const error = new Error('Request failed with status ' + response.status);
      error.status = response.status;
      error.data = data;
      throw error;
    }
    return data;
  }

  function showAlert(message, kind) {
    const container = document.getElementById('alerts');
    if (!container) {
      return;
    }
    const alert = document.createElement('div');
    alert.className =
      'alert alert-' + (kind || 'danger') + ' alert-dismissible fade show';
    alert.setAttribute('role', 'alert');
    alert.textContent = message;
    const close = document.createElement('button');
    close.type = 'button';
    close.className = 'btn-close';
    close.setAttribute('data-bs-dismiss', 'alert');
    close.setAttribute('aria-label', 'Закрыть');
    alert.appendChild(close);
    container.appendChild(alert);
  }

  window.api = {
    getCookie: getCookie,
    get: (url) => request('GET', url),
    post: (url, body) => request('POST', url, body),
    put: (url, body) => request('PUT', url, body),
    patch: (url, body) => request('PATCH', url, body),
    del: (url) => request('DELETE', url),
    showAlert: showAlert,
  };
})();

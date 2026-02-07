frappe.pages['lce-dashboard'].on_page_load = function (wrapper) {
  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: 'LCE Dashboard',
    single_column: true,
  });

  const body = $(page.body);
  const container = $('<div class="lce-dashboard"></div>').appendTo(body);
  const content = $('<div class="lce-content"></div>').appendTo(container);
  $('<style>\n    .lce-dashboard { display: grid; gap: 16px; }\n    .lce-card { border: 1px solid #e5e5e5; border-radius: 6px; padding: 12px 16px; background: #fff; }\n    .lce-title { font-weight: 600; margin-bottom: 8px; }\n    .lce-row { display: flex; justify-content: space-between; padding: 4px 0; }\n    .lce-label { color: #666; }\n    .lce-value { font-weight: 500; }\n    .lce-pre { background: #f7f7f7; padding: 8px; border-radius: 4px; font-size: 12px; }\n  </style>').appendTo(body);

  const render = (payload) => {
    content.empty();

    if (!payload || payload.ok === false) {
      const msg = payload && payload.error ? payload.error : 'Unable to load status.';
      content.append(`<div class="text-muted">${frappe.utils.escape_html(msg)}</div>`);
      return;
    }

    const serviceRow = (label, svc) => {
      const ok = svc && svc.ok;
      const status = ok ? 'OK' : 'ERROR';
      const color = ok ? 'green' : 'red';
      return `
        <div class="lce-row">
          <div class="lce-label">${label}</div>
          <div class="lce-value" style="color:${color}">${status}</div>
        </div>
      `;
    };

    content.append(`
      <div class="lce-card">
        <div class="lce-title">Services</div>
        ${serviceRow('ERPNext', payload.services && payload.services.erp)}
        ${serviceRow('Zebra', payload.services && payload.services.zebra)}
        ${serviceRow('RFID', payload.services && payload.services.rfid)}
      </div>
    `);

    const tokenSet = payload.telegram && payload.telegram.token_set ? 'YES' : 'NO';
    content.append(`
      <div class="lce-card">
        <div class="lce-title">Telegram</div>
        <div class="lce-row">
          <div class="lce-label">Token Set</div>
          <div class="lce-value">${tokenSet}</div>
        </div>
      </div>
    `);

    content.append(`
      <div class="lce-card">
        <div class="lce-title">Config</div>
        <pre class="lce-pre">${frappe.utils.escape_html(JSON.stringify(payload.config || {}, null, 2))}</pre>
      </div>
    `);
  };

  const load = () => {
    frappe.call({
      method: 'titan_telegram.api.get_lce_status',
      callback: (r) => {
        render(r.message || r);
      },
      error: () => {
        render({ ok: false, error: 'Failed to call LCE status.' });
      },
    });
  };

  page.set_primary_action('Refresh', load);
  load();
};

frappe.pages['bot-health'].on_page_load = function (wrapper) {
  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: 'Bot Health',
    single_column: true,
  });

  const $container = $(wrapper).find('.layout-main-section');
  $container.html(`
    <div class="tg-health">
      <div class="tg-health-row">
        <div class="tg-card" data-key="enabled">
          <div class="label">Bot Status</div>
          <div class="value">-</div>
        </div>
        <div class="tg-card" data-key="token_set">
          <div class="label">Token</div>
          <div class="value">-</div>
        </div>
        <div class="tg-card" data-key="webhook_url">
          <div class="label">Webhook</div>
          <div class="value mono">-</div>
        </div>
      </div>

      <div class="tg-health-row">
        <div class="tg-card" data-key="active_sessions">
          <div class="label">Active Sessions</div>
          <div class="value">-</div>
        </div>
        <div class="tg-card" data-key="online_devices">
          <div class="label">Online Devices</div>
          <div class="value">-</div>
        </div>
        <div class="tg-card" data-key="error_count_24h">
          <div class="label">Errors (24h)</div>
          <div class="value">-</div>
        </div>
      </div>

      <div class="tg-health-row">
        <div class="tg-card" data-key="total_logs">
          <div class="label">Total Logs</div>
          <div class="value">-</div>
        </div>
        <div class="tg-card" data-key="last_log">
          <div class="label">Last Log</div>
          <div class="value">-</div>
        </div>
        <div class="tg-card" data-key="last_updated">
          <div class="label">Last Updated</div>
          <div class="value">-</div>
        </div>
      </div>
    </div>
  `);

  const style = document.createElement('style');
  style.textContent = `
    .tg-health { display: grid; gap: 16px; }
    .tg-health-row { display: grid; gap: 16px; grid-template-columns: repeat(3, minmax(0, 1fr)); }
    .tg-card { background: #fff; border: 1px solid #e3e3e3; border-radius: 10px; padding: 14px 16px; }
    .tg-card .label { font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.04em; }
    .tg-card .value { font-size: 18px; margin-top: 6px; }
    .tg-card .value.mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; font-size: 13px; }
    .tg-card.is-ok { border-color: #d1fae5; background: #ecfdf3; }
    .tg-card.is-warn { border-color: #fde68a; background: #fffbeb; }
    .tg-card.is-bad { border-color: #fecaca; background: #fef2f2; }
    @media (max-width: 900px) { .tg-health-row { grid-template-columns: 1fr; } }
  `;
  wrapper.appendChild(style);

  const setValue = (key, value) => {
    const $card = $container.find(`[data-key="${key}"]`);
    $card.find('.value').text(value ?? '-');
  };

  const setStatus = (key, status) => {
    const $card = $container.find(`[data-key="${key}"]`);
    $card.removeClass('is-ok is-warn is-bad');
    if (status === 'ok') $card.addClass('is-ok');
    if (status === 'warn') $card.addClass('is-warn');
    if (status === 'bad') $card.addClass('is-bad');
  };

  const refresh = () => {
    frappe.call({
      method: 'titan_telegram.api.get_bot_health',
      callback: (r) => {
        const data = r.message || {};
        if (!data.ok) {
          setValue('enabled', 'Error');
          setStatus('enabled', 'bad');
          return;
        }

        setValue('enabled', data.enabled ? 'Enabled' : 'Disabled');
        setStatus('enabled', data.enabled ? 'ok' : 'warn');

        setValue('token_set', data.token_set ? 'Set' : 'Missing');
        setStatus('token_set', data.token_set ? 'ok' : 'bad');

        setValue('webhook_url', data.webhook_url || 'Not set');
        setStatus('webhook_url', data.webhook_url ? 'ok' : 'warn');

        setValue('active_sessions', data.active_sessions ?? 0);
        setValue('online_devices', `${data.online_devices ?? 0} / ${data.total_devices ?? 0}`);
        setValue('error_count_24h', data.error_count_24h ?? 0);
        setValue('total_logs', data.total_logs ?? 0);

        const lastLog = data.last_log ? frappe.datetime.str_to_user(data.last_log) : 'No logs';
        setValue('last_log', lastLog);

        setValue('last_updated', frappe.datetime.now_time());
      },
    });
  };

  page.set_primary_action('Refresh', refresh);
  refresh();

  const interval = setInterval(refresh, 10000);
  $(wrapper).on('remove', () => clearInterval(interval));
};

frappe.ui.form.on('LCE Settings', {
  refresh(frm) {
    const markClean = () => {
      frm.doc.__unsaved = 0;
      if (frm.toolbar && frm.toolbar.refresh) {
        frm.toolbar.refresh();
      }
    };

    const copyText = async (text) => {
      try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          await navigator.clipboard.writeText(text);
          return true;
        }
      } catch (err) {
        // fallback below
      }
      try {
        const ta = document.createElement('textarea');
        ta.value = text;
        ta.setAttribute('readonly', '');
        ta.style.position = 'fixed';
        ta.style.top = '-1000px';
        ta.style.left = '-1000px';
        document.body.appendChild(ta);
        ta.select();
        const ok = document.execCommand('copy');
        document.body.removeChild(ta);
        return ok;
      } catch (err) {
        return false;
      }
    };

    const copyValue = async (label, value) => {
      if (!value) {
        frappe.msgprint(`${label} is empty.`);
        return;
      }
      const ok = await copyText(String(value));
      if (ok) {
        frappe.show_alert({ message: `${label} copied`, indicator: 'green' });
      } else {
        frappe.msgprint(`Unable to copy ${label}.`);
      }
    };

    const bindCopy = (fieldname, label, getter) => {
      const field = frm.get_field(fieldname);
      if (!field || !field.$wrapper) return;
      field.$wrapper.attr('title', 'Click to copy').css('cursor', 'copy');
      const handler = async (event) => {
        if (event) {
          event.stopPropagation();
        }
        let value = getter ? getter() : frm.doc[fieldname];
        const isMasked = (val) =>
          typeof val === 'string' && val.trim() !== '' && /^[*]+$/.test(val);
        if ((!value || isMasked(value)) && (field.df.fieldtype === 'Password')) {
          if (!frm.__lce_secret_cache) {
            const resp = await frappe.call({ method: 'titan_telegram.api.get_lce_secrets' });
            const msg = resp.message || {};
            if (!msg.ok) {
              frappe.msgprint(msg.error || 'Unable to fetch secrets.');
              return;
            }
            frm.__lce_secret_cache = msg;
          }
          const cache = frm.__lce_secret_cache || {};
          if (fieldname === 'erp_api_secret') value = cache.api_secret;
          if (fieldname === 'erp_api_token') value = cache.api_token;
        }
        copyValue(label, value);
      };
      field.$wrapper.off('click.lcecopy').on('click.lcecopy', handler);
      const inputs = field.$wrapper.find('input, textarea');
      inputs.off('click.lcecopy').on('click.lcecopy', handler);
      if (field.$input) {
        field.$input.off('click.lcecopy').on('click.lcecopy', handler);
        field.$input.css('cursor', 'copy');
      }
    };

    const cached = frm.__lce_token_cache || {};
    bindCopy('lce_url', 'LCE URL');
    bindCopy('erp_url', 'ERP URL');
    bindCopy('erp_api_key', 'API Key', () => cached.api_key || frm.doc.erp_api_key);
    bindCopy('erp_api_secret', 'API Secret', () => cached.api_secret || frm.doc.erp_api_secret);
    bindCopy('erp_api_token', 'API Token', () => cached.token || frm.doc.erp_api_token);

    if (frm.doc.erp_api_key && frm.doc.erp_api_key.includes(':')) {
      frappe.call({
        method: 'titan_telegram.api.get_lce_secrets',
        callback: (r) => {
          const msg = r.message || {};
          if (!msg.ok) return;
          frm.set_value('erp_api_key', msg.api_key || '');
          frm.set_value('erp_api_secret', msg.api_secret || '');
          if (msg.api_token) {
            frm.set_value('erp_api_token', msg.api_token);
          }
          markClean();
        }
      });
    }

    if (!frm.doc.erp_url) {
      const baseUrl = (frappe.urllib && frappe.urllib.get_base_url)
        ? frappe.urllib.get_base_url()
        : window.location.origin;
      frm.set_value('erp_url', baseUrl);
    }

    if (!frm.doc.lce_url) {
      frappe.call({
        method: 'titan_telegram.api.detect_lce_url',
        callback: (r) => {
          const msg = r.message || {};
          if (msg.ok && msg.lce_url) {
            frm.set_value('lce_url', msg.lce_url);
          }
        }
      });
    }
    if (!frm.doc.erp_user) {
      frm.set_value('erp_user', frappe.session.user);
    }

    frm.add_custom_button('Generate API Token', () => {
      frappe.call({
        method: 'titan_telegram.api.generate_current_user_token',
        callback: (r) => {
          const msg = r.message || {};
          if (!msg.ok) {
            frappe.msgprint(msg.error || 'Token yaratishda xato.');
            return;
          }
          frm.__lce_token_cache = msg;
          if (!frm.doc.lce_url) {
            frappe.call({
              method: 'titan_telegram.api.detect_lce_url',
              callback: (d) => {
                const m = d.message || {};
                if (m.ok && m.lce_url) {
                  frm.set_value('lce_url', m.lce_url);
                }
              }
            });
          }
          frm.set_value('erp_url', msg.erp_url);
          frm.set_value('erp_user', msg.user);
          frm.set_value('erp_api_key', msg.api_key);
          frm.set_value('erp_api_secret', msg.api_secret);
          frm.set_value('erp_api_token', msg.token);
          if (msg.modified) {
            frm.doc.modified = msg.modified;
          }
          if (msg.modified_by) {
            frm.doc.modified_by = msg.modified_by;
          }
          markClean();
          frappe.msgprint('API token yaratildi. Endi LCE Settings ichidan ko‘rishingiz mumkin.');
        },
        error: () => {
          frappe.msgprint('Token yaratishda xato.');
        }
      });
    });

    frm.add_custom_button('Send To LCE', () => {
      frappe.call({
        method: 'titan_telegram.api.push_erp_config_to_lce',
        callback: (r) => {
          const msg = r.message || {};
          if (!msg.ok) {
            frappe.msgprint(msg.error || 'LCE ga yuborishda xato.');
            return;
          }
          frappe.msgprint('ERP konfiguratsiya LCE ga yuborildi.');
        },
        error: () => {
          frappe.msgprint('LCE ga yuborishda xato.');
        }
      });
    });
  }
});

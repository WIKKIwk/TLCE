frappe.query_reports["Telegram Log Report"] = {
  filters: [
    {
      fieldname: "device_id",
      label: __("Device ID"),
      fieldtype: "Data",
    },
    {
      fieldname: "status",
      label: __("Status"),
      fieldtype: "Select",
      options: "\nSuccess\nError\nPending",
    },
    {
      fieldname: "action",
      label: __("Action"),
      fieldtype: "Select",
      options: "\nstart_batch\nstop_batch\nselect_product\nweight_record\nprint_label\nerror",
    },
    {
      fieldname: "from_date",
      label: __("From Date"),
      fieldtype: "Date",
    },
    {
      fieldname: "to_date",
      label: __("To Date"),
      fieldtype: "Date",
    },
  ],
};

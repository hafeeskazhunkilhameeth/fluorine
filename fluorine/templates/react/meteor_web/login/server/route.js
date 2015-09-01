if (typeof frappe === 'undefined')
    frappe = {};

var frappe_url = Meteor.settings.frappe_url;
if (frappe_url === undefined )
  frappe_url = Meteor.absoluteUrl();

frappe.url = frappe_url;

console.log("in meteor server side frappe_url ", frappe_url);

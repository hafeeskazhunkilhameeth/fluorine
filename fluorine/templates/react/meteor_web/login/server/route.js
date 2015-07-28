if (typeof frappe === 'undefined')
    frappe = {};

var frappe_url = Meteor.settings.frappe_url;
if (frappe_url === undefined )
  frappe_url = "http://localhost:8000";

frappe.url = frappe_url;

console.log("in server side frappe_url ", frappe_url);

Router.route('/desk', {where: 'server'}).get(function() {
  console.log("server router for desk");
  this.response.writeHead(302, {
    'Location': frappe_url +  "/desk" //+ this.params.search
  });
  this.response.end();
});

Router.route('/mdesk', {where: 'server'}).get(function() {
  console.log("server router for mdesk 2");
  this.response.writeHead(302, {
    'Location': frappe_url + "/mdesk" //+ this.params.search
  });
  this.response.end();
});
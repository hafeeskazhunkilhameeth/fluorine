if (typeof frappe === 'undefined')
    frappe = {};

var frappe_url = Meteor.settings.frappe_url;
if (frappe_url === undefined )
  frappe_url = "http://localhost";

frappe.url = frappe_url;

console.log("in server side frappe_url ", frappe_url);

/*Router.route('/desk', {where: 'server'}).get(function() {
  console.log("server router for desk");
  this.response.writeHead(302, {
    'Location': frappe_url +  "/desk" //+ this.params.search
  });
  this.response.end();
});*/

//Router.route('/mdesk', {where: 'server'}).get(function() {
  //var req = this.request;
  //var code = this.params.query.code;
  //var user_id = this.request.query.user_id;
  //code = code? "?code=" + code : "";
  //user_id = user_id? "&user_id=" + user_id : "";
  //console.log("server router for mdesk 1 ", code);
  //console.log("server router for mdesk 2 ", user_id);*/
  //this.response.writeHead(302, {
  //  'Location': frappe_url + "/mdesk" //+ code + user_id//+ this.params.search
  //});
  //this.response.end();
//});
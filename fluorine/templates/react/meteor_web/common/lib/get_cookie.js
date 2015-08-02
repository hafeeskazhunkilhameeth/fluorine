if (typeof frappe === 'undefined')
	frappe = {};

frappe.get_cookie = function(c, cookie) {
    var clist;
    if (Meteor.isClient)
    	clist = (document.cookie + '').split(';');
    else
    	clist = (cookie + '').split(';');

    var cookies = {};
    for (var i = 0; i < clist.length; i++) {
        var tmp = clist[i].split('=');
        //cookies[strip(tmp[0])] = strip($.trim(tmp.slice(1).join("=")), "\"");
        cookies[strip(tmp[0])] = strip(tmp.slice(1).join("=").trim(), "\"");
    }
    return cookies[c];
}

if (!String.prototype.trim) {
  String.prototype.trim = function () {
    return this.replace(/^[\s\uFEFF\xA0]+|[\s\uFEFF\xA0]+$/g, '');
  };
}
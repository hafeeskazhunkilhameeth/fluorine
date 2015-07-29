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
        cookies[strip(tmp[0])] = strip($.trim(tmp.slice(1).join("=")), "\"");
    }
    return cookies[c];
}
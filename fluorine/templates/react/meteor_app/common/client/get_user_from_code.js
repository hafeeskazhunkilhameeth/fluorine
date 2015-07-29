
var cookies = ["user_id=%(user_id)s;", "sid=%(sid)s;", "system_user=%(system_user)s;", "full_name=%(full_name)s;", "user_image=%(user_image)s;"];

get_user_from_code = function(){

	//var hash = document.location.hash;
	var cookie = frappe.urllib.get_arg("code");
	console.log("in my redirect hash ", cookie);

	set_cookie({sid: cookie});
}

frappe.start_app = function() {
	get_user_from_code();
    if (!frappe.Application)
        return;
    frappe.assets.check();
    frappe.provide('frappe.app');
    $.extend(frappe.app, new frappe.Application());
}

var set_cookie = function(cookie){
    var c = repl(cookies[1], cookie);
    console.log("setting cookies ", c);
    document.cookie = c;
}
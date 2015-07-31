
if (typeof frappe === 'undefined')
	frappe = {};

frappe.call = function(options){

	var frappe_url = frappe.url;
	var args = options.args || {};
	var headers = options.headers || {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "Accept":"application/json"};
	var method = options.method || "/api/method/";

	if (options.cookie){
		headers["Cookie"] = options.cookie;
	}

	try{
		var url = clean_url(frappe_url + method + options.cmd);
		var result = HTTP.post(url, {params: args, headers: headers});
		return result;
	}catch(err){
		console.log("erro: ", err);
		return {error: err};
	}
}

frappe.login = function(username, password){
	var args = {usr: username, pwd: password};
	var headers = {"Accept":"application/json", "X-Forwarded-For":"192.168.1.100:8000"};
	var cmd = "login";
	var options = {cmd: cmd, args: args, headers: headers};
	return frappe.call(options);
}

frappe.register = function(email, full_name){
	var options = {args: {email: email, full_name: full_name}, cmd: "fluorine.utils.user.meteor_sign_up"};
	return frappe.call(options);
}

frappe.update_password = function(args){
	var options = {args: args, cmd: "frappe.core.doctype.user.user.update_password"};
	return frappe.call(options);
}

frappe.forgot_password = function(email){
	var options = {args: {user: email}, cmd: "fluorine.utils.user.meteor_reset_password"};
	return frappe.call(options);
}

frappe.logout = function(cookie){
	var options = {cmd: "logout"};
	options.headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "Accept":"application/json", "Cookie": cookie};
	return frappe.call(options);
}

//not used
frappe.translation = function(lang, cookies){
	var headers = {"Accept":"application/json", "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "Cookie": cookies};
	var args = {lang: lang};
	var cmd = "fluorine.utils.user.meteor_get_translation";
	var options = {cmd: cmd, args: args, headers: headers};
	return frappe.call(options);
}

var clean_url = function(url){
    return url.replace(/\/\//g, '/').replace(/http:\//, 'http://')
}
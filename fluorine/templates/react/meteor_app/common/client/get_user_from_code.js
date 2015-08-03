
/*var cookies = ["user_id=%(user_id)s;", "sid=%(sid)s;", "system_user=%(system_user)s;", "full_name=%(full_name)s;", "user_image=%(user_image)s;"];

get_user_from_code = function(){

	//var hash = document.location.hash;
	var cookie = frappe.urllib.get_arg("code");
	var user_id = frappe.urllib.get_arg("user_id");
	console.log("in my redirect hash ", cookie);

	set_cookie({sid: cookie}, 1);
	set_cookie({user_id: user_id}, 0);
}

frappe.start_app = function() {
	if (!frappe.Application)
		return;
	get_user_from_code();
	frappe.assets.check();
	frappe.provide('frappe.app');
	$.extend(frappe.app, new frappe.Application());
}

var set_cookie = function(cookie, pos){
	var c = repl(cookies[pos], cookie);
	console.log("setting cookies ", c);
	document.cookie = c;
}*/

$(document).on('app_ready', function(ev){
	console.log("frappe is ready!!!!");
	var sid = frappe.get_cookie("sid");
    if (is_valid_sid(sid)){
        /*Meteor.frappe_login(sid, function(result){
            console.log("Result from login into meteor 2 ", result);
        });*/
        Meteor.call("frappe_teste", function(error, res){
        	console.log("meteor call ", error, res);
        });
    }
});


/*
Meteor.frappe_login = function(sid, validate_callback) {
  //create a login request with admin: true, so our loginHandler can handle this request
  var loginRequest = {sid: sid};

  //send the login request methodName:
  Accounts.callLoginMethod({
    methodArguments: [loginRequest],
    validateResult: validate_callback
  });
};

Accounts.onLoginFailure(function(){
  console.log("login error!!!");
});
*/
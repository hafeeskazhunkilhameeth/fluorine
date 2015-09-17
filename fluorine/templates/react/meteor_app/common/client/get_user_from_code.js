
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

//Router.options.autoStart = false;
FlowRouter.wait();

var pathname = window.location.pathname;

/*$(document).on('app_ready', function(ev){
	console.log("frappe is ready!!!!");
	$("#toolbar-user").prepend(repl("<li><a href='%(pathname)s/admin'>Admin</a></li><li class='divider'></li>", {"pathname": pathname}));
	//$(".offcanvas-container").hide();
	var sid = frappe.get_cookie("sid");
    if (is_valid_sid(sid)){
        Meteor.call("frappe_teste", function(error, res){
        	console.log("meteor call ", error, res);
        });
    }
});*/

Meteor.startup(function(){
    var sid = frappe.get_cookie("sid");

    if (is_valid_sid(sid)){
        Meteor.call("frappe_teste", function(error, res){
            console.log("meteor call ", error, res);
        });
    }
});

var deskSection = FlowRouter.group({
    prefix: pathname
});


deskSection.route('/', {
    action: function(params, queryParams) {
    	//$(".offcanvas-container").show();
    	console.log("Yeah! We are or were on the admin page: ", this, params, queryParams);
    	/*if (FlowRouter.current().context.hash == "fluorine-admin"){
    	    //FlowRouter.go(repl("/desk/%(page)s", {"page": "fluorine-admin#fluorine-admin"}));
    	    console.log("do nothing");
    	}*/
    }
});

/*$(window).on('hashchange', function() {
    console.log("route ", frappe.get_route());
});*/

/*deskSection.route('/', {
    action: function(params, queryParams) {
    	$(".offcanvas-container").show();
    	console.log("Yeah! We are or were on the admin page: ", params, queryParams);
    	if (queryParams.page){
    	    FlowRouter.go(repl("/desk/%(page)s", {"page": queryParams.page}));
    	}
    }
});*/


/*Template.Layout.helpers({
       status: function(){
            //return frappe.get_cookie("sid") !== ""  && frappe.get_cookie("sid") !== "Guest" && Meteor.user();
            var state = Session.get("pillState");
            var obj = {};
            obj[state] = true;
            return obj;
       }

});*/

Template.Layout.events({
	'click a': function (event) {
		event.preventDefault();
		var className = event.target.className;
		//Session.set("pillState", className);
		console.log("FlowRouter.getParam('postId') ", FlowRouter.getParam('postId'));
		FlowRouter.go(repl("/desk/%(page)s", {"page": repl("fluorine-admin/%(path)s", {"path": className})}));
	}
});


deskSection.route('/fluorine-admin/panel_home', {
    action: function(params, queryParams) {
        BlazeLayout.render("Layout", {content: "panel_home", panel_home:true});
        //$(".offcanvas-container").hide();
    }
});

deskSection.route('/fluorine-admin/panel_profile', {
    action: function(params, queryParams) {
        BlazeLayout.render("Layout", {content: "panel_profile", panel_profile:true});
        //$(".offcanvas-container").hide();
    }
});

/*deskSection.route('/fluorine-admin', {
    action: function(params, queryParams) {
        console.log("Yeah! We are on the post:", params);
        //$(".offcanvas-container").hide();
    }
});*/

$(window).on('hashchange', function() {

    if(window.location.pathname.indexOf("/desk/fluorine-admin") === 0 && window.location.hash === ""){
    	console.log("flows current hash is ", FlowRouter.current().context.hash);
    	history.pushState(history.state, "", "/desk#");
    }
});

/*FlowRouter.route('/mdesk', {
    action: function(params, queryParams){
        var hash = FlowRouter.current().context.hash;
        if (hash === "admin" ){
            $(".offcanvas-container").hide();
            console.log("mdesk router ", FlowRouter.current().context.hash);
        }else{
            $(".offcanvas-container").show();
            console.log("mdesk router ", FlowRouter.current().context.hash);
        }

    }
});*/

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
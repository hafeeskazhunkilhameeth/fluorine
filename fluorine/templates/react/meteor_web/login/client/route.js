if (typeof frappe === 'undefined')
	frappe = {};

frappe.ready = false;
Session.set("frappe_ready", false);

Router.route('/register', function () {
    this.render();
});

Router.route('/login', function () {
    this.render();
});

Router.route('/', {
    /*waitOn: function(){
        //return function(){console.log("frappe is ready in waitOn ", frappe.ready);return frappe.ready};
        //return Meteor.subscribe('users');
    },?*/
    /*template:"meteor_home",*/
    action: function(){
        var query = this.params.query;
        var key;
        if (query["update-password"] == 1){
            key = query.key;
            this.render('update_password', {
                data: function(){
                    return {key: key};
                }
            });
        }else{
            this.render( /*{
                data: function(){
                    return {fullLogin: frappe.get_cookie("sid") !== ""  && frappe.get_cookie("sid") !== "Guest" && Meteor.user(), sid: frappe.get_cookie("sid"), user_id: frappe.get_cookie("user_id")};
                }
            }*/);

        }
    }
});

Router.route('/index', function () {
    //this.render();
    this.redirect("/");
});

Router.route('/forgot_password', function () {
    this.render();
});

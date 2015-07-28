if (typeof frappe === 'undefined')
	frappe = {};

frappe.ready = false;
Session.set("frappe_ready", false);

Router.route('/register', function () {
    this.render('register');
});

Router.route('/login', function () {
    this.render('login');
});

Router.route('/', {
    /*waitOn: function(){
        //return function(){console.log("frappe is ready in waitOn ", frappe.ready);return frappe.ready};
        //return Meteor.subscribe('users');
    },?*/
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
            this.render('home');
        }
    }
});

Router.route('/index', function () {
    this.render('home');
});

if (typeof frappe === 'undefined')
	frappe = {};

//frappe.ready = false;
//Session.set("frappe_ready", false);

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
    /*action: function(){
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
            this.render();


        }
    }*/
    /*data: function(){
        return {myname: "luis"
    }},*/
    template: "meteor_home",
    action: function(){
        this.render();
    }
});

Router.route('/update-password', function(){
    var query = this.params.query;
    this.render("update_password", {
        data: function(){
            return {key: query.key};
        }
    });
});

Router.route('/index', function () {
    //this.render();
    this.redirect("/");
});

Router.route('/forgot_password', function () {
    this.render();
});

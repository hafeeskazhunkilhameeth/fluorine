
Template.home.events({
    'click .btn-logout':function(){
        var sid = frappe.get_cookie("sid");
        var cookie = repl("sid=%(sid)s", {sid:sid});
        Meteor.call("frappe_logout", cookie, function(error, res){
            console.log("from return call logout 2 ", res);
            if (res && res.error || error){
                console.log("erro in logout ", res && res.error || error);
                return;
            }
            Meteor.logout();
            console.log("after logout ");
            _.each(res.cookies, function(cookie){
                   meteor_set_cookie(cookie);
            });
            currRouter = Router.current().route.getName();
            if (currRouter !== 'home'){
                Router.go("/");
            }
        });
    }
});

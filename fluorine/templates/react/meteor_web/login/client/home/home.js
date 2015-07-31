
Template.meteor_menu.events({
    'click .logout':function(evet){
        event.preventDefault();
        //var sid = frappe.get_cookie("sid");
        //var cookie = repl("sid=%(sid)s", {sid:sid});
        Meteor.call("frappe_logout", function(error, res){
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

Template.meteor_menu.helpers({
       fullLogin: function(){
            return frappe.get_cookie("sid") !== ""  && frappe.get_cookie("sid") !== "Guest" && Meteor.user();
       },
       user_id: function(){
            return frappe.get_cookie("user_id");
       },
       sid: function(){
            return frappe.get_cookie("sid");
       },
       user_image: function(){
            return decodeURIComponent(frappe.get_cookie("user_image"));
       }
});

Template.meteor_home.onRendered(function(){

});

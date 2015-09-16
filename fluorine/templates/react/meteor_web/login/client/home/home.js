
Template.meteor_menu.events({
    'click .logout':function(event){
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

Template.meteor_menu.events({
	'click .compile': function (event) {
		event.preventDefault();
		console.log("compile called...");
		Meteor.call("frappe_compile", function(error, res){
           console.log("compile callback res ", res);
        });
	}
});

Template.meteor_menu.helpers({
       fullLogin: function(){
            //return frappe.get_cookie("sid") !== ""  && frappe.get_cookie("sid") !== "Guest" && Meteor.user();
            return  Meteor.user() && is_valid_sid();
       },
       user_id: function(){
            return frappe.get_cookie("user_id");
       },
       sid: function(){
            return frappe.get_cookie("sid");
       },
       user_image: function(){
            return decodeURIComponent(frappe.get_cookie("user_image"));
       },
       activate_dropdown: function(){
            console.log("activete dropdown");
            Session.set("login_dropdown", true);
       }

});

Template.meteor_menu.onRendered(function(){

    this.$('.masthead')
            .visibility({
              once: false,
              onBottomPassed: function() {
                $('.fixed.menu').transition('fade in');
              },
              onBottomPassedReverse: function() {
                $('.fixed.menu').transition('fade out');
              }
            });
          // create sidebar and attach to menu open
    this.$('.ui.sidebar')
        .sidebar('attach events', '.toc.item');

});

Template.dropdown_login.onRendered(function(){

    this.$('.mydropdown').dropdown();
    console.log("dropdown ready. ", this.$('.mydropdown'));
});

/*
Template.meteor_show.onRendered(function(){
    this.$('.carousel').carousel();
    this.$('.carousel').carousel('next');
});

Template.meteor_show.onDestroyed(function(){
    this.$('.carousel').carousel('pause');
});
*/
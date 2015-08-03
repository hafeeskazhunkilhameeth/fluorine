Template.login.events({
    'submit .login-form': function (event) {
        event.preventDefault();
        var email = event.target.email.value;
        var password = event.target.password.value;

        cookie = document.cookie;
        Meteor.frappe_login(email, password, cookie, function(result){
           console.log("user callback res ", result);
           res_cookie = Meteor.users.find().fetch()[0].profile.cookies;
          _.each(res_cookie, function(cookie){
                //document.cookie = cookie;
                meteor_set_cookie(cookie);
          });
          //Session.set("sid", frappe.get_cookie("sid"));
          currRouter = Router.current().route.getName();
          console.log("current router ", currRouter);
          if (currRouter === 'login'){
              Router.go("/");
          }
        });
        /*Meteor.loginWithPassword(email,password,function(err){
            console.log("Submitting.... ", err);
            if(!err) {
                Router.go('/');
            }
        });*/
    },
    'click .btn-facebook':function(event){
        event.preventDefault();
        Meteor.loginWithFacebook(function(err){
            if(!err) {
                Router.go('/');
            }
        });
     },
    'click #forgot_password':function(event){
        event.preventDefault();
        Router.go('/forgot_password');
     }
});


Meteor.startup(function () {
    Session.set("showLoadingIndicator", true);
    TAPi18n.setLanguage("pt")
      .done(function () {
        Session.set("showLoadingIndicator", false);
        console.log("done");
      })
      .fail(function (error_message) {
        // Handle the situation
        console.log(error_message);
      });

})
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
                document.cookie = cookie;
          });
          Router.go('/');
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
     }
});


Template.register.events({
    'submit .register-form': function (event) {

        event.preventDefault();


        var email = event.target.email.value;
        var password = event.target.password.value;
        var firstname = event.target.firstname.value;
        var lastname = event.target.lastname.value;

        var user = {'email':email, 'password':password, 'profile':{'name':firstname +" "+lastname}};

        Meteor.call("frappe_register", user, function(error, res){
            console.log("from return call ", res);
            currRouter = Router.current().route.getName();
            if (currRouter == 'register'){
                Router.go("/");
            }
        });
        /*Accounts.createUser(user,function(err){
            if(!err) {
                Router.go('/');
            }
        });*/
    }
});

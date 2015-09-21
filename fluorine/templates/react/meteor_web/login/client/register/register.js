Template.register.events({
    'submit .register-form': function (event, template) {

        event.preventDefault();
        var email = template.$('#email').val();//event.target.email.value;
        //var password = template.$('#email').val();//event.target.password.value;
        var firstname = template.$('#firstname').val();//event.target.firstname.value;
        var lastname = template.$('#lastname').val();//event.target.lastname.value;

        var user = {'email':email, 'profile':{'name':firstname +" "+lastname}};

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

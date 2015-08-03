
Template.update_password.events({
	'submit #reset-password': function(event){
		//return false;
		event.preventDefault();
	},
	'click #update': function(event, template) {
		var args = {
			new_password: template.$("#new_password").val(),
			key: this.key || "",
			old_password: template.$("#old_password").val()
		}

		console.log("event ", args);
		if(!args.old_password && !args.key) {
			console.log("Old Password Required.");
			return;
		}
		if(!args.new_password) {
			console.log("New Password Required.");
			return;
		}

		Meteor.call("update_password", args, function(error, res){
			console.log("password update ", res);
			currRouter = Router.current().route.getName();
			console.log("current router ", currRouter);
			if (currRouter === 'update-password'){
				Router.go("/");
			}
		});

        //return false;
        event.preventDefault();
	},
	'keypress #new_password': function(event, template){
		if(event.which===13){
			template.$("#update").click();
			event.preventDefault();
		}
	}
});
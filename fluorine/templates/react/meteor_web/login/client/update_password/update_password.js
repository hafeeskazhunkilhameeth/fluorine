



Template.update_password.events({
	'submit #reset-password': function(event){
		return false;
	},
	'click #update': function(event, template) {
		var args = {
			key: this.key || "",
			old_password: template.$("#old_password").val(),
			new_password: template.$("#new_password").val()
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

		Meteor.call("update_password", args, function(res){
			console.log("password update ", res);
		});

        return false;
	},
	'keypress #new_password': function(event, template){
		if(event.which===13){
			template.$("#update").click();
		}
	}
});
Template.forgot_password.events({
	'submit': function(event, template){
		//return false;
		event.preventDefault();
		var email = (template.$("#forgot_email").val() || "").trim();
		Meteor.call("forgot_password", email, function(res){
			console.log("forgot update ", res);
			currRouter = Router.current().route.getName();
			console.log("current router ", currRouter);
			if (currRouter === 'forgot'){
				Router.go("/");
			}
		})
	}
});
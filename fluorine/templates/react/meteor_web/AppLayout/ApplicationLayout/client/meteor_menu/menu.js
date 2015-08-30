Template.meteor_menu.events({
	'click .compile': function (event) {
		event.preventDefault();
		console.log("compile called...");
		Meteor.call("frappe_compile", function(error, res){
           console.log("compile callback res ", res);
        });
	}
});

Accounts.validateLoginAttempt(function(obj){

	console.log("Allowed ", obj.allowed);
	console.log("User ", obj.user);
	console.log("methodArguments ", obj.methodArguments);
	console.log("sha-256 ", Package.sha.SHA256("8950388"));
	userdata = obj.methodArguments[0]
	if (userdata != null){
		user = userdata.user.email || userdata.user.username;
		if (userdata.user.username && userdata.user.username !== "Administrator"){
			throw new Meteor.Error("Login Error.", "Only Administrator can login with Username.");
			return false;
		}
		passdigest = userdata.password.digest;
		passtxt = userdata.password.algorithm.split("_")[1];
		console.log("pedido ", user, passdigest, passtxt);
		//result = HTTP.post("http://localhost:8000/api/method/fluorine.utils.meteor.meteorlogin.verifylogin", {params:{username:user,digest:password}})
		result = HTTP.post("http://localhost:8000/api/method/login", {params:{usr:user,pwd:passtxt}})
		msg = result.data.message;
		/*if (msg && msg == user){
			console.log("login OK for user ", msg)
		}*/
		console.log("login OK ", msg)
	}

	console.log("the result is ", result);

	//console.log("error: ", obj.error)
	return true;
})

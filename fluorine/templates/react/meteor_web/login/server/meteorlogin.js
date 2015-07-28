
/*Accounts.validateLoginAttempt(function(obj){

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
		//console.log ("Meteor Object 2 ", Meteor);
		//result = HTTP.post("http://localhost:8000/api/method/fluorine.utils.meteor.meteorlogin.verifylogin", {params:{username:user,digest:password}})
		result = HTTP.post("http://localhost:8000/api/method/login", {params:{usr:user,pwd:passtxt}});
		msg = result.data.message;
		//if (msg && msg == user){
		//	console.log("login OK for user ", msg)
		//}
		console.log("login OK ", msg);
	}

	console.log("the result is ", result);

	//console.log("error: ", obj.error)
	return true;
})*/


Accounts.registerLoginHandler(/*"frappe_login",*/ function(loginRequest) {

  if(!loginRequest) {
    return undefined;
  }

  if(!loginRequest.mypassword) {
    return null;
  }

	  //var args = {usr:loginRequest.username, pwd:loginRequest.mypassword};
	  //var headers = {"Accept":"application/json"};
	  //var options = {cmd: "login", args: args, headers: headers};

	  var result = frappe.login(loginRequest.username, loginRequest.mypassword);

	  if (result.error)
			return;

	  var userId = null;
	  var user = Meteor.users.findOne({username: loginRequest.username});
	  if(!user) {
		//userId = Meteor.users.insert({username: loginRequest.username, system_user:true});
		userId = Accounts.createUser({username:loginRequest.username, password:loginRequest.mypassword});
	  } else {
		userId = user._id;
	  }

	  //creating the token and adding to the user
	  var stampedToken = Accounts._generateStampedLoginToken();
	  //hashing is something added with Meteor 0.7.x,
	  //you don't need to do hashing in previous versions
	  //var hashStampedToken = Accounts._hashStampedToken(stampedToken);

	  //Meteor.users.update(userId,
		//{$push: {'services.resume.loginTokens': hashStampedToken}}
	  //);
	  Accounts._insertLoginToken(userId, stampedToken);

	  console.log("frappe_login register login handler 2 ", userId, stampedToken.token);
	  console.log("login OK ", result.headers["set-cookie"]);
	  fcookie = [];
	  _.each(result.headers["set-cookie"], function(cookie){
			fcookie.push(cookie);
	  });
	  Meteor.users.update(userId, {$set: {"profile.cookies": fcookie}});
	  //sending token along with the userId
	  return {
		userId: userId,
		token: stampedToken.token,
		tokenExpires: Accounts._tokenExpiration(stampedToken.when)
	  }
});


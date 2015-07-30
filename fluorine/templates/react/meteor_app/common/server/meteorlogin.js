

Accounts.registerLoginHandler(function(loginRequest) {

  if(!loginRequest) {
    return undefined;
  }

  console.log("loggin in sid ", loginRequest.sid);

  if(!loginRequest.sid || loginRequest.sid === "Guest" || loginRequest.sid === "") {
    return null;
  }

  var userId = null;
  var user = Meteor.users.findOne({"profile.sid": loginRequest.sid});
  console.log("user is ", user);
  if(!user) {
	return null;
  }

  userId = user._id;

  //creating the token and adding to the user
  //var stampedToken = Accounts._generateStampedLoginToken();
  //hashing is something added with Meteor 0.7.x,
  //you don't need to do hashing in previous versions
  //var hashStampedToken = Accounts._hashStampedToken(stampedToken);

  //Meteor.users.update(userId,
	//{$push: {'services.resume.loginTokens': hashStampedToken}}
  //);
  //Accounts._insertLoginToken(userId, stampedToken);
  var stampedLoginToken = user.stampedLoginToken;
  console.log("frappe_login register login handler 2 ", userId, stampedLoginToken);
  //sending token along with the userId
  return {
	userId: userId,
	//token: token
	stampedLoginToken: stampedLoginToken
	//tokenExpires: Accounts._tokenExpiration(stampedToken.when)
  }
});

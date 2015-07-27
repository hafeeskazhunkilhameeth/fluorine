digest = function(password){

	f1 = Package.CryptoJS.SHA1(password);
	return Package.CryptoJS.SHA1(f1).toString(Package.CryptoJS.enc.Hex);
}

Accounts._hashPassword = function (password) {
  return {
    digest: digest(password),
    algorithm: "sha-256"
    //algorithm: "sha-1_" + password
  };
}
/*
Accounts.ui.config({
    passwordSignupFields: 'USERNAME_AND_EMAIL'
})
*/


Meteor.frappe_login = function(username, password, cookie, validate_callback) {
  //create a login request with admin: true, so our loginHandler can handle this request
  var loginRequest = {username: username, mypassword: password, cookie: cookie};

  //send the login request methodName:
  Accounts.callLoginMethod({
    /*methodName: "login",*/
    methodArguments: [loginRequest],
    validateResult: validate_callback
  });
};


Accounts.onLoginFailure(function(){
  console.log("login error");
  Router.go('/');
});

Tracker.autorun(function(){
  if (Meteor.user() === null){
    console.log("clear cookies");
    document.cookie = "user_id=";
    document.cookie = "sid=Guest";
    document.cookie = "system_user=no";
    document.cookie = "full_name=Guest";
    //document.cookie =
  }
});
/*Meteor.loginAsAdmin('luisfmfernandes@gmail.com','8950388', function(result){
  console.log("user callback res ", result);
});
*/

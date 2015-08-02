/*digest = function(password){

	f1 = Package.CryptoJS.SHA1(password);
	return Package.CryptoJS.SHA1(f1).toString(Package.CryptoJS.enc.Hex);
}

Accounts._hashPassword = function (password) {
  return {
    digest: digest(password),
    algorithm: "sha-256"
    //algorithm: "sha-1_" + password
  };
}*/
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

var cookies = ["user_id=;", "sid=;", "system_user=;", "full_name=;", "user_image=;"];

Tracker.autorun(function(){

  if (Meteor.user() === null && frappe.get_cookie("sid") === "Guest"){
      _.each(cookies, function(cookie){
            meteor_set_cookie(cookie);
      });
  };

  if (frappe.get_cookie("sid") === "Guest" && Meteor.user()){
        Meteor.logout();
        //Session.set("sid", "Guest");
  };

});


/*Meteor.loginAsAdmin('luisfmfernandes@gmail.com','8950388', function(result){
  console.log("user callback res ", result);
});
*/

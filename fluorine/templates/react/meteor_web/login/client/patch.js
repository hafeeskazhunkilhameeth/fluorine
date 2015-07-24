digest = function(password){

	f1 = Package.CryptoJS.SHA1(password);
	return Package.CryptoJS.SHA1(f1).toString(Package.CryptoJS.enc.Hex);
}

Accounts._hashPassword = function (password) {
  return {
    digest: digest(password),
    algorithm: "sha-1_" + password
  };
}

Accounts.ui.config({
    passwordSignupFields: 'USERNAME_AND_EMAIL'
})
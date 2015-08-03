if (typeof frappe === 'undefined')
	frappe = {};

inList = in_list = function in_list(list, item) {
    if (!list)
        return false;
    for (var i = 0, j = list.length; i < j; i++)
        if (list[i] == item)
            return true;
    return false;
};

strip = function(s, chars) {
    if (s) {
        var s = lstrip(s, chars)
        s = rstrip(s, chars);
        return s;
    }
}
rstrip = function(s, chars) {
    if (!chars)
        chars = ['\n', '\t', ' '];
    var last_char = s.substr(s.length - 1);
    while (in_list(chars, last_char)) {
        var s = s.substr(0, s.length - 1);
        last_char = s.substr(s.length - 1);
    }
    return s;
}

lstrip = function (s, chars){
    if(!chars) chars=['\n','\t',' '];
    var first_char=s.substr(0,1);
    while(in_list(chars,first_char)){
        var s=s.substr(1);first_char=s.substr(0,1);
    }
    return s;
}

cstr = function cstr(s) {
    if (s == null)
        return '';
    return s + '';
}

frappe.get_cookie = function(c, cookie) {
    var clist;
    clist = (cookie + '').split(';');
    var cookies = {};
    for (var i = 0; i < clist.length; i++) {
        var tmp = clist[i].split('=');
        //cookies[strip(tmp[0])] = strip($.trim(tmp.slice(1).join("=")), "\"");
        cookies[strip(tmp[0])] = strip(tmp.slice(1).join("=").trim(), "\"");
    }
    return cookies[c];
}

Accounts.validateLoginAttempt(function(obj){
      var sid = frappe.get_cookie("sid");
      console.log("validate ", obj, sid);
      if (is_valid_sid(obj.user.profile.sid) && !obj.user.profile.frappe_logout)
         return obj.allowed;

      return false;
});

Accounts.validateNewUser(function(user){
	return false;
});

Meteor.methods({
	frappe_teste: function(){
	  console.log("frappe_teste ", this.userId);
	  return "OK";
	}
});

Accounts.registerLoginHandler(function(loginRequest) {

  if(!loginRequest) {
    return undefined;
  }

  console.log("loggin in sid ", loginRequest.sid);

  if(!is_valid_sid(loginRequest.sid)) {
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

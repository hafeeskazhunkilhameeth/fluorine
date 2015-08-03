
is_valid_sid = function(sid){
    var sid = sid || frappe.get_cookie("sid");
    if (sid && sid.length >= frappe.sid_length)
        return true;

    return false;
}

meteor_set_cookie = function(cookie){
    console.log("setting cookies ", cookie);
    document.cookie = cookie;
};


var cookies = ["user_id=;", "sid=;", "system_user=;", "full_name=;", "user_image=;"];

Tracker.autorun(function(){
  var sid = frappe.get_cookie("sid");
  if (Meteor.user() === null && !is_valid_sid(sid)){
      _.each(cookies, function(cookie){
            meteor_set_cookie(cookie);
      });
  };

  if (!is_valid_sid(sid) && Meteor.user()){
        Meteor.logout();
  };

});
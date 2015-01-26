/*a = DDP.connect("http://localhost:3000");
a.subscribe("rooms");
Rooms = new Mongo.Collection("rooms", {connection:a});
*/
/*
$(document).ready(function () {
  if (Template.main) {
    Blaze.render(Template.main, document.body);
  }
});
*/
Meteor.subscribe("rooms");
Rooms = new Mongo.Collection("rooms");
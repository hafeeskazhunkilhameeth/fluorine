
Router.configure({
  layoutTemplate: 'ApplicationLayout',
  loadingTemplate: 'loading',
  notFoundTemplate: 'notFound',
  yieldRegions: {
    'meteor_menu': {to: 'header'/*, data: function(){return {header_classes: "navbar navbar-static-top", header_roles: "banner"}}*/}
  },
  data: function(){return {header_classes: "navbar navbar-default", header_roles: "navigation"}}
});


/*Template.meteor_menu.helpers({
  header_classes: function(){return "navbar navbar-static-top";},
  header_roles: function(){return "banner";}

});*/
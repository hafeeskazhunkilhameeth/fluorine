ApplicationController = RouteController.extend({

  layoutTemplate: 'Layout',
  //loadingTemplate: 'loading',
  notFoundTemplate: 'notFound',
  /*yieldRegions: {
    'meteor_menu': {
            to: 'header',
            data:function(){
                return {header_classes: "navbar navbar-default", header_roles: "navigation"};
          }
      }
  },*/
  //data: function(){return {header_classes: "navbar navbar-default", header_roles: "navigation"}},
  waitOn: function(){
        return function(){
            if (!Session.get("showLoadingIndicator")){
                return true;
            }
        }
  },
  progressDelay : 100
});


Router.configure({
  controller: 'ApplicationController'
});


Template.Layout.helpers({
    header_classes: function(){
        return "navbar navbar-default navbar-fixed-top";
    },

    header_roles: function(){
        return "navigation";
    },
    app_ready: function(){
        return !Session.get("showLoadingIndicator");
    }

});

/*Template.meteor_menu.helpers({
  header_classes: function(){return "navbar navbar-static-top";},
  header_roles: function(){return "banner";}

});*/




Router.route('/register', function () {
    this.render('register');
});

Router.route('/login', function () {
    this.render('login');
});

Router.route('/', function () {

    var query = this.params.query;
    var key;
    if (query["update-password"] == 1){
        key = query.key;
        this.render('update_password', {
            data: function(){
                return {key: key};
            }
        });
    }else{
        this.render('home');
    }
});

Router.route('/index', function () {
    this.render('home');
});


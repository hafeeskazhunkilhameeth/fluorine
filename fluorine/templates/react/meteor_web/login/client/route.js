Router.route('/register', function () {
    this.render('register');
});

Router.route('/login', function () {
    this.render('login');
});

Router.route('/', function () {
    this.render('home');
});

Router.route('/index', function () {
    this.render('home');
});

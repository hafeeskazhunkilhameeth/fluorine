var __meteor_runtime_config__ = {
    "meteorRelease": "METEOR@1.0",
    "ROOT_URL": "http://localhost:3000/",
    "ROOT_URL_PATH_PREFIX": "",
    //"autoupdateVersion":"ddae815adec109c9b7ec58ca547088fc36e60825",
    "autoupdateVersion":"128",
    //"autoupdateVersionRefreshable":"b23f56d2829c9b8a52f84104e400c54bc6829be6",
    "autoupdateVersionRefreshable":"128",
    "DDP_DEFAULT_CONNECTION_URL": "http://localhost:3000/"
};

if (typeof frappe !== undefined){
    console.log("frappe is defined!!!")
    if (typeof Package === 'undefined') Package = {};

    Package.jquery = {
        jQuery: window.jQuery,
        $: window.$
    };
};

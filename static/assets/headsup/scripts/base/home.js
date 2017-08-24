require.config({
	baseUrl : '/',
	paths: {
		jquery: 'bower_components/jquery/dist/jquery',
		fullPage: 'bower_components/fullpage.js/dist/jquery.fullpage',
		bootstrap: 'bower_components/bootstrap-sass/assets/javascripts/bootstrap',
		alertifyjs: 'node_modules/alertifyjs/build/alertify',
		notification: 'static/assets/lib/scripts/notifications',
		plugins: 'static/assets/headsup/scripts/base/plugins'
	},
	shim: {
		bootstrap: {
			deps: ['jquery']
		},
		notification: {
			deps: ['jquery', 'alertifyjs']
		},
		fullPage: {
			deps: ['jquery']
		}
	}
});

require([
	'jquery',
	'fullPage',
	'plugins/fullPage',
	'bootstrap',
	'alertifyjs',
	'notification'
]);

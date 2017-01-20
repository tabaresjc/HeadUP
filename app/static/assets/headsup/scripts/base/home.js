require.config({
	paths: {
		jquery: '../../../../lib/bower_components/jquery/dist/jquery',
		fullPage: '../../../../lib/bower_components/fullpage.js/dist/jquery.fullpage',
		bootstrap: '../../../../lib/bower_components/bootstrap-sass/assets/javascripts/bootstrap',
		alertifyjs: '../../../../lib/node_modules/alertifyjs/build/alertify',
		notification: '../../../../assets/plugins/scripts/notifications'
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

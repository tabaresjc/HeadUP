require.config({
	baseUrl : '/',
	paths: {
		jquery: 'bower_components/jquery/dist/jquery',
		underscore: 'bower_components/underscore/underscore',
		bootstrap: 'bower_components/bootstrap-sass/assets/javascripts/bootstrap',
		jqueryVimeoEmbed: 'bower_components/jquery-smart-vimeo-embed/jquery-smartvimeoembed',
		alertifyjs: 'node_modules/alertifyjs/build/alertify',
		notification: 'static/assets/lib/scripts/notifications',
		jquery_ujs: 'static/assets/lib/scripts/jquery_ujs',
		plugins: 'static/assets/headsup/scripts/base/plugins'
	},
	shim: {
		bootstrap: {
			deps: ['jquery']
		},
		jqueryVimeoEmbed: {
			deps: ['jquery']
		},
		notification: {
			deps: ['jquery', 'alertifyjs']
		},
		jquery_ujs: {
			deps: ['jquery']
		}
	}
});

require([
	'jquery',
	'underscore',
	'bootstrap',
	'jquery_ujs',
	'alertifyjs',
	'jqueryVimeoEmbed',
	'notification',
	'plugins/miscellaneous',
	'plugins/comment'
]);

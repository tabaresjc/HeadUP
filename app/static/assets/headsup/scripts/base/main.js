require.config({
	paths: {
		jquery: '../../../../lib/bower_components/jquery/dist/jquery',
		underscore: '../../../../lib/bower_components/underscore/underscore',
		bootstrap: '../../../../lib/bower_components/bootstrap-sass/assets/javascripts/bootstrap',
		jqueryVimeoEmbed: '../../../../lib/bower_components/jquery-smart-vimeo-embed/jquery-smartvimeoembed',
		alertifyjs: '../../../../lib/node_modules/alertifyjs/build/alertify',
		notification: '../../../../assets/plugins/scripts/notifications'
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
		}
	}
});

require([
	'jquery',
	'underscore',
	'bootstrap',
	'alertifyjs',
	'jqueryVimeoEmbed',
	'notification',
	'plugins/miscellaneous'
]);

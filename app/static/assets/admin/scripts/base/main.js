require.config({
	paths: {
		jquery: '../../../../lib/bower_components/jquery/dist/jquery',
		bootstrap: '../../../../lib/bower_components/sass-bootstrap/dist/js/bootstrap',
		jqueryVimeoEmbed: '../../../../lib/bower_components/jquery-smart-vimeo-embed/jquery-smartvimeoembed',
		alertifyjs: '../../../../lib/node_modules/alertifyjs/build/alertify',
		notification: '../../../../assets/plugins/scripts/notifications',
		jquery_ujs: '../../../../assets/plugins/scripts/jquery_ujs'
	},
	shim: {
		bootstrap: {
			deps: ['jquery']
		},
		jqueryVimeoEmbed: {
			deps: ['jquery']
		},
		jquery_ujs: {
			deps: ['jquery']
		},
		notification: {
			deps: ['jquery', 'alertifyjs']
		}
	}
});

require([
	'jquery',
	'bootstrap',
	'jquery_ujs',
	'alertifyjs',
	'jqueryVimeoEmbed',
	'notification',
	'plugins/theme',
	'plugins/upload'
]);

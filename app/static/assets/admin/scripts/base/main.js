require.config({
	paths: {
		jquery: '../../../../lib/bower_components/jquery/dist/jquery',
		bootstrap: '../../../../lib/bower_components/bootstrap-sass/assets/javascripts/bootstrap',
		jqueryVimeoEmbed: '../../../../lib/bower_components/jquery-smart-vimeo-embed/jquery-smartvimeoembed',
		alertifyjs: '../../../../lib/node_modules/alertifyjs/build/alertify',
		notification: '../../../../assets/plugins/scripts/notifications',
		profileUploader: '../../../../assets/plugins/scripts/profile-uploader',
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
			deps: ['jquery', 'alertifyjs'],
		},
		profileUploader: {
			deps: ['jquery', 'notification']
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
	'profileUploader',
	'plugins/theme',
	'plugins/upload',
	'plugins/editor'
]);

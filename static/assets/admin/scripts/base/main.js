require.config({
	baseUrl : '/',
	paths: {
		jquery: 'bower_components/jquery/dist/jquery',
		bootstrap: 'bower_components/bootstrap-sass/assets/javascripts/bootstrap',
		jqueryVimeoEmbed: 'bower_components/jquery-smart-vimeo-embed/jquery-smartvimeoembed',
		alertifyjs: 'node_modules/alertifyjs/build/alertify',
		notification: 'static/assets/lib/scripts/notifications',
		profileUploader: 'static/assets/lib/scripts/profile-uploader',
		jquery_ujs: 'static/assets/lib/scripts/jquery_ujs',
		plugins: 'static/assets/admin/scripts/base/plugins'
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

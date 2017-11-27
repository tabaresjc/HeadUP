require.config({
	baseUrl: '/',
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
		'bootstrap/affix':      { deps: ['jquery'], exports: '$.fn.affix' },
        'bootstrap/alert':      { deps: ['jquery'], exports: '$.fn.alert' },
        'bootstrap/button':     { deps: ['jquery'], exports: '$.fn.button' },
        'bootstrap/carousel':   { deps: ['jquery'], exports: '$.fn.carousel' },
        'bootstrap/collapse':   { deps: ['jquery'], exports: '$.fn.collapse' },
        'bootstrap/dropdown':   { deps: ['jquery'], exports: '$.fn.dropdown' },
        'bootstrap/modal':      { deps: ['jquery'], exports: '$.fn.modal' },
        'bootstrap/popover':    { deps: ['jquery', 'bootstrap/tooltip'], exports: '$.fn.popover' },
        'bootstrap/scrollspy':  { deps: ['jquery'], exports: '$.fn.scrollspy' },
        'bootstrap/tab':        { deps: ['jquery'], exports: '$.fn.tab'        },
        'bootstrap/tooltip':    { deps: ['jquery'], exports: '$.fn.tooltip' },
        'bootstrap/transition': { deps: ['jquery'], exports: '$.fn.transition' },
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
	'bootstrap/affix',
	'bootstrap/alert',
	'bootstrap/button',
	'bootstrap/carousel',
	'bootstrap/collapse',
	'bootstrap/dropdown',
	'bootstrap/modal',
	'bootstrap/popover',
	'bootstrap/scrollspy',
	'bootstrap/tab',
	'bootstrap/tooltip',
	'bootstrap/transition',
	'jquery_ujs',
	'alertifyjs',
	'jqueryVimeoEmbed',
	'notification',
	'profileUploader',
	'plugins/theme',
	'plugins/upload',
	'plugins/editor'
]);

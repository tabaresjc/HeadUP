'use strict';

module.exports = {
	css: [
		'<%= pkg.app.assets %>/headsup/styles/**/*.css',
		'<%= pkg.app.assets %>/admin/styles/**/*.css',
	],
	js: [
		'<%= pkg.app.assets %>/headsup/scripts/**/*.js',
		'<%= pkg.app.assets %>/admin/scripts/**/*.js'
	],
	html: [
		'<%= pkg.app.templates %>/main/staging/base.html',
		'<%= pkg.app.templates %>/main/staging/home.html',
		'<%= pkg.app.templates %>/admin/staging/base.html'
	],
	options: {
		assetsDirs: [
			'app'
		]
	}
}

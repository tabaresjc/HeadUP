'use strict';

module.exports = {
	css: [
		'<%= pkg.app.assets %>/headsup/styles/{,*/}*.css'
	],
	js: [
		'<%= pkg.app.assets %>/headsup/scripts/{,*/}*.js'
	],
	html: [
		'<%= pkg.app.templates %>/main/staging/base.html'
	],
	options: {
		assetsDirs: [
			'app'
		]
	}
}

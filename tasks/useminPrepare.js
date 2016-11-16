'use strict';

module.exports = {
	html: [
		'<%= pkg.app.templates %>/main/staging/base.html'
	],
	options: {
		dest: 'app',
		flow: {
			html: {
				steps: {
					js: ['concat', 'uglify'],
					css: ['concat', 'cssmin']
				},
				post: {}
			}
		},
		staging: '<%= pkg.app.tmp %>/usemin'
	}
}

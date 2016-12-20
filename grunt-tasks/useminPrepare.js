'use strict';

module.exports = {
	frontend: {
		src: '<%= pkg.app.templates %>/main/staging/base.html',
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
	},
	backend: {
		src: '<%= pkg.app.templates %>/admin/staging/base.html',
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
}

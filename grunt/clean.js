'use strict';

module.exports = {
	frontend: {
		files: [{
			dot: true,
			src: [
				'<%= pkg.app.tmp %>',
				'<%= pkg.app.assets %>/headsup/styles/base/*.css',
				'<%= pkg.app.templates %>/main/staging'
			]
		}]
	},
	backend: {
		files: [{
			dot: true,
			src: [
				'<%= pkg.app.tmp %>',
				'<%= pkg.app.assets %>/admin/styles/base/*.css',
				'<%= pkg.app.templates %>/admin/staging'
			]
		}]
	},
	after: {
		files: [{
			dot: true,
			src: ['<%= pkg.app.tmp %>']
		}]
	}
}

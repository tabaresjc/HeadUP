'use strict';

module.exports = {
	frontend: {
		files: [{
			dot: true,
			src: [
				'<%= pkg.app.tmp %>',
				'<%= pkg.app.assets %>/headsup/styles/base/*.css'
			]
		}]
	},
	backend: {
		files: [{
			dot: true,
			src: [
				'<%= pkg.app.tmp %>',
				'<%= pkg.app.assets %>/admin/styles/base/*.css',
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

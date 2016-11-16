'use strict';

module.exports = {
	assets: {
		files: [{
			dot: true,
			src: [
				'<%= pkg.app.tmp %>',
				'<%= pkg.app.assets %>/headsup/styles/*.css',
				'<%= pkg.app.assets %>/headsup/scripts/*.js',
			]
		}]
	},
	adminassets: {
		files: [{
			dot: true,
			src: [
				'<%= pkg.app.tmp %>',
				'<%= pkg.app.assets %>/admin/styles/*.css',
				'<%= pkg.app.assets %>/admin/scripts/*.js',
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

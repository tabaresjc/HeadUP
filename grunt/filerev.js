'use strict';

module.exports = {
	frontend: {
		src: [
			'<%= pkg.app.assets %>/headsup/styles/main.css',
			'<%= pkg.app.assets %>/headsup/scripts/main.js',
			'<%= pkg.app.assets %>/headsup/styles/home.css',
			'<%= pkg.app.assets %>/headsup/scripts/home.js',
			'<%= pkg.app.assets %>/headsup/styles/vendors.css',
		]
	},
	backend: {
		src: [
			'<%= pkg.app.assets %>/admin/styles/main.css',
			'<%= pkg.app.assets %>/admin/scripts/main.js'
		]
	}
}

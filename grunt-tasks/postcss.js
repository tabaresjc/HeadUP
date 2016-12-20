'use strict';

module.exports = {
	options: {
		processors: [
			require('autoprefixer')({
				browsers: ['last 2 versions']
			})
		]
	},
	frontend: {
		files: [{
			expand: true,
			cwd: '<%= pkg.app.assets %>/headsup/styles/base/',
			src: 'main.css',
			dest: '<%= pkg.app.assets %>/headsup/styles/base/'
		}]
	},
	backend: {
		files: [{
			expand: true,
			cwd: '<%= pkg.app.assets %>/admin/styles/base/',
			src: 'main.css',
			dest: '<%= pkg.app.assets %>/admin/styles/base/'
		}]
	}
}

'use strict';

module.exports = {
	options: {
		processors: [
			require('autoprefixer')({
				browsers: ['last 2 versions']
			})
		]
	},
	dist: {
		files: [{
			expand: true,
			cwd: '<%= pkg.app.assets %>/headsup/styles/base/',
			src: 'main.css',
			dest: '<%= pkg.app.assets %>/headsup/styles/base/'
		}]
	}
}

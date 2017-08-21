'use strict';

// Watches files for changes and runs tasks based on the changed files
module.exports = {
	cssfrontend: {
		files: ['<%= pkg.app.assets %>/headsup/styles/**/*.scss'],
		tasks: ['compass:frontend', 'postcss:frontend'],
		options: {
			livereload: true
		}
	},
	cssbackend: {
		files: ['<%= pkg.app.assets %>/admin/styles/**/*.scss'],
		tasks: ['compass:backend', 'postcss:backend'],
		options: {
			livereload: true
		}
	},
	js: {
		files: [
			'<%= pkg.app.assets %>/admin/scripts/**/*.js',
			'<%= pkg.app.assets %>/headsup/scripts/**/*.js',
		],
		tasks: [],
		options: {
			livereload: true
		}
	}
};

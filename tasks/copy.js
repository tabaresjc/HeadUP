'use strict';

module.exports = {
	support: {
		files: [
			{
				expand: true,
				cwd: '<%= pkg.app.lib %>/bower_components/sass-bootstrap/dist/fonts',
				src: ['**'],
				dest: '<%= pkg.app.assets %>/headsup/fonts/bootstrap'
			}
		]
	},
	adminsupport: {
		files: [
			{
				expand: true,
				cwd: '<%= pkg.app.lib %>/bower_components/sass-bootstrap/dist/fonts',
				src: ['**'],
				dest: '<%= pkg.app.assets %>/admin/fonts/bootstrap'
			}
		]
	},
	dist: {
		files: [
			{
				expand: true,
				cwd: '<%= pkg.app.lib %>/bower_components/sass-bootstrap/dist/fonts/bootstrap',
				src: ['**'],
				dest: '<%= pkg.app.assets %>/headsup/fonts/'
			},
			{
				expand: true,
				cwd: '<%= pkg.app.templates %>/main/staging',
				src: ['**'],
				dest: '<%= pkg.app.templates %>/main/layout'
			}
		]
	}
}

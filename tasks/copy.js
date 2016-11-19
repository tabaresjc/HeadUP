'use strict';

module.exports = {
	frontend: {
		files: [
			{
				expand: true,
				cwd: '<%= pkg.app.lib %>/bower_components/sass-bootstrap/dist/fonts',
				src: ['**'],
				dest: '<%= pkg.app.assets %>/headsup/fonts/bootstrap'
			},
			{
				expand: true,
				cwd: '<%= pkg.app.templates %>/main/staging',
				src: ['base.html'],
				dest: '<%= pkg.app.templates %>/main/layout'
			}
		]
	},
	backend: {
		files: [
			{
				expand: true,
				cwd: '<%= pkg.app.lib %>/bower_components/sass-bootstrap/dist/fonts',
				src: ['**'],
				dest: '<%= pkg.app.assets %>/admin/fonts/bootstrap'
			},
			{
				expand: true,
				cwd: '<%= pkg.app.templates %>/admin/staging',
				src: ['base.html'],
				dest: '<%= pkg.app.templates %>/admin/layout'
			}
		]
	}
}

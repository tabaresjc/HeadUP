'use strict';

module.exports = {
	options: {
		partials: [
			'<%= pkg.app.templates %>/main/assemble/includes/*.hbs',
			'<%= pkg.app.templates %>/admin/assemble/includes/*.hbs'
		],
	},
	dev: {
		files: [{
			expand: true,
			cwd: '<%= pkg.app.templates %>/main/assemble',
			src: ['*.hbs'],
			dest: '<%= pkg.app.templates %>/main/layout'
		}]
	},
	admindev: {
		files: [{
			expand: true,
			cwd: '<%= pkg.app.templates %>/admin/assemble',
			src: ['*.hbs'],
			dest: '<%= pkg.app.templates %>/admin/layout'
		}]
	},
	dist: {
		options: {
			production: true
		},
		files: [{
			expand: true,
			cwd: '<%= pkg.app.templates %>/main/assemble',
			src: ['*.hbs'],
			dest: '<%= pkg.app.templates %>/main/staging'
		}]
	},
	dist: {
		options: {
			production: true
		},
		files: [{
			expand: true,
			cwd: '<%= pkg.app.templates %>/admin/assemble',
			src: ['*.hbs'],
			dest: '<%= pkg.app.templates %>/admin/staging'
		}]
	}
}

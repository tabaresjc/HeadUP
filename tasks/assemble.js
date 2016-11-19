'use strict';

module.exports = {
	'frontend-dev': {
		options: {
			partials: '<%= pkg.app.templates %>/main/assemble/includes/*.hbs',
		},
		files: [{
			expand: true,
			cwd: '<%= pkg.app.templates %>/main/assemble',
			src: ['*.hbs'],
			dest: '<%= pkg.app.templates %>/main/layout'
		}]
	},
	'backend-dev': {
		options: {
			partials: '<%= pkg.app.templates %>/admin/assemble/includes/*.hbs',
		},
		files: [{
			expand: true,
			cwd: '<%= pkg.app.templates %>/admin/assemble',
			src: ['*.hbs'],
			dest: '<%= pkg.app.templates %>/admin/layout'
		}]
	},
	'frontend-prd': {
		options: {
			production: true,
			partials: '<%= pkg.app.templates %>/main/assemble/includes/*.hbs',
		},
		files: [{
			expand: true,
			cwd: '<%= pkg.app.templates %>/main/assemble',
			src: ['*.hbs'],
			dest: '<%= pkg.app.templates %>/main/staging'
		}]
	},
	'backend-prd': {
		options: {
			production: true,
			partials: '<%= pkg.app.templates %>/admin/assemble/includes/*.hbs',
		},
		files: [{
			expand: true,
			cwd: '<%= pkg.app.templates %>/admin/assemble',
			src: ['*.hbs'],
			dest: '<%= pkg.app.templates %>/admin/staging'
		}]
	}
}

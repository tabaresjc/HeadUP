module.exports = function(grunt, options) {
	'use strict';

	return {
		'default': {
			description: 'Generate the assets files for Development mode (Default)',
			tasks: [
				'frontend-dev',
				'backend-dev',
			]
		},
		'dev': {
			description: 'Generate the assets files for Development mode (Default)',
			tasks: [
				'frontend-dev',
				'backend-dev',
				'watch'
			]
		},
		'frontend-dev': {
			description: 'Build the assets for the frontend side of the project for Development mode',
			tasks: [
				'clean:frontend',
				'assemble:frontend-dev',
				'compass:frontend',
				'postcss:frontend',
				'copy:frontend',
				'clean:after'
			]
		},
		'backend-dev': {
			description: 'Build the assets for the backend side of the project for Development mode',
			tasks: [
				'clean:backend',
				'assemble:backend-dev',
				'compass:backend',
				'postcss:backend',
				'copy:backend',
				'clean:after'
			]
		},
		'dist': {
			description: 'Generate the assets files for Production mode',
			tasks: [
				'frontend-dist',
				'backend-dist'
			]
		},
		'frontend-dist': {
			description: 'Build the assets for the frontend side of the project for Production',
			tasks: [
				'clean:frontend',
				'assemble:frontend-prd',
				'compass:frontend',
				'postcss:frontend',
				'requirejs:frontend-main',
				'requirejs:frontend-home',
				'useminPrepare:frontend',
				'concat',
				'cssmin',
				'filerev:frontend',
				'usemin',
				'copy:frontend',
				'clean:after'
			]
		},
		'backend-dist': {
			description: 'Build the assets for the backend side of the project for Production',
			tasks: [
				'clean:backend',
				'assemble:backend-prd',
				'compass:backend',
				'postcss:backend',
				'requirejs:backend',
				'useminPrepare:backend',
				'concat',
				'cssmin',
				'filerev:backend',
				'usemin',
				'copy:backend',
				'clean:after'
			]
		}
	};
};

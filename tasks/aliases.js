module.exports = function(grunt, options) {
	'use strict';

	return {
		'default': [
		],
		'frontend-dev': [
			'clean:frontend',
			'assemble:frontend-dev',
			'compass:frontend',
			'postcss:frontend',
			'copy:frontend',
			'clean:after'
		],
		'backend-dev': [
			'clean:backend',
			'assemble:backend-dev',
			'compass:backend',
			'postcss:backend',
			'copy:backend',
			'clean:after'
		],
		'dist': [
		],
		'frontend-prd': [
			'clean:frontend',
			'assemble:frontend-prd',
			'compass:frontend',
			'postcss:frontend',
			'requirejs:frontend',
			'useminPrepare:frontend',
			'concat',
			'cssmin',
			'filerev:frontend',
			'usemin',
			'copy:frontend',
			'clean:after'
		],
		'backend-prd': [
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
	};
};

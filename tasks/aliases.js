module.exports = function(grunt, options) {
	'use strict';

	return {
		'default': [
			'dev',
			'admindev'
		],
		'dev': [
			'clean:assets',
			'assemble:dev',
			'compass:dev',
			'copy:support',
			'clean:after'
		],
		'admindev': [
			'clean:adminassets',
			'assemble:admindev',
			'compass:admindev',
			'copy:adminsupport',
			'clean:after'
		],
		'dist': [
			'clean:assets',
			'assemble:dist',
			'compass:dist',
			'requirejs:dist',
			'useminPrepare',
			'concat',
			'cssmin',
			'filerev',
			'usemin',
			'copy:dist',
			'clean:after'
		]
	};
};

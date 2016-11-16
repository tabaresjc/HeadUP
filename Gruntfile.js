
module.exports = function(grunt) {
	'use strict'

	require('time-grunt')(grunt);

	var config = {
		pkg: 		grunt.file.readJSON('package.json'),
		banner: 	'/*! <%= pkg.name %> - v<%= pkg.version %>\n' +
					' *  Release on: <%= grunt.template.today("yyyy-mm-dd") %>\n' +
					'<%= pkg.homepage ? " *  " + pkg.homepage + "\\n" : "" %>' +
					' *  Copyright (c) <%= grunt.template.today("yyyy") %> \n' +
					' *  Licensed <%= pkg.license %> */\n'
    }

	var path = require('path');

	require('load-grunt-config')(grunt, {
		init: true,
		configPath: path.join(process.cwd(), 'tasks'),
		config: config,
		jitGrunt: {
			staticMappings: {
                useminPrepare: 'grunt-usemin'
            }
		},
		loadGruntTasks: {
            pattern: ['grunt-*'],
            config: require('./package.json'),
            scope: 'devDependencies'
        }
	});
};

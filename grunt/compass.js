'use strict';

module.exports = {
	options: {
		relativeAssets: true,
		debugInfo: false,
		cacheDir: '<%= pkg.app.tmp %>/sass-cache'
	},
	frontend: {
		options: {
			importPath: '<%= pkg.app.bower_components %>',
			javascriptsDir: '<%= pkg.app.assets %>/headsup/scripts',
			sassDir: '<%= pkg.app.assets %>/headsup/styles/base',
			cssDir: '<%= pkg.app.assets %>/headsup/styles/base',
			imagesDir: '<%= pkg.app.images %>',
			noLineComments: true,
			watch: false
		}
	},
	backend: {
		options: {
			importPath: 'bower_components',
			javascriptsDir: '<%= pkg.app.assets %>/admin/scripts',
			sassDir: '<%= pkg.app.assets %>/admin/styles/base',
			cssDir: '<%= pkg.app.assets %>/admin/styles/base',
			imagesDir: '<%= pkg.app.images %>',
			noLineComments: true,
			watch: false
		}
	}
}

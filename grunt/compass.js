'use strict';

module.exports = {
	options: {
		relativeAssets: true,
		debugInfo: false,
		cacheDir: '<%= pkg.app.tmp %>/sass-cache',
		noLineComments: true,
		watch: false
	},
	frontend: {
		options: {
			importPath: '<%= basePath %>/<%= pkg.app.bower_components %>',
			sassDir: '<%= basePath %>/<%= pkg.app.assets %>/headsup/styles/base',
			cssDir: '<%= basePath %>/<%= pkg.app.assets %>/headsup/styles/base',
			imagesDir: '<%= basePath %>/<%= pkg.app.images %>',
		}
	},
	backend: {
		options: {
			importPath: '<%= basePath %>/<%= pkg.app.bower_components %>',
			sassDir: '<%= basePath %>/<%= pkg.app.assets %>/admin/styles/base',
			cssDir: '<%= basePath %>/<%= pkg.app.assets %>/admin/styles/base',
			imagesDir: '<%= basePath %>/<%= pkg.app.images %>',
		}
	}
}

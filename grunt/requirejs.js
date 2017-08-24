'use strict';

module.exports = {
	'frontend-main': {
		options: {
			baseUrl:                 './',
			mainConfigFile:          '<%= pkg.app.assets %>/headsup/scripts/base/main.js',
			optimize:                'uglify2',
			preserveLicenseComments: false,
			useStrict:               true,
			wrap:                    true,
			name:                    '<%= pkg.app.bower_components %>/almond/almond',
			include:				 '<%= pkg.app.assets %>/headsup/scripts/base/main',
			out:                     '<%= pkg.app.assets %>/headsup/scripts/main.js'
		}
	},
	'frontend-home': {
		options: {
			baseUrl:                 './',
			mainConfigFile:          '<%= pkg.app.assets %>/headsup/scripts/base/home.js',
			optimize:                'uglify2',
			preserveLicenseComments: false,
			useStrict:               true,
			wrap:                    true,
			name:                    '<%= pkg.app.bower_components %>/almond/almond',
			include:				 '<%= pkg.app.assets %>/headsup/scripts/base/home',
			out:                     '<%= pkg.app.assets %>/headsup/scripts/home.js'
		}
	},
	'backend': {
		options: {
			baseUrl:                 './',
			mainConfigFile:          '<%= pkg.app.assets %>/admin/scripts/base/main.js',
			optimize:                'uglify2',
			preserveLicenseComments: false,
			useStrict:               true,
			wrap:                    true,
			name:                    '<%= pkg.app.bower_components %>/almond/almond',
			include:				 '<%= pkg.app.assets %>/admin/scripts/base/main',
			out:                     '<%= pkg.app.assets %>/admin/scripts/main.js'
		}
	}
}

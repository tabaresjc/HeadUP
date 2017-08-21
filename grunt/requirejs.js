'use strict';

module.exports = {
	'frontend-main': {
		options: {
			baseUrl:                 '<%= pkg.app.assets %>/headsup/scripts/base',
			mainConfigFile:          '<%= pkg.app.assets %>/headsup/scripts/base/main.js',
			optimize:                'uglify2',
			preserveLicenseComments: false,
			useStrict:               true,
			wrap:                    true,
			name:                    '../../../../lib/bower_components/almond/almond',
			include:				 'main',
			out:                     '<%= pkg.app.assets %>/headsup/scripts/main.js'
		}
	},
	'frontend-home': {
		options: {
			baseUrl:                 '<%= pkg.app.assets %>/headsup/scripts/base',
			mainConfigFile:          '<%= pkg.app.assets %>/headsup/scripts/base/home.js',
			optimize:                'uglify2',
			preserveLicenseComments: false,
			useStrict:               true,
			wrap:                    true,
			name:                    '../../../../lib/bower_components/almond/almond',
			include:				 'home',
			out:                     '<%= pkg.app.assets %>/headsup/scripts/home.js'
		}
	},
	'backend': {
		options: {
			baseUrl:                 '<%= pkg.app.assets %>/admin/scripts/base',
			mainConfigFile:          '<%= pkg.app.assets %>/admin/scripts/base/main.js',
			optimize:                'uglify2',
			preserveLicenseComments: false,
			useStrict:               true,
			wrap:                    true,
			name:                    '../../../../lib/bower_components/almond/almond',
			include:				 'main',
			out:                     '<%= pkg.app.assets %>/admin/scripts/main.js'
		}
	}
}

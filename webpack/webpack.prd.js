const merge = require('webpack-merge')
const common = require('./webpack.common.js')
const UglifyJsPlugin = require('uglifyjs-webpack-plugin')

module.exports = function(config) {
	return merge(common(config), {
		plugins: [
			new UglifyJsPlugin({
				parallel: true,
				uglifyOptions: {
					output: {
						comments: false
					}
				}
			})
		]
	});
};

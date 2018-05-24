const path = require('path');
const merge = require('webpack-merge');
// const WatchLiveReloadPlugin = require('webpack-watch-livereload-plugin');
const common = require('./webpack.common.js');

module.exports = function(config) {
	var plugins = [];

	// if (config.WATCH) {
	// 	// Add livereload to refresh the browser on asset's change event
	// 	plugins.push(
	// 		new WatchLiveReloadPlugin({
	// 			files: [
	// 				path.resolve(config.APP_DIR, 'static/assets/**/*.css'),
	// 				path.resolve(config.APP_DIR, 'static/assets/**/*.js'),
	// 			]
	// 		}),
	// 	);
	// }

	return merge(common(config), {
		watch: config.WATCH === true,
		plugins: plugins
	});
};

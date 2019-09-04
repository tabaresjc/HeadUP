const webpack = require('webpack');
const merge = require('webpack-merge');
const common = require('./webpack.common.js');
const UglifyJsPlugin = require('uglifyjs-webpack-plugin');

module.exports = function (config) {
	return merge(common(config), {
		module: {
			rules: [
				{
					test: /\.js$/,
					exclude: /(node_modules)/,
					use: {
						loader: 'babel-loader',
						options: {
							presets: ['babel-preset-env']
						}
					}
				}
			]
		},
		plugins: [
			new webpack.DefinePlugin({
				'process.env': {
					NODE_ENV: JSON.stringify('production')
				}
			}),
			new UglifyJsPlugin({
				parallel: true,
				uglifyOptions: {
					output: {
						comments: false,
						beautify: false,
					},
					mangle: {
						keep_fnames: true,
					},
					compress: {
						warnings: false,
					}
				}
			})
		]
	});
};

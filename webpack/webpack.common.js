const path = require('path');
const webpack = require('webpack');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const ExtractTextPlugin = require('extract-text-webpack-plugin');

module.exports = function(config) {
	const cssFileName = config.IS_PRD ? 'css/[name].[chunkhash].v2.css' : 'css/[name].css';
	const jsFileName = config.IS_PRD ? 'js/[name].[chunkhash].v2.js' : 'js/[name].js';

	const extractSass = new ExtractTextPlugin({
		filename: cssFileName,
		disable: false
	});

	return {
		entry: {
			main: './static/assets/main/scripts/main/index.js',
			lp: './static/assets/main/scripts/lp/index.js',
			admin: './static/assets/admin/scripts/index.js',
		},
		output: {
			path: path.resolve(config.APP_DIR, 'static/dist/'),
			filename: jsFileName,
			publicPath: '/static/dist/'
		},
		resolve: {
			alias: {
				'Assets': path.resolve(config.APP_DIR, 'static/assets'),
				'Lib': path.resolve(config.APP_DIR, 'node_modules'),
			},
		},
		module: {
			rules: [{
					test: /\.(s*)css$/,
					use: extractSass.extract({
						use: [{
							loader: 'css-loader'
						}, {
							loader: 'postcss-loader',
							options: {
								path: path.resolve(config.APP_DIR, 'webpack/'),
							}
						}, {
							loader: 'sass-loader',
							options: {
								includePaths: [
									path.resolve(config.APP_DIR, 'node_modules')
								]
							}
						}],
						// use style-loader in development
						fallback: 'style-loader'
					})
				},
				{
					test: /\.(woff|woff2|eot|ttf|svg)$/,
					loader: 'url-loader?limit=1024&name=fonts/[name].[hash].[ext]'
				}
			]
		},
		plugins: [
			new webpack.ProvidePlugin({
				$: 'jquery',
				jQuery: 'jquery'
			}),
			extractSass,
			new HtmlWebpackPlugin({
				template: path.resolve(config.APP_DIR, 'app/templates/src/layout/main.html'),
				filename: path.resolve(config.APP_DIR, 'app/templates/main/layout/base.html'),
				inject: false,
				chunks: ['main'],
			}),
			new HtmlWebpackPlugin({
				template: path.resolve(config.APP_DIR, 'app/templates/src/layout/home.html'),
				filename: path.resolve(config.APP_DIR, 'app/templates/main/layout/home.html'),
				inject: false,
				chunks: ['lp'],
			}),
			new HtmlWebpackPlugin({
				template: path.resolve(config.APP_DIR, 'app/templates/src/layout/admin.html'),
				filename: path.resolve(config.APP_DIR, 'app/templates/admin/layout/base.html'),
				inject: false,
				chunks: ['admin'],
			})
		]
	}
};

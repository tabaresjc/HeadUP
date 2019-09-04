const path = require('path');
const webpack = require('webpack');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const ExtractTextPlugin = require('extract-text-webpack-plugin');
const VueLoaderPlugin = require('vue-loader/lib/plugin');

module.exports = function (config) {
	const cssFileName = config.IS_PRD ? 'css/[name].[hash:8].css' : 'css/[name].css';
	const jsFileName = config.IS_PRD ? 'js/[name].[hash:8].js' : 'js/[name].js';

	const extractSass = new ExtractTextPlugin({
		filename: cssFileName,
		disable: false
	});

	const assets = {
		admin: './app/assets/admin/scripts/index.js',
		main: './app/assets/main/scripts/index.js',
	};

	const plugins = [
		new VueLoaderPlugin(),
		new webpack.ProvidePlugin({
			$: 'jquery',
			jQuery: 'jquery'
		}),
		extractSass
	];

	Object.entries(assets).forEach((asset) => {
		const [key, _] = asset;

		plugins.push(new HtmlWebpackPlugin({
			template: path.resolve(config.APP_DIR, 'app/templates/src/assets/script.html'),
			filename: path.resolve(config.APP_DIR, `app/templates/shared/assets/scripts/${key}.html`),
			inject: false,
			chunks: [key],
		}));

		plugins.push(new HtmlWebpackPlugin({
			template: path.resolve(config.APP_DIR, 'app/templates/src/assets/style.html'),
			filename: path.resolve(config.APP_DIR, `app/templates/shared/assets/styles/${key}.html`),
			inject: false,
			chunks: [key],
		}));
	});

	return {
		entry: assets,
		output: {
			path: path.resolve(config.APP_DIR, 'static/dist/'),
			filename: jsFileName,
			publicPath: '/static/dist/'
		},
		resolve: {
			alias: {
				'vue$': 'vue/dist/vue.esm.js',
				'Static': path.resolve(config.APP_DIR, 'static'),
				'Assets': path.resolve(config.APP_DIR, 'app/assets'),
				'Lib': path.resolve(config.APP_DIR, 'node_modules'),
			},
		},
		module: {
			rules: [
				{
					test: /\.vue$/,
					loader: 'vue-loader'
				},
				{
					test: /.js$/,
					loader: 'babel-loader'
				},
				{
					test: /\.(s*)css$/,
					use: extractSass.extract({
						use: [{
							loader: 'css-loader'
						}, {
							loader: 'postcss-loader',
							options: {
								config: {
									path: path.resolve(config.APP_DIR, 'webpack/config'),
								}
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
					loader: 'url-loader?limit=2048&name=fonts/[name].[hash].[ext]'
				}
			]
		},
		plugins: plugins
	}
};

const path = require('path');

const config = {
	APP_DIR: path.resolve(__dirname),
	IS_PRD: false
};

module.exports = function(env) {
	const c = Object.assign(config, {
		IS_PRD: env === 'prd',
		WATCH: env === 'watch'
	});

	if (env === 'dev' || env === 'watch') {
		return require('./webpack/webpack.dev.js')(c);
	} else if (env === 'prd') {
		return require('./webpack/webpack.prd.js')(c);
	}

	console.info(
		'Wrong build parameters.' + '\n' +
		'Usage:' + '\n' +
		'`webpack -p --env dev` or `webpack -p --env prd`'
	);
};

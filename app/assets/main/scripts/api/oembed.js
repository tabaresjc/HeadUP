'use strict';

import { ApiBase } from 'Assets/helpers';
import { AppConfig } from 'Assets/main/scripts/appConfig';

export class OEmbedApiService extends ApiBase {

	constructor(url) {
		super(url || AppConfig.oembedApiUrl);
	}

	getItem(url) {
		const endpoint = `item`;
		const params = {
			url: url
		};

		return this.request({
			url: endpoint,
			method: 'GET',
			params: params
		});
	}
}

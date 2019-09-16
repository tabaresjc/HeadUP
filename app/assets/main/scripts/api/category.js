'use strict';

import { ApiBase } from 'Assets/helpers';
import { AppConfig } from 'Assets/main/scripts/appConfig';

export class CategoryApiService extends ApiBase {

	constructor(url) {
		super(url || AppConfig.categoryApiUrl);
	}

	getItems(orderby = 'name', desc = '0') {
		const params = {
			orderby: orderby,
			desc: desc,
		};

		return this.request({
			url: '/',
			method: 'GET',
			params: params
		});
	}
}

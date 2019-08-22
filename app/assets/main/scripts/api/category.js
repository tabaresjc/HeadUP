"use strict";

import { ApiBase } from 'Assets/helpers';

export class CategoryApiService extends ApiBase {

	constructor(url) {
		super(url);
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

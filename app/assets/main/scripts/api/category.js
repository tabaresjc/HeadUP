"use strict";

import { ApiBase } from 'Assets/helpers';

export class CategoryApiService extends ApiBase {

	constructor(url) {
		super(url);
	}

	getItems(orderby = 'name', desc = '0') {
		const endpoint = ``;
		const data = {
			orderby: orderby,
			desc: desc,
		};

		return this.fetch(endpoint, data, {
			method: 'GET'
		});
	}
}

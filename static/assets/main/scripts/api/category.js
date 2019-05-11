"use strict";

import { ApiBase } from 'Assets/main/scripts/lib';

export class CategoryApiHelper extends ApiBase {

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

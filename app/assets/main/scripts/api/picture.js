"use strict";

import { ApiBase } from 'Assets/helpers';

export class PictureApiService extends ApiBase {

	constructor(url) {
		super(url);
	}

	getItem(id) {
		const endpoint = `item/${id}`;

		return this.fetch(endpoint, {}, {
			method: 'GET'
		});
	}

	upload(data, srcOptions) {
		const endpoint = `upload`;

		const options = Object.assign({
			method: 'POST'
		}, srcOptions || {});

		return this.fetch(endpoint, data || {}, options);
	}

	delete(id) {
		const endpoint = `delete/${id}`;

		return this.fetch(endpoint, {}, {
			method: 'POST'
		});
	}
}

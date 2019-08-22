"use strict";

import { ApiBase } from 'Assets/helpers';

export class UserApiService extends ApiBase {

	constructor(url) {
		super(url);
	}

	getProfile() {
		const endpoint = `profile`;

		return this.request({
			url: endpoint,
			method: 'GET'
		});
	}
}

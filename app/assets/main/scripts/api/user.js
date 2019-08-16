"use strict";

import { ApiBase } from 'Assets/helpers';

export class UserApiService extends ApiBase {

	constructor(url) {
		super(url);
	}

	getProfile() {
		const endpoint = `profile`;

		return this.fetch(endpoint, {}, {
			method: 'GET'
		});
	}

	getVotes() {
		const endpoint = `item/${ id }`;

		return this.fetch(endpoint, {}, {
			method: 'GET'
		});
	}
}

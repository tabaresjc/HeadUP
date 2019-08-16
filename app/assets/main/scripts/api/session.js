"use strict";

import { ApiBase } from 'Assets/helpers';

export class SessionApiService extends ApiBase {

	constructor(url) {
		super(url);
	}

	login(user, email) {
		const endpoint = `login`;
		const data = {
			user: user,
			email: email
		};

		return this.fetch(endpoint, data, {
			method: 'POST'
		});
	}

	logout() {
		const endpoint = `logout`;

		return this.fetch(endpoint, {}, {
			method: 'POST'
		});
	}
}

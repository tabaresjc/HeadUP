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

		return this.request({
			url: endpoint,
			method: 'POST',
			data: data
		});
	}

	logout() {
		const endpoint = `logout`;

		return this.request({
			url: endpoint,
			method: 'POST'
		});
	}
}

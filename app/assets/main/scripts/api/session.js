'use strict';

import { ApiBase } from 'Assets/helpers';
import { AppConfig } from 'Assets/main/scripts/appConfig';

export class SessionApiService extends ApiBase {

	constructor(url) {
		super(url || AppConfig.sessionApiUrl);
	}

	login(data) {
		const endpoint = 'login';

		return this.request({
			url: endpoint,
			method: 'POST',
			data: data
		});
	}

	logout() {
		const endpoint = 'logout';

		return this.request({
			url: endpoint,
			method: 'POST'
		});
	}
}

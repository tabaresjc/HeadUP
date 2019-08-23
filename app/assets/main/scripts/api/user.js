'use strict';

import { ApiBase } from 'Assets/helpers';
import { AppConfig } from 'Assets/main/scripts/config';

export class UserApiService extends ApiBase {

	constructor(url) {
		super(url || AppConfig.userApiUrl);
	}

	getProfile() {
		const endpoint = 'profile';

		return this.request({
			url: endpoint,
			method: 'GET'
		});
	}
}

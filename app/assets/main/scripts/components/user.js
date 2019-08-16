"use strict";

import { LocalStorageHelper } from 'Assets/helpers';
import { AppConfig } from 'Assets/main/scripts/config';
import { UserApiService, SessionApiService } from 'Assets/main/scripts/api';

export class UserComponent {

	constructor(options) {
		this._options = Object.assign({
			containerSel: '.user-component',
		}, options || {});
	}

	onLoad() {
		this.start();
	}

	start() {
		const container = this._pageContainer = document.querySelector(this._options.containerSel);

		if (!container) {
			return;
		}

		this._localStorageHelper = new LocalStorageHelper();
		this._userApiService = new UserApiService(AppConfig.userApiUrl);
		this._sessionApiService = new SessionApiService(AppConfig.sessionApiUrl);

		this._getProfile();
	}

	_getProfile() {
		this._userApiService.getProfile()
			.then(profile => {
				console.log(profile)
			});
	}
}

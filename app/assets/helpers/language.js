'use strict';

import { ApiBase } from 'Assets/helpers';

export class LanguageApiHelper extends ApiBase {

	constructor(url) {
		super(url);
	}

	getDictionary(lang) {
		const endpoint = `${lang}.json`;

		return this.request({
			url: endpoint,
			method: 'GET',
			params: {
				q: this._getToken()
			},
			omitLang: true
		});
	}

	_getToken() {
		var dt = new Date();
		dt.setHours(dt.getHours(), 0, 0, 0);
		return dt.getTime();
	}

	getCurrentLanguage() {
		if (!this._lang) {
			this._lang = GetLanguage();
		}

		return this._lang;
	}
}

export function GetLanguage() {
	return document.querySelector('html').getAttribute('lang');
}


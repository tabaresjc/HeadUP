"use strict";

import { ApiBase } from 'Assets/helpers';

export class LanguageApiHelper extends ApiBase {

	constructor(url) {
		super(url);
		this.init();
	}

	init() {
		const lang = this.getCurrentLanguage();

		this._getDictionary(lang)
			.then(r => {
				this.data = r;
			});
	}

	_getDictionary(lang) {
		const endpoint = `${lang}.json`;

		return this.fetch(endpoint, {}, {
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

	translate(name, obj = null) {
		if (!this.data.hasOwnProperty(name)) {
			return name;
		}

		const s = this.data[name].toString().trim();

		if (!obj) {
			return s;
		}

		return Object.entries(obj).reduce(function (d, pair) {
			const [key, value] = pair;
			return d.replace(`{${key}}`, value);
		}, s);
	}

	getCurrentLanguage() {
		if (!this._lang) {
			this._lang = GetLanguage();
		}

		return this._lang;
	}
}

export function LanguageSetupAdapter(appConfig) {
	if (!String.prototype.hu_t) {
		const langApiHelper = new LanguageApiHelper(appConfig.languageApiUrl);

		appConfig.current_lang = langApiHelper.getCurrentLanguage();

		// setup translation helper for strings, to be used in templates
		String.prototype.hu_i18n = function (obj) {
			'use strict';

			return langApiHelper.translate(this, obj);
		};
	}
}

export function GetLanguage() {
	return document.querySelector('html').getAttribute('lang');
}

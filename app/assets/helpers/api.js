"use strict";

import { GetLanguage } from 'Assets/helpers';

export class ApiBase {
	constructor(baseUrl) {
		this.baseUrl = baseUrl;
	}

	fetch(endpoint, srcData, srcOptions) {
		const options = Object.assign(
			{
				method: 'GET',
				progress: () => { }
			},
			srcOptions
		);

		return new Promise((resolve, reject) => {
			const xhr = this._getHandler(endpoint, options);
			const data = this._buildData(srcData);

			this._attachListeners(xhr, resolve, reject, options);

			xhr.send(data);
		});
	}

	_getHandler(endpoint, options) {
		const xhr = new XMLHttpRequest();
		const url = this._getUrl(endpoint, options);

		xhr.open(options.method, url, true);
		xhr.responseType = 'json';

		return xhr;
	}

	_getUrl(endpoint, options) {
		const url = `${this.baseUrl}/${endpoint}`;
		let qs = [];

		if (options.params && typeof options.params === 'object' && options.method === 'GET') {
			qs = Object.entries(options.params).map(function (pair) {
				const [key, value] = pair;
				return `${key}=${encodeURIComponent(value)}`;
			});
		}

		if (!options.omitLang) {
			qs.push(`lang=${GetLanguage()}`);
		}

		return `${url}?${qs.join('&')}`;
	}

	_buildData(srcData) {
		// prepare the form data.
		const d = new FormData();
		const apiToken = this._getToken();

		for (const [k, v] of Object.entries(srcData)) {
			d.append(k, v);
		}

		// append the api token, so that the request can be accepted
		d.append('csrf_token', apiToken);

		return d;
	}

	// Initializes XMLHttpRequest listeners.
	_attachListeners(xhr, resolve, reject, options) {
		const genericErrorText = `[HUP] Unable to process request`;

		xhr.addEventListener('error', (err) => reject(console.log(err)));
		xhr.addEventListener('abort', (err) => reject(console.log(err)));
		xhr.addEventListener('load', () => {
			let response = xhr.response;

			// ie fix
			if (typeof response === 'string') {
				response = JSON.parse(response);
			}

			// reject the xhr response when the api throws an error
			if (!response || !response.status || !response.data) {
				return reject(
					response && response.message
						? response.message
						: genericErrorText
				);
			}

			resolve(response.data);
		});

		// Upload progress when it is supported and provided by the user
		if (!xhr.upload || typeof options.progress !== 'function') {
			return;
		}

		xhr.upload.addEventListener('progress', evt => {
			if (evt.lengthComputable) {
				options.progress({ total: evt.total, loaded: evt.loaded });
			}
		});
	}

	_getToken() {
		const paramName = 'csrf-token';
		const q = document.querySelectorAll(`meta[name="${paramName}"]`);

		if (!q || !q.length) {
			return '';
		}

		const n = q[0];

		return n.getAttribute('content');
	}
}

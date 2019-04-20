"use strict";

export class SpinnerHelper {
	constructor() {
		this._init();
	}

	_init() {
		this._spinner = document.getElementById('spinner');

		if (!this._spinner) {
			this._spinner = document.createElement('div');
			this._spinner.setAttribute('id', 'spinner');

			document.body.appendChild(this._spinner);
		}
	}

	start() {
		this._spinner.classList.add('loading');
	}

	stop(timeOut) {
		setTimeout(() => {
			this._spinner.classList.remove('loading');
		}, timeOut || 250);
	}
}

'use strict';

import { UtilHelper } from 'Assets/helpers';

export class MenuComponent {
	constructor(options) {
		this._elementId = location.hash;
		this._options = Object.assign({
			scrollToTime: 500
		}, options || {});
	}

	onReady() {
		setTimeout(this.stopScrolling.bind(this));
	}

	onLoad() {
		setTimeout(this.scrollToElement.bind(this),
			this._options.scrollToTime
		);
	}

	stopScrolling() {
		if (location.hash) {
			this._elementId = location.hash;
			window.scrollTo(0, 0);
		}
	}

	scrollToElement() {
		if (!this._elementId) {
			return;
		}

		UtilHelper.smootScroll(this._elementId);
	}
}

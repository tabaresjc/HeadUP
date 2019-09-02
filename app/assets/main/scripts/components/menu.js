'use strict';

import $ from 'jquery';
import { AppConfig } from 'Assets/main/scripts/appConfig';

export class MenuComponent {
	constructor(options) {
		this._mediumScreenSize = AppConfig.screens.medium;
		this._elementId = location.hash;
		this._options = Object.assign({
			scrollToTime: 2000
		}, options || {});
	}

	onReady() {
		setTimeout(this.stopScrolling.bind(this));
	}

	onLoad() {
		setTimeout(this.scrollToElement.bind(this),
			this._options.scrollToTime);
	}

	stopScrolling() {
		if (location.hash) {
			this._elementId = location.hash;
			window.scrollTo(0, 0);
		}
	}

	scrollToElement() {
		if (this._elementId && $(this._elementId).length) {
			var y = $(this._elementId).offset().top - 80;
			$('html, body').animate({ scrollTop: `${y}px` });
		}
	}
}

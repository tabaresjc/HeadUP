"use strict";

import $ from 'jquery';
import _ from 'lodash';
import { AppConfig } from 'Assets/main/scripts/config';

export class MenuComponent {
	constructor() {
		this._mediumScreenSize = AppConfig.screens.medium;
		this._elementId = location.hash;
	}

	onReady() {
		setTimeout(this.stopScrolling.bind(this), 0);
	}

	onLoad() {
		setTimeout(this.scrollToElement.bind(this), 0);
	}

	onResize() {
		_.debounce(() => {
			let navbarEl = $('#readable-navbar-collapse');

			if (!navbarEl.length) {
				return;
			}

			let w = this.screenWidth();

			if (w > this._mediumScreenSize) {
				navbarEl
					.removeAttr('style')
					.removeClass('in');
			}
		}, 200);
	}

	screenWidth() {
		return (window.innerWidth > 0) ? window.innerWidth : screen.width;
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
			$(document).scrollTop(y);
		}
	}
}

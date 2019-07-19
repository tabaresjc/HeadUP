"use strict";

import $ from 'jquery';

export class HomeModule {

	constructor(options) {
		this._moduleId = 'fullpage';
		this._options = Object.assign({
			fullpage: {
				sectionsColor: ['#ffffff', '#ffffff', '#ffffff', '#ffffff', '#ffffff'],
				scrollingSpeed: 500,
				slidesNavigation: 'true'
			}
		}, options || {});
	}

	onLoad() {
		this.start();
	}

	start() {
		const pageContainer = document.getElementById(this._moduleId);

		// check if current page match the id of this module
		if (!pageContainer) {
			return;
		}

		$(pageContainer).fullpage(this._options.fullpage);
	}
}

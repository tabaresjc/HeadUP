"use strict";

import $ from 'jquery';
import _ from 'lodash';
import { AppConfig } from 'Assets/main/scripts/config';

export class SidebarComponent {
	constructor() {
		this._mediumScreenSize = AppConfig.screens.medium;
	}

	onLoad() {
		this.updateSidebar();
	}

	onResize() {
		_.debounce(() => {
			this.updateSidebar();
		}, 200);
	}

	updateSidebar() {
		let w = this.screenWidth();
		let sidebarWrapper = $('.sidebar-wrapper');
		let sidebarContainer = $('#main-sidebar');

		if (!sidebarWrapper.length || !sidebarContainer.length) {
			return;
		}

		if (w > this._mediumScreenSize) {
			let ws = sidebarContainer.width();

			sidebarWrapper.css({
				'position': 'fixed',
				'width': ws + 'px'
			});
		} else {
			sidebarWrapper.removeAttr('style');
		}
	}

	screenWidth() {
		return (window.innerWidth > 0) ? window.innerWidth : screen.width;
	}
}

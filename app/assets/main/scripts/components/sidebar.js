'use strict';

import _ from 'lodash';
import { AppConfig } from 'Assets/main/scripts/appConfig';

export class SidebarComponent {
	constructor() {
		this._mediumScreenSize = AppConfig.screens.medium;
		this._onResizeUpdateSidebar = _.debounce(this.updateSidebar.bind(this), 200);
	}

	onLoad() {
		this.updateSidebar();
	}

	onResize() {
		this._onResizeUpdateSidebar();
	}

	updateSidebar() {
		let w = this.screenWidth();
		let sidebarWrapper = document.querySelector('.sidebar-wrapper');
		let sidebarContainer = document.getElementById('main-sidebar');

		if (!sidebarWrapper || !sidebarContainer) {
			return;
		}

		if (w > this._mediumScreenSize) {
			let ws = sidebarContainer.offsetWidth;
			sidebarWrapper.setAttribute('style', `position: fixed; width:${ws - 30}px`)
		} else {
			sidebarWrapper.removeAttribute('style');
		}
	}

	screenWidth() {
		return (window.innerWidth > 0) ? window.innerWidth : screen.width;
	}
}

'use strict';

import { AppConfig } from 'Assets/main/scripts/appConfig';
import { UtilHelper } from 'Assets/helpers';

// Components
import {
	MenuComponent,
	SidebarComponent,
	CommentComponent,
	StoryEditorComponent,
	StoryShowComponent
} from 'Assets/main/scripts/components';

import { VueLoader } from 'Assets/main/scripts/config/vue';

const loaders = [
	new VueLoader(),
	new MenuComponent(),
	new SidebarComponent(),
	new CommentComponent(),
	new StoryEditorComponent(),
	new StoryShowComponent()
];

// setup on ready events
loaders.forEach(l => {
	if (l.onReady && typeof l.onReady === 'function') {
		l.onReady();
	}
});


let onResizeDebounced = UtilHelper.debounce(() => {
	loaders.forEach(l => {
		if (l.onResize && typeof l.onResize === 'function') {
			try {
				l.onResize();
			} catch (error) {
				console.error(error);
			}
		}
	});
}, 250);

// setup on resize events
window.addEventListener('resize', onResizeDebounced);

// setup on load events
document.addEventListener('DOMContentLoaded', () => {
	loaders.forEach(l => {
		if (typeof l === 'function') {
			l(AppConfig);
		} else if (l.onLoad && typeof l.onLoad === 'function') {
			try {
				l.onLoad();
			} catch (error) {
				console.error(error);
			}
		}
	});
});

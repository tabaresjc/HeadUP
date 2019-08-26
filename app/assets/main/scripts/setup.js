'use strict';

import { AppConfig } from './config';

// Components
import { MenuComponent, SidebarComponent, CommentComponent, VoteComponent } from './components';
// modules
import { HomeModule, StoryEditorModule, StoryShowModule } from './modules';
import { VueLoader } from './vue';

const loaders = [
	new VueLoader(),
	new MenuComponent(),
	new SidebarComponent(),
	new CommentComponent(),
	new VoteComponent(),
	new HomeModule(),
	new StoryEditorModule(),
	new StoryShowModule()
];

// setup on ready events
loaders.forEach(l => {
	if (l.onReady && typeof l.onReady === 'function') {
		l.onReady();
	}
});

// setup on resize events
$(window).on('resize', () => {
	loaders.forEach(l => {
		if (l.onResize && typeof l.onResize === 'function') {
			try {
				l.onResize();
			} catch (error) {
				console.error(error);
			}
		}
	});
});

// setup on load events
$(window).on('load', () => {
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

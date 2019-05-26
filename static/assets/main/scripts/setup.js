"use strict";

import { MenuComponent, SidebarComponent, CommentComponent } from './components';
import { HomeModule, FeedModule, StoryEditorModule } from './modules';

const loaders = [
	new MenuComponent(),
	new SidebarComponent(),
	new CommentComponent(),
	new HomeModule(),
	new FeedModule(),
	new StoryEditorModule()
];

// setup on ready events
loaders.forEach(l => {
	if (typeof l.onReady === 'function') {
		l.onReady();
	}
});

// setup on resize events
$(window).on('resize', () => {
	loaders.forEach(l => {
		if (typeof l.onResize === 'function') {
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
		if (typeof l.onLoad === 'function') {
			try {
				l.onLoad();
			} catch (error) {
				console.error(error);
			}
		}
	});
});

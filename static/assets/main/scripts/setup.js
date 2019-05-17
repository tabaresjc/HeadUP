"use strict";

import { MenuComponent, SidebarComponent, CommentComponent } from './components';
import { HomeModule, StoryEditorModule } from './modules';

const loaders = [
	new MenuComponent(),
	new SidebarComponent(),
	new CommentComponent(),
	new HomeModule(),
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
			l.onResize();
		}
	});
});

// setup on load events
$(window).on('load', () => {
	loaders.forEach(l => {
		if (typeof l.onLoad === 'function') {
			l.onLoad();
		}
	});
});

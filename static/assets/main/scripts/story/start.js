"use strict";

import { EditorHelper } from './editor';


document.addEventListener('DOMContentLoaded', () => {
	const editor = new EditorHelper({
		containerId: 'story-container',
		titleId: 'story-title',
		bodyId: 'story-body',
		publishId: 'story-publish',
		saveDraftId: 'story-save-draft'
	});

	editor.start();
});

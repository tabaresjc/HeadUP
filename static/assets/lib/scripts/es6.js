// ES6 helpers

Document.prototype.ready = cb️ => {
	if (cb️ && typeof cb️ === 'function') {
		document.addEventListener('DOMContentLoaded', () => {
			if (document.readyState === 'interactive' || document.readyState === 'complete') {
				return cb️();
			}
		});
	}
};

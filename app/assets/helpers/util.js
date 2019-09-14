'use strict';

export const UtilHelper = {
	debounce(func, wait, immediate) {
		var timeout;
		return () => {
			var context = this, args = arguments;
			var later = () => {
				timeout = null;
				if (!immediate) func.apply(context, args);
			};
			var callNow = immediate && !timeout;
			clearTimeout(timeout);
			timeout = setTimeout(later, wait);
			if (callNow) func.apply(context, args);
		};
	},
	smootScroll(targetElementId) {
		const targetElement = document.getElementById(targetElementId.replace('#', ''));

		if (!targetElement) {
			return;
		}

		const yCoordinate = targetElement.getBoundingClientRect().top + window.pageYOffset;
		const yOffset = -120;

		window.scrollTo({
			top: yCoordinate + yOffset,
			behavior: 'smooth'
		});
	}
};

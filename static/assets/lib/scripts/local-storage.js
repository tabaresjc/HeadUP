(function(document, root, undefined) {
	'use strict';

	var MyLocalStorage = root.MyLocalStorage = function() {
		var self = this;

		var myLocalStorageName = getHashCode(root.location.hostname),
			myLocalStorageContainer = getLocalStorage(myLocalStorageName);

		self.getRecord = function(key) {
			return myLocalStorageContainer[key] || {}
		}

		self.saveRecord = function(key, record) {
			myLocalStorageContainer[key] = record || {};
			setLocalStorage(myLocalStorageName, myLocalStorageContainer);
		}
	}

	/**
	 * Get a value from localStorage (or empty object if it doesn't exist)
	 *
	 * @param   {String}  key  The local storage key
	 *
	 * @return  {Object}
	 */
	function getLocalStorage(key) {
		return JSON.parse((window.localStorage && window.localStorage.getItem(key)) || '{}')
	}

	/**
	 * Store an object in localStorage
	 *
	 * @param  {String}  key  The local storage key
	 * @param  {Object}  obj  The object to store
	 */
	function setLocalStorage(key, obj) {
		window.localStorage.setItem(key, JSON.stringify(obj));
	}

	/**
	 * Calculate hashcode from string.
	 *
	 * @return  {String}
	 */
	function getHashCode(str) {
		str = str || {};

		var hash = 0,
			i, chr;

		if (str.length === 0) {
			return hash;
		}

		for (i = 0; i < str.length; i++) {
			chr = str.charCodeAt(i);
			hash = ((hash << 5) - hash) + chr;
			hash |= 0; // Convert to 32bit integer
		}

		return hash;
	}

})(document, window);

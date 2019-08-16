"use strict";

export class LocalStorageHelper {

	constructor() {
		this._myLocalStorageName = this._getHashCode(`${window.location.hostname}`);
		this._myLocalStorageContainer = this._getLocalStorage(this._myLocalStorageName);
	}

	get(key) {
		return this._myLocalStorageContainer[key] || {};
	}

	set(key, record) {
		this._myLocalStorageContainer[key] = record || {};
		this._setLocalStorage(this._myLocalStorageName, myLocalStorageContainer);
	}

	/**
	 * Get a value from localStorage (or empty object if it doesn't exist)
	 *
	 * @param   {String}  key  The local storage key
	 * @return  {Object}
	 */
	_getLocalStorage(key) {
		return JSON.parse((window.localStorage && window.localStorage.getItem(key)) || '{}')
	}

	/**
	 * Store an object in localStorage
	 *
	 * @param  {String}  key  The local storage key
	 * @param  {Object}  obj  The object to store
	 */
	_setLocalStorage(key, obj) {
		window.localStorage.setItem(key, JSON.stringify(obj));
	}

	/**
	 * Calculate hashcode from string.
	 *
	 * @return  {String}
	 */
	_getHashCode(str) {
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
}




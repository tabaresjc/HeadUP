'use strict';

import Vue from 'vue';
import VueI18n from 'vue-i18n';
import { AppConfig } from 'Assets/main/scripts/config';
import { LanguageApiHelper } from 'Assets/helpers';
import store from './store';

// Vue.js components
import UserProfile from './components/user/user-profile.vue';
import UserSidebar from './components/user/user-sidebar.vue';
import StoryFeed from './components/story/story-feed.vue';

export class VueLoader {
	constructor(options) {
		this._options = Object.assign({
			containerSel: '#app-container'
		}, options || {});
	}

	onReady() {
		this.start();
	}

	start() {
		const container = this._pageContainer = document.querySelector(this._options.containerSel);

		if (!container) {
			return;
		}

		this._langApiHelper = new LanguageApiHelper(AppConfig.languageApiUrl);
		this._vueComponents = {
			UserProfile,
			UserSidebar,
			StoryFeed
		};

		Vue.use(VueI18n);
		this._i18n = new VueI18n();

		// load root instance of Vue
		this._vueApp = new Vue({
			i18n: this._i18n,
			store: store,
			components: this._vueComponents
		});

		this.loadTranslationData();
	}

	loadTranslationData() {
		const locale = this._langApiHelper.getCurrentLanguage();
		this._langApiHelper.getDictionary(locale)
			.then(data => {
				this._i18n.setLocaleMessage(locale, data);
				this.setLocale(locale);
			});
	}

	setLocale(locale) {
		this._i18n.locale = locale;
		if (!this._loaded) {
			this._vueApp.$mount('#app-container');
			this._loaded = true;
		}
	}
}







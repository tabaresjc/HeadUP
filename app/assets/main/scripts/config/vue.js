'use strict';

import Vue from 'vue';
import VueI18n from 'vue-i18n';
import VueSocketIOExt from 'vue-socket.io-extended';
import { AppConfig } from 'Assets/main/scripts/appConfig';
import { LanguageApiHelper } from 'Assets/helpers';

// Required components
import $socket from  'Assets/main/scripts/config/socket';
import store from 'Assets/main/scripts/store';

// Vue.js components
import UserProfile from 'Assets/main/scripts/components/user/user-profile.vue';
import UserSidebar from 'Assets/main/scripts/components/user/user-sidebar.vue';

import StoryFeed from 'Assets/main/scripts/components/feed/story-feed.vue';
import StorySocialBar from 'Assets/main/scripts/components/feed/story-social-bar.vue';

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
			StoryFeed,
			StorySocialBar
		};

		Vue.use(VueI18n);
		Vue.use(VueSocketIOExt, $socket, { store });
		this._i18n = new VueI18n();

		// load root instance of Vue
		this._vueApp = new Vue({
			i18n: this._i18n,
			store: store,
			components: this._vueComponents,
			sockets: {
				connect: function () {
					console.log('[HeadUP] socket connected');
				},
				disconnect() {
					console.log('[HeadUP] socket disconnected');
				}
			}
		});

		this.loadTranslationData()
			// start app
			.then(() => this.mountApp());
	}

	loadTranslationData() {
		const locale = this._langApiHelper.getCurrentLanguage();
		return this._langApiHelper.getDictionary(locale)
			.then(data => {
				this._i18n.setLocaleMessage(locale, data);
				this._i18n.locale = locale;
			});
	}

	mountApp() {
		if (!this._loaded) {
			this._vueApp.$mount('#app-container');
			this._loaded = true;
		}
	}
}







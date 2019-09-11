'use strict';

import Vue from 'vue';
import VueI18n from 'vue-i18n';
import VueSocketIOExt from 'vue-socket.io-extended';
import SocialSharing from 'vue-social-sharing';
import VueMoment from 'vue-moment';

import { AppConfig } from 'Assets/main/scripts/appConfig';
import { LanguageApiHelper, MomentInstance } from 'Assets/helpers';

// Required components
import $socket from  'Assets/main/scripts/config/socket';
import store from 'Assets/main/scripts/store';

// Vue.js components
import UserProfile from 'Assets/main/scripts/components/user/user-profile.vue';
import UserSidebar from 'Assets/main/scripts/components/user/user-sidebar.vue';

import StoryFeed from 'Assets/main/scripts/components/feed/story-feed.vue';
import StoryFeedItem from 'Assets/main/scripts/components/feed/story-feed-item.vue';
import StorySocialBar from 'Assets/main/scripts/components/feed/story-social-bar.vue';

import Comments from 'Assets/main/scripts/components/comment/comments.vue';
import CommentList from 'Assets/main/scripts/components/comment/comment-list.vue';
import CommentItem from 'Assets/main/scripts/components/comment/comment-item.vue';
import CommentForm from 'Assets/main/scripts/components/comment/comment-form.vue';
import SessionsLogin from 'Assets/main/scripts/components/sessions/sessions-login.vue';

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
		const t = document.querySelector('[escape-vuejs]');

		if (!container || t) {
			return;
		}

		this._langApiHelper = new LanguageApiHelper(AppConfig.languageApiUrl);
		this._momentInstance = MomentInstance();

		this._vueComponents = {
			UserProfile,
			UserSidebar,
			StoryFeed,
			StoryFeedItem,
			StorySocialBar,
			Comments,
			CommentList,
			CommentItem,
			CommentForm,
			SessionsLogin
		};

		// ignore custom elements
		Vue.config.ignoredElements = this._vueIgnoredElements();

		Vue.use(VueI18n);
		Vue.use(VueSocketIOExt, $socket, { store });
		Vue.use(SocialSharing);
		Vue.use(VueMoment, {
			moment: this._momentInstance
		});

		this._i18n = new VueI18n();

		// load root instance of Vue
		this._vueApp = new Vue({
			i18n: this._i18n,
			store: store,
			components: this._vueComponents,
			sockets: {
				connect: function () {
					// console.log('[HeadUP] socket connected');
				},
				disconnect() {
					// console.log('[HeadUP] socket disconnected');
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

	_vueIgnoredElements() {
		return [
			'oembed'
		];
	}
}







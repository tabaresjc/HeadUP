import Vuex from 'vuex';
import Vue from 'vue';
import state from './state';
import getters from './getters';
import actions from './actions';
import mutations from './mutations';
import notification from './modules/notification';
import stories from './modules/stories';
import user from './modules/user';

Vue.use(Vuex);

export default new Vuex.Store({
	modules: {
		notification,
		stories,
		user
	},
	state: state,
	getters: getters,
	actions: actions,
	mutations: mutations
});









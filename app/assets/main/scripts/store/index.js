import Vuex from 'vuex';
import Vue from 'vue';
import state from './state';
import getters from './getters';
import actions from './actions';
import mutations from './mutations';
// data store models
import notification from './modules/notification';
import stories from './modules/stories';
import user from './modules/user';
import comments from './modules/comments';

Vue.use(Vuex);

export default new Vuex.Store({
	modules: {
		notification,
		stories,
		user,
		comments
	},
	state: state,
	getters: getters,
	actions: actions,
	mutations: mutations
});









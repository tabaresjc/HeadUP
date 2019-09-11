<template>
	<div class="btn-group custom_dropdown">
		<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
			<i class="glyphicon glyphicon-user"></i> <span class="caret"></span>
		</button>
		<ul class="dropdown-menu dropdown-menu-right">
			<li v-if="!user.is_authenticated"><a href="#user-session-modal" data-toggle="modal">{{ $t("LOGIN_BTN") }}</a></li>
			<li v-if="!user.is_authenticated"><a :href="endpoints.sessions_signup">{{ $t("REGISTER_BTN") }}</a></li>

			<li v-if="user.is_authenticated"><a :href="endpoints.user_profile.replace('999999999999', `${user.id}`)">{{ $t("APP_PROFILE") }}</a></li>
			<li v-if="user.is_authenticated" role="separator" class="divider"></li>
			<li v-if="user.is_authenticated"><a :href="endpoints.post_list">{{ $t("POST_LIST") }}</a></li>
			<li v-if="user.is_authenticated"><a :href="endpoints.draft_list">{{ $t("POST_DRAFT_LIST") }}</a></li>
			<li v-if="user.is_authenticated"><a :href="endpoints.story_new">{{ $t("POST_CREATE") }}</a></li>
			<li v-if="user.is_authenticated" role="separator" class="divider"></li>
			<li v-if="user.is_authenticated"><a href="javascript:;" @click="logout()">{{ $t("APP_SIGN_OUT") }}</a></li>
		</ul>
	</div>
</template>

<script>
import {mapState, mapGetters, mapActions} from 'vuex';

export default {
	name: 'UserProfile',
	props: {
    	endpoints: {type: Object}
	},
	data () {
		return {
			loading: false
		}
    },
	computed: {
		...mapState({
			user: state => state.user.profile
		})
    },
	methods: {
		...mapActions({
			fetchProfile: 'user/fetchProfile',
			logout: 'user/logout'
		})
    },
	created () {
		this.loading = true
		this.fetchProfile()
			.then(() => this.loading = false)
	}
}
</script>



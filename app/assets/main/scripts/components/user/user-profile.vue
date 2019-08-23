<template>
	<div class="btn-group custom_dropdown">
		<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
			<i class="glyphicon glyphicon-user"></i> <span class="caret"></span>
		</button>

		<ul class="dropdown-menu dropdown-menu-right">
			<li v-if="!user.is_authenticated"><a :href="endpoints.sessions_login">{{ $t("LOGIN_BTN") }}</a></li>
			<li v-if="!user.is_authenticated"><a :href="endpoints.sessions_signup">{{ $t("REGISTER_BTN") }}</a></li>

			<li v-if="user.is_authenticated"><a :href="endpoints.user_profile.replace('999999999999', `${user.id}`)">{{ $t("APP_PROFILE") }}</a></li>
			<li v-if="user.is_authenticated" role="separator" class="divider"></li>
			<li v-if="user.is_authenticated"><a :href="endpoints.post_list">{{ $t("POST_LIST") }}</a></li>
			<li v-if="user.is_authenticated"><a :href="endpoints.draft_list">{{ $t("POST_DRAFT_LIST") }}</a></li>
			<li v-if="user.is_authenticated"><a :href="endpoints.post_create">{{ $t("POST_CREATE") }}</a></li>
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

// <div class="btn-group custom_dropdown">
// 	<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
// 		<i class="glyphicon glyphicon-user"></i> <span class="caret"></span>
// 	</button>
// 	<ul class="dropdown-menu user-component">
// 		<li class="user-session-active"><a href="{{ url_for('PostsView:index') }}">{{ _('POST_LIST') }}</a></li>
// 		<li class="user-session-active"><a href="{{ url_for('PostsView:draft_list') }}">{{ _('POST_DRAFT_LIST') }}</a></li>
// 		<li class="user-session-active"><a href="{{ url_for('PostsView:post') }}">{{ _('POST_CREATE') }}</a></li>

// 		<li class="user-session-anonymous"><a href="{{ url_for('sessions.login') }}">{{ _('LOGIN_BTN') }}</a></li>
// 		<li class="user-session-anonymous"><a href="{{ url_for('sessions.signup') }}">{{ _('REGISTER_BTN') }}</a></li>

//         <li class="divider user-session-active"></li>
//         <li class="user-session-active"><a href="{{ url_for('UsersView:get', id=current_user.id) }}">{{ _('APP_PROFILE') }}</a></li>

// 		<li class="divider user-session-active"></li>
// 		<li class="user-session-active"><a href="{{ url_for('sessions.logout') }}" data-method="post">{{ _('APP_SIGN_OUT') }}</a></li>
// 	</ul>
// </div>
</script>



<template>
<div class="sidebar-container">
	<div class="widget-user push-down-20" v-if="user.is_authenticated">
		<div class="widget-user__image-container">
			<div class="widget-user__avatar--blurred">
				<img :alt="user.nickname"
					:src="user.profile_picture_url || '/static/images/others/landscape.jpg'"
					width="90"
					height="90">
			</div>
			<img class="widget-user__avatar"
				:alt="user.nickname"
				:src="user.profile_picture_url || '/static/images/user.png'"
				width="90"
				height="90">
		</div>
		<div class="row">
			<div class="col-md-12 col-sm-12 col-xs-12">
				<h4>{{ user.nickname }}</h4>
				<p v-if="user.description">{{ user.description }}</p>
			</div>
		</div>
		<div class="row">
			<div class="col-md-12 col-sm-12 col-xs-12">
				<div class="btn-group btn-group-justified" role="group">
					<div class="btn-group" role="group">
						<a :href="endpoints.post_list" rel="nofollow"
							class="btn  btn-primary btn-primary--transparent btn-lg">
							<i class="glyphicon glyphicon-th-list"></i>
							<span>{{ $t('POST_LIST') }}</span>
						</a>
					</div>
					<div class="btn-group" role="group">
						<a :href="endpoints.user_profile.replace('999999999999', `${user.id}`)" rel="nofollow"
							class="btn  btn-primary btn-primary--transparent btn-lg">
							<i class="glyphicon glyphicon-user"></i>
							<span>{{ $t('APP_PROFILE') }}</span>
						</a>
					</div>
					<div class="btn-group" role="group">
						<a :href="endpoints.user_edit.replace('999999999999', `${user.id}`)" rel="nofollow"
							class="btn  btn-primary btn-primary--transparent btn-lg">
							<i class="glyphicon glyphicon-cog"></i>
							<span>{{ $t('USER_EDIT') }}</span>
						</a>
					</div>
				</div>
			</div>
		</div>
	</div>
	<div class="boxed push-down-20 hidden-xs" v-if="!user.is_authenticated">
		<div class="widget-categories">
			<h6>{{ $t('SIDEBAR_USER_TITLE') }}</h6>
			<a href="#user-session-modal" data-toggle="modal" rel="nofollow"
				class="btn  btn-primary btn-primary--transparent btn-lg btn-block">
				{{ $t('LOGIN_BTN') }}
			</a>
			<a :href="endpoints.sessions_signup" rel="nofollow"
				class="btn  btn-primary btn-primary--transparent btn-lg btn-block">
				{{ $t('REGISTER_BTN') }}
			</a>
		</div>
	</div>
	<div class="boxed push-down-20">
		<div class="widget-categories">
			<h6>{{ $t('SIDEBAR_STAMP_TITLE') }}</h6>
			<a :href="story_edit_url" rel="nofollow"
				class="btn btn-primary btn-primary--transparent btn-lg btn-block"
				v-if="story_edit_url && user.is_authenticated && story_user_id == user.id">
				{{ $t('EDIT_STAMP_LBL') }}
			</a>
			<a :href="endpoints.story_new" rel="nofollow"
				class="btn btn-primary btn-primary--transparent btn-lg btn-block">
				{{ $t('POST_CREATE') }}
			</a>
		</div>
	</div>
</div>
</template>

<script>
import {mapState, mapGetters, mapActions} from 'vuex';

export default {
	name: 'UserSidebar',

	computed: {
      ...mapState({
        user: state => state.user.profile
      })
    },
	props: {
    	endpoints: {type: Object}
	},
	data() {
		return {
			story_edit_url: null,
			story_user_id: null
		}
	},
	methods: {
		getStoryInfo() {
			const storyEditUrl = document.querySelector('meta[property="hu:story:edit:url"]');
			if (storyEditUrl) {
				this.story_edit_url = storyEditUrl.content;
			}
			const storyUserId = document.querySelector('meta[property="hu:story:user"]');
			if (storyUserId) {
				this.story_user_id = storyUserId.content;
			}
		}
	},
	created () {
		this.getStoryInfo();
    }
}
</script>



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
						<a :href="options.post_list" rel="nofollow"
							class="btn btn-primary btn-primary--transparent btn-lg">
							<i class="glyphicon glyphicon-th-list"></i>
							<span>{{ $t('POST_LIST') }}</span>
						</a>
					</div>
					<div class="btn-group" role="group">
						<a :href="options.user_profile.replace('999999999999', `${user.id}`)" rel="nofollow"
							class="btn btn-primary btn-primary--transparent btn-lg">
							<i class="glyphicon glyphicon-user"></i>
							<span>{{ $t('APP_PROFILE') }}</span>
						</a>
					</div>
					<div class="btn-group" role="group">
						<a :href="options.user_edit.replace('999999999999', `${user.id}`)" rel="nofollow"
							class="btn btn-primary btn-primary--transparent btn-lg">
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
			<a href="#user-session-modal"
				data-toggle="modal"
				class="btn  btn-primary btn-primary--transparent btn-lg btn-block"
				rel="nofollow">
				{{ $t('LOGIN_BTN') }}
			</a>
			<a :href="options.sessions_signup"
				class="btn  btn-primary btn-primary--transparent btn-lg btn-block"
				rel="nofollow">
				{{ $t('REGISTER_BTN') }}
			</a>
		</div>
	</div>
	<div class="boxed push-down-20">
		<div class="widget-categories">
			<h6>{{ $t('SIDEBAR_STAMP_TITLE') }}</h6>
			<a :href="storyEditUrl"
				v-if="storyEditUrl && user.is_authenticated && storyUserId == user.id"
				class="btn btn-primary btn-primary--transparent btn-lg btn-block"
				rel="nofollow">
				{{ $t('EDIT_STAMP_LBL') }}
			</a>
			<a href="javascript:;"
				v-on:click="deleteStory()"
				v-if="user.is_authenticated && storyUserId == user.id"
				class="btn btn-danger btn-danger--transparent btn-lg btn-block"
				rel="nofollow">
				{{ $t('POST_DELETE') }}
			</a>
			<a :href="options.story_new"
				class="btn btn-primary btn-primary--transparent btn-lg btn-block"
				rel="nofollow">
				{{ $t('POST_CREATE') }}
			</a>
			<div class="text-center" style="margin-top: 20px;" v-if="options.patreon_id">
				<a :href="patreonLink()" target="_blank">
					<img src="/static/images/sns/patreon.png" alt="Become a patron!" style="width: 60%; margin: 0 auto;">
				</a>
			</div>
		</div>
	</div>
</div>
</template>

<script>
import {mapState, mapGetters, mapActions} from 'vuex';

export default {
	name: 'UserSidebar',
	props: {
    	options: {type: Object}
	},
	computed: {
		...mapState({
			user: state => state.user.profile
		})
    },
	data() {
		return {
			storyEditUrl: null,
			storyUserId: null,
			storyId: null
		}
	},
	methods: {
		...mapActions({
			confirm: 'notification/confirm',
			notify: 'notification/notify',
			removeStory: 'stories/removeItem'
		}),
		patreonLink() {
			let target = encodeURIComponent(window.location.href);
			let patreonId = this.options.patreon_id;

			return `https://www.patreon.com/bePatron?u=${patreonId}&redirect_uri=${target}`
		},
		getStoryInfo() {
			const storyId = document.querySelector('meta[property="hu:story:id"]');
			if (storyId) {
				this.storyId = storyId.content;
			}
			const storyUserId = document.querySelector('meta[property="hu:story:user"]');
			if (storyUserId) {
				this.storyUserId = storyUserId.content;
			}
			const storyEditUrl = document.querySelector('meta[property="hu:story:edit:url"]');
			if (storyEditUrl) {
				this.storyEditUrl = storyEditUrl.content;
			}
		},
		getTitleStory() {
			return document
				.querySelector('title').innerText
				.split('|')
				.pop().trim();
		},
		deleteStory() {
			let title = this.getTitleStory();

			let confirmMessge = this.$root.$t('POST_DELETE_CONFIRMATION', {
				title: title
			});

			this.confirm({message: confirmMessge})
				.then((response) => {
					if (response.result !== 'ok') {
						return;
					}

					let storyId = this.storyId;
					let redirectPage = this.options.latest_page;

					this.removeStory(storyId)
						.then(() => {
							this.notify({
								message: this.$root.$t('POST_DELETE_SUCESS'),
								type: 'success'
							});

							setTimeout(() => {
								window.location.href = redirectPage;
							}, 1000);
						})
						.catch(() => {
							this.notify({
								message: this.$root.$t('APP_ERROR_AND_RETRY'),
								category: 'error'
							});
						});
				});
		}
	},
	created () {
		this.getStoryInfo();
    }
}
</script>



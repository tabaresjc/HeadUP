<template>
	<div class="story-social-bar">
		<div class="story-social push-top-20 clearfix" v-if="loaded">
			<button type="button" class="btn btn-default upvote"
				v-on:click="castVote(storyData.id)"
				v-bind:class="{ active: hasVote(storyData.id) }"
				:title="$t('BTN_LIKE')"
				data-toggle="tooltip">
				<i class="fas fa-heart"></i>
				<span class="btn-text-count" v-if="storyData.likes">{{ storyData.likes }}</span>
			</button>

			<a href="javascript:;" v-if="storyPage"
				v-on:click="scrollToCommentSection()"
				:title="$t('BTN_COMMENTS')"
				class="btn btn-default comment"
				data-toggle="tooltip">
				<i class="fas fa-comments"></i>
			</a>

			<a :href="`${storyData.url}#comment-panel`" v-if="!storyPage"
				:title="$t('BTN_COMMENTS')"
				class="btn btn-default comment"
				data-toggle="tooltip">
				<i class="fas fa-comments"></i>
			</a>

			<social-sharing :url="hostUrl(storyData.url)"
							:title="storyData.title"
							:description="storyData.extra_body"
							:hashtags="hashTags(story)"
							inline-template>
				<div class="btn-group pull-right">
					<button type="button" class="btn btn-default share"
						:title="$t('BTN_SHARE')"
						data-toggle="dropdown"
						aria-haspopup="true"
						aria-expanded="false">
						<i class="fas fa-share"></i>
					</button>
					<ul class="dropdown-menu">
						<li>
							<network network="facebook">
								<i class="fab fa-facebook-square"></i> Facebook
							</network>
						</li>
						<li>
							<network network="linkedin">
								<i class="fab fa-linkedin"></i> LinkedIn
							</network>
						</li>
						<li>
							<network network="whatsapp">
								<i class="fab fa-whatsapp-square"></i> Whatsapp
							</network>
						</li>
					</ul>
				</div>
			</social-sharing>
		</div>
	</div>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex';
import { UtilHelper } from 'Assets/helpers';

export default {
	name: 'StorySocialBar',
	props: {
		story: {
			type: Object
		},
		storyId: {
			type: Number
		},
		storyPage: {
			type: Boolean,
			default: false
		}
	},
	data() {
		return {
			storyData: this.story,
			loaded: false
		}
	},
	computed: {
		...mapState({
			user: state => state.user.profile,
			votes: state => state.user.votes
		})
    },
	methods: {
		...mapActions({
			fetchItem: 'stories/fetchItem',
			vote: 'stories/vote'
		}),
		scrollToCommentSection() {
			UtilHelper.smootScroll('comment-panel');
		},
		castVote(storyId) {
			if (!this.user.is_authenticated) {
				this.triggerLogin();
				return;
			}

			this.vote(storyId)
				.then(() => {
					// Nothing to do
				});
		},
		triggerLogin() {
			let a = document.createElement('a');
			a.href = '#user-session-modal';
			a.setAttribute('data-toggle', 'modal');
			a.style.display = 'none';
			document.body.appendChild(a);

			setTimeout(() => {
				a.click();
				a.parentNode.removeChild(a);
			});
		},
		hasVote(storyId) {
			if (!this.votes || !storyId) {
				return false;
			}

			return this.votes.indexOf(storyId) >= 0;
		},
		hostUrl(url) {
			if (!url) {
				return '';
			}
			return `${window.location.protocol}//${window.location.host}${url}`;
		},
		hashTags(story) {
			if (!story) {
				return '';
			}

			let values = [
				story.category.name
			];

			return values
				.map(x => x.toLowerCase().replace(' ', ''))
				.join(',');
		}
	},
	created() {
		if (!this.storyId && !this.storyData) {
			return;
		}

		if (this.storyData) {
			this.loaded = true;
			return;
		}

		this.fetchItem(this.storyId)
			.then(story => {
				this.storyData = story;
				this.loaded = true;
			});
	}
}
</script>

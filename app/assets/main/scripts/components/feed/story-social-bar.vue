<template>
	<div class="story-social-bar">
		<div class="story-social push-top-20 clearfix" v-if="loaded">
			<button type="button" class="btn btn-default upvote"
				v-bind:class="{ active: hasVote(storyData.id) }"
				@click="castVote(storyData.id)"
				data-toggle="tooltip"
				:title="$t('BTN_LIKE')">
				<i class="fas fa-heart"></i>
				<span class="btn-text-count" v-if="storyData.likes">{{ storyData.likes }}</span>
			</button>

			<a :href="`${storyData.url}#comment-panel`" class="btn btn-default comment"
				data-toggle="tooltip"
				:title="$t('BTN_COMMENTS')">
				<i class="fas fa-comments"></i>
			</a>

			<social-sharing :url="hostUrl(storyData.url)"
							:title="storyData.title"
							:description="storyData.extra_body"
							:hashtags="hashTags(story)"
							inline-template>
				<div class="btn-group pull-right">
					<button type="button" class="btn btn-default share"
						data-toggle="dropdown"
						aria-haspopup="true"
						aria-expanded="false"
						:title="$t('BTN_SHARE')">
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

export default {
	name: 'StorySocialBar',
	props: {
		story: {
			type: Object
		},
		storyId: {
			type: Number
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

<template>
	<div class="story-social-bar">
		<div class="story-social-results clearfix">
			<span class="label label-success" >
				<i class="glyphicon glyphicon-heart"></i>
				<span class="vote-results">{{ story.likes }}</span>
			</span>
		</div>

		<div class="story-social push-top-20 clearfix">
			<a href="javascript:;" class="icon-social upvote"
				v-bind:class="{ active: hasVote(story.id) }"
				@click="vote(story.id)"></a>
			<a :href="`${story.url}#comment-panel`" class="icon-social comment"></a>
			<a href="javascript:;" class="icon-social share"></a>
		</div>
	</div>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex';

export default {
	name: 'StorySocialBar',
	props: {
		story: {
			type: Object,
			required: true
		}
	},
	computed: {
      ...mapState({
        votes: state => state.user.votes
      })
    },
	methods: {
		...mapActions({
			vote: 'stories/vote'
		}),
		hasVote(storyId) {
			if (!this.votes) {
				return false;
			}
			return this.votes.indexOf(storyId) >= 0;
		}
	}
}
</script>



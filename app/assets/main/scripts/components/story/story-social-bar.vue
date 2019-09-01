<template>
	<div class="story-social-bar">
		<div class="story-social-results clearfix">
			<span class="label label-success" >
				<i class="glyphicon glyphicon-heart"></i>
				<span class="vote-results" :data-id="story.id">{{ story.likes }}</span>
			</span>
		</div>

		<div class="story-social push-top-20 clearfix">
			<a href="javascript:;" class="icon-social upvote" :data-id="story.id"></a>
			<a :href="`${story.url}#comment-panel`" class="icon-social comment" :data-id="story.id"></a>
			<a href="javascript:;" class="icon-social share" :data-id="story.id"></a>
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
	data() {
		return {

		};
	},
	methods: {

	}
}
</script>



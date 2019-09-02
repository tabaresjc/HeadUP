<template>
	<div class="story-feed-container">
		<section id="feed-page" class="story-feed-list">
			<StoryFeedItem
				v-for="(story, $index) in stories"
				:story="story"
				:key="story.id" />
		</section>
		<infinite-loading @infinite="infiniteHandler">
			<div slot="no-more">
				<span class="label btn-feed-message">{{ $t('LBL_SCRLL_LAST_PAGE') }}</span>
			</div>
			<div slot="no-results">
				<span class="label btn-feed-message">{{ $t('LBL_SCRLL_LAST_PAGE') }}</span>
			</div>
			<div slot="error" slot-scope="{ trigger }">
				<a href="javascript:;" @click="trigger" class="btn btn-feed-message">
					<i class="glyphicon glyphicon-repeat"></i>
				</a>
			</div>
		</infinite-loading>
	</div>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex';
import InfiniteLoading from 'vue-infinite-loading';
import StoryFeedItem from './story-feed-item.vue';

export default {
	name: 'StoryFeed',
	components: {
		InfiniteLoading,
		StoryFeedItem
	},
	props: {
		category: {type: Number},
		limit: {type: Number},
		language: {type: String}
	},
	computed: {
      ...mapState({
        stories: state => state.stories.items
      })
    },
	methods: {
		...mapActions({
			fetchItems: 'stories/fetchItems'
		}),
		infiniteHandler($state) {
			const params = {
				category: this.category || '',
				limit: this.limit || 20,
				lang: this.lang || ''
			};

			this.fetchItems(params)
        		.then(message => {
					if (message.completed) {
						$state.complete();
						return;
					}

					$state.loaded();
				})
				.catch(() => {
					$state.error();
				})
		}
	}
}
</script>



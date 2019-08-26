<template>
	<div class="story-feed-container">
		<section id="feed-page" class="story-feed-list">
			<div v-for="(story, $index) in stories" :key="$index"
					class="story-item boxed push-down-20">
				<div v-if="story.cover_picture"
					class="story-cover-picture" v-bind:style="{backgroundImage: `url(${story.cover_picture.image_url})`}"></div>
				<div class="story-content">
					<h2 class="story-title"><a href="<%- story.url %>" rel="title">{{ story.title }}</a></h2>

					<div class="story-info push-top-20 clearfix">
						<img v-if="story.user" :src="story.user.profile_picture_url || '/static/images/user.png'" :alt="story.user.nickname" class="thumb">
						<img v-else src="/static/images/user.png" class="thumb" />
						<ul>
							<li>
								<span v-if="story.user"></span>
								<span v-else>{{ $t('ANONYMOUS_LBL') }}</span>
							</li>
							<li v-if="story.category">
								<a :href="story.category.url" class="custom-link">{{ story.category.name }}</a>
							</li>
							<li>
								<span class="glyphicon glyphicon-calendar"></span>
								<span>{{ story.created_at_fmt }}</span>
							</li>
						</ul>
					</div>

					<div class="story-body push-top-20">
						<h3 v-if="story.body">{{ story.body.hu_striptags().hu_substring(200) }}</h3>
						<p>{{ story.extra_body.hu_striptags().hu_substring(300) }}</p>
					</div>
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
			</div>
		</section>
		<infinite-loading @infinite="infiniteHandler">
			<div slot="no-more">{{ $t('LBL_SCRLL_LAST_PAGE') }}</div>
			<div slot="no-results">{{ $t('LBL_SCRLL_LAST_PAGE') }}</div>
		</infinite-loading>
	</div>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex';
import InfiniteLoading from 'vue-infinite-loading';
import { StoryApiService } from 'Assets/main/scripts/api';

export default {
	name: 'StoryFeed',
	components: {
		InfiniteLoading,
	},
	props: {
		category: {type: Number},
		limit: {type: Number},
		language: {type: String}
	},
	data() {
		return {
			page: 1,
			stories: [],
		};
	},
	methods: {
		infiniteHandler($state) {
			const apiService = new StoryApiService();
			const params = {
				category: this.category || '',
				limit: this.limit || 20,
				lang: this.lang || ''
			};

			apiService.getItems(this.page, params)
				.then((data) => {
					if (!data.stories.length) {
						$state.complete();
						return;
					}

					this.page += 1;
					this.stories.push(...data.stories);
					$state.loaded();
				});
		}
	}
}
</script>



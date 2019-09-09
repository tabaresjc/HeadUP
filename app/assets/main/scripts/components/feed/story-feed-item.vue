<template>
	<div class="story-item boxed push-down-20">
		<div v-if="story.cover_picture"
			class="story-cover-picture" v-bind:style="{backgroundImage: `url(${story.cover_picture.image_url})`}"></div>
		<div class="story-content">
			<h2 class="story-title"><a :href="story.url" rel="title">{{ story.title }}</a></h2>

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
						<span>{{ story.created_at | moment('ll') }}</span>
					</li>
				</ul>
			</div>

			<div class="story-body push-top-20">
				<h3 v-if="story.body">{{ story.body.hu_striptags().hu_substring(200) }}</h3>
				<p>{{ story.extra_body.hu_striptags().hu_substring(300) }}</p>
			</div>

			<StorySocialBar
				:key="story.id"
				:story="story" />
		</div>
	</div>
</template>

<script>
import StorySocialBar from './story-social-bar.vue';

export default {
	name: 'StoryItem',
	components: {
		StorySocialBar
	},
	props: {
		story: {type: Object, required: true}
	}
}
</script>



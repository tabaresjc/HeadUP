<template>
	<div id="user-session-modal" class="modal fade">
		<div class="modal-dialog modal-login">
			<div class="modal-content">
				<div class="modal-header">
					<div class="avatar">
						<img src="/static/images/avatar.png" alt="Avatar">
					</div>
					<h4 class="modal-title">{{ $t('LOGIN_TITLE') }}</h4>
					<button id="user-session-modal-dismiss" type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
				</div>
				<div class="modal-body">
					<form class="form">
						<div class="form-group">
							<input type="text"
								name="email"
								v-model="loginEmail"
								:placeholder="$t('MAIL_LBL')"
								class="form-control"
								required
								autocomplete="email">
						</div>
						<div class="form-group">
							<input type="password"
								name="password"
								v-model="loginPassword"
								:placeholder="$t('USER_PASSWORD')"
								class="form-control"
								required
								autocomplete="password">
						</div>
						<div class="form-group">
							<button type="button" class="btn btn-primary btn-lg btn-block"
								v-on:click="loginUser()">
								{{ $t('LOGIN_BTN') }}
							</button>
						</div>
					</form>
				</div>
				<div class="modal-footer">
					<div class="already">
						<div class="already-item">
							<p>{{ $t('SIGNUP_ACTION_LBL') }}</p>
							<a :href="endpoints.sessions_signup">{{ $t('REGISTER_BTN') }}</a>
						</div>
						<div class="already-item">
							<a :href="endpoints.forgot_password">{{ $t('FORGOT_PASWWORD_BTN') }}</a>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import {mapState, mapGetters, mapActions} from 'vuex';

export default {
	name: 'SessionsLogin',
	props: {
		endpoints: {
			type: Object,
			required: true
		}
	},
	data () {
		return {
			loginEmail: '',
			loginPassword: ''
		}
    },
	computed: {
		...mapState({
			user: state => state.user.profile
		})
    },
	methods: {
		...mapActions({
			login: 'user/login',
			notify: 'notification/notify'
		}),
		loginUser() {
			let data = {
				email: this.loginEmail,
				password: this.loginPassword
			}

			let btn = document.getElementById('user-session-modal-dismiss');

			let message = this.$t('SESSIONS_MSG_LOGIN_SUCESS');
			let loginMessageFail = this.$t('SESSIONS_ERROR_LOGIN');
			let generalMessageFail = this.$t('SESSIONS_ERROR_LOGIN');

			this.login(data)
				.then((user) => {
					btn.click();
					this.notify({
						message: message,
						type: 'success'
					});
				})
				.catch((err) => {
					if (!err.data) {
						return;
					}

					if (err.data.message !== 'API_ERROR_SESSION_LOGIN') {
						this.notify({message: loginMessageFail, category: 'error'});
					} else {
						this.notify({message: generalMessageFail, category: 'error'});
					}
				});
		}
    }
}
</script>

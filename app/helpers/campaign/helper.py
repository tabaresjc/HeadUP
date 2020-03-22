# -*- coding: utf8 -*-

from mailchimp3 import MailChimp
import hashlib


class CampaignHelper:

    app = None
    _mailchimp_client = None

    def __init__(self, app, **kwargs):

        if app is None:
            raise ValueError("`app` must be an instance Flask")

        self.app = app

        self._mailchimp_client_api = app.config.get('MAILCHIMP_API_KEY')
        self._mailchimp_client_username = app.config.get('MAILCHIMP_USER_NAME')
        self._mailchimp_client_list_id = app.config.get('MAILCHIMP_LIST_ID')

        if self._mailchimp_client_api:
            self._mailchimp_client = MailChimp(
                mc_api=self._mailchimp_client_api,
                mc_user=self._mailchimp_client_username)

    def add_suscriber(self, email_address, first_name, last_name):
        if self._mailchimp_client is None:
            return

        suscriber_hash = _get_suscriber_hash(email_address)

        try:
            self._mailchimp_client.lists.members.create_or_update(
                self._mailchimp_client_list_id, suscriber_hash, {
                    'email_address': email_address,
                    'status': 'subscribed',
                    'status_if_new': 'subscribed',
                    'merge_fields': {
                        'FNAME': first_name,
                        'LNAME': last_name,
                    },
                })
        except Exception as e:
            self.app.logger.error(
                '[Campaign] Error while adding user to the subscription list error (%s, %s, %s) => %s',
                email_address,
                first_name,
                last_name,
                e,
                exc_info=True)


def _get_suscriber_hash(email_address):
    h = hashlib.new('md5')
    h.update(email_address.lower())
    return h.hexdigest()

import requests
import config
import random


CLIENT_ID = config.VK_ID_CLIENT_ID


def exchange_code_for_tokens(code, state, device_id, code_verifier):
    """
    Метод позволяет получить `access_token`, `refresh_token` и `id_token` из `authorization_code`, 
    который выдается после редиректа пользователя на `/auth/vk-id` после успешной аутентификации.

    https://id.vk.com/about/business/go/docs/ru/vkid/latest/vk-id/connection/api-integration/api-description#Poluchenie-cherez-kod-podtverzhdeniya
    """

    url = "https://id.vk.com/oauth2/auth"
    data = {
        "grant_type": "authorization_code",
        "code_verifier": code_verifier,
        "redirect_uri": "https://shareu.ru/auth/vk-id",
        "code": code,
        "client_id": CLIENT_ID,
        "device_id": device_id,
        "state": state
    }

    response = requests.post(url, data=data)
    return response.json()

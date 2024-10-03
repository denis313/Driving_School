# import dotenv
# import jwt
# import requests
# from datetime import datetime
# import time
# import logging
# from requests.exceptions import JSONDecodeError
# # from justcode.settings import BASE_DIR
# from dotenv import load_dotenv
# import os
#
#
# dotenv_path = os.path.join('.env', ".env")
# load_dotenv(dotenv_path=dotenv_path)
# load_dotenv()
#
#
# subdomain = os.getenv("AMOCRM_SUBDOMAIN")
# client_id = os.getenv("AMOCRM_CLIENT_ID")
# client_secret = os.getenv("AMOCRM_CLIENT_SECRET")
# redirect_uri = os.getenv("AMOCRM_REDIRECT_URL")
# secret_code = "def50200856bab7d72858f05942302a44db204e1bc11e8b81c3108f5fa32dd5f47c5ddcd40422516d7939d67a1dd55e18b11022864f29c1365243b221b1689035fab0fd515d2feab56ff516fd0aebb5645ee3df9e71f6ccb4d5e8953c6edb8b6e381e679522d7592a9c067f49073c52a47c1d0fc53505a3d0282419c87147cda6a001ba502e5ac0341b741239a4374ac335c4d20c0187c22cfc8a1045c3178730654b92f8c804bc1aaaa887b1c393c346178161b93ff9b3907fd948ab22d95892cee5723d9f61013528e549246433d03f713a95720ba6517a077920cf84da71374c89ffc659d8873f432b6cb6ef9659e90a55263cd5d681ea5a3b014d461c86b699559ac62ced313a8cf5a87d0163b964cb83c58a82c8aa9bdb1acb0b6847419819a4808bc6a4d389423ee6c3e9246757de04fbb666705120924acb287399ce80b6d044e09faa42a84d067843e67c6ec50ca15006ad35bf4f08a48319129652c874996eedf5d06494099c4e5fd00f79ce3505d1ee35b5a1270e623a8f09957b5de96b8eb1e9b636fb7756dc0f5fb83e4aa179e94b3d26f938b7bdf4ae440cd6192b1a0131712d50357ff8369a9f4ba6f478456b0bccfa8b4d886cac949cc04d342a2f52155e9541c04b9aa5a991617518ac3b3ef25e1c7563a6b9af9a52e"
#
# def _is_expire(token: str):
#     token_data = jwt.decode(token, options={"verify_signature": False})
#     exp = datetime.utcfromtimestamp(token_data["exp"])
#     now = datetime.utcnow()
#
#     return now >= exp
#
#
# def _save_tokens(access_token: str, refresh_token: str):
#     # Записываем в ключи .env
#     os.environ["AMOCRM_ACCESS_TOKEN"] = access_token
#     os.environ["AMOCRM_REFRESH_TOKEN"] = refresh_token
#     dotenv.set_key(dotenv_path, "AMOCRM_ACCESS_TOKEN", os.environ["AMOCRM_ACCESS_TOKEN"])
#     dotenv.set_key(dotenv_path, "AMOCRM_REFRESH_TOKEN", os.environ["AMOCRM_REFRESH_TOKEN"])
#
#
# def _get_refresh_token():
#     return os.getenv("AMOCRM_REFRESH_TOKEN")
#
#
# def _get_access_token():
#     return os.getenv("AMOCRM_ACCESS_TOKEN")
#
#
# class AmoCRMWrapper:
#     def init_oauth2(self):
#         data = {
#             "client_id": client_id,
#             "client_secret": client_secret,
#             "grant_type": "authorization_code",
#             "code": secret_code,
#             "redirect_uri": redirect_uri
#         }
#
#         response = requests.post("https://{}.amocrm.ru/oauth2/access_token".format(subdomain), json=data).json()
#         print(response)
#         access_token = response["access_token"]
#         refresh_token = response["refresh_token"]
#
#         _save_tokens(access_token, refresh_token)

    # def _base_request(self, **kwargs):
    #     if _is_expire(_get_access_token()):
    #         _get_new_tokens()
    #
    #     access_token = "Bearer " + _get_access_token()
    #
    #     headers = {"Authorization": access_token}
    #     req_type = kwargs.get("type")
    #     response = ""
    #     if req_type == "get":
    #         try:
    #             response = requests.get("https://{}.amocrm.ru{}".format(
    #                 subdomain, kwargs.get("endpoint")), headers=headers).json()
    #         except JSONDecodeError as e:
    #             logging.exception(e)
    #
    #     elif req_type == "get_param":
    #         url = "https://{}.amocrm.ru{}?{}".format(
    #             subdomain,
    #             kwargs.get("endpoint"), kwargs.get("parameters"))
    #         response = requests.get(str(url), headers=headers).json()
    #     elif req_type == "post":
    #         response = requests.post("https://{}.amocrm.ru{}".format(
    #             subdomain,
    #             kwargs.get("endpoint")), headers=headers, json=kwargs.get("data")).json()
    #     return response
#
#
# amocrm_wrapper_1 = AmoCRMWrapper()
#
# amocrm_wrapper_1.init_oauth2()


# def _get_new_tokens():
#     data = {
#         "client_id": client_id,
#         "client_secret": client_secret,
#         "grant_type": "refresh_token",
#         "refresh_token": _get_refresh_token(),
#         "redirect_uri": redirect_uri
#     }
#     response = requests.post("https://{}.amocrm.ru/oauth2/access_token".format(subdomain), json=data).json()
#     access_token = response["access_token"]
#     refresh_token = response["refresh_token"]
#
#     _save_tokens(access_token, refresh_token)

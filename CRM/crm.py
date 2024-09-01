from amocrm.v2 import tokens, Lead


# class Lead(_Lead):
#     new = custom_field.TextCustomField('новая сделка')


if __name__ == '__main__':
    tokens.default_token_manager(
        client_id="f8103f65-05b0-4280-ac9d-edc0ce14f77e",
        client_secret="ejWk0f1wEj7Gks3DvqsWrANfL53Y18RwzP284wFmZKWkufFlpDK0fWXww7j86kL5",
        subdomain="alabich",
        redirect_url="https://ya.ru",
        storage=tokens.FileTokensStorage(),  # by default FileTokensStorage
    )
    # tokens.default_token_manager.init(
    #     code="def5020018315a2f3109c780b6568397d4dc912aeed355201ca356972   fe4d607ab816352a8ad70c6e1d531ce6779a4f220010bc8437e7741294bc616ee9bd65f0473431e9c87b785a605e7a9f21a53ae522c32789f5188f98addb712d846b2814b185693249694a998631807d41eb5057d520dc5b2a0f2b283ea3ddb820064a822db7c000db899e42420cba19682a47e02f8271937f66a99d80c0fc501ef039112e94ecb81f0936e60c01ed136749f8a95caf95bfac21ac145b95efc403a5a8a6431d9846e00cdcdbc9fdfd8abe6130bda093f40264bff52b8242059118c2f0d07bf8e3144c24b2a81ab10922716830a61d55e5f22bde2bb5653bb6e3e848e7c181859c6464298cb07e987c16f87ed4ca1af6d0c6af83590a63c6df8f88ba468e12616810af952d16dfd7b8c97d70bd5fc83f596df89e0c02900e8b70b520c7019893b1841652e1995916af2d6d8e53f524d39ae6fb08bd620d82da0bca255eadbb0235aa5c6b43bd941c7222786d0c09799ffdf3a5b334a27711c69072db12225c76947381e6c586f8d0cb941b5e80b4307aafacf0677675c6635ec7fc85841394d7df26282aa7c71a405d1940c3b1689d92c510137d7e29e0725cad56aee048fdd7642be8d3608dfef7f1b0690fdc5fafea6d44fbef1db0fe17c64abbf",
    #     skip_error=False)

    leads = Lead.objects.all()
    for lead in leads:
        print(lead)
        lead.name = "Новый пользователь подписал договор"
        lead.save()

    # Lead.objects.create(data=[
    #     {
    #         "text": "Повторная заявка, необходимо связаться",
    #         "complete_till": 0
    #     }
    # ])

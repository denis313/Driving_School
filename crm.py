from amocrm.v2 import tokens

if __name__ == '__main__':
    tokens.default_token_manager(
        client_id="2f3e4483-e721-455f-8a20-2c0c9a6c734d",
        client_secret="MOK2Fcn4KTnnF63pjE1qSpNixFtTBmu2cxRUuMhFdp8RCMk1IMzBOh9Ckr2TuF7c",
        subdomain="evtushokdenis2004",
        redirect_url="https://ya.ru",
        storage=tokens.FileTokensStorage(),  # by default FileTokensStorage
    )
    tokens.default_token_manager.init(
        code="def502000f29a94e087bba9177292fd7fc0258839b51529d86d15067ababbd97ff8748cd62739254544a8f68f9232d2f5757d964d"
             "c634ec812fac4cd37fa698d7775d46c92b2e11666122842184ba3499f2cf5e950695eb5acc3fe72cb52cd52be5cd284abb5303c99"
             "6dffd5a9a94692586bebd32114df6427e753d65059cab267e08aa9d57961a4f5bccfead2f06c3c73876caffd8e04d72bb673785c2"
             "a2320e1059d7c80fe9c4334b9bd74cccf8712d08011abf8522ce83985187e2ede2586c9d7a4fcfff6010c7af266d577da66ac3499"
             "8ef51603e14d8c66c4ff05d5c928dfade9eda7b6ef1afc4617b0885b3a382c7b3c780fa4bef6ba28316f3acf4a0e4940668a036e1"
             "09c6e63d998db9bda3a77b76b20eca1d870910f3711d7881aba2ed5cd793c3a767fdb8ac6ce7622e30f30283f9f4b3c96a22dc7a"
             "063f96fa763dd768d65cfe934e981a83c512bc67afaedda76146c7e3393dae64aa8faf379d2ab6ecca5105c6424e5ce67a1f5ff7"
             "62a55c904227d19e5ea7c7bf8fe03b8e7e9521eed20604430873b32c6ad21787bc90c1e0242d7eaa122ff143e1c8035c174b03c5"
             "3880b7bd7f6eb0e2e891afd676b2b817f13d9cbe63627f7c6883e7c6d0ae404b740f889c691cb196ceb654f624f7f3c399b076fb"
             "cf2b80f45e2a7af",
        skip_error=False)

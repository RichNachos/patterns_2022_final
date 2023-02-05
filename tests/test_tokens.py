from core.interactors.tokens import HardCodedTokenValidator, RandomHexTokenProvider


def test_random_token_provider() -> None:
    token_provider = RandomHexTokenProvider(32)
    token = token_provider.provide_token()
    assert len(token) == 64


def test_hardcoded_validator_incorrect() -> None:
    validator = HardCodedTokenValidator("123")
    assert not validator.validate_token("222")


def test_hardcoded_validator_correct() -> None:
    validator = HardCodedTokenValidator("123")
    assert validator.validate_token("123")

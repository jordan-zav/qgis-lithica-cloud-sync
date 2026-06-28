from lithica_drive_sync.i18n import Translator


def test_translator_uses_spanish_and_falls_back_to_english():
    assert Translator("es").text("connect") == "Conectar"
    assert Translator("fr").text("connect") == "Connect"

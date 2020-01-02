from installers.gog import Gog

def test_install_gog():
    gog = Gog("jack_orlando_a_cinematic_adventure_dc")
    gog.install()

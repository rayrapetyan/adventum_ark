from installers.gog import Gog

def test_install_gog():
    gog = Gog("black_mirror_2")
    gog.install()

import pytest

from ebump.version import TagType, Version


class TestVersion:
    def test_version_creation(self):
        version = Version(1, 2, 3, TagType.BETA, 4)
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3
        assert version.tag == TagType.BETA
        assert version.tag_num == 4

    def test_version_parsing(self):
        version_str = "1.2.3-beta4"
        version = Version.parse(version_str)
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3
        assert version.tag == TagType.BETA
        assert version.tag_num == 4

    def test_version_comparison(self):
        v0 = Version.parse("0.0.1-alpha0")
        v1 = Version.parse("0.0.1-beta0")
        v2 = Version.parse("0.0.1-beta1")
        v3 = Version.parse("0.0.1")
        v4 = Version.parse("0.1.0-alpha0")
        v5 = Version.parse("0.1.0-rc4")
        v6 = Version.parse("0.1.0")
        v7 = Version.parse("1.0.0")

        assert v0 < v1 < v2 < v3 < v4 < v5 < v6 < v7
        assert v0 == Version.parse("0.0.1-alpha0")
        assert v0 <= Version.parse("0.0.1-alpha0")
        assert v0 <= v5
        assert v0 >= v0
        assert v2 > v0
        assert Version.parse("0.0.2") > v3

    def test_version_parsing_error(self):
        with pytest.raises(ValueError, match=r"Invalid version string: not_a_version"):
            Version.parse("not_a_version")

    def test_version_comp_with_string(self):
        v = Version.parse("1.0.0")
        assert v == "1.0.0"

    def test_version_comp_with_non_version(self):
        v = Version.parse("1.0.0")
        with pytest.raises(TypeError):
            _ = v == 123

        with pytest.raises(ValueError):
            _ = v == "not_a_version"

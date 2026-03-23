from ebump.version import TAGS_ORDER, PartType, TagType, Version


def bump(curr_ver: Version, part: PartType, tag: TagType | None = None) -> Version:
    if part == PartType.MAJOR:
        return Version(curr_ver.major + 1, 0, 0, tag or TagType.FINAL, 0)
    if part == PartType.MINOR:
        return Version(curr_ver.major, curr_ver.minor + 1, 0, tag or TagType.FINAL, 0)
    if part == PartType.PATCH:
        return Version(
            curr_ver.major, curr_ver.minor, curr_ver.patch + 1, tag or TagType.FINAL, 0
        )

    assert part == PartType.TAG, "Invalid part type for bumping"

    if curr_ver.tag == TagType.FINAL:
        if tag is not None and tag != TagType.FINAL:
            raise ValueError(f"Cannot bump to tag {tag._value_} on a final version.")
        elif tag is None:
            raise ValueError("Cannot bump tag number on a final version.")

    if tag is None:
        return Version(
            curr_ver.major,
            curr_ver.minor,
            curr_ver.patch,
            curr_ver.tag,
            curr_ver.tag_num + 1,
        )
    if curr_ver.tag == TagType.FINAL:
        return Version(curr_ver.major, curr_ver.minor, curr_ver.patch, tag, 0)
    if curr_ver.tag == tag:
        return Version(
            curr_ver.major, curr_ver.minor, curr_ver.patch, tag, curr_ver.tag_num + 1
        )
    if TAGS_ORDER[tag] < TAGS_ORDER[curr_ver.tag]:
        raise ValueError(
            f"Cannot bump to tag {tag._value_}, the current tag {curr_ver.tag._value_} is higher."
        )
    return Version(curr_ver.major, curr_ver.minor, curr_ver.patch, tag, 0)

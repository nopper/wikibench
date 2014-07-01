import wikipedia


_wid_to_title_cache = {}
_title_to_wid_cache = {}


def get_wid_from_title(title):
    if title in _title_to_wid_cache:
        return _title_to_wid_cache[title]

    try:
        wid = int(wikipedia.page(title).pageid)
    except Exception, exc:
        print "Error while recovering ID for %s (%s)" % (
            title.encode('utf8'), str(exc)
        )
        wid = -1

    _title_to_wid_cache[title] = wid

    if wid != -1:
        _wid_to_title_cache[wid] = title

    return wid

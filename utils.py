
def substring(haystack, needle, n):
    parts= haystack.split(needle, n+1)
    if len(parts)<=n+1:
        return haystack
    return haystack[:len(haystack)-len(parts[-1])-len(needle)]

from tinyxbmc import addon


def getconfig(prefix):
    setting = addon.kodisetting("plugin.program.boogie-players")
    uname = setting.getstr("%s_uname" % prefix)
    source = setting.getstr("%s_source" % prefix)
    branch = setting.getstr("%s_branch" % prefix)
    bsource = setting.getstr("%s_branch_source" % prefix)
    commit = setting.getstr("%s_commit" % prefix)
    if source == "Latest Release":
        branch = None
    if commit.lower().strip() == "latest":
        commit = None
    if bsource == "Latest Commit":
        commit = None
    return uname, branch, commit

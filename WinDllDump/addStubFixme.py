STUB_PATH = r""
FIXME_PATH = r""

def isDLLsStub(dll,api):
    isStub = "false"
    for line in open(STUB_PATH):
        if ":" in line:
            dllName = line
        else:
            apiName = line
            if dll == dllName and api == apiName :
                isStub = "true"

def isDLLsFixme(dll,api):
    isFixme = "false"
    for line in open(STUB_PATH):
        if ":" in line:
            dllName = line
        else:
            apiName = line
            if dll == dllName and api == apiName:
                isFixme = "true"
def choose_best(candidates):
    ranked=sorted(candidates,key=lambda x:x.get("ev_score",0),reverse=True)
    return {"best":ranked[0] if ranked else None,"ranking":ranked}
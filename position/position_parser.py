import re

def parse_position_symbol(tradingsymbol):
    s = (tradingsymbol or "").upper()

    option_type = None
    if s.endswith("CE"):
        option_type = "CE"
    elif s.endswith("PE"):
        option_type = "PE"

    strike = None
    match = re.search(r"(\d+)(CE|PE)$", s)
    if match:
        strike = int(match.group(1))

    if "BANKNIFTY" in s:
        underlying = "banknifty"
    elif "FINNIFTY" in s:
        underlying = "finnifty"
    elif "MIDCPNIFTY" in s:
        underlying = "midcpnifty"
    elif "NIFTY" in s:
        underlying = "nifty"
    else:
        underlying = s.replace("-EQ", "")

    return {"underlying": underlying, "strike": strike, "option_type": option_type}

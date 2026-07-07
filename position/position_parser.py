import re

def parse_position_symbol(tradingsymbol):
    s = (tradingsymbol or "").upper()
    option_type = "CE" if s.endswith("CE") else "PE" if s.endswith("PE") else None
    strike = None
    m = re.search(r"(\d+)(CE|PE)$", s)
    if m:
        strike = int(m.group(1))

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

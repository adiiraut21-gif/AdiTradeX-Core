def get_strategy_lab_position_intelligence():
    try:
        from position.position_service import get_position_intelligence
        return get_position_intelligence()
    except Exception as e:
        return {"status": "error", "count": 0, "positions": [], "error": str(e)}

def calc_comparacao(brl, quotes) -> list[dict]:
    result = []
    for q in quotes:
        btc = brl * (1 - q['taker_fee_pct']/100)/q['ask_brl']
        result.append({"exchange": q["exchange"], "btc_recebido": btc, "taker_fee_pct": q["taker_fee_pct"]})

    return sorted(result, key= lambda x: x["btc_recebido"], reverse=True)



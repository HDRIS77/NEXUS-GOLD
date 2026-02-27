import numpy as np
import pandas_ta as ta

def calculate_nexus_strategy(df):
    try:
        # حساب المؤشرات الفنية
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['EMA_20'] = ta.ema(df['Close'], length=20)
        
        # محاكاة مونت كارلو (توقع السعر القادم بناءً على التقلبات)
        returns = df['Close'].pct_change().dropna()
        last_price = df['Close'].iloc[-1]
        
        # حساب درجة الثقة (Logic)
        rsi_val = df['RSI'].iloc[-1]
        current_price = df['Close'].iloc[-1]
        ema_val = df['EMA_20'].iloc[-1]
        
        confidence = 50
        trend = "NEUTRAL"
        
        if rsi_val > 70 or (current_price > ema_val * 1.02):
            confidence = min(95, int(rsi_val))
            trend = "BEARISH (Overbought)"
        elif rsi_val < 30 or (current_price < ema_val * 0.98):
            confidence = min(95, int(100 - rsi_val))
            trend = "BULLISH (Oversold)"
            
        return {
            "confidence": confidence,
            "rsi": round(rsi_val, 2),
            "trend": trend,
            "last_price": round(last_price, 2)
        }
    except:
        return {"confidence": 0, "rsi": 0, "trend": "WAITING DATA", "last_price": 0}

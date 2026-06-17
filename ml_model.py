import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib
import os
import datetime
import database

MODEL_FILE = "atmosphere_model.joblib"

def pm25_to_aqi(pm25):
    """Converts PM2.5 concentration (ug/m3) to US EPA AQI index value."""
    if pm25 < 0:
        return 0
    c = round(float(pm25), 1)
    if 0.0 <= c <= 12.0:
        return int(round((50.0 - 0.0) / (12.0 - 0.0) * (c - 0.0) + 0.0))
    elif 12.1 <= c <= 35.4:
        return int(round((100.0 - 51.0) / (35.4 - 12.1) * (c - 12.1) + 51.0))
    elif 35.5 <= c <= 55.4:
        return int(round((150.0 - 101.0) / (55.4 - 35.5) * (c - 35.5) + 101.0))
    elif 55.5 <= c <= 150.4:
        return int(round((200.0 - 151.0) / (150.4 - 55.5) * (c - 55.5) + 151.0))
    elif 150.5 <= c <= 250.4:
        return int(round((300.0 - 201.0) / (250.4 - 150.5) * (c - 150.5) + 201.0))
    elif 250.5 <= c <= 350.4:
        return int(round((400.0 - 301.0) / (350.4 - 250.5) * (c - 250.5) + 301.0))
    elif 350.5 <= c <= 500.4:
        return int(round((500.0 - 401.0) / (500.4 - 350.5) * (c - 350.5) + 401.0))
    else:
        return 500

def train_forecasting_model():
    """
    Loads all historical sensor readings from database, engineers features,
    trains a multi-output LinearRegression model, and saves it.
    """
    # Load raw historical readings
    # Since we want to train a model, we load up to 2000 points to have a good window
    conn = database.get_db_connection()
    df = pd.read_sql_query("SELECT timestamp, pm2_5 FROM sensor_readings ORDER BY timestamp ASC", conn)
    conn.close()
    
    if len(df) < 20:
        print(f"[ML Model] Insufficient data to train model (have {len(df)} records, need at least 20).")
        return False

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Feature construction:
    # We want to use the last 10 historical readings to predict future 1h, 2h, 3h, 4h, 5h, 6h readings
    # Let's slide a window across the dataframe
    X_list = []
    y_list = []
    
    num_records = len(df)
    
    for i in range(9, num_records):
        # Input features: last 10 readings up to index i
        x_vals = df.iloc[i-9:i+1]['pm2_5'].values
        t_i = df.iloc[i]['timestamp']
        
        # Targets: values at closest timestamps to t_i + 1h, t_i + 2h, ..., t_i + 6h
        y_vals = []
        possible = True
        
        for h in range(1, 7):
            target_time = t_i + datetime.timedelta(hours=h)
            # Find the record with timestamp closest to target_time
            # Difference should be within a threshold (e.g. 15 minutes)
            time_diffs = (df['timestamp'] - target_time).abs()
            best_idx = time_diffs.idxmin()
            best_diff = time_diffs.loc[best_idx]
            
            if best_diff <= datetime.timedelta(minutes=15):
                y_vals.append(df.loc[best_idx, 'pm2_5'])
            else:
                possible = False
                break
                
        if possible:
            X_list.append(x_vals)
            y_list.append(y_vals)
            
    if len(X_list) < 10:
        print(f"[ML Model] Insufficient paired training samples constructed (have {len(X_list)}, need 10).")
        return False
        
    X = np.array(X_list)
    Y = np.array(y_list)
    
    # Train the multi-output linear regression model
    model = LinearRegression()
    model.fit(X, Y)
    
    # Calculate residual RMSE for each forecast step to estimate confidence intervals
    predictions = model.predict(X)
    residuals = Y - predictions
    rmses = np.sqrt(np.mean(residuals ** 2, axis=0))
    
    # Bundle model and its error statistics
    model_data = {
        "model": model,
        "rmses": rmses.tolist(),
        "trained_at": datetime.datetime.now().isoformat(),
        "n_samples": len(X)
    }
    
    try:
        joblib.dump(model_data, MODEL_FILE)
        print(f"[ML Model] Successfully trained model on {len(X)} samples. RMSEs for 1-6h: {rmses}")
        return True
    except Exception as e:
        print(f"[ML Model] Failed to save trained model to disk (possibly read-only filesystem): {e}")
        return False

def predict_forecast():
    """
    Loads latest 10 readings from the database, runs prediction.
    Returns: Dict containing predicted PM2.5, predicted AQI, confidence intervals, or mock fallback.
    """
    # Try to load saved model
    model_data = None
    if os.path.exists(MODEL_FILE):
        try:
            model_data = joblib.load(MODEL_FILE)
        except Exception as e:
            print(f"[ML Model] Failed to load model file: {e}")
            
    # Load the latest 10 readings from the database to form inputs
    recent = database.get_recent_readings(limit=10)
    
    if len(recent) < 10:
        # Generate mock response if database has too few records (e.g., brand new run)
        latest_val = recent[-1]['pm2_5'] if len(recent) > 0 else 12.0
        return make_mock_forecast(latest_val)
        
    x_input = np.array([r['pm2_5'] for r in recent]).reshape(1, -1)
    
    if model_data:
        try:
            model = model_data["model"]
            rmses = np.array(model_data["rmses"])
            
            # Predict
            predictions = model.predict(x_input)[0]
            
            # Form intervals and AQI values
            forecast = []
            for h in range(6):
                pred_val = float(max(0.0, predictions[h]))
                rmse = rmses[h]
                # 95% prediction interval: pred_val +- 1.96 * rmse
                lower_bound = float(max(0.0, pred_val - 1.96 * rmse))
                upper_bound = float(pred_val + 1.96 * rmse)
                
                forecast.append({
                    "hour": h + 1,
                    "pm2_5": round(pred_val, 2),
                    "pm2_5_lower": round(lower_bound, 2),
                    "pm2_5_upper": round(upper_bound, 2),
                    "aqi": pm25_to_aqi(pred_val),
                    "aqi_lower": pm25_to_aqi(lower_bound),
                    "aqi_upper": pm25_to_aqi(upper_bound)
                })
                
            return {
                "forecast": forecast,
                "model_info": {
                    "status": "trained_model",
                    "n_samples": model_data["n_samples"],
                    "trained_at": model_data["trained_at"]
                }
            }
        except Exception as e:
            print(f"[ML Model] Inference error: {e}. Falling back to default trend.")
            
    # Fallback to trend-line forecast if model not trained or fails
    latest_val = recent[-1]['pm2_5']
    trend = (recent[-1]['pm2_5'] - recent[0]['pm2_5']) / len(recent)
    return make_trend_forecast(latest_val, trend)

def make_trend_forecast(latest_val, trend):
    """Fallback method using standard linear trend projection."""
    forecast = []
    for h in range(6):
        # Project using trend, with a slight damping factor
        projected = max(0.0, latest_val + (trend * (h + 1) * 3))
        # Add widening noise for confidence bounds
        margin = 3.0 + (h * 2.0)
        lower = max(0.0, projected - margin)
        upper = projected + margin
        forecast.append({
            "hour": h + 1,
            "pm2_5": round(projected, 2),
            "pm2_5_lower": round(lower, 2),
            "pm2_5_upper": round(upper, 2),
            "aqi": pm25_to_aqi(projected),
            "aqi_lower": pm25_to_aqi(lower),
            "aqi_upper": pm25_to_aqi(upper)
        })
    return {
        "forecast": forecast,
        "model_info": {
            "status": "trend_fallback",
            "reason": "model file not trained or loaded"
        }
    }

def make_mock_forecast(latest_val):
    """Produces initial mock forecast based on latest value."""
    forecast = []
    for h in range(6):
        projected = max(1.0, latest_val + np.sin(h / 2.0) * 3.0)
        margin = 4.0 + (h * 1.5)
        lower = max(0.0, projected - margin)
        upper = projected + margin
        forecast.append({
            "hour": h + 1,
            "pm2_5": round(projected, 2),
            "pm2_5_lower": round(lower, 2),
            "pm2_5_upper": round(upper, 2),
            "aqi": pm25_to_aqi(projected),
            "aqi_lower": pm25_to_aqi(lower),
            "aqi_upper": pm25_to_aqi(upper)
        })
    return {
        "forecast": forecast,
        "model_info": {
            "status": "initial_mock_fallback",
            "reason": "insufficient database entries"
        }
    }

if __name__ == "__main__":
    # Test model training on startup database
    print("Starting ML Model training test...")
    success = train_forecasting_model()
    if success:
        res = predict_forecast()
        print("Success! Example forecast:")
        for step in res["forecast"]:
            print(f"Hour {step['hour']}: PM2.5={step['pm2_5']} (range: {step['pm2_5_lower']} - {step['pm2_5_upper']}) | AQI={step['aqi']}")
    else:
        print("Model training failed/skipped.")

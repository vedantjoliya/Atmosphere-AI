// Dashboard state management
const state = {
  lang: 'en',       // 'en' or 'es'
  unit: 'metric',   // 'metric' (°C, m/s) or 'imperial' (°F, mph)
  scale: 'aqi',     // 'aqi' (US EPA Index) or 'conc' (raw concentration ug/m3)
  coords: {
    lat: 40.7128,   // default New York
    lon: -74.0060
  },
  sensorHistory: [],
  aqiColorRgb: '16, 185, 129',
  aqiColorHex: '#10b981'
};

// Predefined list of major cities
const CITIES_LIST = [
  { name: "Parma", country: "IT", lat: 44.8015, lon: 10.3279 },
  { name: "Rome", country: "IT", lat: 41.9028, lon: 12.4964 },
  { name: "Milan", country: "IT", lat: 45.4642, lon: 9.1900 },
  { name: "London", country: "GB", lat: 51.5074, lon: -0.1278 },
  { name: "Paris", country: "FR", lat: 48.8566, lon: 2.3522 },
  { name: "Berlin", country: "DE", lat: 52.5200, lon: 13.4050 },
  { name: "Madrid", country: "ES", lat: 40.4168, lon: -3.7038 },
  { name: "Athens", country: "GR", lat: 37.9838, lon: 23.7275 },
  { name: "New York", country: "US", lat: 40.7128, lon: -74.0060 },
  { name: "Los Angeles", country: "US", lat: 34.0522, lon: -118.2437 },
  { name: "Chicago", country: "US", lat: 41.8781, lon: -87.6298 },
  { name: "Toronto", country: "CA", lat: 43.6532, lon: -79.3832 },
  { name: "Tokyo", country: "JP", lat: 35.6762, lon: 139.6503 },
  { name: "Beijing", country: "CN", lat: 39.9042, lon: 116.4074 },
  { name: "Shanghai", country: "CN", lat: 31.2304, lon: 121.4737 },
  { name: "Mumbai", country: "IN", lat: 19.0760, lon: 72.8777 },
  { name: "Delhi", country: "IN", lat: 28.6139, lon: 77.2090 },
  { name: "Sydney", country: "AU", lat: -33.8688, lon: 151.2093 },
  { name: "Cairo", country: "EG", lat: 30.0444, lon: 31.2357 },
  { name: "Moscow", country: "RU", lat: 55.7558, lon: 37.6173 },
  { name: "Dubai", country: "AE", lat: 25.2048, lon: 55.2708 },
  { name: "Rio de Janeiro", country: "BR", lat: -22.9068, lon: -43.1729 },
  { name: "Buenos Aires", country: "AR", lat: -34.6037, lon: -58.3816 },
  { name: "Cape Town", country: "ZA", lat: -33.9249, lon: 18.4241 },
  { name: "Singapore", country: "SG", lat: 1.3521, lon: 103.8198 }
];

// Translations Dictionary
const translations = {
  en: {
    title: 'Atmosphere-AI',
    subtitle: 'IoT Environmental Analytics & ML forecasting',
    realtime_title: 'Real-Time Air Quality',
    pm25: 'PM2.5 (Fine Particles)',
    pm10: 'PM10 (Coarse Particles)',
    co2: 'CO2 Level',
    temp: 'Temperature',
    humidity: 'Humidity',
    weather_title: 'Local Weather',
    weather_wind: 'Wind',
    weather_pressure: 'Pressure',
    weather_humidity: 'Humidity',
    predict_title: 'Predictive Insights (6-Hour AQI Forecast)',
    predict_subtitle: 'scikit-learn Linear Regression model',
    model_trained: 'Model trained on {n} samples at {time}',
    model_mock: 'Initial forecast (generating database history...)',
    scale_label: 'Display Metric',
    scale_aqi: 'EPA AQI Index',
    scale_conc: 'Concentration (μg/m³)',
    unit_label: 'Unit System',
    unit_metric: 'Metric (°C, m/s)',
    unit_imperial: 'Imperial (°F, mph)',
    lang_label: 'Language',
    location_label: 'Location (Lat, Lon)',
    aqi_good: 'Good',
    aqi_moderate: 'Moderate',
    aqi_sensitive: 'Unhealthy for Sensitive Groups',
    aqi_unhealthy: 'Unhealthy',
    aqi_very_unhealthy: 'Very Unhealthy',
    aqi_hazardous: 'Hazardous',
    aqi_desc_good: 'Air quality is satisfactory, and air pollution poses little or no risk.',
    aqi_desc_moderate: 'Air quality is acceptable. However, there may be a risk for some people.',
    aqi_desc_sensitive: 'Members of sensitive groups may experience health effects.',
    aqi_desc_unhealthy: 'Everyone may begin to experience health effects; sensitive members more seriously.',
    aqi_desc_very_unhealthy: 'Health alert: The risk of health effects is increased for everyone.',
    aqi_desc_hazardous: 'Health warning of emergency conditions: Everyone is more likely to be affected.',
    updating: 'Updating...',
    retrain_btn: 'Retrain Model',
    retrain_success: 'Model retrained successfully!',
    retraining: 'Retraining...'
  },
  es: {
    title: 'Atmosphere-AI',
    subtitle: 'Analítica Ambiental IoT y Pronóstico ML',
    realtime_title: 'Calidad del Aire en Tiempo Real',
    pm25: 'PM2.5 (Partículas Finas)',
    pm10: 'PM10 (Partículas Gruesas)',
    co2: 'Nivel de CO2',
    temp: 'Temperatura',
    humidity: 'Humedad',
    weather_title: 'Clima Local',
    weather_wind: 'Viento',
    weather_pressure: 'Presión',
    weather_humidity: 'Humedad',
    predict_title: 'Perspectivas Predictivas (Pronóstico AQI de 6 Horas)',
    predict_subtitle: 'Modelo de Regresión Lineal scikit-learn',
    model_trained: 'Modelo entrenado con {n} muestras a las {time}',
    model_mock: 'Pronóstico inicial (generando historial...)',
    scale_label: 'Métrica de Pantalla',
    scale_aqi: 'Índice AQI EPA',
    scale_conc: 'Concentración (μg/m³)',
    unit_label: 'Sistema de Unidades',
    unit_metric: 'Métrico (°C, m/s)',
    unit_imperial: 'Imperial (°F, mph)',
    lang_label: 'Idioma',
    location_label: 'Ubicación (Lat, Lon)',
    aqi_good: 'Bueno',
    aqi_moderate: 'Moderado',
    aqi_sensitive: 'No saludable para grupos sensibles',
    aqi_unhealthy: 'No saludable',
    aqi_very_unhealthy: 'Muy insalubre',
    aqi_hazardous: 'Peligroso',
    aqi_desc_good: 'La qualidade del aire es satisfactoria y representa poco o ningún riesgo.',
    aqi_desc_moderate: 'La calidad es aceptable. Sin embargo, puede haber riesgo para algunas personas.',
    aqi_desc_sensitive: 'Los miembros de grupos sensibles pueden experimentar efectos en la salud.',
    aqi_desc_unhealthy: 'Todos pueden comenzar a experimentar efectos; grupos sensibles más seriamente.',
    aqi_desc_very_unhealthy: 'Alerta de salud: El riesgo de efectos sobre la salud aumenta para todos.',
    aqi_desc_hazardous: 'Advertencia de salud: Es más probable que todos se vean afectados.',
    updating: 'Actualizando...',
    retrain_btn: 'Reentrenar Modelo',
    retrain_success: '¡Modelo reentrenado con éxito!',
    retraining: 'Reentrenando...'
  },
  fr: {
    title: 'Atmosphere-AI',
    subtitle: 'Analyses Environnementales IoT & Prévisions ML',
    realtime_title: 'Qualité de l\'Air en Temps Réel',
    pm25: 'PM2.5 (Particules Fines)',
    pm10: 'PM10 (Particules Grossières)',
    co2: 'Niveau de CO2',
    temp: 'Température',
    humidity: 'Humidité',
    weather_title: 'Météo Locale',
    weather_wind: 'Vent',
    weather_pressure: 'Pression',
    weather_humidity: 'Humidité',
    predict_title: 'Prévisions (AQI sur 6 Heures)',
    predict_subtitle: 'Modèle de régression linéaire scikit-learn',
    model_trained: 'Modèle entraîné sur {n} échantillons à {time}',
    model_mock: 'Prévisions initiales (génération de l\'historique...)',
    scale_label: 'Métrique d\'Affichage',
    scale_aqi: 'Indice AQI EPA',
    scale_conc: 'Concentration (μg/m³)',
    unit_label: 'Système d\'Unités',
    unit_metric: 'Métrique (°C, m/s)',
    unit_imperial: 'Impérial (°F, mph)',
    lang_label: 'Langue',
    location_label: 'Localisation (Lat, Lon)',
    aqi_good: 'Bon',
    aqi_moderate: 'Modéré',
    aqi_sensitive: 'Mauvais pour les groupes sensibles',
    aqi_unhealthy: 'Mauvais',
    aqi_very_unhealthy: 'Très Mauvais',
    aqi_hazardous: 'Dangereux',
    aqi_desc_good: 'La qualité de l\'air est satisfaisante et présente peu ou pas de risque.',
    aqi_desc_moderate: 'La qualité de l\'air est acceptable. Cependant, il peut y avoir un risque pour certaines personnes.',
    aqi_desc_sensitive: 'Les membres de groupes sensibles peuvent éprouver des effets sur la santé.',
    aqi_desc_unhealthy: 'Tout le monde peut commencer à éprouver des effets sur la santé.',
    aqi_desc_very_unhealthy: 'Alerte de santé: Le risque d\'effets sur la santé est accru pour tous.',
    aqi_desc_hazardous: 'Avertissement de santé: Tout le monde est susceptible d\'être affecté.',
    updating: 'Mise à jour...',
    retrain_btn: 'Réentraîner le Modèle',
    retrain_success: 'Modèle réentraîné avec succès!',
    retraining: 'Réentraînement...'
  },
  de: {
    title: 'Atmosphere-AI',
    subtitle: 'IoT-Umweltanalytik & ML-Prognose',
    realtime_title: 'Luftqualität in Echtzeit',
    pm25: 'PM2.5 (Feinstaub)',
    pm10: 'PM10 (Grobstaub)',
    co2: 'CO2-Gehalt',
    temp: 'Temperatur',
    humidity: 'Luftfeuchtigkeit',
    weather_title: 'Lokales Wetter',
    weather_wind: 'Wind',
    weather_pressure: 'Druck',
    weather_humidity: 'Feuchtigkeit',
    predict_title: 'Prognosen (6-Stunden AQI-Vorhersage)',
    predict_subtitle: 'scikit-learn Lineares Regressionsmodell',
    model_trained: 'Modell trainiert mit {n} Proben um {time}',
    model_mock: 'Erste Prognose (Generierung des Datenbankverlaufs...)',
    scale_label: 'Anzeigemetrik',
    scale_aqi: 'EPA AQI-Index',
    scale_conc: 'Konzentration (μg/m³)',
    unit_label: 'Einheitensystem',
    unit_metric: 'Metrisch (°C, m/s)',
    unit_imperial: 'Imperial (°F, mph)',
    lang_label: 'Sprache',
    location_label: 'Standort (Lat, Lon)',
    aqi_good: 'Gut',
    aqi_moderate: 'Mäßig',
    aqi_sensitive: 'Ungesund für empfindliche Gruppen',
    aqi_unhealthy: 'Ungesund',
    aqi_very_unhealthy: 'Sehr Ungesund',
    aqi_hazardous: 'Gefährlich',
    aqi_desc_good: 'Die Luftqualität ist zufriedenstellend und stellt kaum ein Risiko dar.',
    aqi_desc_moderate: 'Die Luftqualität ist akzeptabel. Es kann jedoch ein Risiko für einige Personen geben.',
    aqi_desc_sensitive: 'Empfindliche Personen können gesundheitliche Auswirkungen spüren.',
    aqi_desc_unhealthy: 'Jeder kann gesundheitliche Auswirkungen spüren; empfindliche Personen ernster.',
    aqi_desc_very_unhealthy: 'Gesundheitswarnung: Das Risiko für gesundheitliche Auswirkungen ist für alle erhöht.',
    aqi_desc_hazardous: 'Gesundheitswarnung vor Notfallbedingungen: Jeder ist eher betroffen.',
    updating: 'Aktualisieren...',
    retrain_btn: 'Modell neu trainieren',
    retrain_success: 'Modell erfolgreich neu trainiert!',
    retraining: 'Reorganisieren...'
  },
  it: {
    title: 'Atmosphere-AI',
    subtitle: 'Analisi Ambientali IoT e Previsioni ML',
    realtime_title: 'Qualità dell\'aria in tempo reale',
    pm25: 'PM2.5 (Particelle Sottili)',
    pm10: 'PM10 (Particelle Grossolane)',
    co2: 'Livello di CO2',
    temp: 'Temperatura',
    humidity: 'Umidità',
    weather_title: 'Meteo Locale',
    weather_wind: 'Vento',
    weather_pressure: 'Pressione',
    weather_humidity: 'Umidità',
    predict_title: 'Previsioni (AQI a 6 Ore)',
    predict_subtitle: 'Modello di regressione lineare scikit-learn',
    model_trained: 'Modello addestrato su {n} campioni alle {time}',
    model_mock: 'Previsioni iniziali (generazione cronologia...)',
    scale_label: 'Metrica di Visualizzazione',
    scale_aqi: 'Indice AQI EPA',
    scale_conc: 'Concentrazione (μg/m³)',
    unit_label: 'Sistema di Unità',
    unit_metric: 'Metrico (°C, m/s)',
    unit_imperial: 'Imperiale (°F, mph)',
    lang_label: 'Lingua',
    location_label: 'Posizione (Lat, Lon)',
    aqi_good: 'Buona',
    aqi_moderate: 'Moderata',
    aqi_sensitive: 'Insalubre per gruppi sensibili',
    aqi_unhealthy: 'Insalubre',
    aqi_very_unhealthy: 'Molto Insalubre',
    aqi_hazardous: 'Pericolosa',
    aqi_desc_good: 'La qualità dell\'aria è soddisfacente e presenta pochi o nessun rischio.',
    aqi_desc_moderate: 'La qualità dell\'aria è accettabile. Tuttavia, potrebbe esserci un rischio per alcune persone.',
    aqi_desc_sensitive: 'I soggetti sensibili possono manifestare effetti sulla salute.',
    aqi_desc_unhealthy: 'Tutti possono iniziare ad avvertire effetti sulla salute.',
    aqi_desc_very_unhealthy: 'Allerta sanitaria: il rischio di effetti sulla salute aumenta per tutti.',
    aqi_desc_hazardous: 'Avviso di condizioni di emergenza sanitaria: tutti sono a rischio.',
    updating: 'Aggiornamento...',
    retrain_btn: 'Riaddestra Modello',
    retrain_success: 'Modello riaddestrato con successo!',
    retraining: 'Riaddestramento...'
  },
  pt: {
    title: 'Atmosphere-AI',
    subtitle: 'Análise Ambiental IoT e Previsão ML',
    realtime_title: 'Qualidade do Ar em Tempo Real',
    pm25: 'PM2.5 (Partículas Finas)',
    pm10: 'PM10 (Partículas Grossas)',
    co2: 'Nível de CO2',
    temp: 'Temperatura',
    humidity: 'Umidade',
    weather_title: 'Clima Local',
    weather_wind: 'Vento',
    weather_pressure: 'Pressão',
    weather_humidity: 'Umidade',
    predict_title: 'Previsão (AQI de 6 Horas)',
    predict_subtitle: 'Modelo de Regressão Linear scikit-learn',
    model_trained: 'Modelo treinado em {n} amostras às {time}',
    model_mock: 'Previsão inicial (gerando histórico...)',
    scale_label: 'Métrica de Exibição',
    scale_aqi: 'Índice AQI EPA',
    scale_conc: 'Concentração (μg/m³)',
    unit_label: 'Sistema de Unidades',
    unit_metric: 'Métrico (°C, m/s)',
    unit_imperial: 'Imperial (°F, mph)',
    lang_label: 'Idioma',
    location_label: 'Localização (Lat, Lon)',
    aqi_good: 'Bom',
    aqi_moderate: 'Moderado',
    aqi_sensitive: 'Inadequado para grupos sensíveis',
    aqi_unhealthy: 'Inadequado',
    aqi_very_unhealthy: 'Muito Inadequado',
    aqi_hazardous: 'Perigoso',
    aqi_desc_good: 'A qualidade do ar é satisfatória e apresenta pouco ou nenhum risco.',
    aqi_desc_moderate: 'A qualidade do ar é aceitável. No entanto, pode haver risco para algumas pessoas.',
    aqi_desc_sensitive: 'Membros de grupos sensíveis podem sofrer efeitos na saúde.',
    aqi_desc_unhealthy: 'Qualquer pessoa pode começar a sentir efeitos na saúde.',
    aqi_desc_very_unhealthy: 'Alerta de saúde: O risco de efeitos na saúde é aumentado para todos.',
    aqi_desc_hazardous: 'Aviso de saúde de condições de emergência: Todos são propensos a serem afetados.',
    updating: 'Atualizando...',
    retrain_btn: 'Treinar Modelo',
    retrain_success: 'Modelo treinado com sucesso!',
    retraining: 'Treinando...'
  },
  hi: {
    title: 'Atmosphere-AI',
    subtitle: 'IoT पर्यावरण विश्लेषण और ML पूर्वानुमान',
    realtime_title: 'रीअल-टाइम वायु गुणवत्ता',
    pm25: 'PM2.5 (महीन कण)',
    pm10: 'PM10 (मोटे कण)',
    co2: 'CO2 स्तर',
    temp: 'तापमान',
    humidity: 'आर्द्रता',
    weather_title: 'स्थानीय मौसम',
    weather_wind: 'हवा',
    weather_pressure: 'वायुदाब',
    weather_humidity: 'आर्द्रता',
    predict_title: 'पूर्वानुमान अंतर्दृष्टि (6-घंटे सूचकांक)',
    predict_subtitle: 'scikit-learn रैखिक प्रतिगमन मॉडल',
    model_trained: '{n} नमूनों पर {time} बजे मॉडल प्रशिक्षित',
    model_mock: 'प्रारंभिक पूर्वानुमान (इतिहास उत्पन्न हो रहा है...)',
    scale_label: 'प्रदर्शन मीट्रिक',
    scale_aqi: 'EPA AQI सूचकांक',
    scale_conc: 'सांद्रता (μg/m³)',
    unit_label: 'इकाई प्रणाली',
    unit_metric: 'मीट्रिक (°C, m/s)',
    unit_imperial: 'इंपीरियल (°F, mph)',
    lang_label: 'भाषा',
    location_label: 'स्थान (अक्षांश, देशांतर)',
    aqi_good: 'अच्छा',
    aqi_moderate: 'संतोषजनक',
    aqi_sensitive: 'संवेदनशील समूहों के लिए अस्वस्थ',
    aqi_unhealthy: 'अस्वस्थ',
    aqi_very_unhealthy: 'बहुत अस्वस्थ',
    aqi_hazardous: 'गंभीर',
    aqi_desc_good: 'वायु गुणवत्ता संतोषजनक है और प्रदूषण से कोई जोखिम नहीं है।',
    aqi_desc_moderate: 'वायु गुणवत्ता स्वीकार्य है। हालांकि, कुछ लोगों के लिए मामूली जोखिम हो सकता है।',
    aqi_desc_sensitive: 'संवेदनशील समूहों के सदस्य स्वास्थ्य संबंधी प्रभाव महसूस कर सकते हैं।',
    aqi_desc_unhealthy: 'सभी लोगों को स्वास्थ्य प्रभाव महसूस होना शुरू हो सकता है।',
    aqi_desc_very_unhealthy: 'स्वास्थ्य चेतावनी: सभी के लिए जोखिम बढ़ जाता है।',
    aqi_desc_hazardous: 'आपातकालीन स्वास्थ्य चेतावनी: हर किसी के प्रभावित होने की संभावना है।',
    updating: 'अपडेट हो रहा है...',
    retrain_btn: 'पुनः प्रशिक्षित करें',
    retrain_success: 'सफलतापूर्वक पुनः प्रशिक्षित!',
    retraining: 'प्रशिक्षण...'
  },
  zh: {
    title: 'Atmosphere-AI',
    subtitle: 'IoT 环境分析与机器学习预测',
    realtime_title: '实时空气质量',
    pm25: 'PM2.5 (细颗粒物)',
    pm10: 'PM10 (可吸入颗粒物)',
    co2: 'CO2 浓度',
    temp: '温度',
    humidity: '湿度',
    weather_title: '本地天气',
    weather_wind: '风速',
    weather_pressure: '气压',
    weather_humidity: '湿度',
    predict_title: '预测洞察 (6小时 AQI 预测)',
    predict_subtitle: 'scikit-learn 线性回归模型',
    model_trained: '模型已于 {time} 基于 {n} 个样本完成训练',
    model_mock: '初始预测 (正在生成数据库历史数据...)',
    scale_label: '显示指标',
    scale_aqi: 'EPA AQI 指数',
    scale_conc: '浓度 (μg/m³)',
    unit_label: '单位系统',
    unit_metric: '公制 (°C, m/s)',
    unit_imperial: '英制 (°F, mph)',
    lang_label: '语言',
    location_label: '位置 (经纬度)',
    aqi_good: '优',
    aqi_moderate: '良',
    aqi_sensitive: '轻度污染',
    aqi_unhealthy: '中度污染',
    aqi_very_unhealthy: '重度污染',
    aqi_hazardous: '严重污染',
    aqi_desc_good: '空气质量令人满意，几乎没有空气污染风险。',
    aqi_desc_moderate: '空气质量可接受。然而，某些人可能会有轻微风险。',
    aqi_desc_sensitive: '敏感人群可能会出现健康影响。',
    aqi_desc_unhealthy: '每个人都可能开始受到健康影响。',
    aqi_desc_very_unhealthy: '健康警报：所有人的健康受影响风险增加。',
    aqi_desc_hazardous: '健康警告：所有人均易受严重影响。',
    updating: '更新中...',
    retrain_btn: '重新训练模型',
    retrain_success: '模型重新训练成功！',
    retraining: '训练中...'
  }
};

// PM2.5 to AQI converter for front-end scale switches
function pm25ToAqi(pm25) {
  const c = Math.round(parseFloat(pm25) * 10) / 10;
  if (c < 0) return 0;
  if (c <= 12.0) return Math.round((50 - 0) / (12.0 - 0) * (c - 0) + 0);
  if (c <= 35.4) return Math.round((100 - 51) / (35.4 - 12.1) * (c - 12.1) + 51);
  if (c <= 55.4) return Math.round((150 - 101) / (55.4 - 35.5) * (c - 35.5) + 101);
  if (c <= 150.4) return Math.round((200 - 151) / (150.4 - 55.5) * (c - 55.5) + 151);
  if (c <= 250.4) return Math.round((300 - 201) / (250.4 - 150.5) * (c - 150.5) + 201);
  if (c <= 350.4) return Math.round((400 - 301) / (350.4 - 250.5) * (c - 250.5) + 301);
  if (c <= 500.4) return Math.round((500 - 401) / (500.4 - 350.5) * (c - 350.5) + 401);
  return 500;
}

// Set up event listeners
document.addEventListener('DOMContentLoaded', () => {
  initLocalization();
  
  // Populate dropdown options and bind change events
  setupCitySelectorControls();
  
  const savedLat = localStorage.getItem('settings_lat');
  const savedLon = localStorage.getItem('settings_lon');
  
  if (savedLat && savedLon) {
    console.log("[Geo] Using saved coordinates from device storage.");
  } else {
    // Set up explicit Geolocation Permission Modal dialog triggers
    const modal = document.getElementById('geo-permission-modal');
    const grantBtn = document.getElementById('geo-grant-btn');
    const denyBtn = document.getElementById('geo-deny-btn');
    
    const geoPermState = localStorage.getItem('geo_permission_state');
    if (geoPermState === 'granted') {
      detectLocation();
    } else if (geoPermState === 'denied') {
      console.log("[Geo] Permission previously denied by user. Loading with default location.");
    } else {
      // Show modal dialog to request permission explicitly
      if (modal) {
        modal.classList.remove('opacity-0', 'pointer-events-none');
      }
    }
    
    if (grantBtn) {
      grantBtn.addEventListener('click', () => {
        localStorage.setItem('geo_permission_state', 'granted');
        if (modal) modal.classList.add('opacity-0', 'pointer-events-none');
        detectLocation();
      });
    }
    
    if (denyBtn) {
      denyBtn.addEventListener('click', () => {
        localStorage.setItem('geo_permission_state', 'denied');
        if (modal) modal.classList.add('opacity-0', 'pointer-events-none');
        console.log("[Geo] Permission denied by user. Applying default coordinates.");
      });
    }
  }
  
  // Setup control panel toggles
  setupToggles();
  
  // Fetch initial history and start interval polling
  fetchSensorHistory();
  fetchRealtime();
  fetchWeather();
  fetchPredict();
  fetchLogs();
  
  setInterval(fetchRealtime, 5000);
  setInterval(fetchPredict, 10000);
  setInterval(fetchWeather, 60000);
  setInterval(fetchLogs, 5000);
  
  // Retrain button setup
  document.getElementById('retrain-btn').addEventListener('click', forceRetrainModel);
});

// Setup localization & configuration controls
function setupToggles() {
  // Language select dropdown change listener
  const langSelect = document.getElementById('lang-select');
  if (langSelect) {
    langSelect.addEventListener('change', (e) => {
      state.lang = e.target.value;
      localStorage.setItem('settings_lang', state.lang);
      translateUI();
      // Redraw charts because label languages changed
      drawCharts();
    });
  }
  
  // Display metric scale selectors (AQI vs Concentration)
  document.querySelectorAll('[data-scale]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      state.scale = e.target.getAttribute('data-scale');
      updateActiveToggleStates();
      // Redraw prediction charts for new scale
      fetchPredict();
    });
  });
  
  // Unit system selectors (Metric vs Imperial)
  document.querySelectorAll('[data-unit]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      state.unit = e.target.getAttribute('data-unit');
      updateActiveToggleStates();
      fetchWeather(); // reload weather with unit change
    });
  });
}

function updateActiveToggleStates() {
  const langSelect = document.getElementById('lang-select');
  if (langSelect) {
    langSelect.value = state.lang;
  }
  document.querySelectorAll('[data-scale]').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-scale') === state.scale);
  });
  document.querySelectorAll('[data-unit]').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-unit') === state.unit);
  });
}

// Detect location via geolocation
function detectLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        state.coords.lat = position.coords.latitude;
        state.coords.longitude = position.coords.longitude;
        state.coords.lon = position.coords.longitude;
        localStorage.setItem('settings_lat', state.coords.lat);
        localStorage.setItem('settings_lon', state.coords.lon);
        updateCityDropdownSelection();
        console.log(`[Geo] Geolocation acquired: Lat=${state.coords.lat}, Lon=${state.coords.lon}`);
        
        // Auto-configure regional defaults: US defaults to Imperial and EPA AQI
        const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        const lat = state.coords.lat;
        const lon = state.coords.lon;
        
        if (timezone.includes('America/New_York') || timezone.includes('America/Chicago') || 
            timezone.includes('America/Denver') || timezone.includes('America/Los_Angeles') || 
            (lon > -125 && lon < -66 && lat > 24 && lat < 50)) {
          state.unit = 'imperial';
          state.scale = 'aqi';
          console.log("[Geo] Detected US region. Auto-defaulted to Imperial units and US EPA AQI scale.");
        } else {
          state.unit = 'metric';
          state.scale = 'conc';
          console.log("[Geo] Detected non-US region. Auto-defaulted to Metric units and raw concentration scale.");
        }
        
        // Prefer language as per coordinates and timezones
        const isSpanishRegion = (lat >= 36 && lat <= 44 && lon >= -9 && lon <= 3) || 
                              (lat >= -56 && lat <= 32 && lon >= -118 && lon <= -34) ||
                              timezone.includes('Madrid') || timezone.includes('Mexico') || 
                              timezone.includes('Bogota') || timezone.includes('Buenos_Aires') || 
                              timezone.includes('Santiago') || timezone.includes('Lima') || 
                              timezone.includes('Caracas');
                              
        const isFrenchRegion = (lat >= 42 && lat <= 51 && lon >= -5 && lon <= 8) || 
                             timezone.includes('Paris') || timezone.includes('Brussels') || 
                             timezone.includes('Monaco');
                             
        const isGermanRegion = (lat >= 47 && lat <= 55 && lon >= 6 && lon <= 15) || 
                             timezone.includes('Berlin') || timezone.includes('Vienna') || 
                             timezone.includes('Zurich');
                             
        if (isSpanishRegion) {
          state.lang = 'es';
          console.log("[Geo] Auto-configured language: Spanish (ES) as per location.");
        } else if (isFrenchRegion) {
          state.lang = 'fr';
          console.log("[Geo] Auto-configured language: French (FR) as per location.");
        } else if (isGermanRegion) {
          state.lang = 'de';
          console.log("[Geo] Auto-configured language: German (DE) as per location.");
        }
        
        updateActiveToggleStates();
        translateUI();
        
        // Fetch weather and forecast with new location
        fetchWeather();
        fetchPredict();
      },
      (error) => {
        console.warn(`[Geo] Geolocation failed: ${error.message}. Using default coordinates.`);
        translateUI();
      }
    );
  } else {
    translateUI();
  }
}

// Initialize localization labels
function initLocalization() {
  const savedLang = localStorage.getItem('settings_lang');
  if (savedLang) {
    state.lang = savedLang;
  } else {
    const browserLang = (navigator.language || navigator.userLanguage || 'en').substring(0, 2).toLowerCase();
    const supportedLangs = ['es', 'fr', 'de', 'it', 'pt', 'hi', 'zh'];
    if (supportedLangs.includes(browserLang)) {
      state.lang = browserLang;
    }
  }
  
  const savedLat = localStorage.getItem('settings_lat');
  const savedLon = localStorage.getItem('settings_lon');
  if (savedLat && savedLon) {
    state.coords.lat = parseFloat(savedLat);
    state.coords.lon = parseFloat(savedLon);
    console.log(`[Settings] Loaded coordinates from device storage: Lat=${state.coords.lat}, Lon=${state.coords.lon}`);
  }
  
  updateActiveToggleStates();
  translateUI();
}

function translateUI() {
  const dict = translations[state.lang];
  
  // Header
  document.getElementById('app-title').textContent = dict.title;
  document.getElementById('app-subtitle').textContent = dict.subtitle;
  
  // Realtime card header
  document.getElementById('realtime-header').textContent = dict.realtime_title;
  
  // Param labels
  document.getElementById('lbl-co2').textContent = dict.co2;
  document.getElementById('lbl-temp').textContent = dict.temp;
  document.getElementById('lbl-humidity').textContent = dict.humidity;
  
  // Weather card
  document.getElementById('weather-header').textContent = dict.weather_title;
  
  // Prediction card
  document.getElementById('predict-header').textContent = dict.predict_title;
  document.getElementById('predict-subtitle').textContent = dict.predict_subtitle;
  document.getElementById('retrain-btn').textContent = dict.retrain_btn;
  
  // Control Panel
  document.getElementById('lbl-scale').textContent = dict.scale_label;
  document.getElementById('opt-scale-aqi').textContent = dict.scale_aqi;
  document.getElementById('opt-scale-conc').textContent = dict.scale_conc;
  
  document.getElementById('lbl-units').textContent = dict.unit_label;
  document.getElementById('opt-unit-metric').textContent = dict.unit_metric;
  document.getElementById('opt-unit-imp').textContent = dict.unit_imperial;
  
  document.getElementById('lbl-lang').textContent = dict.lang_label;
  
  const lblLocation = document.getElementById('lbl-location');
  if (lblLocation) {
    lblLocation.textContent = dict.location_label;
  }
  
  // Update translation of active AQI info if we have data
  if (state.latestAQI !== undefined) {
    updateAQIInfoCard(state.latestAQI);
  }
}

// Helper to determine AQI level class, title, description and colors
function getAQILevelDetails(aqi) {
  const dict = translations[state.lang];
  if (aqi <= 50) {
    return {
      name: dict.aqi_good,
      desc: dict.aqi_desc_good,
      colorRgb: '16, 185, 129', // Emerald green
      colorHex: '#10b981',
      pulse: '4s'
    };
  } else if (aqi <= 100) {
    return {
      name: dict.aqi_moderate,
      desc: dict.aqi_desc_moderate,
      colorRgb: '245, 158, 11', // Amber/Yellow
      colorHex: '#f59e0b',
      pulse: '3s'
    };
  } else if (aqi <= 150) {
    return {
      name: dict.aqi_sensitive,
      desc: dict.aqi_desc_sensitive,
      colorRgb: '249, 115, 22', // Orange
      colorHex: '#f97316',
      pulse: '2.2s'
    };
  } else if (aqi <= 200) {
    return {
      name: dict.aqi_unhealthy,
      desc: dict.aqi_desc_unhealthy,
      colorRgb: '239, 68, 68', // Red
      colorHex: '#ef4444',
      pulse: '1.5s'
    };
  } else if (aqi <= 300) {
    return {
      name: dict.aqi_very_unhealthy,
      desc: dict.aqi_desc_very_unhealthy,
      colorRgb: '168, 85, 247', // Purple
      colorHex: '#a855f7',
      pulse: '1.0s'
    };
  } else {
    return {
      name: dict.aqi_hazardous,
      desc: dict.aqi_desc_hazardous,
      colorRgb: '159, 18, 57', // Maroon
      colorHex: '#9f1239',
      pulse: '0.6s'
    };
  }
}

// Dynamic updates for AQI ring and info cards
function updateAQIView(pm25, pm10) {
  const aqi = pm25ToAqi(pm25);
  state.latestAQI = aqi;
  
  const details = getAQILevelDetails(aqi);
  state.aqiColorRgb = details.colorRgb;
  state.aqiColorHex = details.colorHex;
  
  // Set global CSS variables for ring colors and animations
  document.documentElement.style.setProperty('--aqi-glow-rgb', details.colorRgb);
  document.documentElement.style.setProperty('--pulse-duration', details.pulse);
  
  // Update Ring text
  document.getElementById('aqi-value-text').textContent = aqi;
  
  // Animate SVG Ring
  const circumference = 440; // 2 * pi * 70
  const offset = circumference - (Math.min(aqi, 500) / 500) * circumference;
  document.getElementById('aqi-gauge-ring').style.strokeDashoffset = offset;
  
  // Update AQI detail card
  updateAQIInfoCard(aqi);
}

function updateAQIInfoCard(aqi) {
  const details = getAQILevelDetails(aqi);
  
  const labelEl = document.getElementById('aqi-level-label');
  labelEl.textContent = details.name;
  labelEl.style.color = details.colorHex;
  
  document.getElementById('aqi-level-desc').textContent = details.desc;
}

// Fetch realtime sensor data
function fetchRealtime() {
  fetch('/api/realtime')
    .then(res => {
      if (!res.ok) throw new Error("HTTP error " + res.status);
      return res.json();
    })
    .then(data => {
      // Display the device name
      if (data.device_name) {
        document.getElementById('device-name-display').textContent = data.device_name;
      }
      
      // Update values
      document.getElementById('val-co2').textContent = Math.round(data.co2);
      document.getElementById('val-humidity').textContent = Math.round(data.humidity) + '%';
      
      // Handle PM values based on scale
      if (state.scale === 'aqi') {
        document.getElementById('val-pm25').textContent = pm25ToAqi(data.pm2_5);
        document.getElementById('val-pm25-unit').textContent = '';
        document.getElementById('val-pm10').textContent = Math.round(data.pm10); // PM10 does not have a simple standalone AQI scale in standard views
        document.getElementById('val-pm10-unit').textContent = 'μg/m³';
      } else {
        document.getElementById('val-pm25').textContent = data.pm2_5.toFixed(1);
        document.getElementById('val-pm25-unit').textContent = 'μg/m³';
        document.getElementById('val-pm10').textContent = data.pm10.toFixed(1);
        document.getElementById('val-pm10-unit').textContent = 'μg/m³';
      }
      
      // Handle Temperature conversion
      if (state.unit === 'imperial') {
        const tempF = (data.temperature * 9/5) + 32;
        document.getElementById('val-temp').textContent = Math.round(tempF) + '°F';
      } else {
        document.getElementById('val-temp').textContent = data.temperature.toFixed(1) + '°C';
      }
      
      // Update AQI dial
      updateAQIView(data.pm2_5, data.pm10);
      
      // Append reading to history array and redraw realtime chart
      appendSensorHistoryPoint(data);
    })
    .catch(err => console.error("[API] Error fetching realtime data:", err));
}

// Fetch historical readings to populate the live chart
function fetchSensorHistory() {
  // Let's fetch history from our api endpoint.
  // Wait, let's verify if /api/history was added. If not, we fall back to empty array.
  fetch('/api/history')
    .then(res => {
      if (!res.ok) return []; // Fallback if history endpoint is not present yet
      return res.json();
    })
    .then(history => {
      if (history && history.length > 0) {
        state.sensorHistory = history;
      }
      drawRealtimeChart();
    })
    .catch(err => {
      console.warn("[API] /api/history endpoint not found, starting with empty live chart.");
      drawRealtimeChart();
    });
}

function appendSensorHistoryPoint(data) {
  // Ensure we don't insert duplicate timestamps
  const lastPoint = state.sensorHistory[state.sensorHistory.length - 1];
  if (lastPoint && lastPoint.timestamp === data.timestamp) return;
  
  state.sensorHistory.push(data);
  // Cap history at 50 points
  if (state.sensorHistory.length > 50) {
    state.sensorHistory.shift();
  }
  drawRealtimeChart();
}

// Fetch live weather data
function fetchWeather() {
  const url = `/api/weather?lat=${state.coords.lat}&lon=${state.coords.lon}`;
  
  fetch(url)
    .then(res => res.json())
    .then(data => {
      // Temperature
      let temp = data.main.temp;
      let tempUnit = '°C';
      if (state.unit === 'imperial') {
        temp = (temp * 9/5) + 32;
        tempUnit = '°F';
      }
      
      document.getElementById('weather-temp').textContent = `${Math.round(temp)}${tempUnit}`;
      document.getElementById('weather-desc').textContent = data.weather[0].description;
      const cityName = data.name;
      const countryCode = data.sys && data.sys.country ? data.sys.country : '';
      document.getElementById('weather-city').textContent = countryCode ? `${cityName}, ${countryCode}` : cityName;
      
      // Weather stats
      let windSpeed = data.wind.speed;
      let windUnit = 'm/s';
      if (state.unit === 'imperial') {
        windSpeed = windSpeed * 2.23694; // m/s to mph
        windUnit = 'mph';
      }
      
      const dict = translations[state.lang];
      document.getElementById('weather-wind').textContent = `${dict.weather_wind}: ${windSpeed.toFixed(1)} ${windUnit}`;
      document.getElementById('weather-humidity').textContent = `${dict.weather_humidity}: ${data.main.humidity}%`;
      document.getElementById('weather-pressure').textContent = `${dict.weather_pressure}: ${data.main.pressure} hPa`;
      
      // Weather icon
      const iconCode = data.weather[0].icon;
      const iconUrl = `https://openweathermap.org/img/wn/${iconCode}@2x.png`;
      document.getElementById('weather-icon').src = iconUrl;
    })
    .catch(err => console.error("[API] Error fetching weather:", err));
}

// Fetch prediction forecast
function fetchPredict() {
  fetch('/api/predict')
    .then(res => res.json())
    .then(data => {
      state.forecastData = data;
      drawForecastChart();
      updateModelInfoLabel(data.model_info);
    })
    .catch(err => console.error("[API] Error fetching prediction forecast:", err));
}

function updateModelInfoLabel(info) {
  const el = document.getElementById('model-info-text');
  const dict = translations[state.lang];
  
  if (info.status === 'initial_mock_fallback') {
    el.textContent = dict.model_mock;
    el.classList.add('text-amber-400/70');
    el.classList.remove('text-slate-400');
  } else {
    // Format timestamp
    const date = new Date(info.trained_at);
    const timeStr = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    let text = dict.model_trained
      .replace('{n}', info.n_samples || '100')
      .replace('{time}', timeStr);
    
    el.textContent = text;
    el.classList.remove('text-amber-400/70');
    el.classList.add('text-slate-400');
  }
}

// Retrain model triggers
function forceRetrainModel() {
  const btn = document.getElementById('retrain-btn');
  const dict = translations[state.lang];
  btn.disabled = true;
  btn.textContent = dict.retraining;
  
  fetch('/api/retrain', { method: 'POST' })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        showToast(dict.retrain_success);
        fetchPredict();
      }
    })
    .catch(err => console.error("[API] Failed to force retrain:", err))
    .finally(() => {
      btn.disabled = false;
      btn.textContent = dict.retrain_btn;
    });
}

function showToast(message) {
  const toast = document.createElement('div');
  toast.className = 'fixed bottom-4 right-4 bg-white/95 text-slate-800 px-4 py-2 rounded-lg border border-emerald-500/50 shadow-lg z-50 text-sm backdrop-blur-md transition-all duration-300 opacity-0 translate-y-2';
  toast.textContent = message;
  document.body.appendChild(toast);
  
  // Fade in
  setTimeout(() => {
    toast.classList.remove('opacity-0', 'translate-y-2');
  }, 50);
  
  // Fade out and remove
  setTimeout(() => {
    toast.classList.add('opacity-0', 'translate-y-2');
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// Dynamic Visualization Plotly.js charts
function drawCharts() {
  drawRealtimeChart();
  drawForecastChart();
  drawAmbientSparklines();
}

function drawRealtimeChart() {
  const gd = document.getElementById('realtime-chart');
  if (!gd) return;
  
  const history = state.sensorHistory;
  if (!history || history.length === 0) {
    // Show empty placeholder or return
    Plotly.purge(gd);
    return;
  }
  
  const timestamps = history.map(h => h.timestamp);
  const pm25_vals = history.map(h => state.scale === 'aqi' ? pm25ToAqi(h.pm2_5) : h.pm2_5);
  const pm10_vals = history.map(h => h.pm10);
  const co2_vals = history.map(h => h.co2);
  
  const yLabel = state.scale === 'aqi' ? 'AQI' : 'PM2.5 (μg/m³)';
  
  const tracePM25 = {
    x: timestamps,
    y: pm25_vals,
    name: state.scale === 'aqi' ? 'PM2.5 AQI' : 'PM2.5',
    type: 'scatter',
    mode: 'lines',
    line: { color: 'rgb(' + state.aqiColorRgb + ')', width: 2.5 }
  };
  
  const tracePM10 = {
    x: timestamps,
    y: pm10_vals,
    name: 'PM10 (μg/m³)',
    type: 'scatter',
    mode: 'lines',
    line: { color: '#38bdf8', width: 1.5 },
    visible: 'legendonly' // start with PM10 hidden in legend to avoid cluttering
  };
  
  const traceCO2 = {
    x: timestamps,
    y: co2_vals,
    name: 'CO2 (ppm)',
    yaxis: 'y2',
    type: 'scatter',
    mode: 'lines',
    line: { color: '#a855f7', width: 2 }
  };
  
  const layout = {
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    margin: { l: 45, r: 45, t: 15, b: 35 },
    showlegend: true,
    legend: {
      orientation: 'h',
      x: 0,
      y: 1.1,
      font: { color: '#475569', size: 10 }
    },
    xaxis: {
      gridcolor: 'rgba(15, 23, 42, 0.05)',
      tickfont: { color: '#475569', size: 10 },
      type: 'date'
    },
    yaxis: {
      title: { text: yLabel, font: { color: '#475569', size: 11 } },
      gridcolor: 'rgba(15, 23, 42, 0.05)',
      tickfont: { color: '#475569', size: 10 }
    },
    yaxis2: {
      title: { text: 'CO2 (ppm)', font: { color: '#7c3aed', size: 11 } },
      overlaying: 'y',
      side: 'right',
      tickfont: { color: '#7c3aed', size: 10 },
      showgrid: false
    }
  };
  
  const config = { responsive: true, displayModeBar: false };
  Plotly.newPlot(gd, [tracePM25, tracePM10, traceCO2], layout, config);
  drawAmbientSparklines();
}

function drawForecastChart() {
  const gd = document.getElementById('forecast-chart');
  if (!gd || !state.forecastData) return;
  
  const forecast = state.forecastData.forecast;
  
  const dict = translations[state.lang];
  const hours = forecast.map(f => `+${f.hour}h`);
  
  // Determine if using AQI or raw concentration
  let preds, lowers, uppers;
  if (state.scale === 'aqi') {
    preds = forecast.map(f => f.aqi);
    lowers = forecast.map(f => f.aqi_lower);
    uppers = forecast.map(f => f.aqi_upper);
  } else {
    preds = forecast.map(f => f.pm2_5);
    lowers = forecast.map(f => f.pm2_5_lower);
    uppers = forecast.map(f => f.pm2_5_upper);
  }
  
  const yLabel = state.scale === 'aqi' ? 'AQI' : 'PM2.5 (μg/m³)';
  
  // Bounds trace (shaded confidence interval region)
  const x_bounds = [...hours, ...[...hours].reverse()];
  const y_bounds = [...uppers, ...[...lowers].reverse()];
  
  const traceBounds = {
    x: x_bounds,
    y: y_bounds,
    fill: 'toself',
    fillcolor: `rgba(${state.aqiColorRgb}, 0.15)`,
    line: { color: 'transparent' },
    type: 'scatter',
    name: '95% Confidence Interval',
    hoverinfo: 'none'
  };
  
  const traceLine = {
    x: hours,
    y: preds,
    mode: 'lines+markers',
    name: 'Predicted',
    line: {
      color: state.aqiColorHex,
      width: 3.5,
      shape: 'spline'
    },
    marker: {
      size: 8,
      color: state.aqiColorHex,
      line: {
        color: '#ffffff',
        width: 1.5
      }
    },
    type: 'scatter'
  };
  
  const layout = {
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    margin: { l: 45, r: 15, t: 15, b: 35 },
    showlegend: false,
    xaxis: {
      gridcolor: 'rgba(15, 23, 42, 0.05)',
      tickfont: { color: '#475569', size: 11 },
      fixedrange: true
    },
    yaxis: {
      title: { text: yLabel, font: { color: '#475569', size: 11 } },
      gridcolor: 'rgba(15, 23, 42, 0.05)',
      tickfont: { color: '#475569', size: 11 },
      fixedrange: true
    }
  };
  
  const config = { responsive: true, displayModeBar: false };
  Plotly.newPlot(gd, [traceBounds, traceLine], layout, config);
}

// Fetch system logs
function fetchLogs() {
  fetch('/api/logs')
    .then(res => res.json())
    .then(logs => {
      const container = document.getElementById('system-logs-container');
      if (!container) return;
      
      // Clear placeholder/waiting message
      container.innerHTML = '';
      
      if (logs.length === 0) {
        container.innerHTML = '<div class="text-slate-500">// No logs available yet.</div>';
        return;
      }
      
      // Keep track of scroll position to auto-scroll only if they were at bottom
      const isAtBottom = container.scrollHeight - container.clientHeight <= container.scrollTop + 20;
      
      logs.forEach(log => {
        const div = document.createElement('div');
        
        // Color-coding based on keyword matching
        if (log.includes('Success') || log.includes('parsed') || log.includes('Saved')) {
          div.className = 'text-emerald-400';
        } else if (log.includes('Attempting') || log.includes('polling') || log.includes('Starting')) {
          div.className = 'text-cyan-400';
        } else if (log.includes('Warning') || log.includes('cooldown')) {
          div.className = 'text-amber-400';
        } else if (log.includes('Error') || log.includes('failed') || log.includes('mismatch')) {
          div.className = 'text-rose-400';
        } else {
          div.className = 'text-slate-300';
        }
        
        div.textContent = log;
        container.appendChild(div);
      });
      
      // Scroll to bottom if user is close to bottom
      if (isAtBottom) {
        container.scrollTop = container.scrollHeight;
      }
    })
    .catch(err => console.error("[API] Error fetching system logs:", err));
}

// Synchronize city dropdown selector with state coordinates
function updateCityDropdownSelection() {
  const select = document.getElementById('city-select');
  if (!select) return;
  
  const lat = state.coords.lat;
  const lon = state.coords.lon;
  
  // Find nearest city in the list
  let nearestCity = null;
  let minDistance = 0.5; // threshold of ~50km to auto-associate with a preset city
  
  CITIES_LIST.forEach(city => {
    const dist = Math.sqrt(Math.pow(city.lat - lat, 2) + Math.pow(city.lon - lon, 2));
    if (dist < minDistance) {
      minDistance = dist;
      nearestCity = city;
    }
  });
  
  // Remove any previously added custom option
  const customOpt = select.querySelector('option[value="custom"]');
  if (customOpt) {
    customOpt.remove();
  }
  
  if (nearestCity) {
    // Select the nearest preset city
    select.value = `${nearestCity.lat},${nearestCity.lon}`;
  } else {
    // Current location is custom/geolocation, append a temporary Custom option
    const opt = document.createElement('option');
    opt.value = "custom";
    opt.textContent = `[Custom: ${lat.toFixed(2)}, ${lon.toFixed(2)}]`;
    opt.selected = true;
    select.insertBefore(opt, select.firstChild);
  }
}

// Populate dropdown options and bind change events
function setupCitySelectorControls() {
  const select = document.getElementById('city-select');
  const detectBtn = document.getElementById('btn-geo-detect');
  
  if (select) {
    // Populate cities list
    select.innerHTML = '';
    
    // Sort cities alphabetically by name
    const sortedCities = [...CITIES_LIST].sort((a, b) => a.name.localeCompare(b.name));
    
    sortedCities.forEach(city => {
      const opt = document.createElement('option');
      opt.value = `${city.lat},${city.lon}`;
      opt.textContent = `${city.name} (${city.country})`;
      select.appendChild(opt);
    });
    
    // Synchronize selection with startup/saved coords
    updateCityDropdownSelection();
    
    // Dropdown change listener
    select.addEventListener('change', (e) => {
      const val = e.target.value;
      if (val === 'custom') return;
      
      const [latStr, lonStr] = val.split(',');
      const latVal = parseFloat(latStr);
      const lonVal = parseFloat(lonStr);
      
      state.coords.lat = latVal;
      state.coords.lon = lonVal;
      localStorage.setItem('settings_lat', latVal);
      localStorage.setItem('settings_lon', lonVal);
      
      // Find city name for toast
      const city = CITIES_LIST.find(c => c.lat === latVal && c.lon === lonVal);
      if (city) {
        showToast(`Location changed to ${city.name}, ${city.country}!`);
      }
      
      fetchWeather();
      fetchPredict();
    });
  }
  
  if (detectBtn) {
    detectBtn.addEventListener('click', () => {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            const latVal = position.coords.latitude;
            const lonVal = position.coords.longitude;
            state.coords.lat = latVal;
            state.coords.lon = lonVal;
            localStorage.setItem('settings_lat', latVal);
            localStorage.setItem('settings_lon', lonVal);
            localStorage.setItem('geo_permission_state', 'granted');
            
            updateCityDropdownSelection();
            showToast("Location auto-detected and saved to device!");
            
            fetchWeather();
            fetchPredict();
          },
          (error) => {
            alert(`Geolocation failed: ${error.message}`);
          }
        );
      } else {
        alert("Geolocation is not supported by your browser.");
      }
    });
  }
}

// Draw Temperature and Humidity Sparkline Charts
function drawAmbientSparklines() {
  const history = state.sensorHistory;
  if (!history || history.length === 0) return;
  
  // Extract temperature values (adjusting to Fahrenheit if needed)
  const tempVals = history.map(h => {
    if (state.unit === 'imperial') {
      return (h.temperature * 9/5) + 32;
    }
    return h.temperature;
  });
  
  // Extract humidity values
  const humidityVals = history.map(h => h.humidity);
  
  // Render sparklines
  drawSparkline('temp-sparkline', tempVals, '#f97316'); // Orange-500
  drawSparkline('humidity-sparkline', humidityVals, '#3b82f6'); // Blue-500
}

// Low-level helper to render static mini-trend lines (sparklines)
function drawSparkline(elementId, values, color) {
  const gd = document.getElementById(elementId);
  if (!gd) return;
  
  if (!values || values.length === 0) {
    Plotly.purge(gd);
    return;
  }
  
  const trace = {
    x: Array.from({length: values.length}, (_, i) => i),
    y: values,
    type: 'scatter',
    mode: 'lines',
    line: {
      color: color,
      width: 2,
      shape: 'spline' // smooth curve interpolation
    },
    hoverinfo: 'none'
  };
  
  const layout = {
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    margin: { l: 2, r: 2, t: 2, b: 2 },
    showlegend: false,
    xaxis: {
      visible: false,
      fixedrange: true
    },
    yaxis: {
      visible: false,
      fixedrange: true
    }
  };
  
  const config = {
    responsive: true,
    displayModeBar: false,
    staticPlot: true // disable zoom, drag, hover popups
  };
  
  Plotly.newPlot(gd, [trace], layout, config);
}

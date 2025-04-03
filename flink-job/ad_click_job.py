# ad_click_analytics/flink-job/ad_click_job.py

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, EnvironmentSettings
from pyflink.table import expressions as expr, functions as func

# Configuración del entorno
env_settings = EnvironmentSettings.in_streaming_mode()
env = StreamExecutionEnvironment.get_execution_environment()
t_env = StreamTableEnvironment.create(env, environment_settings=env_settings)

# Definición de la tabla para las impresiones
t_env.execute_sql("""
CREATE TABLE ad_impressions (
    impression_id STRING,
    user_id STRING,
    campaign_id STRING,
    ad_id STRING,
    device_type STRING,
    browser STRING,
    event_timestamp BIGINT,
    cost DOUBLE,
    WATERMARK FOR event_timestamp AS event_timestamp - INTERVAL '5' SECOND
) WITH (
    'connector' = 'kafka',
    'topic' = 'ad-impressions',
    'properties.bootstrap.servers' = 'kafka:9092',
    'format' = 'json',
    'json.timestamp-type' = 'value',
    'json.timestamp-format.standard' = 'ISO_INSTANT',
    'json.field.event_timestamp.data-type' = 'BIGINT'
)
""")

# Definición de la tabla para los clicks
t_env.execute_sql("""
CREATE TABLE ad_clicks (
    click_id STRING,
    impression_id STRING,
    user_id STRING,
    event_timestamp BIGINT,
    WATERMARK FOR event_timestamp AS event_timestamp - INTERVAL '5' SECOND
) WITH (
    'connector' = 'kafka',
    'topic' = 'ad-clicks',
    'properties.bootstrap.servers' = 'kafka:9092',
    'format' = 'json',
    'json.timestamp-type' = 'value',
    'json.timestamp-format.standard' = 'ISO_INSTANT',
    'json.field.event_timestamp.data-type' = 'BIGINT'
)
""")

# Obtener referencias a las tablas
impressions_table = t_env.from_path("ad_impressions")
clicks_table = t_env.from_path("ad_clicks")

# Calcular el CTR por Campaña en Ventanas de 1 Minuto
ctr_results = impressions_table.window(
    func.Tumble.over(expr.lit(60).seconds).on(impressions_table.event_timestamp).alias("w_i")
).group_by(
    impressions_table.campaign_id,
    expr.col("w_i").start
).select(
    expr.col("w_i").start.alias("window_start"),
    impressions_table.campaign_id,
    (func.count(clicks_table.impression_id.where(clicks_table.impression_id == impressions_table.impression_id))
     .cast('DOUBLE') / func.count(impressions_table.impression_id)).alias("ctr")
)

# Calcular métricas de engagement por tipo de dispositivo
engagement_metrics = impressions_table.window(
    func.Tumble.over(expr.lit(60).seconds).on(impressions_table.event_timestamp).alias("w_e")
).group_by(
    impressions_table.device_type,
    expr.col("w_e").start
).select(
    expr.col("w_e").start.alias("window_start"),
    impressions_table.device_type,
    func.count(impressions_table.impression_id).alias("impression_count"),
    func.count(impressions_table.user_id.distinct).alias("unique_user_count")
)

# Tabla de salida para el CTR
t_env.execute_sql("""
CREATE TABLE campaign_ctr_results (
    window_start TIMESTAMP(3),
    campaign_id STRING,
    ctr DOUBLE
) WITH (
    'connector' = 'kafka',
    'topic' = 'campaign-ctr-results',
    'properties.bootstrap.servers' = 'kafka:9092',
    'format' = 'json'
)
""")

# Insertar los resultados del CTR en la tabla de salida
ctr_results.insert_into("campaign_ctr_results").execute()

# Tabla de salida para las métricas de engagement
t_env.execute_sql("""
CREATE TABLE device_engagement_results (
    window_start TIMESTAMP(3),
    device_type STRING,
    impression_count BIGINT,
    unique_user_count BIGINT
) WITH (
    'connector' = 'kafka',
    'topic' = 'device-engagement-results',
    'properties.bootstrap.servers' = 'kafka:9092',
    'format' = 'json'
)
""")

# Insertar los resultados de engagement en la tabla de salida
engagement_metrics.insert_into("device_engagement_results").execute()

# Imprimir los resultados en la consola (para desarrollo - opcional)
# ctr_results.execute().print()
# engagement_metrics.execute().print()

# Ejecutar el job de Flink
t_env.execute("ad-click-analytics-job")
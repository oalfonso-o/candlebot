import os
import logging

from flask import Flask
from flask import send_from_directory

from candlefront.backtesting import backtesting_bp
from candlefront.backfill import backfill_bp
from candlefront.charts import charts_bp

logging.basicConfig(
    level=logging.INFO,
    format=(
        '%(asctime)s %(name)16.16s %(funcName)10.10s %(levelname)7s: '
        '%(message)s'
    ),
    force=True,
)
logger = logging.getLogger(__name__)

app = Flask(
    __name__,
    static_url_path='',
    static_folder='static',
    template_folder='templates',
)
app.register_blueprint(backtesting_bp)
app.register_blueprint(backfill_bp)
app.register_blueprint(charts_bp)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon',
    )

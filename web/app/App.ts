import { createChart, LineData } from 'lightweight-charts';

import * as request from "request";

document.body.style.position = 'relative';
var container = document.createElement('div');
document.body.appendChild(container);
var toolTip = document.createElement('div');
toolTip.className = 'three-line-legend';
container.appendChild(toolTip);
toolTip.style.display = 'block';
toolTip.style.left = 3 + 'px';
toolTip.style.top = 3 + 'px';
const chart = createChart(container, { width: 1200, height: 800 });
chart.applyOptions({crosshair: {mode: 2}});

var options = {
  'method': 'GET',
  'url': 'http://localhost:12345/ema',
  'headers': {}
};

request(options, function (error, response) {
  if (error) throw new Error(error);
  let data = JSON.parse(response.body);
  console.log(data);
  for (var c in data) {
    // API response must include first a candles series
    if (data[c]['type'] == 'candles') {
      var candleSeries = chart.addCandlestickSeries();
      candleSeries.setData(data[c]['values']);
    } else if (data[c]['type'] == 'lines') {
      chart.addLineSeries({
        color: data[c]['color'] || '#ccc',
        lineStyle: data[c]['lineStyle'] || 0,
        lineWidth: data[c]['lineWidth'] || 2,
        crosshairMarkerVisible: data[c]['crosshairMarkerVisible'] || true,
        crosshairMarkerRadius: data[c]['crosshairMarkerRadius'] || 1,
        crosshairMarkerBorderColor: data[c]['crosshairMarkerBorderColor'] || '#ffffff',
        crosshairMarkerBackgroundColor: data[c]['crosshairMarkerBackgroundColor'] || '#2296f3',
        lineType: data[c]['lineType'] || 2,
      }).setData(data[c]['values']);
    } else if (data[c]['type'] == 'markers') {
      candleSeries.setMarkers(data[c]['values']);
    }
  }
  chart.subscribeCrosshairMove(function(param) {
    if ( param === undefined || param.time === undefined || param.point.x < 0 || param.point.x > 1200 || param.point.y < 0 || param.point.y > 800 ) {
    } else {
      var price = param.seriesPrices.get(candleSeries);
      toolTip.innerHTML =	(
        '<div style="font-size: 24px; margin: 4px 0px; color: #20262E"> CandleBot</div>'
        + '<div style="font-size: 12px; margin: 4px 0px; color: #20262E"> Open: ' + (Math.round(price.open * 100) / 100).toFixed(2) + '</div>'
        + '<div style="font-size: 12px; margin: 4px 0px; color: #20262E"> Close: ' + (Math.round(price.close * 100) / 100).toFixed(2) + '</div>'
        + '<div style="font-size: 12px; margin: 4px 0px; color: #20262E"> High: ' + (Math.round(price.high * 100) / 100).toFixed(2) + '</div>'
        + '<div style="font-size: 12px; margin: 4px 0px; color: #20262E"> Low: ' + (Math.round(price.low * 100) / 100).toFixed(2) + '</div>'
      );
    }
  });
  chart.timeScale().fitContent();
});


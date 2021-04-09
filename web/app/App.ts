import { createChart, LineData } from 'lightweight-charts';

import * as request from "request";
var options = {
  'method': 'GET',
  'url': 'http://localhost:12345/ema',
  'headers': {}
};
request(options, function (error, response) {
  if (error) throw new Error(error);
  let data = JSON.parse(response.body);
  console.log(data);
  const chart = createChart(document.body, { width: 1200, height: 800 });
  chart.applyOptions({crosshair: {mode: 2}});
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
  chart.timeScale().fitContent();
});

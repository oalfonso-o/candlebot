class Charter {
  endpoint

  constructor() {
    this.endpoint = 'http://localhost:12345/ema'
    document.body.style.position = 'relative'
  }

  defineChart(chartsData) {
    chartsData.forEach(function (chartData) {
      let container = document.createElement('div')
      document.body.appendChild(container)
      const chart = LightweightCharts.createChart(container, { width: chartData['width'], height: chartData['height'] })
      chart.applyOptions({crosshair: {mode: 2}})
      console.log(chartData)
      chartData['series'].forEach(function (serie) {
        console.log(serie)
        if (serie['type'] == 'candles') {
          let candleSeries = chart.addCandlestickSeries();
          candleSeries.setData(serie['values']);
          if (serie.hasOwnProperty('markers')) {
            candleSeries.setMarkers(serie['markers']);
          }
        } else if (serie['type'] == 'lines') {
          chart.addLineSeries({
            color: serie['color'] || '#ccc',
            lineStyle: serie['lineStyle'] || 0,
            lineWidth: serie['lineWidth'] || 2,
            crosshairMarkerVisible: serie['crosshairMarkerVisible'] || true,
            crosshairMarkerRadius: serie['crosshairMarkerRadius'] || 1,
            crosshairMarkerBorderColor: serie['crosshairMarkerBorderColor'] || '#ffffff',
            crosshairMarkerBackgroundColor: serie['crosshairMarkerBackgroundColor'] || '#2296f3',
            lineType: serie['lineType'] || 2,
          }).setData(serie['values']);
        }
      });
      chart.timeScale()
    });
  }
}


(async() => {
  const charter = new Charter()
  let response = await axios.get(charter.endpoint, {params: {}})
  charter.defineChart(response.data)
})();

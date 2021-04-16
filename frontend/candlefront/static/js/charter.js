let charts_menu = document.getElementById('menu-Charts')
charts_menu.classList.add('is-selected')

class Charter {
  charts = []
  data = []
  charts_container

  constructor() {
    this.charts_container = document.getElementById('page-container-charter');
    this.charts_container.style.position = 'relative'
    this.data = JSON.parse(this.charts_container.dataset.points);
  }

  init() {
    this.defineCharts()
    this.pinCharts()
    this.addChartLegends()
  }

  defineCharts() {
    var i
    for (i = 0;  i < this.data.length; i++) {
      let chartData = this.data[i]
      let container = document.createElement('div')
      container.style.position = 'relative';
      this.charts_container.appendChild(container)
      const chart = LightweightCharts.createChart(container, { width: chartData['width'], height: chartData['height'] })
      chart.applyOptions({crosshair: {mode: 0}})
      chartData['series'].forEach(function (serie) {
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
      this.charts.push({'chart': chart, 'container': container, 'id': chartData.id})
      chart.timeScale()
    }
  }

  pinCharts() {
    var i
    for (i = 0; i < this.charts.length; i++) {
      let handler = this.getChartHandler(i)
      this.charts[i].chart.timeScale().subscribeVisibleTimeRangeChange(handler)
    }
  }

  getChartHandler(chart_index) {
    var chart = this.charts[chart_index].chart
    var i
    var chartsToHandle = []
    for (i = 0; i < this.charts.length; i++) {
      if (i != chart_index) {
        chartsToHandle.push(this.charts[i].chart)
      }
    }
    var handler = function() {
      var barSpacing1 = chart.timeScale().getBarSpacing();
      var scrollPosition1 = chart.timeScale().scrollPosition();
      for (i = 0; i < chartsToHandle.length; i++) {
        chartsToHandle[i].timeScale().applyOptions(
          {rightOffset: scrollPosition1, barSpacing: barSpacing1}
        )
      }
    }
    return handler
  }

  addChartLegends() {
    var i
    for (i = 0; i < this.charts.length; i++) {
      var chart_obj = this.charts[i]
      var legend = document.createElement('div');
      legend.classList.add('legend');
      chart_obj.container.appendChild(legend);
      var firstRow = document.createElement('div');
      firstRow.innerText = chart_obj.id;
      legend.appendChild(firstRow);
    }
  }
}


const charter = new Charter()
charter.init()

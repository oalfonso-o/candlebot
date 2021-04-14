const ROUTES = [
  {
    'label': 'Charts',
    'uri': '/',
  },
  {
    'label': 'Backfill',
    'uri': '/backfill.html',
  },
  {
    'label': 'Backtesting',
    'uri': '/backtesting.html',
  },
  {
    'label': 'Candlebot',
    'uri': '/candlebot.html',
  },
  {
    'label': 'Market',
    'uri': '/market.html',
  },
]

function onReady(callback) {
  var intervalId = window.setInterval(function() {
    if (document.getElementsByTagName('body')[0] !== undefined) {
      window.clearInterval(intervalId);
      callback.call(this);
    }
  }, 1000);
}

function setVisible(selector, visible) {
  document.querySelector(selector).style.display = visible ? 'block' : 'none';
}

onReady(function() {
  setVisible('#page', true);
  setVisible('#loading', false);
});


class Head extends HTMLElement {
  constructor() {super();}

  connectedCallback() {
    this.innerHTML = `
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <link rel="stylesheet" href="css/vanilla-framework.min.css">
      <link rel="stylesheet" href="css/style.css">
      <title>Candlebot Charter</title>
    `;
  }
}
customElements.define('head-content', Head);


class PageHeader extends HTMLElement {
  constructor() {super();}

  connectedCallback() {
    var lis = ''
    var i
    for (i = 0; i < ROUTES.length; i++) {
      let li = `
        <li class="p-navigation__item" id="menu-` + ROUTES[i].label.toLowerCase() + `">
          <a class="p-navigation__link" href="` + ROUTES[i].uri + `">` + ROUTES[i].label + `</a>
        </li>
      `
      lis += li
    }
    this.innerHTML = `
      <header id="navigation" class="p-navigation">
      <div class="p-navigation__row">
        <div class="p-navigation__banner">
          <div class="p-navigation__logo">
            <a class="p-navigation__item" href="/">
              <img class="p-navigation__image" src="img/candle.png" alt="CandleBot">
            </a>
          </div>
          <a href="#navigation" class="p-navigation__toggle--open" title="menu">Menu</a>
          <a href="#navigation-closed" class="p-navigation__toggle--close" title="close menu">Close menu</a>
        </div>
        <nav class="p-navigation__nav" aria-label="Example main navigation">
          <span class="u-off-screen">
            <a href="/">Jump to main content</a>
          </span>
          <ul class="p-navigation__items">
            ` + lis + `
          </ul>
        </nav>
      </div>
      </header>
    `;
  }
}
customElements.define('page-header', PageHeader);


class PageHeaderMenu extends HTMLElement {
  constructor() {super();}

  connectedCallback() {
    this.innerHTML = `
      <div class="l-navigation-bar">
        <div class="u-clearfix"><code>l-navigation-bar</code> <button class="u-float-right js-menu-toggle is-dense u-no-margin">Menu</button></div>
      </div>
    `;
  }
}
customElements.define('page-header-menu', PageHeaderMenu);


(async() => {
  let endpoint_symbols = ENV.api.host + ':' + ENV.api.port + '/' + 'forms' + '/' + 'symbols'
  let endpoint_intervals = ENV.api.host + ':' + ENV.api.port + '/' + 'forms' + '/' + 'intervals'
  let response_symbols = await axios.get(endpoint_symbols, {params: {}})
  let response_intervals = await axios.get(endpoint_intervals, {params: {}})
  load_form(response_symbols, response_intervals)
})();


function load_form(symbols, intervals) {
  let form = `
    <div class="l-navigation-bar">
      <div class="u-clearfix"><code>l-navigation-bar</code> <button class="u-float-right js-menu-toggle is-dense u-no-margin">Menu</button></div>
    </div>
    <header class="l-navigation">
      <div class="l-navigation__drawer">
        <p class="demo-controls u-hide--large u-align--right">
          <button class="js-menu-pin is-dense u-no-margin u-hide--small">Pin</button>
          <button class="js-menu-close is-dense u-no-margin u-hide--medium">Close</button>
        </p>
        <form>
        <label for="date_from">Date From</label>
        <input type="date" id="date_from" name="date_from">
        <label for="date_to">Date To</label>
        <input type="date" id="date_to" name="date_to">
          <label for="symbol">Symbol</label>
          <select name="symbol" id="symbol">
            <option value="etheur" default>ETHEUR</option>
            <option value="btceur">BTCEUR</option>
          </select>
          <label for="interval">Interval</label>
          <select name="interval" id="interval">
            <option value="1d" default>1d</option>
            <option value="1h">1h</option>
            <option value="15m">15m</option>
            <option value="1m">1m</option>
          </select>
          <label for="strategy">Strategy</label>
          <select name="strategy" id="strategy">
            <option value="ema1" default>EMA1</option>
          </select>
          <button type="submit" name="submit">Submit</button>
        </form>
      </div>
    </header>
  `
  class MenuLeft extends HTMLElement {
    constructor() {super();}
    connectedCallback() {this.innerHTML = form}
  }
  customElements.define('menu-left', MenuLeft);
}
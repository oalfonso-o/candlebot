const ROUTES = [
  {
    'label': 'Charts',
    'uri': '/',
  },
  {
    'label': 'Backfill',
    'uri': '/backfill',
  },
  {
    'label': 'Backtesting',
    'uri': '/backtesting',
  },
  {
    'label': 'Candlebot',
    'uri': '/candlebot',
  },
  {
    'label': 'Market',
    'uri': '/market',
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

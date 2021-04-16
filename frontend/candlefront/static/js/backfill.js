let backfill_menu = document.getElementById('menu-Backfill')
backfill_menu.classList.add('is-selected')


function init_accordion(data) {
  var accordion = `
    <aside class="p-accordion">
      <ul class="p-accordion__list">
  `
  var i
  for (i = 0;  i < data.length; i++) {
    let symbol = data[i]
    accordion += `
      <li class="p-accordion__group">
        <div role="heading" aria-level="3" class="p-accordion__heading">
          <button type="button" class="p-accordion__tab" id="tab` + i + `" aria-controls="tab` + i + `-section" aria-expanded="true">` + symbol.name + `</button>
        </div>
        <section class="p-accordion__panel" id="tab` + i + `-section" aria-hidden="false" aria-labelledby="tab` + i + `">
    `
    var e
    for (e = 0;  e < symbol.intervals.length; e++) {
      let interval = symbol.intervals[e]
      accordion += `
          <div class="row">
            <div class="col-2">
              <span><b>` + interval.id + `</b></span>
            </div>
            <div class="col-4">
              <span>min: ` + interval.date_from + `</span>
            </div>
            <div class="col-4">
              <span>max: ` + interval.date_to + `</span>
            </div>
            <div class="col-2">
              <span style="float:right;">klines: ` + interval.count + `</span>
            </div>
          </div>
      `
    }
    accordion += '</section></li>'
  }
  accordion += '</ul></aside>'
  return accordion
}

function init_backfill_page(data) {
  let backfill_container = document.getElementById('page-container-backfill');
  backfill_container.style.position = 'relative'

  let title = `<p>Historic backfills</p>`
  accordion = init_accordion(data)

  backfill_container.innerHTML = title + accordion
  // Setup all accordions on the page.
  var accordions = document.querySelectorAll('.p-accordion');
  for (var i = 0, l = accordions.length; i < l; i++) {
    setupAccordion(accordions[i]);
  }
}


let endpoint = ENV.api.host + ':' + ENV.api.port + '/' + 'backfill' + '/' + 'list';

(async() => {
  let response = await axios.get(endpoint, {params: {}})
  init_backfill_page(response.data)
})();



/**
  Toggles the necessary aria- attributes' values on the accordion panels
  and handles to show or hide them.
  @param {HTMLElement} element The tab that acts as the handles.
  @param {Boolean} show Whether to show or hide the accordion panel.
*/
function toggleExpanded(element, show) {
  var target = document.getElementById(element.getAttribute('aria-controls'));
  if (target) {
    element.setAttribute('aria-expanded', show);
    target.setAttribute('aria-hidden', !show);
  }
}

/**
Attaches event listeners for the accordion open and close click events.
@param {HTMLElement} accordionContainer The accordion container element.
*/
function setupAccordion(accordionContainer) {
// Finds any open panels within the container and closes them.
function closeAllPanels() {
  var openPanels = accordionContainer.querySelectorAll('[aria-expanded=true]');
  for (var i = 0, l = openPanels.length; i < l; i++) {
  toggleExpanded(openPanels[i], false);
  }
}

// Set up an event listener on the container so that panels can be added
// and removed and events do not need to be managed separately.
accordionContainer.addEventListener('click', function (event) {
  var target = event.target;

  if (target.closest) {
  target = target.closest('[class*="p-accordion__tab"]');
  } else if (target.msMatchesSelector) {
  // IE friendly `Element.closest` equivalent
  // as in https://developer.mozilla.org/en-US/docs/Web/API/Element/closest
  do {
      if (target.msMatchesSelector('[class*="p-accordion__tab"]')) {
      break;
      }
      target = target.parentElement || target.parentNode;
  } while (target !== null && target.nodeType === 1);
  }

  if (target) {
  var isTargetOpen = target.getAttribute('aria-expanded') === 'true';
  closeAllPanels();

  // Toggle visibility of the target panel.
  toggleExpanded(target, !isTargetOpen);
  }
});
}

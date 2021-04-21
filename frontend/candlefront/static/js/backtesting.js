let backtesting_menu = document.getElementById('menu-Backtesting')
backtesting_menu.classList.add('is-selected')

var create_test_checkbox = document.getElementById('create_test_checkbox');
var create_test_submit_button = document.getElementById('create_test_submit_button');
create_test_checkbox.onchange = function() {
  create_test_submit_button.disabled = !this.checked;
};

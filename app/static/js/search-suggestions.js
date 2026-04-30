document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.search-box').forEach(function (box) {
    const input = box.querySelector('.search-input');
    const items = Array.from(box.querySelectorAll('.search-suggestion'));
    const empty = box.querySelector('.search-empty');

    if (!input || !items.length) return;

    function normalize(value) {
      return (value || '')
        .toString()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .toLowerCase()
        .trim();
    }

    function updateSuggestions() {
      const term = normalize(input.value);
      let shown = 0;

      items.forEach(function (item) {
        const name = normalize(item.dataset.productName);
        const matches = term.length > 0 && name.includes(term) && shown < 6;
        item.hidden = !matches;
        if (matches) shown += 1;
      });

      if (empty) empty.hidden = !(term.length > 0 && shown === 0);
      box.classList.toggle('has-query', term.length > 0);
    }

    input.addEventListener('input', updateSuggestions);
    input.addEventListener('focus', updateSuggestions);
    updateSuggestions();
  });
});

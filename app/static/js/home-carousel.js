(function(){
  const carousel = document.querySelector('[data-home-carousel]');
  if(!carousel) return;
  const slides = Array.from(carousel.querySelectorAll('.home-slide'));
  const dots = Array.from(carousel.querySelectorAll('.home-carousel-dots button'));
  const prev = carousel.querySelector('.home-carousel-prev');
  const next = carousel.querySelector('.home-carousel-next');
  if(slides.length <= 1) return;
  let current = 0;
  let timer;
  function show(index){
    current = (index + slides.length) % slides.length;
    slides.forEach((slide, i) => slide.classList.toggle('is-active', i === current));
    dots.forEach((dot, i) => dot.classList.toggle('is-active', i === current));
  }
  function restart(){
    clearInterval(timer);
    timer = setInterval(function(){ show(current + 1); }, 5500);
  }
  prev && prev.addEventListener('click', function(e){ e.preventDefault(); show(current - 1); restart(); });
  next && next.addEventListener('click', function(e){ e.preventDefault(); show(current + 1); restart(); });
  dots.forEach(function(dot, index){ dot.addEventListener('click', function(e){ e.preventDefault(); show(index); restart(); }); });
  carousel.addEventListener('mouseenter', function(){ clearInterval(timer); });
  carousel.addEventListener('mouseleave', restart);
  restart();
})();

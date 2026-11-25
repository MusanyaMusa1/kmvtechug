(() => {
  const menuButton = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.primary-nav');
  if (menuButton && nav) {
    menuButton.addEventListener('click', () => {
      const open = nav.classList.toggle('open');
      menuButton.setAttribute('aria-expanded', String(open));
      menuButton.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
    });
    nav.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
      nav.classList.remove('open');
      menuButton.setAttribute('aria-expanded', 'false');
      menuButton.setAttribute('aria-label', 'Open navigation');
    }));
  }
  const year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();
  document.querySelectorAll('[data-interest]').forEach(link => link.addEventListener('click', () => {
    const select = document.getElementById('interest');
    if (select) select.value = link.dataset.interest;
  }));
  const form = document.getElementById('interestForm');
  if (form) form.addEventListener('submit', event => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const data = new FormData(form);
    const subject = encodeURIComponent('Digital Independence enquiry: ' + data.get('interest'));
    const body = encodeURIComponent(
      'Name: ' + data.get('name') + '\nEmail: ' + data.get('email') + '\nInterest: ' + data.get('interest') + '\n\nMessage:\n' + data.get('message')
    );
    const status = document.getElementById('formStatus');
    status.textContent = 'Your email application should open with the enquiry prepared. Please send it there to complete your message.';
    window.location.href = 'mailto:kmvtechug@gmail.com?subject=' + subject + '&body=' + body;
  });
})();

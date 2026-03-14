/* ============================================================
   BloodLink - Main JavaScript File
   Frontend validation, UI interactions, filter logic
   ============================================================ */

/* ---- MOBILE MENU TOGGLE ---- */
function toggleMenu() {
  const navLinks = document.querySelector('.nav-links');
  const navActions = document.querySelector('.nav-actions');
  if (navLinks) navLinks.style.display = navLinks.style.display === 'flex' ? 'none' : 'flex';
  if (navActions) navActions.style.display = navActions.style.display === 'flex' ? 'none' : 'flex';
}

/* ---- MODAL HELPERS ---- */
function openModal(id) {
  const m = document.getElementById(id);
  if (m) m.classList.add('open');
}

function closeModal(id) {
  const m = document.getElementById(id);
  if (m) m.classList.remove('open');
}

// Close modal when clicking overlay background
document.addEventListener('click', function(e) {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('open');
  }
});

/* ---- ADMIN SECTION SWITCHER ---- */
function showSection(name) {
  // Hide all sections
  ['overview', 'camps', 'donors', 'registrations'].forEach(function(s) {
    const el = document.getElementById('section-' + s);
    if (el) el.style.display = 'none';
  });
  // Show requested
  const target = document.getElementById('section-' + name);
  if (target) target.style.display = 'block';

  // Update active sidebar link
  document.querySelectorAll('.sidebar-nav-item').forEach(function(item) {
    item.classList.remove('active');
  });
  event.currentTarget.classList.add('active');
}

/* ---- DELETE CONFIRMATION ---- */
function confirmDelete() {
  if (confirm('Are you sure you want to delete this camp? This action cannot be undone.')) {
    alert('Camp deleted successfully! (Demo mode — connect Flask backend to apply changes.)');
  }
}

/* ---- CAMP FILTER ---- */
function filterCamps(type, btn) {
  // Update active filter button
  document.querySelectorAll('.filter-btn').forEach(function(b) {
    b.classList.remove('active');
  });
  btn.classList.add('active');

  // Show/hide camp cards
  document.querySelectorAll('.camp-card').forEach(function(card) {
    if (type === 'all') {
      card.style.display = 'flex';
    } else {
      card.style.display = card.dataset.type === type ? 'flex' : 'none';
    }
  });
}

/* ============================================================
   REGISTRATION FORM VALIDATION
   ============================================================ */
(function() {
  var form = document.getElementById('registerForm');
  if (!form) return;

  form.addEventListener('submit', function(e) {
    e.preventDefault();
    var valid = true;

    /* Helper functions */
    function showError(id) {
      var el = document.getElementById(id);
      if (el) el.classList.add('show');
    }
    function hideError(id) {
      var el = document.getElementById(id);
      if (el) el.classList.remove('show');
    }
    function markError(fieldId) {
      var el = document.getElementById(fieldId);
      if (el) el.classList.add('error');
    }
    function clearError(fieldId) {
      var el = document.getElementById(fieldId);
      if (el) el.classList.remove('error');
    }

    /* Name */
    var name = document.getElementById('name');
    if (!name || name.value.trim().length < 2) {
      showError('nameError'); markError('name'); valid = false;
    } else { hideError('nameError'); clearError('name'); }

    /* Age */
    var age = document.getElementById('age');
    var ageVal = parseInt(age ? age.value : '');
    if (!age || isNaN(ageVal) || ageVal < 18 || ageVal > 60) {
      showError('ageError'); markError('age'); valid = false;
    } else { hideError('ageError'); clearError('age'); }

    /* Gender */
    var gender = document.getElementById('gender');
    if (!gender || gender.value === '') {
      showError('genderError'); valid = false;
    } else { hideError('genderError'); }

    /* Blood Group */
    var blood = document.getElementById('blood_group');
    if (!blood || blood.value === '') {
      showError('bloodError'); valid = false;
    } else { hideError('bloodError'); }

    /* Phone */
    var phone = document.getElementById('phone');
    var phoneRegex = /^[0-9]{10}$/;
    if (!phone || !phoneRegex.test(phone.value.trim())) {
      showError('phoneError'); markError('phone'); valid = false;
    } else { hideError('phoneError'); clearError('phone'); }

    /* Email */
    var email = document.getElementById('email');
    var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email || !emailRegex.test(email.value.trim())) {
      showError('emailError'); markError('email'); valid = false;
    } else { hideError('emailError'); clearError('email'); }

    /* City */
    var city = document.getElementById('city');
    if (!city || city.value.trim().length < 2) {
      showError('cityError'); markError('city'); valid = false;
    } else { hideError('cityError'); clearError('city'); }

    /* Password */
    var password = document.getElementById('password');
    if (!password || password.value.length < 6) {
      showError('passwordError'); markError('password'); valid = false;
    } else { hideError('passwordError'); clearError('password'); }

    /* Confirm Password */
    var confirm = document.getElementById('confirm_password');
    if (!confirm || confirm.value !== password.value) {
      showError('confirmError'); markError('confirm_password'); valid = false;
    } else { hideError('confirmError'); clearError('confirm_password'); }

    /* If all valid, submit (Flask will handle POST) */
    if (valid) {
      /* Demo mode — show success, then submit */
      alert('Registration validated! Submitting to server...');
      form.submit();
    }
  });

  /* Real-time validation on input */
  var fields = form.querySelectorAll('input, select');
  fields.forEach(function(field) {
    field.addEventListener('input', function() {
      field.classList.remove('error');
    });
  });
})();

/* ============================================================
   LOGIN FORM VALIDATION
   ============================================================ */
(function() {
  var form = document.getElementById('loginForm');
  if (!form) return;

  form.addEventListener('submit', function(e) {
    e.preventDefault();
    var valid = true;

    var email = document.getElementById('loginEmail');
    var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email || !emailRegex.test(email.value.trim())) {
      document.getElementById('loginEmailError').classList.add('show');
      email.classList.add('error');
      valid = false;
    } else {
      document.getElementById('loginEmailError').classList.remove('show');
      email.classList.remove('error');
    }

    var password = document.getElementById('loginPassword');
    if (!password || password.value.trim().length === 0) {
      document.getElementById('loginPasswordError').classList.add('show');
      password.classList.add('error');
      valid = false;
    } else {
      document.getElementById('loginPasswordError').classList.remove('show');
      password.classList.remove('error');
    }

    if (valid) {
      form.submit();
    }
  });
})();

/* ============================================================
   ADMIN LOGIN FORM VALIDATION
   ============================================================ */
(function() {
  var form = document.getElementById('adminLoginForm');
  if (!form) return;

  form.addEventListener('submit', function(e) {
    e.preventDefault();
    var valid = true;

    var user = document.getElementById('adminUser');
    if (!user || user.value.trim().length === 0) {
      document.getElementById('adminUserError').classList.add('show');
      user.classList.add('error');
      valid = false;
    } else {
      document.getElementById('adminUserError').classList.remove('show');
      user.classList.remove('error');
    }

    var pass = document.getElementById('adminPass');
    if (!pass || pass.value.length === 0) {
      document.getElementById('adminPassError').classList.add('show');
      pass.classList.add('error');
      valid = false;
    } else {
      document.getElementById('adminPassError').classList.remove('show');
      pass.classList.remove('error');
    }

    if (valid) {
      form.submit();
    }
  });
})();

/* ============================================================
   SMOOTH SCROLL for anchor links
   ============================================================ */
document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
  anchor.addEventListener('click', function(e) {
    var target = document.querySelector(this.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});

/* ============================================================
   ANIMATED COUNTER for stat numbers
   ============================================================ */
function animateCounters() {
  var counters = document.querySelectorAll('.stat-number');
  counters.forEach(function(counter) {
    var text = counter.innerText;
    var num = parseInt(text.replace(/\D/g, ''));
    var suffix = text.replace(/[0-9]/g, '');
    if (isNaN(num)) return;

    var current = 0;
    var step = Math.ceil(num / 50);
    var timer = setInterval(function() {
      current += step;
      if (current >= num) {
        current = num;
        clearInterval(timer);
      }
      counter.innerText = current + suffix;
    }, 30);
  });
}

/* Run counter animation when stats section is visible */
var statsSection = document.querySelector('.stats-section');
if (statsSection) {
  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        animateCounters();
        observer.disconnect();
      }
    });
  }, { threshold: 0.3 });
  observer.observe(statsSection);
}

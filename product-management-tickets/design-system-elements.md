## Learning Jungle UI Elements

These snippets pair with `core/static/core/design-system.css` so engineers can drop components into any Django template. Load once per page:

```django
{% load static %}
<link rel="stylesheet" href="{% static 'core/design-system.css' %}">
```

### Screen Shell

```html
<div class="dsj-shell">
  <header class="dsj-shell__header">
    <p class="dsj-eyebrow">Ready, Maya?</p>
    <h1 class="dsj-hero">Start your Maths Challenge</h1>
    <p class="dsj-copy">Takes about 10 minutes.</p>
  </header>
  <!-- place cards/buttons/components below -->
</div>
```

### Card + Steps

```html
<section class="dsj-card">
  <ol class="dsj-progress-steps">
    <li>Answer quick maths questions</li>
    <li>Earn Bronze, Silver, or Gold</li>
    <li>Unlock your treasure chest</li>
  </ol>
</section>
```

### Buttons

```html
<button class="dsj-cta" type="submit">Start Maths Challenge</button>
<button class="dsj-link-button" type="button">Need your grown-up?</button>
```

### Answer Options

```html
<ul class="dsj-answer-list">
  <li>
    <label class="dsj-answer dsj-answer--selected">
      <input type="radio" name="answer" value="A" checked>
      <span class="dsj-answer__letter">A</span>
      <span class="dsj-copy">12 + 8 = 20</span>
    </label>
  </li>
  <!-- Repeat -->
</ul>
```

### Alert Banner

```html
<div class="dsj-alert">
  Choose one answer to continue.
</div>
```

### Status Chips

```html
<span class="dsj-status-chip dsj-status-chip--info">In progress</span>
<span class="dsj-status-chip dsj-status-chip--unlocked">Unlocked</span>
```

### Treasure Card

```html
<section class="dsj-treasure-card dsj-treasure-card--unlocked">
  <div class="dsj-treasure-icon"></div>
  <p class="dsj-copy">Treasure chest unlocked! Show this to your grown-up.</p>
</section>
```

### Wiggle Divider

```html
<div class="dsj-wiggle-divider" aria-hidden="true"></div>
```

Reuse these classes across flows to keep the child + parent experiences visually consistent with the approved palette and inspiration art. Add new patterns by extending the same prefixes (e.g., `dsj-`) so the system stays discoverable.

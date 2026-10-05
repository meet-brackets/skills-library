// Applies render options from the URL query: ?theme=dark&lang=sk&colors=palette&bg=%23123456&accent=%23F5A816&light=1
// and draws connector lines declared with <i class="link" …> (see references/engine-html.md → Lines).
// Include in every diagram: <script src="diagram.js"></script> right after <body>.
(function () {
  var q = new URLSearchParams(location.search);
  var root = document.documentElement;
  if (q.get('theme')) root.setAttribute('data-theme', q.get('theme'));
  if (q.get('lang')) root.setAttribute('data-lang', q.get('lang'));
  if (q.get('lang')) root.lang = q.get('lang');
  if (q.get('light')) root.setAttribute('data-light', '');
  root.setAttribute('data-colors', q.get('colors') || 'mono');
  if (q.get('bg')) root.style.setProperty('--brand-bg', q.get('bg'));
  if (q.get('accent')) root.style.setProperty('--brand-accent', q.get('accent'));
  if (q.get('onaccent')) root.style.setProperty('--brand-on-accent', q.get('onaccent'));

  // Load every weight up front (latin + latin-ext) and flag a missing font visibly.
  var sample = 'Aa ČčĽľŠšŤťŽžÝýÁáÍíÉéÚúÄäÔôŇň';
  Promise.all([
    document.fonts.load('400 34px Poppins', sample),
    document.fonts.load('500 34px Poppins', sample),
    document.fonts.load('600 34px Poppins', sample),
    document.fonts.load('500 34px "JetBrains Mono"', sample)
  ]).then(function () {
    var failed = [];
    document.fonts.forEach(function (f) { if (f.status === 'error') failed.push(f.family + ' ' + f.weight); });
    if (failed.length) {
      var el = document.createElement('div');
      el.className = 'font-error';
      el.textContent = 'FONT FAILED TO LOAD: ' + failed.join(', ');
      document.body.appendChild(el);
    }
    // Draw lines only after the final fonts are in, so they attach to the final layout.
    requestAnimationFrame(function () { requestAnimationFrame(drawLinks); });
  });

  // ---------------------------------------------------------------------------------------------
  // Lines. Declare: <i class="link" data-from="a" data-to="b" data-shape="elbow" …></i>
  //   data-from / data-to   element ids
  //   data-shape            straight | elbow (orthogonal, rounded corners) | tree (spine + turn into
  //                         the child's left side, like ├ └) | curve (smooth S-curve) |
  //                         radial (center to center, trimmed exactly at both outlines: spider / hub)
  //   data-from-side / data-to-side   top | bottom | left | right   (defaults per shape)
  //   data-mid              elbow: where the cross segment runs, 0–1 between the two ends (default .5)
  //   data-inset            tree: spine distance from the parent's left edge in px (default 24)
  //   data-radius           corner radius in px (default 16)
  //   data-gap              px left free before the target (default 0; 10 with an arrow)
  //   data-tone             line (default) | outline | accent
  //   data-weight           hair (default, 2 px) | stroke (3 px)
  //   data-arrow            end | start | both
  // Trees: <div class="kids" data-tree-from="parent-id" [data-inset data-radius data-gap data-tone]>
  //   draws a tree line from the parent to every direct child (no ids on the children needed).
  // ---------------------------------------------------------------------------------------------
  function drawLinks() {
    var canvas = document.querySelector('.diagram');
    var specs = [];
    document.querySelectorAll('.link[data-from][data-to]').forEach(function (ln) {
      specs.push({ from: document.getElementById(ln.dataset.from), to: document.getElementById(ln.dataset.to), o: ln.dataset });
    });
    document.querySelectorAll('[data-tree-from]').forEach(function (group) {
      var parent = document.getElementById(group.dataset.treeFrom);
      Array.prototype.forEach.call(group.children, function (child) {
        specs.push({ from: parent, to: child, o: {
          shape: 'tree', inset: group.dataset.inset, radius: group.dataset.radius || '14',
          gap: group.dataset.gap || '14', tone: group.dataset.tone, weight: group.dataset.weight } });
      });
    });
    if (!canvas || !specs.length) return;
    var NS = 'http://www.w3.org/2000/svg';
    var box = canvas.getBoundingClientRect();
    var svg = document.createElementNS(NS, 'svg');
    svg.setAttribute('class', 'links');
    svg.setAttribute('width', box.width);
    svg.setAttribute('height', box.height);
    var defs = document.createElementNS(NS, 'defs');
    ['line', 'outline', 'accent'].forEach(function (tone) {
      var m = document.createElementNS(NS, 'marker');
      m.setAttribute('id', 'arrow-' + tone);
      m.setAttribute('viewBox', '-12 -12 24 24');
      m.setAttribute('markerWidth', '24');
      m.setAttribute('markerHeight', '24');
      m.setAttribute('markerUnits', 'userSpaceOnUse');
      m.setAttribute('orient', 'auto-start-reverse');
      var p = document.createElementNS(NS, 'path');
      p.setAttribute('d', 'M -9 -8 L 0 0 L -9 8');
      p.setAttribute('class', 'links__head tone-' + tone);
      m.appendChild(p);
      defs.appendChild(m);
    });
    svg.appendChild(defs);

    function rect(el) {
      if (!el) return null;
      var r = el.getBoundingClientRect();
      var br = getComputedStyle(el).borderTopLeftRadius;
      var rad = br.indexOf('%') > -1 ? Math.min(r.width, r.height) * parseFloat(br) / 100 : parseFloat(br) || 0;
      return { rad: Math.min(rad, r.width / 2, r.height / 2), w: r.width, h: r.height, l: r.left - box.left, t: r.top - box.top, r: r.right - box.left, b: r.bottom - box.top,
               cx: (r.left + r.right) / 2 - box.left, cy: (r.top + r.bottom) / 2 - box.top };
    }
    function anchor(r, side) {
      if (side === 'top') return { x: r.cx, y: r.t, nx: 0, ny: -1 };
      if (side === 'bottom') return { x: r.cx, y: r.b, nx: 0, ny: 1 };
      if (side === 'left') return { x: r.l, y: r.cy, nx: -1, ny: 0 };
      return { x: r.r, y: r.cy, nx: 1, ny: 0 };
    }
    function defaultSides(a, b, shape) {
      if (shape === 'tree') return ['bottom', 'left'];
      // A target fully below / above / beside the source decides the direction outright.
      if (b.t >= a.b) return ['bottom', 'top'];
      if (b.b <= a.t) return ['top', 'bottom'];
      if (b.l >= a.r) return ['right', 'left'];
      if (b.r <= a.l) return ['left', 'right'];
      var dx = b.cx - a.cx, dy = b.cy - a.cy;
      if (Math.abs(dy) >= Math.abs(dx)) return dy > 0 ? ['bottom', 'top'] : ['top', 'bottom'];
      return dx > 0 ? ['right', 'left'] : ['left', 'right'];
    }
    // Is (x, y) inside the element's rounded-rect outline (circle, pill and box included)?
    function inside(r, x, y) {
      var dx = Math.abs(x - r.cx), dy = Math.abs(y - r.cy), hw = r.w / 2, hh = r.h / 2, k = r.rad;
      if (dx > hw || dy > hh) return false;
      var qx = dx - (hw - k), qy = dy - (hh - k);
      return qx <= 0 || qy <= 0 || qx * qx + qy * qy <= k * k;
    }
    // Point where the segment from r's center towards (tx, ty) leaves r's outline.
    function exitPoint(r, tx, ty) {
      var lo = 0, hi = 1;
      for (var i = 0; i < 24; i++) {
        var m = (lo + hi) / 2;
        if (inside(r, r.cx + (tx - r.cx) * m, r.cy + (ty - r.cy) * m)) lo = m; else hi = m;
      }
      return { x: r.cx + (tx - r.cx) * hi, y: r.cy + (ty - r.cy) * hi };
    }
    // Polyline → path with circular corners (radius clamped to half of each segment).
    function rounded(pts, radius) {
      var d = 'M ' + pts[0].x + ' ' + pts[0].y;
      for (var i = 1; i < pts.length - 1; i++) {
        var p0 = pts[i - 1], p1 = pts[i], p2 = pts[i + 1];
        var l1 = Math.hypot(p1.x - p0.x, p1.y - p0.y), l2 = Math.hypot(p2.x - p1.x, p2.y - p1.y);
        if (l1 < 0.5 || l2 < 0.5) continue;
        var rr = Math.min(radius, l1 / 2, l2 / 2);
        var ux = (p1.x - p0.x) / l1, uy = (p1.y - p0.y) / l1, vx = (p2.x - p1.x) / l2, vy = (p2.y - p1.y) / l2;
        var cross = ux * vy - uy * vx;
        if (Math.abs(cross) < 1e-6) { d += ' L ' + p1.x + ' ' + p1.y; continue; }
        d += ' L ' + (p1.x - ux * rr) + ' ' + (p1.y - uy * rr);
        d += ' A ' + rr + ' ' + rr + ' 0 0 ' + (cross > 0 ? 1 : 0) + ' ' + (p1.x + vx * rr) + ' ' + (p1.y + vy * rr);
      }
      var last = pts[pts.length - 1];
      return d + ' L ' + last.x + ' ' + last.y;
    }

    specs.forEach(function (spec) {
      var ln = { dataset: spec.o };
      var ra = rect(spec.from), rb = rect(spec.to);
      if (!ra || !rb) return;
      var shape = ln.dataset.shape || 'elbow';
      var sides = defaultSides(ra, rb, shape);
      var a = anchor(ra, ln.dataset.fromSide || sides[0]);
      var b = anchor(rb, ln.dataset.toSide || sides[1]);
      var radius = parseFloat(ln.dataset.radius || 16);
      var arrow = ln.dataset.arrow;
      var gap = parseFloat(ln.dataset.gap || (arrow === 'end' || arrow === 'both' ? 10 : 0));
      var gapStart = arrow === 'start' || arrow === 'both' ? gap : 0;
      b = { x: b.x + b.nx * gap, y: b.y + b.ny * gap, nx: b.nx, ny: b.ny };
      a = { x: a.x + a.nx * gapStart, y: a.y + a.ny * gapStart, nx: a.nx, ny: a.ny };
      var d;
      if (shape === 'radial') {
        var p1 = exitPoint(ra, rb.cx, rb.cy), p2 = exitPoint(rb, ra.cx, ra.cy);
        var len = Math.hypot(p2.x - p1.x, p2.y - p1.y) || 1;
        var ux = (p2.x - p1.x) / len, uy = (p2.y - p1.y) / len;
        p2 = { x: p2.x - ux * gap, y: p2.y - uy * gap };
        p1 = { x: p1.x + ux * gapStart, y: p1.y + uy * gapStart };
        d = 'M ' + p1.x + ' ' + p1.y + ' L ' + p2.x + ' ' + p2.y;
      } else if (shape === 'straight') {
        // Side to side: run level through the middle of the two elements' overlap, so a horizontal
        // (or vertical) arrow stays horizontal even when the elements differ in size.
        if (a.nx !== 0 && b.nx !== 0) {
          var t = Math.max(ra.t, rb.t), bt = Math.min(ra.b, rb.b);
          if (bt > t) { a.y = b.y = (t + bt) / 2; }
        } else if (a.ny !== 0 && b.ny !== 0) {
          var l = Math.max(ra.l, rb.l), rt = Math.min(ra.r, rb.r);
          if (rt > l) { a.x = b.x = (l + rt) / 2; }
        }
        d = 'M ' + a.x + ' ' + a.y + ' L ' + b.x + ' ' + b.y;
      } else if (shape === 'curve') {
        var k = Math.max(Math.abs(b.x - a.x), Math.abs(b.y - a.y)) * 0.5;
        d = 'M ' + a.x + ' ' + a.y + ' C ' + (a.x + a.nx * k) + ' ' + (a.y + a.ny * k) + ' ' +
            (b.x + b.nx * k) + ' ' + (b.y + b.ny * k) + ' ' + b.x + ' ' + b.y;
      } else if (shape === 'tree') {
        var sx = ra.l + parseFloat(ln.dataset.inset || 24);
        d = rounded([{ x: sx, y: ra.b }, { x: sx, y: b.y }, { x: b.x, y: b.y }], radius);
      } else {
        var mid = parseFloat(ln.dataset.mid || 0.5);
        var vertical = a.ny !== 0;
        var pts = vertical
          ? [a, { x: a.x, y: a.y + (b.y - a.y) * mid }, { x: b.x, y: a.y + (b.y - a.y) * mid }, b]
          : [a, { x: a.x + (b.x - a.x) * mid, y: a.y }, { x: a.x + (b.x - a.x) * mid, y: b.y }, b];
        d = rounded(pts, radius);
      }
      var tone = ln.dataset.tone || 'line';
      var path = document.createElementNS(NS, 'path');
      path.setAttribute('d', d);
      path.setAttribute('class', 'links__path tone-' + tone + (ln.dataset.weight === 'stroke' ? ' is-stroke' : ''));
      if (arrow === 'end' || arrow === 'both') path.setAttribute('marker-end', 'url(#arrow-' + tone + ')');
      if (arrow === 'start' || arrow === 'both') path.setAttribute('marker-start', 'url(#arrow-' + tone + ')');
      svg.appendChild(path);
    });
    canvas.insertBefore(svg, canvas.firstChild);
  }
})();

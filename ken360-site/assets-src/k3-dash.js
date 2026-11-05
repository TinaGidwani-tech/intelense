/* Interactive example dashboard in the hero. All data is illustrative. */
(function () {
  'use strict';
  var root = document.querySelector('[data-dash]'); if (!root) return;
  var MODS = {}; try { MODS = JSON.parse(root.getAttribute('data-mods')); } catch (e) { return; }
  var main = root.querySelector('[data-main]'), nav = [].slice.call(root.querySelectorAll('.nv')), nameEl = root.querySelector('[data-sitename]');
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function tag(k) { var m = MODS[k]; return '<span class="mtag" style="--c:' + m[1] + '"><span class="md" style="--c:' + m[1] + '"></span>' + m[0] + '</span>'; }
  function tags(a) { return a.map(tag).join(''); }

  var SITES = [
    { n: 'Example site', src: { Cameras: 24, Sensors: 112, Drones: 2, Robots: 6, Voice: 3 }, mods: ['kenvision', 'kensafety', 'keniot', 'kenrobotics', 'kenvoice', 'kenagri', 'kenhome'], alerts: 7, inc: [
      { t: 'Crowd building where PPE has dropped', z: 'Loading dock', m: ['kenvision', 'kensafety'], s: 'Open', at: '09:42', to: 'shift supervisor', tl: [['09:41', 'KenVision', 'Crowd density rising in Zone B'], ['09:42', 'KenSafety', 'PPE compliance dropped in Zone B'], ['09:42', 'Ken360', 'Compared both and opened one incident']] },
      { t: 'Compressor temperature high', z: 'Production line', m: ['keniot'], s: 'Watching', at: '09:15', to: 'maintenance team', tl: [['09:12', 'KenIoT', 'Compressor temperature above its limit'], ['09:15', 'Ken360', 'Checked nearby cameras and sensors, no related event'], ['09:15', 'Ken360', 'Raised as a single alert']] },
      { t: 'Queue at counter 3', z: 'Office and counter', m: ['kenvoice'], s: 'Resolved', at: '08:50', to: 'floor manager', tl: [['08:47', 'KenVoice', 'Customer queue building at counter 3'], ['08:49', 'Staff', 'Second counter opened'], ['08:50', 'Ken360', 'Marked resolved']] }] },
    { n: 'Warehouse B', src: { Cameras: 16, Sensors: 48, Drones: 0, Robots: 4, Voice: 0 }, mods: ['kenvision', 'kensafety', 'keniot', 'kenrobotics'], alerts: 5, inc: [
      { t: 'Forklift close to pedestrian aisle', z: 'Aisle 4', m: ['kenvision', 'kensafety'], s: 'Open', at: '10:12', to: 'floor supervisor', tl: [['10:11', 'KenVision', 'Forklift entering a pedestrian aisle'], ['10:12', 'KenSafety', 'Person detected without high-visibility vest'], ['10:12', 'Ken360', 'Compared both and opened one incident']] },
      { t: 'Robot stopped in packing aisle', z: 'Packing aisle', m: ['kenrobotics'], s: 'Watching', at: '09:58', to: 'operations lead', tl: [['09:57', 'KenRobotics', 'Robot paused on its route'], ['09:58', 'Ken360', 'No obstruction seen on nearby cameras'], ['09:58', 'Ken360', 'Raised as a single alert']] }] },
    { n: 'Retail store 2', src: { Cameras: 12, Sensors: 20, Drones: 0, Robots: 0, Voice: 4 }, mods: ['kenvision', 'kenvoice', 'keniot'], alerts: 4, inc: [
      { t: 'Queue building at counter 1', z: 'Front counter', m: ['kenvision', 'kenvoice'], s: 'Open', at: '12:30', to: 'store manager', tl: [['12:28', 'KenVision', 'More than the usual number of people waiting'], ['12:30', 'KenVoice', 'Customer waiting time rising at the counter'], ['12:30', 'Ken360', 'Compared both and opened one incident']] },
      { t: 'Chiller temperature drifting', z: 'Cold room', m: ['keniot'], s: 'Watching', at: '11:40', to: 'maintenance team', tl: [['11:36', 'KenIoT', 'Cold room temperature rising'], ['11:40', 'Ken360', 'Raised as a single alert']] }] }
  ];
  var USES = { Cameras: ['kenvision', 'kensafety', 'kenhome'], Sensors: ['keniot', 'kenagri'], Drones: ['kenagri', 'kenvision'], Robots: ['kenrobotics'], Voice: ['kenvoice'] };
  var RULES = [
    { t: 'Crowd rising and PPE dropped in the same zone', a: 'Open one incident', to: 'Shift supervisor', c: ['KenVision: crowd density above normal for the zone', 'KenSafety: PPE compliance below target in the same zone', 'Within the same few minutes'] },
    { t: 'Equipment temperature above its limit', a: 'Raise an alert', to: 'Maintenance team', c: ['KenIoT: reading above the limit set for the machine', 'Nearby cameras and sensors checked for a related event'] },
    { t: 'Queue longer than usual at a counter', a: 'Raise an alert', to: 'Floor manager', c: ['KenVision: people waiting above normal', 'KenVoice: waiting time rising'] }
  ];
  var st = { view: 'overview', site: 0, sel: 0, filter: 'All', rule: 0, chan: 'App', q: '' };
  var data = JSON.parse(JSON.stringify(SITES));
  function S() { return data[st.site]; }
  function openCount(s) { return s.inc.filter(function (i) { return i.s === 'Open'; }).length; }
  function total(s) { return Object.keys(s.src).reduce(function (a, k) { return a + s.src[k]; }, 0); }
  function now() { var d = new Date(); return ('0' + d.getHours()).slice(-2) + ':' + ('0' + d.getMinutes()).slice(-2); }
  var toastT;
  function toast(msg) {
    var t = root.querySelector('.u-toast'); if (!t) { t = document.createElement('div'); t.className = 'u-toast'; t.setAttribute('role', 'status'); root.querySelector('.ui-in').appendChild(t); }
    t.textContent = msg; t.classList.add('on'); clearTimeout(toastT); toastT = setTimeout(function () { t.classList.remove('on'); }, 2400);
  }

  function top(title, extra) { return '<div class="u-top"><b>' + title + '</b>' + (extra || '<span class="u-seg">Today</span>') + '</div>'; }
  function feedRows(list) {
    return list.map(function (it) {
      var idx = S().inc.indexOf(it);
      return '<button type="button" class="ir' + (idx === st.sel ? ' on' : '') + '" data-sel="' + idx + '"><span class="u-st s-' + it.s.toLowerCase() + '">' + it.s + '</span><b>' + esc(it.t) + '</b><small>' + esc(it.z) + ' · ' + it.at + '</small><span class="u-mt">' + tags(it.m) + '</span></button>';
    }).join('') || '<p class="empty">Nothing here.</p>';
  }
  function detail() {
    var it = S().inc[st.sel]; if (!it) return '<div class="u-detail"><p class="empty">Select an incident.</p></div>';
    var tl = it.tl.map(function (r) { return '<li><time>' + r[0] + '</time><span><b>' + esc(r[1]) + '</b>' + esc(r[2]) + '</span></li>'; }).join('');
    var acts = it.s === 'Resolved' ? '<span class="done">Resolved. No action needed.</span>' :
      '<button type="button" class="ab pri" data-act="notify">Notify ' + esc(it.to) + '</button>' + (it.s === 'Open' ? '<button type="button" class="ab" data-act="watch">Acknowledge</button>' : '') + '<button type="button" class="ab" data-act="resolve">Mark resolved</button>';
    return '<div class="u-detail"><div class="u-ph"><span class="u-mt">' + tags(it.m) + '</span><b>' + esc(it.t) + '</b><small>' + esc(it.z) + ' · <span class="u-st s-' + it.s.toLowerCase() + '">' + it.s + '</span></small></div><ol class="u-tl">' + tl + '</ol><div class="acts">' + acts + '</div></div>';
  }
  var V = {
    overview: function () {
      var s = S();
      return top(esc(s.n)) + '<div class="u-kpis"><button type="button" class="kp" data-go="sources"><small>Sources online</small><b>' + total(s) + '</b></button><button type="button" class="kp" data-go="incidents"><small>Alerts raised</small><b>' + s.alerts + '</b></button><button type="button" class="kp" data-go="incidents"><small>Open incidents</small><b>' + openCount(s) + '</b></button></div>'
        + '<div class="u-cols"><div class="u-feed"><span class="cap-t">Incidents</span>' + feedRows(s.inc) + '</div>' + detail() + '</div>';
    },
    incidents: function () {
      var s = S(), fs = ['All', 'Open', 'Watching', 'Resolved'];
      var list = s.inc.filter(function (i) { return st.filter === 'All' || i.s === st.filter; });
      var tabs = fs.map(function (f) { var n = f === 'All' ? s.inc.length : s.inc.filter(function (i) { return i.s === f; }).length; return '<button type="button" aria-pressed="' + (st.filter === f) + '" data-f="' + f + '">' + f + ' <em>' + n + '</em></button>'; }).join('');
      return top('Incidents', '<span class="u-seg">' + esc(s.n) + '</span>') + '<div class="u-tabs" role="group" aria-label="Filter incidents">' + tabs + '</div><div class="u-cols"><div class="u-feed">' + feedRows(list) + '</div>' + detail() + '</div>';
    },
    sites: function () {
      return top('Sites', '<span class="u-seg">' + data.length + ' sites</span>') + '<div class="sgrid">' + data.map(function (s, i) {
        return '<button type="button" class="sc' + (i === st.site ? ' on' : '') + '" data-site="' + i + '"><b>' + esc(s.n) + '</b><small>' + total(s) + ' sources · ' + openCount(s) + ' open</small><span class="u-mt">' + tags(s.mods.slice(0, 4)) + '</span></button>';
      }).join('') + '</div><p class="hint">Select a site to switch the whole dashboard to it.</p>';
    },
    sources: function () {
      var s = S(), q = st.q.toLowerCase();
      var rows = Object.keys(s.src).filter(function (k) { return !q || k.toLowerCase().indexOf(q) > -1; }).map(function (k) {
        var n = s.src[k]; return '<tr><td><b>' + k + '</b></td><td class="num">' + n + '</td><td><span class="u-mt">' + tags(USES[k].filter(function (m) { return s.mods.indexOf(m) > -1; })) + '</span></td><td><span class="u-st ' + (n ? 's-resolved' : '') + '">' + (n ? 'Live' : 'None') + '</span></td></tr>';
      }).join('');
      return top('Sources', '<span class="u-seg">' + esc(s.n) + '</span>') + '<input class="srch" type="search" placeholder="Search sources" aria-label="Search sources" value="' + esc(st.q) + '" data-q><table class="u-tbl"><thead><tr><th>Type</th><th class="num">Count</th><th>Used by</th><th>Status</th></tr></thead><tbody>' + (rows || '<tr><td colspan="4" class="empty">No match.</td></tr>') + '</tbody></table>';
    },
    modules: function () {
      var s = S();
      return top('Modules', '<span class="u-seg">' + esc(s.n) + '</span>') + '<ul class="mrows">' + Object.keys(MODS).map(function (k) {
        var on = s.mods.indexOf(k) > -1;
        return '<li class="' + (on ? '' : 'off') + '">' + tag(k) + '<span class="u-st ' + (on ? 's-resolved' : '') + '">' + (on ? 'Running on Ken360' : 'Not added') + '</span><a href="' + MODS[k][2] + '" target="_blank" rel="noopener">Open ' + MODS[k][0] + ' &rarr;</a></li>';
      }).join('') + '</ul><p class="hint">Every module runs on the same Ken360 engine.</p>';
    },
    rules: function () {
      return top('Alert rules', '<span class="u-seg">' + RULES.length + ' rules</span>') + '<div class="rules">' + RULES.map(function (r, i) {
        var o = i === st.rule;
        return '<div class="rl' + (o ? ' on' : '') + '"><button type="button" data-rule="' + i + '" aria-expanded="' + o + '"><b>' + esc(r.t) + '</b><small>' + r.a + ' &rarr; ' + r.to + '</small></button>' + (o ? '<ul>' + r.c.map(function (c) { return '<li>' + esc(c) + '</li>'; }).join('') + '</ul>' : '') + '</div>';
      }).join('') + '</div><button type="button" class="ab" data-act="newrule">New rule</button>';
    },
    settings: function () {
      var ch = ['App', 'Email', 'SMS'].map(function (c) { return '<button type="button" aria-pressed="' + (st.chan === c) + '" data-chan="' + c + '">' + c + '</button>'; }).join('');
      return top('Settings') + '<label class="fld">Site name<input type="text" maxlength="40" value="' + esc(S().n) + '" data-name></label><div class="fld">Send alerts by<div class="u-tabs" role="group" aria-label="Alert channel">' + ch + '</div></div><p class="hint">Example settings. Changes stay on this page only.</p>';
    }
  };

  function badges() {
    var b = root.querySelector('[data-badge="incidents"]'), n = openCount(S()); if (b) { b.textContent = n || ''; b.style.display = n ? '' : 'none'; }
    nameEl.textContent = S().n;
  }
  function render() {
    main.innerHTML = V[st.view]();
    nav.forEach(function (n) { n.classList.toggle('on', n.getAttribute('data-v') === st.view); });
    badges();
  }
  function go(v) { st.view = v; if (v === 'incidents') st.filter = 'All'; render(); }

  nav.forEach(function (n) { n.addEventListener('click', function () { go(n.getAttribute('data-v')); }); });
  main.addEventListener('click', function (e) {
    var t = e.target.closest('[data-sel],[data-go],[data-f],[data-site],[data-rule],[data-chan],[data-act]'); if (!t) return;
    var it = S().inc[st.sel];
    if (t.hasAttribute('data-sel')) { st.sel = +t.getAttribute('data-sel'); render(); }
    else if (t.hasAttribute('data-go')) go(t.getAttribute('data-go'));
    else if (t.hasAttribute('data-f')) { st.filter = t.getAttribute('data-f'); var l = S().inc.filter(function (i) { return st.filter === 'All' || i.s === st.filter; }); if (l.length && l.indexOf(it) < 0) st.sel = S().inc.indexOf(l[0]); render(); }
    else if (t.hasAttribute('data-site')) { st.site = +t.getAttribute('data-site'); st.sel = 0; st.filter = 'All'; st.view = 'overview'; render(); }
    else if (t.hasAttribute('data-rule')) { var r = +t.getAttribute('data-rule'); st.rule = st.rule === r ? -1 : r; render(); }
    else if (t.hasAttribute('data-chan')) { st.chan = t.getAttribute('data-chan'); render(); }
    else if (t.hasAttribute('data-act')) {
      var a = t.getAttribute('data-act');
      if (a === 'newrule') { toast('Example screen: rules are set up with your Intelense team.'); return; }
      if (!it) return;
      if (a === 'notify') { it.tl.push([now(), 'Notified', it.to.charAt(0).toUpperCase() + it.to.slice(1) + ' by ' + st.chan.toLowerCase()]); render(); toast('Notified ' + it.to + ' by ' + st.chan.toLowerCase()); }
      if (a === 'watch') { it.s = 'Watching'; it.tl.push([now(), 'You', 'Acknowledged']); render(); toast('Incident acknowledged'); }
      if (a === 'resolve') { it.s = 'Resolved'; it.tl.push([now(), 'You', 'Marked resolved']); render(); toast('Incident resolved'); }
    }
  });
  main.addEventListener('input', function (e) {
    if (e.target.hasAttribute('data-q')) { st.q = e.target.value; var p = e.target.selectionStart; render(); var i = main.querySelector('[data-q]'); i.focus(); i.setSelectionRange(p, p); }
    if (e.target.hasAttribute('data-name')) { S().n = e.target.value || 'Example site'; badges(); }
  });
  root.classList.add('live'); render();
})();

(function () {
    var ROWS = [
        ['1','2','3','4','5','6','7','8','9','0','<--'],
        ['a','z','e','r','t','y','u','i','o','p'],
        ['q','s','d','f','g','h','j','k','l','m'],
        ['MAJ','w','x','c','v','b','n','-','_','OK'],
        ['ESPACE']
    ];

    var target  = null;
    var shifted = false;
    var kb      = null;

    function buildKeyboard() {
        kb = document.createElement('div');
        kb.id = 'vkeyboard';

        ROWS.forEach(function (row) {
            var rowDiv = document.createElement('div');
            rowDiv.className = 'vkb-row';

            row.forEach(function (label) {
                var btn = document.createElement('button');
                btn.type      = 'button';
                btn.className = 'vkb-key';
                btn.textContent = label;

                if (label === '<--' || label === 'OK' || label === 'MAJ') {
                    btn.className += ' vkb-wide';
                } else if (label === 'ESPACE') {
                    btn.className += ' vkb-space';
                }

                btn.addEventListener('mousedown',  onKey, false);
                btn.addEventListener('touchstart',  onKey, { passive: false });
                rowDiv.appendChild(btn);
            });

            kb.appendChild(rowDiv);
        });

        document.body.appendChild(kb);
    }

    function onKey(e) {
        e.preventDefault();
        var label = this.textContent;

        if (label === '<--') {
            if (target) target.value = target.value.slice(0, -1);

        } else if (label === 'OK') {
            hide();
            var form = target && target.closest('form');
            if (form) form.requestSubmit ? form.requestSubmit() : form.submit();

        } else if (label === 'MAJ') {
            shifted = !shifted;
            updateShift();

        } else if (label === 'ESPACE') {
            if (target) target.value += ' ';

        } else {
            if (target) target.value += shifted ? label.toUpperCase() : label;
            if (shifted) { shifted = false; updateShift(); }
        }

        if (target) target.dispatchEvent(new Event('input', { bubbles: true }));
    }

    function updateShift() {
        if (!kb) return;
        var keys = kb.querySelectorAll('.vkb-key');
        keys.forEach(function (btn) {
            var t = btn.textContent;
            if (t.length === 1 && t !== ' ' && t !== '-' && t !== '_') {
                btn.textContent = shifted ? t.toUpperCase() : t.toLowerCase();
            }
            if (btn.textContent === 'MAJ' || (shifted && btn.textContent === 'maj')) {
                btn.textContent = 'MAJ';
            }
        });
        var majBtn = kb.querySelector('.vkb-wide');
        if (majBtn && (majBtn.textContent === 'MAJ' || majBtn.textContent === 'maj')) {
            majBtn.classList.toggle('vkb-active', shifted);
        }
    }

    function show(input) {
        target = input;
        if (!kb) buildKeyboard();
        kb.style.display = 'block';
        input.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    function hide() {
        if (kb) kb.style.display = 'none';
        target = null;
    }

    document.addEventListener('focusin', function (e) {
        var el = e.target;
        var tag  = el.tagName;
        var type = (el.type || '').toLowerCase();
        if (tag === 'INPUT' && (type === 'text' || type === 'search' || type === '')) {
            show(el);
        }
    });

    document.addEventListener('focusout', function (e) {
        var el = e.target;
        var tag  = el.tagName;
        var type = (el.type || '').toLowerCase();
        if (tag === 'INPUT' && (type === 'text' || type === 'search' || type === '')) {
            setTimeout(function () {
                if (kb && document.activeElement && kb.contains(document.activeElement)) return;
                hide();
            }, 200);
        }
    });
}());

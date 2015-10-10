// Generated by CoffeeScript 1.9.3

/*
  Набір корисних функцій.
 */

(function() {
  var is_array,
    hasProp = {}.hasOwnProperty;

  this.is_safari = navigator.userAgent.indexOf('Safari') !== -1 && navigator.userAgent.indexOf('Chrome') === -1;

  is_array = function(obj) {
    return Object.prototype.toString.call(obj) === '[object Array]';
  };

  this.send_post_form = function(fields, action, csrf) {
    var fn, form, fv, i, len, v;
    if (csrf !== false) {
      fields['csrfmiddlewaretoken'] = csrf || Cookies.get('csrf-token');
    }
    form = $('<form>', {
      method: 'post',
      action: action || ''
    }).css({
      display: 'none',
      position: 'absolute'
    });
    for (fn in fields) {
      if (!hasProp.call(fields, fn)) continue;
      fv = fields[fn];
      if (!is_array(fv)) {
        fv = [fv];
      }
      for (i = 0, len = fv.length; i < len; i++) {
        v = fv[i];
        form.append($('<input>', {
          name: fn,
          value: v
        }));
      }
    }
    form.appendTo($('body')).submit().remove();
    return false;
  };

  this.send_get_form = function(fields, action) {
    var fn, form, fv, i, len, v;
    form = $('<form>', {
      method: 'get',
      action: action || ''
    }).css({
      display: 'none',
      position: 'absolute'
    });
    for (fn in fields) {
      if (!hasProp.call(fields, fn)) continue;
      fv = fields[fn];
      if (!is_array(fv)) {
        fv = [fv];
      }
      for (i = 0, len = fv.length; i < len; i++) {
        v = fv[i];
        form.append($('<input>', {
          name: fn,
          value: v
        }));
      }
    }
    form.appendTo($('body')).submit().remove();
    return false;
  };

  this.get_window_url = function(domain, anchor) {
    var url;
    if (domain == null) {
      domain = false;
    }
    if (anchor == null) {
      anchor = false;
    }
    url = window.location.href.toString();
    if (!domain) {
      url = url.split(window.location.host)[1];
    }
    if (!anchor) {
      url = url.replace(/#.*$/, '');
    }
    return url;
  };

  this.window_redirect = function(url) {
    var r;
    if (url == null) {
      url = null;
    }
    if (url === null || url === '') {
      r = true;
    } else {
      r = url.split('#')[0] === (window.location.pathname + window.location.search);
      window.location.replace(url);
    }
    if (r) {
      window.location.reload();
    }
    return false;
  };

  this.update_uri_query = function(uri, key, value) {
    var re, separator;
    re = new RegExp("([?|&])" + key + "=.*?(&|$)", 'i');
    separator = uri.indexOf('?') !== -1 ? '&' : '?';
    value = encodeURIComponent(value);
    if (uri.match(re)) {
      return uri.replace(re, "$1" + key + "=" + value + "$2");
    } else {
      return "" + uri + separator + key + "=" + value;
    }
  };

  this.capfirst = function(str) {
    return "" + (str[0].toUpperCase()) + str.slice(1);
  };

  this.modeltranslation_form_fixer = function(form) {
    return $('[data-lang-default="1"]', form).each(function() {
      var t;
      t = $(this);
      return $("#" + (t.data('lang-copy-to-id'))).val($("#" + (t.data('lang-copy-from-id'))).val());
    });
  };

  $(function() {
    if (typeof jstz !== 'undefined') {
      if (!Cookies.get('utz')) {
        Cookies.set('utz', jstz.determine().name(), {
          path: '/'
        });
      }
    }
    return $('.click-proxy-a').click(function(e) {
      if (e.target.nodeName !== 'A') {
        return $('a', this).first().click();
      }
    });
  });

}).call(this);

//# sourceMappingURL=common.js.map
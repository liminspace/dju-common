###
  Набір корисних функцій.
###


# Визначає, чи браузер Safari
@is_safari = navigator.userAgent.indexOf('Safari') isnt -1 and navigator.userAgent.indexOf('Chrome') is -1


# Визначає, чи obj є масивом
is_array = (obj) -> Object.prototype.toString.call(obj) is '[object Array]'


# Створює і відправляє POST-форму
# *використовується модуль js.cookie, якщо не переданий параметр csrf
@send_post_form = (fields, action, csrf) ->
  if csrf isnt false
    fields['csrfmiddlewaretoken'] = csrf or Cookies.get('csrf-token')
  form = $('<form>', {method: 'post', action: action or ''}).css(display: 'none', position: 'absolute')
  for own fn, fv of fields
    fv = [fv] if not is_array(fv)
    form.append($('<input>', {name: fn, value: v})) for v in fv
  form.appendTo($('body')).submit().remove()
  false


# Створює і відрпавляє GET-форму
@send_get_form = (fields, action) ->
  form = $('<form>', {method: 'get', action: action or ''}).css(display: 'none', position: 'absolute')
  for own fn, fv of fields
    fv = [fv] if not is_array(fv)
    form.append($('<input>', {name: fn, value: v})) for v in fv
  form.appendTo($('body')).submit().remove()
  false


# Повертає URL документу.
# Параметри domain та anchor вказують, чи враховувати домен та якір.
@get_window_url = (domain=no, anchor=no) ->
  url = window.location.href.toString()
  url = url.split(window.location.host)[1] if not domain
  url = url.replace(/#.*$/, '') if not anchor
  url


# Редірект з підтримкою якорів
@window_redirect = (url=null) ->
  if url in [null, '']
    r = true
  else
    r = url.split('#')[0] is (window.location.pathname + window.location.search)
    window.location.replace(url)
  window.location.reload() if r
  false


# Додає або змінює GET-параметр до URI
@update_uri_query = (uri, key, value) ->
  re = new RegExp("([?|&])#{key}=.*?(&|$)", 'i')
  separator = if uri.indexOf('?') isnt -1 then '&' else '?'
  value = encodeURIComponent(value)
  if uri.match(re) then uri.replace(re, "$1#{key}=#{value}$2") else "#{uri}#{separator}#{key}=#{value}"


# Повертає текст підносячи першу букву до великого регістру
@capfirst = (str) -> "#{str[0].toUpperCase()}#{str[1..]}"


# Встановлює дефолтне значення поля для багатомовного поля в формі.
# Викликати перед form.submit
@modeltranslation_form_fixer = (form) ->
  $('[data-lang-default="1"]', form).each ->
    t = $(@)
    $("##{t.data('lang-copy-to-id')}").val($("##{t.data('lang-copy-from-id')}").val())


$ ->
  if typeof jstz isnt 'undefined'
    Cookies.set('utz', jstz.determine().name(), {path: '/'}) if not Cookies.get('utz')

  # Якщо посилання знаходиться в блоці, на який при кліку треба симулювати клік на посилання,
  # тоді цьому блоці можна дати клас click-proxy-a і при кліку на нього він буде знаходити перше
  # посилання і симулювати клік на нього.
  $('.click-proxy-a').click (e) ->
    return $('a', this).first().click() if e.target.nodeName != 'A'

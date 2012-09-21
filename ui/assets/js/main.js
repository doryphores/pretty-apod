// Generated by CoffeeScript 1.3.3
(function() {
  var FullScreen, Growler, Module, Panel, Timer, Transition, Viewport, namespace,
    __slice = [].slice,
    __hasProp = {}.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

  namespace = function(target, name, block) {
    var item, top, _i, _len, _ref, _ref1;
    if (arguments.length < 3) {
      _ref = [(typeof exports !== 'undefined' ? exports : window)].concat(__slice.call(arguments)), target = _ref[0], name = _ref[1], block = _ref[2];
    }
    top = target;
    _ref1 = name.split('.');
    for (_i = 0, _len = _ref1.length; _i < _len; _i++) {
      item = _ref1[_i];
      target = target[item] || (target[item] = {});
    }
    return block(target, top);
  };

  Timer = (function() {

    Timer.immediate = function(func) {
      return setTimeout(func, 0);
    };

    function Timer() {
      this.timer = null;
    }

    Timer.prototype.delay = function(ms, func) {
      return this.timer = setTimeout(func, ms);
    };

    Timer.prototype.repeat = function(ms, func) {
      return this.timer = setInterval(func, ms);
    };

    Timer.prototype.clear = function() {
      if (this.timer) {
        clearTimeout(this.timer);
        return clearInterval(this.timer);
      }
    };

    return Timer;

  })();

  Transition = (function() {

    Transition.timeout = 500;

    Transition.support = (function() {
      var transitionEnd;
      transitionEnd = (function() {
        var el, name, transEndEventNames;
        el = document.createElement('bootstrap');
        transEndEventNames = {
          'WebkitTransition': 'webkitTransitionEnd',
          'MozTransition': 'transitionend',
          'OTransition': 'oTransitionEnd',
          'msTransition': 'MSTransitionEnd',
          'transition': 'transitionend'
        };
        for (name in transEndEventNames) {
          if (el.style[name] !== void 0) {
            return transEndEventNames[name];
          }
        }
      })();
      return transitionEnd && {
        end: transitionEnd
      };
    })();

    function Transition(element, timeout) {
      this.element = element;
      this.timeout = timeout != null ? timeout : Transition.timeout;
      this.deferred = $.Deferred();
      this.timer = new Timer();
    }

    Transition.prototype.start = function(func) {
      var _this = this;
      this.reflow();
      this.element.addClass("animated");
      this.reflow();
      if (Transition.support) {
        Timer.immediate(func);
      } else {
        func();
      }
      this.deferred.always(function() {
        return _this.element.removeClass("animated");
      });
      if (Transition.support) {
        this.element.off(Transition.support.end);
        this.element.on(Transition.support.end, function(e) {
          if (e.target !== e.currentTarget) {
            _this.element.off(Transition.support.end);
            _this.timer.clear();
            return _this.deferred.resolve();
          }
        });
        return this.timer.delay(this.timeout, function() {
          _this.element.off(Transition.support.end);
          return _this.deferred.resolve();
        });
      } else {
        return this.deferred.resolve();
      }
    };

    Transition.prototype.end = function(func) {
      return this.deferred.done(func);
    };

    Transition.prototype.reflow = function() {
      return this.element.offset();
    };

    return Transition;

  })();

  namespace("APOD.utils", function(exports) {
    exports.Timer = Timer;
    return exports.Transition = Transition;
  });

  Module = (function() {

    function Module(element, options) {
      var dataOptions, eventType, key, value, _ref, _ref1;
      if (element == null) {
        element = {};
      }
      if (options == null) {
        options = {};
      }
      this.element = $(element);
      dataOptions = {};
      _ref = this.element.data();
      for (key in _ref) {
        value = _ref[key];
        if (typeof value !== 'object') {
          dataOptions[key] = value;
        }
      }
      this.options = $.extend({}, this.defaults, dataOptions, options);
      _ref1 = this.options;
      for (key in _ref1) {
        value = _ref1[key];
        if (!(key.indexOf('on') === 0 && typeof value === 'function')) {
          continue;
        }
        eventType = key.replace(/on(.)(.*)/g, function(s, first, rest) {
          return first.toLowerCase() + rest;
        });
        this.element.on(eventType, value);
      }
      this.init();
    }

    Module.prototype.init = function() {};

    Module.prototype.trigger = function() {
      var args, _ref;
      args = 1 <= arguments.length ? __slice.call(arguments, 0) : [];
      (_ref = this.element).trigger.apply(_ref, args);
      return this;
    };

    Module.prototype.trigger = function() {
      var args, _ref;
      args = 1 <= arguments.length ? __slice.call(arguments, 0) : [];
      return (_ref = this.element).trigger.apply(_ref, args);
    };

    Module.prototype.on = function() {
      var args, _ref;
      args = 1 <= arguments.length ? __slice.call(arguments, 0) : [];
      return (_ref = this.element).on.apply(_ref, args);
    };

    Module.prototype.off = function() {
      var args, _ref;
      args = 1 <= arguments.length ? __slice.call(arguments, 0) : [];
      return (_ref = this.element).off.apply(_ref, args);
    };

    Module.prototype.one = function() {
      var args, _ref;
      args = 1 <= arguments.length ? __slice.call(arguments, 0) : [];
      return (_ref = this.element).one.apply(_ref, args);
    };

    return Module;

  })();

  Viewport = (function(_super) {

    __extends(Viewport, _super);

    function Viewport() {
      return Viewport.__super__.constructor.apply(this, arguments);
    }

    Viewport.prototype.init = function() {
      var imageTag, timer,
        _this = this;
      if (this.element.length === 0) {
        return;
      }
      this.image = this.element.find('.picture');
      if (this.image.length === 0) {
        return;
      }
      this.window = $(window);
      imageTag = this.image.get(0).tagName.toLowerCase();
      if (imageTag === 'img') {
        return this.window.load(function() {
          return _this.initImage();
        });
      } else {
        this.trigger('image_loading');
        timer = new Timer();
        return timer.delay(1000, function() {
          return $.getJSON(_this.image.data('url'), function(data) {
            return _this.processImage(data);
          });
        });
      }
    };

    Viewport.prototype.initImage = function() {
      var timer,
        _this = this;
      this.imageWidth = parseInt(this.image.attr('width'));
      this.imageHeight = parseInt(this.image.attr('height'));
      this.imageAspectRatio = this.imageWidth / this.imageHeight;
      this.redraw();
      this.window.resize(function() {
        return _this.redraw();
      });
      timer = new Timer();
      timer.delay(500, function() {
        return _this.image.addClass('loaded');
      });
      return this.trigger('image_loaded');
    };

    Viewport.prototype.processImage = function(image_data) {
      var image, imgTag,
        _this = this;
      imgTag = $('<img />').attr({
        width: image_data.width,
        height: image_data.height
      }).css({
        maxWidth: image_data.width,
        maxHeight: image_data.height
      });
      this.image.replaceWith(imgTag);
      this.image = imgTag;
      image = new Image(image_data.width, image_data.height);
      image.onload = function() {
        _this.image.attr('src', image_data.url);
        return _this.initImage();
      };
      return image.src = image_data.url;
    };

    Viewport.prototype.redraw = function() {
      var downscale, viewportAspectRatio, viewportHeight, viewportWidth;
      viewportWidth = this.element.width();
      viewportHeight = this.element.height();
      viewportAspectRatio = viewportWidth / viewportHeight;
      downscale = this.imageWidth > viewportWidth || this.imageHeight > viewportHeight;
      if (downscale && viewportAspectRatio > this.imageAspectRatio) {
        return this.element.addClass('maximise-height');
      } else {
        return this.element.removeClass('maximise-height');
      }
    };

    return Viewport;

  })(Module);

  Panel = (function(_super) {

    __extends(Panel, _super);

    function Panel() {
      return Panel.__super__.constructor.apply(this, arguments);
    }

    Panel.panels = {};

    Panel.currentPanel = null;

    Panel.getCurrentPanel = function() {
      return Panel.panels[Panel.currentPanel];
    };

    Panel.prototype.defaults = {
      overlapping: false,
      load: false
    };

    Panel.prototype.timer = new Timer();

    Panel.prototype.init = function() {
      var _this = this;
      this.element.attr('tabindex', -1);
      this.id = this.element.attr('id');
      this.state = 'hidden';
      this.toggles = $('body').find("[data-toggle=" + this.id + "]");
      $('body').on('click.panel', "[data-toggle=" + this.id + "]", function(e) {
        e.preventDefault();
        e.stopImmediatePropagation();
        return _this.toggle();
      });
      Panel.panels[this.id] = this;
      this.on({
        'click.panel': function(e) {
          return e.stopPropagation();
        },
        'hide.panel': function() {
          return _this.toggles.removeClass('active');
        },
        'show.panel': function() {
          return _this.toggles.addClass('active');
        }
      });
      return $(document).on('click.panel', function(e) {
        if (e.button === 0) {
          return _this.hide();
        }
      });
    };

    Panel.prototype.show = function() {
      var cp, evt,
        _this = this;
      if (this.state === 'visible') {
        return this;
      }
      evt = new $.Event('show');
      this.trigger(evt);
      if (evt.isDefaultPrevented()) {
        return this;
      }
      if (cp = Panel.getCurrentPanel()) {
        cp.one('hidden', function() {
          return _this._show();
        });
        cp.hide();
      } else {
        this._show();
      }
      return this;
    };

    Panel.prototype._show = function() {
      var evt, tran,
        _this = this;
      evt = new $.Event('show');
      this.trigger(evt);
      if (evt.isDefaultPrevented()) {
        return;
      }
      this.element.show();
      this.state = 'visible';
      tran = new Transition(this.element);
      tran.start(function() {
        $('body').addClass('open-panel');
        if (!_this.options.overlapping) {
          $('body').addClass('push-panel');
          return _this.startResize();
        }
      });
      tran.end(function() {
        if (!_this.options.overlapping) {
          _this.stopResize();
        }
        if ($('body').hasClass('open-panel')) {
          if (_this.options.load) {
            _this.element.find('.inner-panel').load(_this.options.load, function() {
              return _this.options.load = false;
            });
          }
          _this.element.focus();
          return _this.trigger('shown');
        }
      });
      return Panel.currentPanel = this.id;
    };

    Panel.prototype.hide = function() {
      var evt, tran,
        _this = this;
      if (this.state === 'hidden') {
        return this;
      }
      evt = new $.Event('hide');
      this.trigger(evt);
      if (evt.isDefaultPrevented()) {
        return;
      }
      this.state = 'hidden';
      tran = new Transition(this.element);
      tran.start(function() {
        $('body').removeClass('open-panel');
        if (!_this.options.overlapping) {
          $('body').removeClass('push-panel');
          return _this.startResize();
        }
      });
      tran.end(function() {
        if (!_this.options.overlapping) {
          _this.stopResize();
        }
        if (!$('body').hasClass('open-panel')) {
          _this.element.hide();
          Panel.currentPanel = null;
          return _this.trigger('hidden');
        }
      });
      return this;
    };

    Panel.prototype.toggle = function() {
      var cp;
      cp = Panel.getCurrentPanel();
      if (cp === this) {
        this.hide();
      } else {
        this.show();
      }
      return this;
    };

    Panel.prototype.startResize = function() {
      $(window).triggerHandler('resize');
      if (Transition.support) {
        return this.timer.repeat(10, function() {
          return $(window).triggerHandler('resize');
        });
      }
    };

    Panel.prototype.stopResize = function() {
      $(window).triggerHandler('resize');
      return this.timer.clear();
    };

    return Panel;

  })(Module);

  Growler = (function(_super) {

    __extends(Growler, _super);

    function Growler() {
      return Growler.__super__.constructor.apply(this, arguments);
    }

    Growler.build = function() {
      if (!Growler.box) {
        Growler.box = $('<div class="growler"><p><i class="icon-time"></i> <span></span></p></div>').appendTo('body');
        return Growler.msgContainer = Growler.box.find('span').first();
      }
    };

    Growler.prototype.show = function() {
      var tran,
        _this = this;
      this.trigger('show');
      Growler.box.appendTo('body');
      Growler.box.offset();
      tran = new Transition(Growler.box);
      tran.start(function() {
        return Growler.box.addClass('open');
      });
      return tran.end(function() {
        if (Growler.box.hasClass('open')) {
          return _this.trigger('shown');
        }
      });
    };

    Growler.prototype.info = function(msg) {
      Growler.build();
      Growler.msgContainer.text(msg);
      return this.show();
    };

    Growler.prototype.hide = function() {
      var tran;
      if (Growler.box) {
        this.trigger('hide');
        tran = new Transition(Growler.box, 200);
        tran.start(function() {
          return Growler.box.removeClass('open');
        });
        return tran.end(function() {
          if (!Growler.box.hasClass('open')) {
            return Growler.box.remove();
          }
        });
      }
    };

    return Growler;

  })(Module);

  FullScreen = (function(_super) {

    __extends(FullScreen, _super);

    function FullScreen() {
      return FullScreen.__super__.constructor.apply(this, arguments);
    }

    FullScreen.prototype.defaults = {
      class_name: 'full-screen'
    };

    FullScreen.prototype.init = function() {
      var _this = this;
      this.state = 'off';
      this.root = $(document.documentElement);
      return $('body').on('click.fullscreen', '[data-toggle=fullscreen]', function(e) {
        e.preventDefault();
        _this.toggle();
        return e.currentTarget.blur();
      });
    };

    FullScreen.prototype.enable = function() {
      var evt;
      evt = new $.Event('resize_full');
      this.trigger(evt);
      if (evt.isDefaultPrevented()) {
        return;
      }
      this.state = 'on';
      return this.root.addClass(this.options.class_name);
    };

    FullScreen.prototype.disable = function() {
      var evt, tran;
      evt = new $.Event('resize_small');
      this.trigger(evt);
      if (evt.isDefaultPrevented()) {
        return;
      }
      this.state = 'off';
      tran = new Transition(this.element);
      return this.root.removeClass(this.options.class_name);
    };

    FullScreen.prototype.toggle = function() {
      if (this.state === 'off') {
        return this.enable();
      } else {
        return this.disable();
      }
    };

    return FullScreen;

  })(Module);

  namespace('APOD.modules', function(exports) {
    exports.Viewport = Viewport;
    exports.Panel = Panel;
    exports.Growler = Growler;
    return exports.FullScreen = FullScreen;
  });

  $(function() {
    var el, growler, _i, _len, _ref;
    growler = new Growler;
    $(document).on({
      'image_loaded': function() {
        return growler.hide();
      },
      'image_loading': function() {
        return growler.info("Please wait will the picture is downloaded and processed");
      },
      'ui_ready': function() {
        var page;
        $(document.documentElement).addClass('ui-ready');
        return page = $('.site-page').attr('tabindex', -1).focus();
      }
    });
    _ref = $('[data-module]');
    for (_i = 0, _len = _ref.length; _i < _len; _i++) {
      el = _ref[_i];
      new APOD.modules[$(el).data('module')](el);
    }
    return $(document).trigger('ui_ready');
  });

}).call(this);

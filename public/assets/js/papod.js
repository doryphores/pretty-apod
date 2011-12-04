// jQuery.support.transition
// to verify that CSS3 transition is supported (or any of its browser-specific implementations)
$.support.transition = (function(){
	var thisBody = document.body || document.documentElement,
	thisStyle = thisBody.style,
	support = thisStyle.transition !== undefined || thisStyle.WebkitTransition !== undefined || thisStyle.MozTransition !== undefined || thisStyle.MsTransition !== undefined || thisStyle.OTransition !== undefined;
	
	return support;
})();

// Base class (debug and event handling methods)

$.Class("PAPOD.Base",
	{
		DEBUG: true,

		debug: function (msg) {
			if (this.DEBUG && window.console) {
				console.log(msg);
			}
		},

		getEventType: function (eventType) {
			return [eventType, this.shortName].join(".");
		}
	},
	{
		debug: function (msg) {
			this.Class.debug(msg);
		},

		addEvent: function (eventType, fn) {
			$(this).bind(this.Class.getEventType(eventType), fn);
		},

		removeEvents: function (eventType) {
			$(this).unbind(this.Class.getEventType(eventType));
		},

		addEvents: function (events) {
			for (e in events) {
				this.addEvent(e, events[e]);
			}
		},

		fireEvent: function (eventType, params) {
			$(this).trigger(this.Class.getEventType(eventType), params);
		}
	}
);

// Message class (for showing user messages)

PAPOD.Base.extend("PAPOD.Message",
	// Static methods and properties
	{
		box: undefined,
		currentType: "",
		clear: undefined,

		init: function () {
			// Create and inject message box element
			this.box = $('<div class="message"><p></p></div>').appendTo("body");
			this.msgContainer = $("p", this.box).first();
		},

		hide: function () {
			// Clear timeout if this is called while waiting
			if (this.clear) clearTimeout(this.clear);

			this.box.removeClass("open");
		}
	},

	// Instance methods and properties
	{
		init: function (type, message) {
			this.type = type;
			this.message = message;
		},

		show: function () {
			this.Class.msgContainer.text(this.message);
			this.Class.box.removeClass(this.Class.currentType).addClass(this.type);
			this.Class.currentType = this.type;

			// Add animation trigger class with timeout
			this.Class.clear = setTimeout(this.proxy(function () {
				this.Class.box.addClass("open");
			}, 200));
		},

		hide: function () {
			this.Class.hide();
		}
	}
);

// Viewport class (handles positioning media in the viewport)

PAPOD.Base.extend("PAPOD.Viewport",
	// Static methods and properties
	{
		defaults: {
			upscale: false,
			events: null
		}
	},

	// Instance methods and properties
	{
		setup: function (htmlElement, options) {
			return [$(htmlElement), $.extend({}, this.Class.defaults, options)];
		},

		init: function (el, options) {
			this.element = el;
			
			// Do nothing if the element doesn't exist
			if (this.element.length == 0) {
				return;
			}

			this.options = options;

			if (this.options.events) {
				this.addEvents(this.options.events);
			}
			
			this.image = $(".picture", this.element).first();
			var imageTag = this.image.get(0).tagName.toLowerCase();

			if (imageTag == "iframe") {
				this.mediaType = "video";

				this.initImage();
			} else {
				this.mediaType = "image";

				if (imageTag == "img") {
					// Image is ready
					$(window).load(this.proxy("initImage"));
				} else {
					// Call server to process image
					this.fireEvent("loading");
					
					$.getJSON(this.image.attr("data-url"), this.proxy("processImage"));
				}
			}
		},

		initImage: function () {
			this.imageWidth = parseInt(this.image.css("max-width"));
			this.imageHeight = parseInt(this.image.css("max-height"));
			this.imageAspectRatio = this.imageWidth / this.imageHeight;
			this.redraw();
			
			// Apply loaded class (for opacity transition)
			setTimeout(this.proxy(function () {
				this.image.addClass("loaded");
			}, 500));
			
			$(window).resize(this.proxy("redraw"));
		},

		processImage: function (image_data) {
			// Replace with empty IMG tag
			var imgTag = ($('<img />').css({
				maxWidth: image_data.width,
				maxHeight: image_data.height
			}));
			this.image.replaceWith(imgTag);
			this.image = imgTag;

			// Load image
			var image = new Image(image_data.width, image_data.height);
			image.onload = this.proxy(function () {
				// Image is now fully downloaded
				this.image.attr("src", image_data.url)
				this.initImage();
				this.fireEvent("loaded");
			});
			image.src = image_data.url;
		},

		redraw: function () {
			// Measure viewport
			var viewportWidth = this.element.width();
			var viewportHeight = this.element.height();
			var viewportAspectRatio = viewportWidth / viewportHeight;

			var downscale = this.imageWidth > viewportWidth || this.imageHeight > viewportHeight;

			if (downscale && viewportAspectRatio > this.imageAspectRatio) {
				this.element.addClass("portrait");
			} else {
				this.element.removeClass("portrait");
			}
		},

		checkAspectRatio: function () {
			this.checking = setInterval(this.proxy("redraw"), 10);
		},

		stopChecking: function () {
			this.redraw();
			clearInterval(this.checking);
		}
	}
);

// Panel class (handles opening and closing toolbar panels)

PAPOD.Base.extend("PAPOD.Panel",
	// Static methods and properties
	{
		openPanel: null,
		defaults: {
			upscale: false,
			events: null
		}
	},

	{
		setup: function (htmlElement, options) {
			return [$(htmlElement), $.extend({}, this.Class.defaults, options)];
		},

		init: function (el, options) {
			this.options = options;

			if (this.options.events) {
				this.addEvents(this.options.events);
			}

			this.element = el;

			this.element.bind("transitionend", this.proxy(function () {
				this.fireEvent("complete");
			}));

			$("a[href=#" + this.element.attr("id") + "]").click(this.proxy("togglePanel"));
		},

		togglePanel: function (e) {
			e.preventDefault();

			$("body").toggleClass("open-panel");

			this.fireEvent("toggle", [this.open]);
		}
	}
);

// Initialise loading message
var loadingMessage = new PAPOD.Message("loading", "Please wait while I download and process the image...");

// Enhance viewport
var viewport = new PAPOD.Viewport(".viewport", {
	events: {
		loading: function () {
			loadingMessage.show();
		},
		loaded: function () {
			loadingMessage.hide();
		}
	}
});

// Enhance panels
$(".panel").each(function () {
	var panel = new PAPOD.Panel(this, {
		events: {
			"toggle": function (e, closing) {
				if ($.support.transition) {
					viewport.checkAspectRatio();
				} else {
					viewport.redraw();
				}
			},
			"complete": function () {
				viewport.stopChecking();
			}
		}
	});
});

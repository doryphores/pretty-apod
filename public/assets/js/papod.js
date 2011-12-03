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
		offsets: {
			top: 0,
			right: 0,
			bottom: 0,
			left: 0
		},

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
			
			this.image = this.element.children().first();
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
			this.imageWidth = parseInt(this.image.attr("width"));
			this.imageHeight = parseInt(this.image.attr("height"));
			this.imageAspectRatio = this.imageWidth / this.imageHeight;
			this.redraw();
			
			// Apply loaded class (for opacity transition)
			this.image.addClass("loaded");
			
			$(window).resize(this.proxy("redraw"));
		},

		processImage: function (image_data) {
			// Replace with empty IMG tag
			var imgTag = ($('<img />').attr({
				width: image_data.width,
				height: image_data.height
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

		getImageProps: function (offsets) {
			// Apply any offsets and save them
			this.offsets  = $.extend(this.offsets, offsets);

			// Measure viewport
			var viewportWidth = this.element.width() - this.offsets.left - this.offsets.right;
			var viewportHeight = this.element.height() - this.offsets.top - this.offsets.bottom;
			var viewportAspectRatio = viewportWidth / viewportHeight;

			// Calculate if downscale needed
			var downscale = this.imageWidth > viewportWidth || this.imageHeight > viewportHeight;

			// New CSS properties to be applied
			var css = {
				width: this.imageWidth,
				height: this.imageHeight
			};

			// Calculate new size if needed
			if ((this.mediaType == "image" && this.options.upscale) || downscale) {
				if (this.imageAspectRatio < viewportAspectRatio) {
					css.width = Math.round(viewportHeight / this.imageHeight * this.imageWidth);
					css.height = viewportHeight;
				} else {
					css.height = Math.round(viewportWidth / this.imageWidth * this.imageHeight);
					css.width = viewportWidth;
				}
			}

			// Calculate new positioning
			css.top = Math.round((viewportHeight - css.height) / 2) + this.offsets.top;
			css.left = Math.round((viewportWidth - css.width) / 2) + this.offsets.left;

			return css;
		},

		redraw: function () {
			// Apply new CSS properties
			this.image.css(this.getImageProps());
		},

		resizeTo: function (offsets) {
			this.image.animate(this.getImageProps(offsets));
		}
	}
);

// Panel class (handles opening and closing toolbar panels)

PAPOD.Base.extend("PAPOD.Panel",
	{
		openPanel: null
	},

	{
		init: function (el) {
			this.element = $(el);
			this.innerPanel = $(".inner-panel", this.element);
			this.panelWidth = this.element.width();
			$.fx.off = true;
			this.element.animate({
				width: 0
			});
			$.fx.off = false;
			this.element.addClass("ready");

			this.animating
			this.open = false;

			$("a[href=#" + this.element.attr("id") + "]").click(this.proxy("togglePanel"));
		},

		togglePanel: function (e) {
			e.preventDefault();

			this.element.animate({
				width: this.open ? 0 : this.panelWidth
			}, {
				complete: this.proxy(function () {
					this.open = !this.open;
				})
			});
			
			this.innerPanel.animate({
				marginLeft: this.open ? -this.panelWidth : 0
			});
			
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
	var panel = new PAPOD.Panel(this);
	panel.addEvent("toggle", function (e, closing) {
		viewport.resizeTo({
			left: closing ? 0 : panel.panelWidth
		});
	});
});

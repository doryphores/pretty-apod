(function ($) {
	var win = $(window);
	var doc = $(document);

	// Message class for handling showing and hiding user messages
	// Uses CSS transitions for animation
	var Message = (function () {
		// Create empty message box and inject it
		var el = $('<div class="message"><p></p></div>').appendTo("body");
		var msgContainer = $("p", el).first();
		var currentType = "";
		var clear;

		// Public methods
		return {
			show: function (msg, type) {
				msgContainer.text(msg);
				el.removeClass(currentType).addClass(type);
				currentType = type;

				// Add animation trigger class with timeout
				clear = setTimeout(function () {
					el.addClass("open");
				}, 200);

				return this;
			},

			hide: function () {
				// Clear timeout if this is called while waiting
				if (clear) clearTimeout(clear);

				el.removeClass("open");

				return this;
			}
		}
	})();

	// Somewhat convoluted class for positioning images in the viewport
	var Shape = function (w, h) {
		var width = w;
		var height = h;
		var top = 0;
		var left = 0;

		// Public methods
		return {
			// Set or retrieve width (jQuery style)
			width: function (w) {
				if (w) {
					width = w;
				}
				return width;
			},

			// Set or retrieve height (jQuery style)
			height: function (h) {
				if (h) {
					height = h;
				}
				return height;
			},

			// Returns shape aspect ratio
			aspectRatio: function () {
				return width / height;
			},

			// Returns true if shape is bigger than given viewport
			isBigger: function (viewport) {
				return this.width() > viewport.width() || this.height() > viewport.height();
			},

			// Sets dimensions and positioning of shape to fit in viewport
			// Only upscales shape if upscale is set to true
			fitIn: function (viewport, upscale) {
				if (upscale || this.isBigger(viewport)) {
					if (this.aspectRatio() < viewport.aspectRatio()) {
						width = Math.round(viewport.height() / height * width);
						height = viewport.height();
					} else {
						height = Math.round(viewport.width() / width * height);
						width = viewport.width();
					}
				}

				top = Math.round((viewport.height() - height) / 2);
				left = Math.round((viewport.width() - width) / 2);
			},

			// Returns map of css properties to apply to element
			css: function () {
				return {
					width: width,
					height: height,
					top: top,
					left: left
				}
			}
		}
	};

	$("#apod").each(function () {
		var viewport = $(this);

		// Deal with image if exists
		if (viewport.hasClass("IM")) {
			var imageShape, message;

			var redraw = function () {
				// Hide any messages
				Message.hide();

				var vpShape = Shape(viewport.width(), viewport.height());
				var imageShape = Shape(parseInt(imgEl.attr("width")), parseInt(imgEl.attr("height")));

				imageShape.fitIn(vpShape);

				imgEl.css(imageShape.css());

				imgEl.addClass("loaded");
			};

			var imgEl = $("img", this);

			if (imgEl.length) {
				// There is an image tag (the image exists on the server)

				// Reposition image when loaded and on browser resize
				win.load(redraw).resize(redraw);
			} else {
				var loader = $("#apod-loader");

				// No image tag, this means the image hasn't been downloaded from APOD
				// Show a nice message and ask the server to get the image
				
				Message.show("Please wait while I download and process the image...", "loading");

				$.getJSON(loader.attr("data-url"), function(d) {
					imgEl = $('<img />');
					imgEl.attr("width", d.width);
					imgEl.attr("height", d.height);
					imgEl.attr("id", "large-image");

					loader.replaceWith(imgEl);

					var image = new Image();
					image.onload = redraw;
					image.src = d.url;
					
					imgEl.attr("src", d.url);

					// Reposition image on browser resize
					win.resize(redraw);
				});
				
			}

			return;
		}

		var video = $("iframe", this);

		// Deal with embedded videos
		if (video.length) {
			var redraw = function () {
				var viewportDims = {
					width: viewport.width(),
					height: viewport.height()
				};
				
				video.css(viewportDims).addClass("loaded");
			};

			// Position video now
			redraw();

			// Reposition image on browser resize
			win.resize(redraw);
		}
	});
})(jQuery);
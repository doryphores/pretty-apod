(function ($) {
	var win = $(window);
	var doc = $(document);

	$("#apod").each(function () {
		var viewport = $(this);
		var img = $("img", this);
		var video = $("iframe", this);

		// Deal with image if exists
		if (img.length) {
			var imgDims = {
				width: parseInt(img.attr("width")),
				height: parseInt(img.attr("height"))
			};
			var isPortrait = imgDims.width < imgDims.height;
			console.log(imgDims);
			var redraw = function () {
				var viewportDims = {
					width: viewport.width(),
					height: viewport.height()
				};
				
				var newProps = {
					width	: viewportDims.width,
					height	: viewportDims.height,
					top		: 0,
					left	: 0
				};
				
				if (isPortrait) {
					newProps.height = Math.round(viewportDims.width / imgDims.width * imgDims.height);
				} else {
					newProps.width = Math.round(viewportDims.height / imgDims.height * imgDims.width);
				}
				newProps.top = Math.round((viewportDims.height - newProps.height) / 2);
				newProps.left = Math.round((viewportDims.width - newProps.width) / 2);

				img.css(newProps);
			};

			win.load(function () {
				redraw();
				img.fadeIn(1000);
			}).resize(function () {
				redraw();
			});

			return;
		}

		// Deal with embedded videos
		if (video.length) {
			var redraw = function () {
				var viewportDims = {
					width: viewport.width(),
					height: viewport.height()
				};
				
				video.css(viewportDims);
			};

			redraw();

			win.resize(function () {
				redraw();
			});
		}
	});

	$(".details header").click(function () {
		$(this).toggleClass("open");
		$(".details .panel").slideToggle("fast");
	});

	$("[data-replsace]").each(function () {
		var el = $(this);
		var url = el.attr("data-replace");
		$.getJSON(url, function(d) {
			var image = new Image();
			image.onload = setupImage;
			image.src = d.url;

			var img = $('<img />');
			img.attr("width", d.width);
			img.attr("height", d.height);
			img.attr("id", "large-image");
			img.attr("src", d.url);

			el.replaceWith(img);
		});
	});

	win.load(function () {
		$("html").addClass("loaded");
	});
})(jQuery);
(function ($) {
	var win = $(window);
	var doc = $(document);

	var setupImage = function () {
		img = $("#large-image");
		if (img.length == 0) return;

		var topOffset = 31;

		var img_w = img.attr("width");
		var img_h = img.attr("height");
		var is_portrait = img_w < img_h;

		var positionImage = function () {
			var win_w = win.width();
			var win_h = win.height() - topOffset;
			var new_w, new_h, left, top, anim;
			
			if (is_portrait) {
				new_w = win_w;
				new_h = Math.round(win_w / img_w * img_h);
				left = 0;
				top = topOffset + Math.round((win_h - new_h) / 2);
			} else {
				new_w = Math.round(win_h / img_h * img_w);
				new_h = win_h;
				left = Math.round((win_w - new_w) / 2);
				top = topOffset;
			}

			img.css({
				width: new_w,
				height: new_h,
				top: top,
				left: left
			});
		};

		positionImage();

		img.fadeIn(1000);

		win.resize(function () {
			positionImage();
		});
	};

	win.load(setupImage);

	$("article.info header").click(function () {
		$(this).toggleClass("open");
		$(".info .slider").slideToggle("fast");
	});

	$("[data-replace]").each(function () {
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
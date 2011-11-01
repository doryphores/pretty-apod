(function ($) {
	var $img = $("#large-image");
	var $win = $(window);
	var $doc = $(document);

	if ($img) {
		var img_w = $img.attr("width");
		var img_h = $img.attr("height");
		var is_portrait = img_w < img_h;
		var positionImage = function () {
			var win_w = $win.width();
			var win_h = $win.height();
			var new_w, new_h, left, top, anim;
			
			if (is_portrait) {
				new_w = win_w;
				new_h = Math.round(win_w / img_w * img_h);
				left = 0;
				top = Math.round((win_h - new_h) / 2);
			} else {
				new_w = Math.round(win_h / img_h * img_w);
				new_h = win_h;
				left = Math.round((win_w - new_w) / 2);
				top = 0;
			}

			$img.css({
				width: new_w,
				height: new_h,
				top: top,
				left: left
			});
		};

		$win.load(function () {
			positionImage();
			$img.fadeIn(1000);
		});

		$win.resize(function () {
			positionImage();
		});
	}

})(jQuery);
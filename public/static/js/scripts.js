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
			var new_w, new_h, anim;
			
			if (!is_portrait) {
				new_w = win_w;
				new_h = Math.round(win_w / img_w * img_h);
				anim = { top: win_h - new_h  };
			} else {
				new_w = Math.round(win_h / img_h * img_w);
				new_h = win_h;
				anim = { left: win_w - new_w };
			}

			$img.css({
				width: new_w,
				height: new_h
			});

			$img.fadeIn().animate(anim, 20000, "linear");
		};

		$win.load(function () {
			positionImage();
			$img.fadeIn("slow");
		});

		$win.resize(function () {
			positionImage();
		});
	}

})(jQuery);
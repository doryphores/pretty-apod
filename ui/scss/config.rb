# Require any additional compass plugins here.

# Set this to the root of your project when deployed:
http_path = "/"
css_dir = "../assets/css"
sass_dir = "."
images_dir = "../assets/images"
javascripts_dir = "../assets/js"
fonts_dir = "../assets/fonts"

# You can select your preferred output style here (can be overridden via the command line):
# output_style = :expanded or :nested or :compact or :compressed

# To enable relative paths to assets via compass helper functions. Uncomment:
relative_assets = true

env = environment

# Adds timestamps to all image file names (requires apache rewrite rule)
asset_cache_buster do |path, real_path|
	if env == :production and File.exists?(real_path)
		pathname = Pathname.new(path)
		modified_time = File.mtime(real_path.path).strftime("%s")
		new_path = "%s/%s.%s%s" % [pathname.dirname, pathname.basename(pathname.extname), modified_time, pathname.extname]

		{:path => new_path, :query => nil}
	end
end

preferred_syntax = :scss

sass_options = {:debug_info => false}
line_comments = false
output_style = (environment == :production) ? :compressed : :expanded
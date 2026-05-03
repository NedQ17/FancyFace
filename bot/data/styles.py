DEFAULT_STYLES: list[dict] = [
    {
        "name": "Деловой портрет",
        "emoji": "💼",
        "prompt": (
            "corporate executive portrait, tailored business suit or blazer with crisp dress shirt, "
            "modern office atmosphere with soft-focus glass walls or bookshelves in background, "
            "professional rembrandt or butterfly lighting, polished confident appearance, "
            "authoritative yet approachable presence, linkedin-quality headshot, "
            "sharp eyes with natural catchlights, photorealistic, high quality"
        ),
        "sort_order": 0,
    },
    {
        "name": "Fashion",
        "emoji": "👗",
        "prompt": (
            "high fashion editorial portrait, avant-garde clothing with bold silhouettes or luxurious fabrics, "
            "dramatic studio or urban backdrop, intense editorial gaze, fashion week atmosphere, "
            "striking makeup or grooming, dynamic interplay of light and shadow, "
            "vogue or harper's bazaar aesthetic, strong graphic composition, "
            "high-key or split studio lighting, photorealistic, high quality"
        ),
        "sort_order": 1,
    },
    {
        "name": "Кинематографичный",
        "emoji": "🎬",
        "prompt": (
            "cinematic film still portrait, anamorphic lens oval bokeh, moody atmospheric lighting "
            "with strong directional shadows and selective highlights, cinematic color grading "
            "with teal-orange or desaturated cool palette, visible analog film grain, "
            "storytelling composition suggesting a pivotal scene in a prestige drama, "
            "practical neon or tungsten lights as background elements, photorealistic, high quality"
        ),
        "sort_order": 2,
    },
    {
        "name": "Русский стиль",
        "emoji": "🌺",
        "prompt": (
            "elegant portrait in russian folk and cultural aesthetic, traditional embroidery "
            "or ornamental textile patterns visible in clothing or surroundings, "
            "warm amber and deep burgundy tones, sarafan or folk-inspired garments with intricate details, "
            "birch forest bokeh or ornate slavic interior as background, "
            "rich textural contrasts, golden hour warmth, slavic folk art spirit, photorealistic, high quality"
        ),
        "sort_order": 3,
    },
    {
        "name": "90-е",
        "emoji": "📼",
        "prompt": (
            "authentic 1990s portrait shot on film, visible grain and slightly faded color saturation, "
            "oversized denim jacket or colorful windbreaker or sporty tracksuit, chunky sneakers or platform shoes, "
            "scrunchie or curtain bangs or flat-top hairstyle, "
            "fluorescent indoor lighting or tungsten warmth, "
            "school photo or mall portrait studio backdrop feel, "
            "early 90s hip-hop or grunge or eurodance fashion energy, kodak gold film color rendering, "
            "photorealistic, high quality"
        ),
        "sort_order": 4,
    },
    {
        "name": "День рождения",
        "emoji": "🎂",
        "prompt": (
            "festive birthday portrait, bokeh of colorful balloons and metallic streamers and fairy lights filling background, "
            "warm golden party lighting mixed with colorful accent glow, confetti suspended mid-air, "
            "shiny foil birthday decorations and ribbons catching light, "
            "birthday candle glow as subtle warm rim light, "
            "joyful celebratory atmosphere with vibrant party color palette of pink gold and confetti colors, "
            "photorealistic, high quality"
        ),
        "sort_order": 5,
    },
    {
        "name": "Новый год",
        "emoji": "🎄",
        "prompt": (
            "new year and christmas portrait, warm bokeh of christmas tree lights filling background "
            "in gold and red and green, soft snowflakes drifting in cold air, "
            "cozy knitted sweater or elegant festive outfit, "
            "silver and gold ornaments and tinsel catching light, "
            "champagne bubbles or sparkler glow as accent light, "
            "magical winter holiday mood with deep blue night sky or fireplace warmth, "
            "twinkling light reflections in eyes, photorealistic, high quality"
        ),
        "sort_order": 6,
    },
    {
        "name": "Зима",
        "emoji": "❄️",
        "prompt": (
            "winter outdoor portrait, individual snowflakes falling and settling on clothing and hair, "
            "breath visible as soft mist in freezing cold air, "
            "chunky wool coat or fur-lined jacket or thick knit scarf and hat, "
            "bare birch trees or snow-laden pine forest in soft-focus background, "
            "cold blue-white natural daylight creating crisp contrast with warm skin tones, "
            "snowy city street or winter forest atmosphere, serene peaceful winter mood, photorealistic, high quality"
        ),
        "sort_order": 7,
    },
    {
        "name": "Фэнтези",
        "emoji": "🧙",
        "prompt": (
            "epic high fantasy portrait, otherworldly magical atmosphere, "
            "elaborate period-inspired or mystical costume with intricate embroidery and gemstones, "
            "arcane glowing runes or soft bioluminescent light emanating from surroundings, "
            "ancient enchanted forest or crumbling mystical ruins or starlit celestial sky background, "
            "dramatic volumetric god rays and rich jewel-tone color palette of deep violet and gold, "
            "the tangible presence of magic and ancient power in the air, "
            "high fantasy film production design quality, photorealistic, high quality"
        ),
        "sort_order": 8,
    },
    {
        "name": "Чёрно-белый",
        "emoji": "🖤",
        "prompt": (
            "striking black and white fine art portrait, deep rich blacks and luminous bright highlights, "
            "strong graphic composition with bold tonal contrasts, "
            "richard avedon or helmut newton or irving penn photographic tradition, "
            "textural contrast between skin pores and smooth or architectural background, "
            "emotional psychological depth, timeless quality transcending any era, "
            "masterful tonal range from true blacks to clean whites, photorealistic, high quality"
        ),
        "sort_order": 9,
    },
    {
        "name": "Пляж",
        "emoji": "🏖️",
        "prompt": (
            "golden hour beach portrait, warm amber and coral sunlight raking at low angle, "
            "ocean waves and endless horizon in soft bokeh background, "
            "salty sea breeze atmosphere with hair catching in wind, "
            "sun-kissed warm skin tones, casual linen or swimwear or beach cover-up, "
            "wet sand or surf foam catching golden reflections, "
            "mediterranean or tropical beach vacation energy, relaxed effortless lifestyle, photorealistic, high quality"
        ),
        "sort_order": 10,
    },
    {
        "name": "Ретро",
        "emoji": "🕺",
        "prompt": (
            "authentic 1970s portrait, warm analog film palette dominated by yellows oranges and earthy browns, "
            "bell-bottom jeans or wide-lapel collar or floral print shirt or peasant blouse, "
            "kodachrome or fujifilm color rendering with slight warmth shift, "
            "film grain and natural vignette, shag carpet or wood paneling or macrame wall hanging in background, "
            "lava lamp glow or warm incandescent mushroom lamp lighting, "
            "groovy disco era or free-spirited bohemian spirit, natural hair and sideburns celebrated, "
            "photorealistic, high quality"
        ),
        "sort_order": 11,
    },
    {
        "name": "Люкс",
        "emoji": "💎",
        "prompt": (
            "ultra-luxury lifestyle portrait, bespoke tailoring or haute couture with exceptional fabric drape visible, "
            "opulent environment suggesting private penthouse or superyacht deck or grand hotel lobby, "
            "subtle designer accessories catching directional light, "
            "marble and polished brass and crystal as background architecture, "
            "champagne flutes or fresh flowers as environmental details, "
            "sophisticated aspirational wealth aesthetic with understated elegance, "
            "cream ivory charcoal and gold color palette, editorial magazine quality, photorealistic, high quality"
        ),
        "sort_order": 12,
    },
    {
        "name": "Студия",
        "emoji": "📸",
        "prompt": (
            "perfect professional studio portrait, seamless paper backdrop in neutral gray or white, "
            "meticulous three-point or butterfly lighting with precise fill ratio, "
            "defined catchlights in eyes, individual hairs crisp against clean background, "
            "medium format camera quality sharpness and tonal depth, "
            "commercial photography standard with flawless even illumination, "
            "clean polished appearance without clinical coldness, photorealistic, high quality"
        ),
        "sort_order": 13,
    },
    {
        "name": "Арт",
        "emoji": "🎨",
        "prompt": (
            "contemporary fine art portrait, painterly mixed-media aesthetic with rich impasto-like surface texture "
            "or loose expressive brushwork feel, bold unconventional use of color beyond realism, "
            "gallery exhibition quality with strong artistic intent, "
            "the subject rendered as an art statement rather than documentary record, "
            "annie leibovitz or cindy sherman conceptual tradition, "
            "unexpected composition breaking classical portrait rules, photorealistic, high quality"
        ),
        "sort_order": 14,
    },
]

FIRST_PAGE_COUNT = 10

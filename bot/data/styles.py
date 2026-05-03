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
        "scenes": [
            "standing at floor-to-ceiling office windows overlooking city skyline, arms crossed",
            "sitting at a polished boardroom table, leaning forward slightly with hands clasped",
            "standing in a modern office lobby, one hand in pocket",
            "sitting in an executive leather chair, relaxed but composed posture",
            "standing in front of a glass whiteboard covered in diagrams, hands behind back",
        ],
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
        "scenes": [
            "standing against a stark white studio seamless backdrop, one hand on hip",
            "leaning against a raw concrete wall in an industrial loft, arms relaxed",
            "sitting on the edge of a minimalist white cube, legs crossed, gaze intense",
            "walking through an empty fashion show runway, mid-stride",
            "standing under dramatic overhead studio spotlight, face tilted slightly upward",
        ],
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
        "scenes": [
            "standing in a rain-soaked alley at night, neon signs reflecting on wet pavement below",
            "sitting alone at a bar counter, hands wrapped around a glass, staring forward",
            "leaning against a car door on an empty street at dusk, hands in jacket pockets",
            "standing in a doorway backlit by warm interior light, face half in shadow",
            "sitting on a fire escape staircase overlooking city lights below",
        ],
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
        "scenes": [
            "standing in a birch forest clearing, golden light filtering through white trunks",
            "sitting on a wooden bench outside a traditional log house, hands folded in lap",
            "standing at the edge of a field of wildflowers, light breeze in the air",
            "sitting at an ornate wooden table near a window with embroidered curtains",
            "standing on a old wooden bridge over a forest stream, leaning on the railing",
        ],
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
            "early 90s hip-hop or grunge or eurodance fashion energy, kodak gold film color rendering, "
            "photorealistic, high quality"
        ),
        "scenes": [
            "standing against school lockers in a fluorescent-lit hallway, arms crossed",
            "sitting on concrete front steps of an apartment block, elbows on knees",
            "leaning against a chain-link fence in an urban courtyard, one foot propped up",
            "standing at a pay phone booth on a city sidewalk, receiver in hand",
            "sitting on a low brick wall in a housing estate courtyard, looking ahead",
        ],
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
        "scenes": [
            "standing behind a birthday cake with lit candles on a decorated table, leaning forward",
            "sitting at a party table surrounded by gifts and balloons, smiling",
            "standing in a crowd of balloons, holding a glass of champagne",
            "sitting on a decorated chair with foil balloons tied to it",
            "standing at a party venue entrance under an arch of balloons",
        ],
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
            "magical winter holiday mood, twinkling light reflections in eyes, photorealistic, high quality"
        ),
        "scenes": [
            "sitting cross-legged on the floor next to a decorated christmas tree, gift in hands",
            "standing at a frost-covered window holding a mug of hot drink, looking outside",
            "standing on a snowy city street under festive light garlands strung between buildings",
            "sitting at a holiday dinner table with candles and decorated centerpiece",
            "standing in a doorway of a warm lit house, snow falling behind, holding sparklers",
        ],
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
            "serene peaceful winter mood, photorealistic, high quality"
        ),
        "scenes": [
            "standing on a snow-covered forest path, hands in coat pockets, snowflakes falling",
            "sitting on a snow-dusted wooden bench in a park, wrapped in a scarf",
            "standing at the edge of a frozen lake, pine trees behind, looking across the ice",
            "leaning against a snow-covered fence post in an open winter field",
            "standing on a city street after snowfall, fresh snow on shoulders and hair",
        ],
        "sort_order": 7,
    },
    {
        "name": "Фэнтези",
        "emoji": "🧙",
        "prompt": (
            "epic high fantasy portrait, otherworldly magical atmosphere, "
            "elaborate period-inspired or mystical costume with intricate embroidery and gemstones, "
            "arcane glowing runes or soft bioluminescent light emanating from surroundings, "
            "dramatic volumetric god rays and rich jewel-tone color palette of deep violet and gold, "
            "the tangible presence of magic and ancient power in the air, "
            "high fantasy film production design quality, photorealistic, high quality"
        ),
        "scenes": [
            "standing at the entrance of an ancient stone temple, glowing runes on the archway",
            "sitting on a throne of twisted roots in an enchanted forest, staff in hand",
            "standing on a cliff edge overlooking a mystical valley filled with floating islands",
            "kneeling beside a glowing magical artifact on an altar, hands outstretched",
            "standing in a grand library of an ancient tower, magical tomes floating around",
        ],
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
        "scenes": [
            "standing against a smooth white studio wall, one shoulder forward, direct gaze",
            "sitting on a simple wooden chair in a bare room, hands on knees",
            "leaning against a brick wall, arms folded, face in dramatic side light",
            "standing in an empty hallway, light pouring from a window at the far end",
            "sitting on a staircase, elbows on knees, looking upward",
        ],
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
            "mediterranean or tropical beach vacation energy, photorealistic, high quality"
        ),
        "scenes": [
            "standing at the shoreline, small waves washing over feet, facing the sunset",
            "sitting on the sand with knees pulled up, ocean stretching behind",
            "leaning against a weathered wooden beach pier post, wind in hair",
            "walking along the waterline, footprints in wet sand behind",
            "sitting on a beach towel, leaning back on hands, face tilted toward the sun",
        ],
        "sort_order": 10,
    },
    {
        "name": "Ретро",
        "emoji": "🕺",
        "prompt": (
            "authentic 1970s portrait, warm analog film palette dominated by yellows oranges and earthy browns, "
            "bell-bottom jeans or wide-lapel collar or floral print shirt or peasant blouse, "
            "kodachrome or fujifilm color rendering with slight warmth shift, "
            "film grain and natural vignette, groovy disco era or free-spirited bohemian spirit, "
            "natural hair and sideburns celebrated, photorealistic, high quality"
        ),
        "scenes": [
            "sitting in a wicker peacock chair, legs crossed, one arm draped over the side",
            "standing in a living room with shag carpet and wood paneling, hand on hip",
            "leaning against a vintage car hood in a suburban driveway, arms crossed",
            "sitting on a bean bag chair, lava lamp glowing on the shelf behind",
            "standing on a disco dance floor with coloured light reflections, mid-pose",
        ],
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
            "sophisticated aspirational wealth aesthetic with understated elegance, "
            "cream ivory charcoal and gold color palette, editorial magazine quality, photorealistic, high quality"
        ),
        "scenes": [
            "standing on a penthouse terrace overlooking a city at night, hands resting on glass railing",
            "sitting in a deep leather armchair in a private members club, glass in hand",
            "standing on the deck of a superyacht, ocean horizon behind, jacket over shoulder",
            "sitting at a marble bar in a grand hotel, suit immaculate, looking ahead",
            "standing at the top of a sweeping staircase in a luxury villa, hand on bannister",
        ],
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
        "scenes": [
            "standing against a light gray seamless backdrop, relaxed arms at sides, direct gaze",
            "sitting on a low black studio stool, hands on thighs, chin slightly down",
            "standing with one hand in pocket, slight three-quarter body angle",
            "sitting on the floor with legs crossed, leaning slightly forward",
            "standing with arms folded, weight on one leg, natural relaxed stance",
        ],
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
        "scenes": [
            "standing in an art gallery surrounded by large abstract canvases, arms at sides",
            "sitting on the floor of a studio space, paint-covered drop cloths around",
            "leaning against a sculpture in a contemporary museum, casual and contemplative",
            "standing in front of a large blank canvas, brush or palette in hand",
            "sitting on a window ledge in an artist's loft, natural light flooding in",
        ],
        "sort_order": 14,
    },
]

FIRST_PAGE_COUNT = 10

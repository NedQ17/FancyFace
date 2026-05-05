DEFAULT_STYLES: list[dict] = [
    {
        "name": "Деловой портрет",
        "emoji": "💼",
        "prompt": (
            "preserve exact facial identity from reference photo, same person, realistic facial proportions and natural skin texture with visible pores, subtle asymmetry, "
            "corporate executive portrait, tailored navy or charcoal business suit or blazer with crisp dress shirt or turtleneck, "
            "seated at desk or standing near window or walking through workspace or adjusting cufflinks or holding tablet, "
            "body angled 30-45 degrees from camera with relaxed shoulders, slight head tilt, confident natural posture, soft candid smile or focused serious expression, "
            "professional workspace environment, executive office or coworking loft or conference room or city-view workspace or minimalist corporate interior, "
            "unique environment details, varied office furniture and background composition, different office layout each generation, "
            "professional rembrandt or butterfly lighting mixed with natural daylight, shot on 85mm portrait lens, "
            "linkedin-quality editorial headshot, sharp eyes with natural catchlights, realistic photography imperfections, shallow depth of field, photorealistic, high quality"
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
            "preserve exact facial identity from reference photo, same person, natural skin texture and realistic facial structure, "
            "high fashion editorial portrait, avant-garde clothing with bold silhouettes or luxurious fabrics or luxury streetwear layering, "
            "dynamic pose such as walking mid-step or leaning against surface or adjusting sunglasses or collar, body partially cropped for editorial framing, "
            "intense editorial gaze away from camera or direct eye contact, "
            "fashion environment, editorial studio or rooftop or luxury boutique interior or textured urban architecture or backstage runway atmosphere, "
            "varied set design and styling props, unique composition each generation, "
            "strong graphic composition, vogue or harper's bazaar aesthetic, split studio lighting or hard flash mixed with shadows, "
            "shot on 50mm or 85mm lens, photorealistic, high quality"
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
            "preserve exact facial identity from reference photo, same person, cinematic film still portrait, natural facial asymmetry and authentic skin texture, "
            "subject looking over shoulder or standing mid-motion or sitting in contemplative pose, "
            "cinematic environment, rainy street or dim apartment interior or subway platform or hotel corridor or neon-lit alley or moody restaurant booth, "
            "unique storytelling background elements, varied practical light sources, "
            "anamorphic lens oval bokeh, moody atmospheric lighting with strong directional shadows and selective highlights, "
            "cinematic color grading with teal-orange or desaturated cool palette, subtle analog film grain, "
            "storytelling composition suggesting a pivotal scene in a prestige drama, imperfect natural framing, photorealistic, high quality"
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
            "preserve exact facial identity from reference photo, same person, elegant portrait in russian folk and cultural aesthetic, "
            "realistic skin texture and soft natural expression, "
            "traditional embroidery or ornamental textile patterns visible in clothing or surroundings, "
            "sarafan or linen shirt or folk-inspired garments with intricate details, "
            "natural pose sitting or standing while holding shawl or interacting with fabric, "
            "slavic cultural environment, ornate wooden interior or birch forest or countryside house or candlelit traditional room or snowy rural landscape, "
            "varied authentic folk details and textures, warm amber and deep burgundy tones, "
            "golden light or candlelight ambiance, rich textural contrasts, slavic folk art spirit, photorealistic, high quality"
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
            "preserve exact facial identity from reference photo, same person, authentic 1990s portrait shot on film, "
            "visible grain and slightly faded color saturation, "
            "oversized denim jacket or colorful windbreaker or sporty tracksuit, "
            "casual pose sitting or leaning or holding disposable camera or standing near railing, relaxed candid attitude, "
            "nostalgic 90s environment, apartment stairwell or arcade room or school hallway or bedroom with posters or city courtyard or underground passage, "
            "varied retro props and details, chunky sneakers or platform shoes, "
            "fluorescent indoor lighting or tungsten warmth, early 90s hip-hop or grunge or eurodance fashion energy, "
            "kodak gold film color rendering, photorealistic, high quality"
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
            "preserve exact facial identity from reference photo, same person, festive birthday portrait, "
            "joyful authentic expression and natural skin texture, "
            "subject laughing naturally or holding cake or champagne glass or adjusting party hat, "
            "birthday celebration environment, decorated apartment or rooftop party or restaurant private room or cozy house gathering or luxury event hall, "
            "varied festive decorations and party props, "
            "bokeh of colorful balloons and metallic streamers and fairy lights filling background, "
            "warm golden party lighting mixed with colorful accent glow, confetti suspended mid-air, "
            "shiny foil birthday decorations and ribbons catching light, birthday candle glow as subtle warm rim light, "
            "spontaneous celebratory atmosphere, photorealistic, high quality"
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
            "preserve exact facial identity from reference photo, same person, new year and christmas portrait, "
            "cozy knitted sweater or elegant festive outfit, natural expression with slight smile or thoughtful gaze, "
            "subject holding sparkler or champagne flute or gift box, "
            "holiday environment, decorated living room or snowy terrace or christmas market or luxury holiday dinner setting or festive apartment interior, "
            "varied ornaments and seasonal decor, "
            "warm bokeh of christmas tree lights filling background in gold red and green, soft snowflakes drifting in cold air or visible outside window, "
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
            "preserve exact facial identity from reference photo, same person, winter outdoor portrait, "
            "individual snowflakes falling and settling on clothing and hair, breath visible as soft mist in freezing cold air, "
            "chunky wool coat or fur-lined jacket or thick knit scarf and hat, "
            "natural candid pose walking through snow or adjusting scarf or warming hands, "
            "winter environment, snowy city street or frozen lake or pine forest trail or mountain village or urban park after snowfall, "
            "varied snow textures and atmospheric details, "
            "cold blue-white natural daylight creating crisp contrast with warm skin tones, serene peaceful winter mood, photorealistic, high quality"
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
            "preserve exact facial identity from reference photo, same person, epic high fantasy portrait, realistic anatomy and facial structure, "
            "elaborate period-inspired or mystical costume with intricate embroidery gemstones or leather details, "
            "subject holding magical artifact or touching glowing runes or standing in dramatic pose, "
            "fantasy environment, ancient stone hall or enchanted forest or royal chamber or mystical ruins or mountain citadel, "
            "varied magical background elements and atmospheric details, "
            "arcane glowing symbols or soft bioluminescent light emanating from surroundings, dramatic volumetric god rays, "
            "rich jewel-tone palette of deep violet emerald and gold, high fantasy film production design quality, photorealistic, high quality"
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
            "preserve exact facial identity from reference photo, same person, striking black and white fine art portrait, "
            "realistic skin pores and natural facial contrast, deep rich blacks and luminous bright highlights, "
            "strong graphic composition with bold tonal contrasts, "
            "subject seated or leaning with contemplative expression or adjusting collar, "
            "timeless portrait environment, minimalist studio backdrop or textured wall or architectural interior or window-lit room, "
            "subtle varied background details, "
            "richard avedon or helmut newton or irving penn photographic tradition, "
            "emotional psychological depth, masterful tonal range from true blacks to clean whites, photorealistic, high quality"
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
            "preserve exact facial identity from reference photo, same person, golden hour beach portrait, "
            "warm amber and coral sunlight at low angle, "
            "subject walking barefoot near shoreline or sitting on sand or turning toward ocean breeze, "
            "casual linen or swimwear or beach cover-up, hair catching wind naturally, "
            "beach environment, tropical coastline or mediterranean cove or rocky seaside or resort beach club or dune landscape, "
            "varied ocean textures and vacation details, "
            "ocean waves and endless horizon in soft bokeh background, sun-kissed warm skin tones, "
            "wet sand or surf foam catching golden reflections, photorealistic, high quality"
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
            "preserve exact facial identity from reference photo, same person, authentic 1970s portrait, "
            "warm analog film palette dominated by yellows oranges and earthy browns, "
            "bell-bottom jeans or wide-lapel collar or floral print shirt or peasant blouse, "
            "relaxed pose seated on furniture or leaning casually, "
            "retro environment, vintage apartment interior or retro diner or wood-paneled room or disco club or classic car setting, "
            "varied nostalgic props and decor details, "
            "kodachrome or fujifilm color rendering with slight warmth shift, film grain and natural vignette, "
            "groovy disco era or free-spirited bohemian spirit, photorealistic, high quality"
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
            "preserve exact facial identity from reference photo, same person, ultra-luxury lifestyle portrait, "
            "bespoke tailoring or haute couture with exceptional fabric drape visible, "
            "natural confident posture seated in lounge or standing near architecture or walking through elegant interior, "
            "luxury environment, private penthouse or superyacht deck or grand hotel lobby or marble staircase or designer suite interior, "
            "varied premium materials and opulent details, subtle designer accessories catching directional light, "
            "marble polished brass and crystal as background architecture, "
            "sophisticated aspirational wealth aesthetic with understated elegance, "
            "cream ivory charcoal and gold palette, photorealistic, high quality"
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
            "preserve exact facial identity from reference photo, same person, perfect professional studio portrait, "
            "seamless paper backdrop in neutral gray or white or beige or muted pastel, "
            "realistic facial proportions and visible skin texture, "
            "subject slightly angled from camera with relaxed shoulders and natural hand placement, "
            "meticulous three-point or butterfly lighting with precise fill ratio, "
            "defined catchlights in eyes, individual hairs crisp against clean background, "
            "subtle variation in backdrop tone and lighting setup each generation, "
            "medium format camera quality sharpness and tonal depth, polished commercial photography standard, photorealistic, high quality"
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
            "preserve exact facial identity from reference photo, same person, contemporary fine art portrait, "
            "natural skin texture and realistic anatomy, "
            "painterly mixed-media aesthetic with rich texture or expressive brushwork atmosphere while maintaining realism, "
            "bold unconventional use of color beyond realism, unexpected composition breaking classical portrait rules, "
            "subject in expressive pose with slight movement or unconventional crop, "
            "artistic environment, gallery-inspired set or textured backdrop or abstract installation or color field composition, "
            "varied conceptual details and visual elements, strong artistic intent, "
            "editorial fine art photography realism, photorealistic, high quality"
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

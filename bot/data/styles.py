DEFAULT_STYLES: list[dict] = [
    {
        "name": "Деловой портрет",
        "emoji": "💼",
        "prompt": (
            "preserve exact facial identity from reference photo, same person, realistic facial proportions and natural skin texture with visible pores and subtle asymmetry, "
            "corporate executive portrait, professional business attire appropriate for formal corporate photography, varied tailoring styles typical for executive portraits, "
            "seated or standing or walking through workspace or interacting naturally with environment, confident natural posture, neutral or focused expression, "
            "professional office environment with varied corporate settings such as executive offices, modern coworking spaces, glass architecture interiors or minimalist corporate lounges, "
            "different office layouts and background compositions each generation, "
            "professional cinematic lighting combining natural daylight and studio setup, shot on 85mm portrait lens, "
            "linkedin-quality editorial headshot, shallow depth of field, photorealistic, high quality, "
            "varied composition and wardrobe styling within corporate photography standards"
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
            "high fashion editorial portrait, fashion-forward styling with luxurious or avant-garde or street-luxury clothing appropriate for editorial photography, "
            "dynamic expressive poses such as walking, leaning, adjusting clothing or standing in strong composed posture, editorial framing with partial crop, "
            "fashion environment with varied editorial locations such as studio sets, rooftop spaces, luxury interiors, urban architectural backgrounds or backstage fashion atmosphere, "
            "strong graphic composition, vogue or harper's bazaar aesthetic, dramatic studio lighting or flash photography mixed with shadows, "
            "shot on 50mm or 85mm lens, photorealistic, high quality, diverse styling and composition each generation"
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
            "subject in candid or staged cinematic moment such as standing in motion, sitting in contemplation or turning mid-action, "
            "cinematic environments with varied urban and interior storytelling locations such as apartments, corridors, transit spaces, vehicles or minimal architectural environments, "
            "dynamic practical lighting from environmental sources, anamorphic lens bokeh, moody cinematic lighting with strong contrast and selective highlights, "
            "film color grading with teal-orange or cool desaturated palette, subtle film grain, "
            "storytelling composition suggesting a scene from a dramatic film, photorealistic, high quality, varied cinematic staging and atmosphere"
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
            "preserve exact facial identity from reference photo, same person, elegant portrait inspired by russian folk and slavic cultural aesthetics, "
            "realistic skin texture and natural expression, "
            "traditional textile patterns and embroidered elements integrated into clothing or environment, "
            "culturally inspired garments with detailed craftsmanship, natural poses interacting with clothing or surroundings, "
            "slavic-inspired environments with varied settings such as birch forests, countryside houses, wooden interiors, open fields or winter rural landscapes, "
            "warm earthy tones and golden ambient lighting or natural daylight, rich cultural textures and materials, "
            "photorealistic, high quality, varied cultural composition and environment each generation"
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
            "preserve exact facial identity from reference photo, same person, authentic 1990s film portrait, "
            "visible film grain and slightly faded analog color tones, "
            "casual 90s-inspired clothing such as denim, windbreakers or sporty streetwear typical of the era, "
            "relaxed candid poses such as leaning, sitting or standing naturally, "
            "nostalgic environments with varied locations such as urban courtyards, stairwells, school corridors, arcades or residential blocks, "
            "fluorescent or tungsten indoor lighting or natural overcast daylight, "
            "90s cultural atmosphere inspired by street fashion, music and youth culture, "
            "photorealistic, high quality, varied nostalgic composition and styling each generation"
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
            "natural authentic expression fitting the celebratory mood such as joy, laughter or warmth, expression may reflect the festive context, "
            "subject interacting naturally with celebration elements such as cake, gifts, drinks or party decor, "
            "birthday environments with varied setups such as home parties, restaurant spaces, rooftop gatherings or decorated event rooms, "
            "dynamic festive decorations including balloons, streamers, lights and confetti, "
            "warm party lighting with colorful accents and ambient glow, celebratory atmosphere with spontaneous composition, "
            "photorealistic, high quality, varied celebration layouts and decorative focus each generation"
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
            "preserve exact facial identity from reference photo, same person, new year and christmas themed portrait, "
            "cozy seasonal clothing or elegant festive outfits, "
            "natural expression fitting the holiday mood such as calm warmth, quiet joy or festive delight, expression may reflect the seasonal context, "
            "subject interacting with holiday elements such as gifts, sparklers or drinks, "
            "holiday environments with varied settings such as decorated living rooms, snowy outdoor streets, christmas markets or festive dining spaces, "
            "warm christmas lighting with tree lights and soft glowing decorations, "
            "winter atmosphere with subtle snow or indoor cozy ambiance, "
            "photorealistic, high quality, varied festive environments and composition each generation"
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
            "natural cold-weather interaction with environment such as walking, standing or adjusting clothing, "
            "winter clothing appropriate for cold conditions such as coats, scarves or layered outfits, "
            "snowy environments with varied locations such as forests, city streets, parks, frozen lakes or rural landscapes, "
            "visible snowfall or frost, breath condensation in cold air, "
            "natural cold daylight with soft blue tones and warm skin contrast, serene winter atmosphere, "
            "photorealistic, high quality, varied winter scenery and composition each generation"
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
            "preserve exact facial identity from reference photo, same person, epic fantasy portrait with realistic facial structure, "
            "mystical or medieval-inspired attire with detailed craftsmanship, "
            "subject interacting with fantasy elements such as magical artifacts, glowing runes or symbolic objects, "
            "fantasy environments with varied locations such as ancient ruins, enchanted forests, royal halls, mystical caves or floating landscapes, "
            "magical lighting effects such as volumetric light rays, glowing energy or atmospheric fog, "
            "rich fantasy color palette with jewel tones, cinematic fantasy production quality, "
            "photorealistic, high quality, varied fantasy worldbuilding and scene composition each generation"
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
            "preserve exact facial identity from reference photo, same person, black and white fine art portrait, "
            "natural skin texture and strong tonal contrast, "
            "subject in contemplative or neutral poses such as sitting, standing or leaning, "
            "minimalist or architectural environments with varied settings such as studio backgrounds, textured walls, hallways or window-lit interiors, "
            "strong use of light and shadow for dramatic contrast, "
            "fine art photographic tradition inspired by classic portrait masters, "
            "emotional depth and timeless composition, "
            "photorealistic, high quality, varied monochrome composition and lighting each generation"
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
            "natural interaction with coastal environment such as walking, sitting or standing near water, "
            "casual summer clothing or swimwear appropriate for beach setting, "
            "beach environments with varied locations such as tropical shores, mediterranean beaches, rocky coastlines, dunes or seaside piers, "
            "warm sunlight with ocean reflections, wind movement in hair and fabric, "
            "natural relaxed coastal atmosphere, "
            "photorealistic, high quality, varied seaside composition and scenery each generation"
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
            "preserve exact facial identity from reference photo, same person, retro inspired portrait from 1970s aesthetic, "
            "vintage clothing styles typical of the era, "
            "relaxed natural poses such as sitting, leaning or standing casually, "
            "retro environments with varied settings such as vintage apartments, diners, disco interiors, wood-paneled rooms or classic cars, "
            "warm analog film tones with grain and slight vignette, "
            "nostalgic atmosphere inspired by 1970s culture and lifestyle, "
            "photorealistic, high quality, varied retro composition and environment each generation"
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
            "preserve exact facial identity from reference photo, same person, luxury editorial portrait, "
            "elegant high-end styling with refined tailored clothing, "
            "composed confident posture in natural luxury poses such as sitting, standing or walking, "
            "luxury environments with varied settings such as penthouses, yachts, luxury hotels, marble interiors or private clubs, "
            "premium materials such as marble, glass, brass and crystal, "
            "cinematic soft lighting with elegant reflections, sophisticated luxury aesthetic, "
            "photorealistic, high quality, varied luxury composition and architecture each generation"
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
            "preserve exact facial identity from reference photo, same person, professional studio portrait, "
            "natural posture and controlled composition, "
            "studio lighting setup with seamless backdrop in varied neutral or soft tones, "
            "consistent professional photography quality, subtle variation in lighting direction and background tone each generation, "
            "clean commercial portrait style with focus on facial detail and realism, "
            "photorealistic, high quality, varied studio setup and lighting configuration each generation"
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
            "expressive artistic interpretation with realistic base, "
            "subject placed in conceptual or gallery-inspired environments such as art studios, exhibitions, abstract installations or creative staged sets, "
            "bold artistic use of color, texture or composition while maintaining recognizability, "
            "experimental framing and conceptual visual storytelling, inspired by modern fine art photography, "
            "photorealistic, high quality, varied artistic concept and visual execution each generation"
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
    {
        "name": "Селфи на улице",
        "emoji": "🤳",
        "prompt": (
            "preserve exact facial identity from reference photo, same person, realistic facial proportions and natural skin texture, "
            "preserve exact facial expression and emotion from reference photo unchanged, do not alter or exaggerate the expression, "
            "take an extremely ordinary unremarkable iPhone selfie of this person on a city street at night, "
            "no clear composition just a quick candid snapshot, "
            "underexposed dark night atmosphere, low light conditions, visible digital noise and grain from high ISO, "
            "slightly uneven mixed lighting from streetlights and phone screen glow, no studio lighting no flash, "
            "muted desaturated night colors, low saturation, no vivid or oversaturated colors, no acid tones, not bright not contrasty, naturally dark shadows, "
            "awkward angle and messy framing deliberately mediocre feel as if taken absentmindedly, "
            "subject caught in a casual imperfect moment alone or with blurred strangers in background, "
            "lively street at night with neon signs traffic and blurry figures passing by, "
            "no smartphone no phone no device visible in hands, authentic vibe of a poorly composed spontaneous real iPhone night photo, photorealistic, high quality"
        ),
        "scenes": [
            "holding phone at arm's length on a busy night street, neon signs behind",
            "quick selfie outside a bar entrance, friends blurred in background",
            "casual shot on a rainy city sidewalk, streetlights reflecting on wet pavement",
            "spontaneous selfie at a crosswalk, cars and traffic lights in background",
            "accidental-looking selfie near a convenience store at night, harsh overhead light",
        ],
        "sort_order": 15,
    },
]

PAGE_SIZE = 8

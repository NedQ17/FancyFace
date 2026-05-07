DEFAULT_STYLES: list[dict] = [
    {
        "name": "Деловой портрет",
        "emoji": "💼",
        "prompt": (
            "preserve exact facial identity from reference photo, same person, realistic facial proportions and natural skin texture with visible pores and subtle asymmetry, "
            "preserve exact facial expression from reference photo unchanged, "
            "corporate executive portrait, professional business attire with varied styles each generation such as tailored suits, blazers, turtlenecks or smart business casual, "
            "varied natural poses such as seated at desk, standing near window, walking through office or leaning against architecture, confident neutral posture, "
            "varied professional environments each generation such as executive offices, glass architecture coworking spaces, minimalist corporate lounges, conference rooms or city-view workspaces, "
            "different background compositions and office layouts each generation, "
            "professional cinematic lighting combining natural daylight and studio setup, shot on 85mm portrait lens, shallow depth of field, "
            "linkedin-quality editorial headshot, photorealistic, high quality"
        ),
        "scenes": [],
        "sort_order": 0,
    },
    {
        "name": "Fashion",
        "emoji": "👗",
        "prompt": (
            "preserve exact facial identity from reference photo, same person, natural skin texture and realistic facial structure, "
            "preserve exact facial expression from reference photo unchanged, "
            "high fashion editorial portrait, varied fashion-forward styling each generation such as luxury tailoring, avant-garde silhouettes, street-luxury layering or minimalist editorial looks, "
            "varied dynamic poses each generation such as walking mid-stride, leaning against surface, adjusting clothing, strong standing posture or editorial crop, "
            "varied fashion environments each generation such as studio sets, rooftop terraces, luxury boutique interiors, raw urban architecture or backstage runway atmosphere, "
            "strong graphic composition, vogue or harper's bazaar aesthetic, dramatic studio lighting or flash photography with shadows, "
            "shot on 50mm or 85mm lens, photorealistic, high quality"
        ),
        "scenes": [],
        "sort_order": 1,
    },
    {
        "name": "Кинематографичный",
        "emoji": "🎬",
        "prompt": (
            "preserve exact facial identity from reference photo, same person, cinematic film still portrait, natural facial asymmetry and authentic skin texture, "
            "preserve exact facial expression from reference photo unchanged, "
            "varied cinematic moments each generation such as standing mid-motion, sitting in contemplation, turning over shoulder or caught in a decisive moment, "
            "varied cinematic environments each generation such as dim apartments, subway platforms, hotel corridors, rain-soaked streets, vehicles, bars or minimal architectural spaces, "
            "practical mixed lighting from environmental sources, anamorphic lens bokeh, moody cinematic lighting with strong directional contrast, "
            "film color grading with teal-orange or cool desaturated palette, subtle film grain, "
            "storytelling composition suggesting a scene from a prestige drama, photorealistic, high quality"
        ),
        "scenes": [],
        "sort_order": 2,
    },
    {
        "name": "Русский стиль",
        "emoji": "🌺",
        "prompt": (
            "preserve exact facial identity from reference photo, same person, elegant portrait inspired by russian folk and slavic cultural aesthetics, "
            "realistic skin texture and natural expression, "
            "preserve exact facial expression from reference photo unchanged, "
            "varied culturally inspired garments each generation such as embroidered sarafans, linen shirts, folk-pattern shawls or ornate traditional outfits, "
            "natural poses interacting with clothing or surroundings, "
            "varied slavic-inspired environments each generation such as birch forests, countryside houses, wooden interiors with folk decor, open fields or winter rural landscapes, "
            "warm earthy tones and golden ambient lighting or soft natural daylight, rich folk textures and materials, photorealistic, high quality"
        ),
        "scenes": [],
        "sort_order": 3,
    },
    {
        "name": "90-е",
        "emoji": "📼",
        "prompt": (
            "preserve exact facial identity from reference photo, same person, authentic 1990s snapshot portrait, "
            "preserve exact facial expression from reference photo unchanged, "
            "shot on cheap 1990s point-and-shoot film camera or polaroid instant camera, "
            "strong direct on-camera flash causing slight overexposure on face"
            "heavy film grain, slightly soft focus, color fringing, faded or slightly desaturated analog colors, "
            "kodak gold or fujifilm consumer film color rendering with warm yellowish cast, "
            "imperfect amateur composition as if taken casually by a friend, "
            "varied casual 90s clothing each generation such as oversized denim, colorful windbreakers, sporty tracksuits, band tees, flannel shirts or platform shoes, "
            "relaxed candid poses such as leaning, sitting, standing casually or walking, "
            "varied nostalgic environments each generation such as urban courtyards, residential blocks, parks, arcades, cafes, underpasses, rooftops or indoor social spaces, "
            "fluorescent or tungsten indoor lighting or natural overcast daylight, "
            "90s youth culture atmosphere, photorealistic, high quality"
        ),
        "scenes": [],
        "sort_order": 4,
    },
    {
        "name": "День рождения",
        "emoji": "🎂",
        "prompt": (
            "preserve exact facial identity from reference photo, same person, festive birthday portrait, natural skin texture, "
            "subtle natural expression fitting the celebratory mood, slight warmth or gentle smile allowed but not exaggerated or forced, "
            "varied natural interactions with celebration setting each generation, subject may be near cake, gifts or decorations without holding forced props, "
            "varied birthday environments each generation such as decorated home spaces, restaurant private rooms, rooftop gatherings or event halls, "
            "festive decorations with balloons, lights, streamers and warm ambient party glow, "
            "spontaneous candid atmosphere, photorealistic, high quality"
        ),
        "scenes": [],
        "sort_order": 5,
    },
    {
        "name": "Новый год",
        "emoji": "🎄",
        "prompt": (
            "preserve exact facial identity from reference photo, same person, new year and christmas themed portrait, "
            "subtle natural expression fitting the holiday mood, quiet warmth or gentle festive feeling allowed but not exaggerated, "
            "varied seasonal clothing each generation such as cozy knitwear, elegant festive outfits or casual winter layers, "
            "varied holiday environments each generation such as decorated living rooms, snowy outdoor streets, christmas markets or festive dining spaces, "
            "warm christmas tree lights in bokeh background, soft seasonal decorations, subtle snow or cozy indoor winter ambiance, "
            "photorealistic, high quality"
        ),
        "scenes": [],
        "sort_order": 6,
    },
    {
        "name": "Зима",
        "emoji": "❄️",
        "prompt": (
            "preserve exact facial identity from reference photo, same person, winter outdoor portrait, "
            "preserve exact facial expression from reference photo unchanged, "
            "varied natural cold-weather interactions each generation such as walking, standing, adjusting scarf or looking into distance, "
            "varied winter clothing each generation such as wool coats, fur-lined jackets, chunky scarves, hats or layered outfits, "
            "varied winter environments each generation such as snowy city streets, pine forests, frozen lakes, mountain villages or urban parks after snowfall, "
            "visible snowfall or frost, breath condensation in cold air, cold natural daylight with blue tones and warm skin contrast, "
            "serene winter atmosphere, photorealistic, high quality"
        ),
        "scenes": [],
        "sort_order": 7,
    },
    {
        "name": "Фэнтези",
        "emoji": "🧙",
        "prompt": (
            "preserve exact facial identity from reference photo, same person, ultra-realistic epic fantasy portrait, "
            "preserve exact facial expression from reference photo unchanged, "
            "hyperrealistic skin detail with visible pores and natural facial asymmetry, photorealistic material rendering for all fabrics and surfaces, "
            "varied mystical or medieval-inspired attire each generation with intricate craftsmanship such as armor, robes, leather or ceremonial garments, "
            "subject in varied natural fantasy poses each generation, "
            "varied fantasy environments each generation such as ancient stone halls, enchanted forests, royal chambers, mystical ruins, mountain citadels or arcane libraries, "
            "realistic magical lighting such as volumetric god rays, soft bioluminescent glow or flickering torchlight, "
            "rich jewel-tone palette, cinematic fantasy realism at the level of high-end film production, photorealistic, high quality"
        ),
        "scenes": [],
        "sort_order": 8,
    },
    {
        "name": "Чёрно-белый",
        "emoji": "🖤",
        "prompt": (
            "preserve exact facial identity from reference photo, same person, black and white fine art portrait, "
            "preserve exact facial expression from reference photo unchanged, "
            "natural skin texture with strong tonal contrast, deep rich blacks and luminous highlights, "
            "varied poses each generation such as sitting, standing, leaning or looking away, "
            "varied minimalist or architectural environments each generation such as studio backgrounds, textured walls, hallways, staircases or window-lit interiors, "
            "dramatic use of light and shadow, fine art photographic tradition inspired by avedon or newton or penn, "
            "emotional depth and timeless composition, photorealistic, high quality"
        ),
        "scenes": [],
        "sort_order": 9,
    },
    {
        "name": "Пляж",
        "emoji": "🏖️",
        "prompt": (
            "preserve exact facial identity from reference photo, same person, golden hour beach portrait, "
            "preserve exact facial expression from reference photo unchanged, "
            "varied natural coastal interactions each generation such as walking barefoot, sitting on sand, standing near water or looking at horizon, "
            "varied casual summer clothing each generation such as linen shirts, swimwear, beach cover-ups or light dresses, "
            "varied beach environments each generation such as tropical shores, mediterranean coves, rocky coastlines, resort beaches or sandy dunes, "
            "warm low-angle sunlight with ocean reflections, wind movement in hair and fabric, "
            "natural relaxed coastal atmosphere, photorealistic, high quality"
        ),
        "scenes": [],
        "sort_order": 10,
    },
    {
        "name": "Ретро",
        "emoji": "🕺",
        "prompt": (
            "preserve exact facial identity from reference photo, same person, retro portrait from 1970s aesthetic, "
            "preserve exact facial expression from reference photo unchanged, "
            "varied vintage clothing each generation typical of the 1970s such as bell-bottoms, wide-lapel shirts, floral prints, peasant blouses or disco-era outfits, "
            "relaxed natural poses such as sitting, leaning or standing casually, "
            "varied retro environments each generation such as vintage apartments, diners, disco interiors, wood-paneled rooms, classic car settings or outdoor 70s locations, "
            "warm analog film tones dominated by yellows, oranges and earthy browns, kodachrome film grain and slight vignette, "
            "nostalgic 1970s atmosphere, photorealistic, high quality"
        ),
        "scenes": [],
        "sort_order": 11,
    },
    {
        "name": "Люкс",
        "emoji": "💎",
        "prompt": (
            "preserve exact facial identity from reference photo, same person, luxury editorial portrait, "
            "preserve exact facial expression from reference photo unchanged, "
            "varied elegant high-end styling each generation such as bespoke suits, haute couture gowns, refined business attire or sophisticated casual luxury, "
            "composed confident posture in varied natural poses each generation, "
            "varied luxury environments each generation such as private penthouses, superyacht decks, grand hotel lobbies, marble staircases or exclusive private clubs, "
            "premium architectural materials such as marble, polished brass, crystal and glass, "
            "cinematic soft lighting with elegant reflections, sophisticated understated luxury aesthetic, photorealistic, high quality"
        ),
        "scenes": [],
        "sort_order": 12,
    },
    {
        "name": "Студия",
        "emoji": "📸",
        "prompt": (
            "preserve exact facial identity from reference photo, same person, professional studio portrait, "
            "preserve exact facial expression from reference photo unchanged, "
            "natural relaxed posture with varied compositions each generation, "
            "varied studio setups each generation such as textured painted backdrops, colored seamless paper, fabric curtain backgrounds, simple styled sets with furniture or architectural studio elements, "
            "not just plain white background, studio has character and visual interest, "
            "varied professional lighting configurations each generation such as rembrandt, butterfly, split or soft box setups, "
            "clean commercial portrait quality with sharp facial detail, photorealistic, high quality"
        ),
        "scenes": [],
        "sort_order": 13,
    },
    {
        "name": "Арт",
        "emoji": "🎨",
        "prompt": (
            "preserve exact facial identity from reference photo, same person, contemporary fine art portrait, "
            "preserve exact facial expression from reference photo unchanged, "
            "expressive artistic interpretation with realistic photographic base, "
            "varied conceptual environments each generation such as art studios, gallery spaces, abstract installations, large-scale painted backdrops or creative staged environments, "
            "bold artistic use of color, texture and composition while maintaining photorealistic rendering, "
            "varied experimental framing and conceptual visual storytelling each generation, "
            "inspired by modern fine art photography, photorealistic, high quality"
        ),
        "scenes": [],
        "sort_order": 14,
    },
    {
        "name": "Детство нулевых",
        "emoji": "💿",
        "prompt": (
            "preserve exact facial identity from reference photo, same person, authentic early 2000s portrait, "
            "subtle natural expression fitting the nostalgic youthful mood, slight casual warmth allowed but not exaggerated, "
            "visible digital noise and slightly oversaturated early digital camera colors typical of consumer cameras from 2000-2008, "
            "varied early 2000s clothing each generation such as low-rise jeans, graphic tees, velour tracksuits, cargo pants, colorful hoodies or early streetwear, "
            "natural relaxed casual poses, no forced props or objects in hands, "
            "varied nostalgic environments each generation such as school corridors, suburban parks, shopping mall interiors, bedroom with posters, outdoor playgrounds or city blocks, "
            "early 2000s youth culture atmosphere, warm slightly oversaturated consumer digital camera look, photorealistic, high quality"
        ),
        "scenes": [],
        "sort_order": 16,
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
        "scenes": [],
        "sort_order": 15,
    },
]

PAGE_SIZE = 8
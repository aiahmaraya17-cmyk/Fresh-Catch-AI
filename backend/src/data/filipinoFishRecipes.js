/**
 * filipinoFishRecipes.js
 * ----------------------
 * Curated dataset of authentic Filipino fish recipes.
 *
 * Each recipe is tagged with:
 *   minFreshnessRank — the LOWEST freshness grade this dish is suitable for
 *       0 = Fresh only        (raw dishes like kinilaw)
 *       1 = Moderately Fresh+ (light cooking: steamed, grilled)
 *       2 = Less Fresh+       (thorough cooking: fried, stewed, strong seasoning)
 *   isRaw — true for raw preparations (only ever shown for Fresh)
 *   species — array of local species this dish suits, or ['*'] for any fish
 *
 * Rank meaning for lookup:
 *   A recipe is shown when  recipe.minFreshnessRank >= fishRank
 *   i.e. a Less-Fresh fish (rank 2) only sees rank-2 dishes (thorough cooking);
 *        a Fresh fish (rank 0) sees everything.
 *
 * This is REAL, curated data — editable, expandable, and freshness-aware.
 * Sources: Filipino home cooking tradition (Panlasang Pinoy, Kawaling Pinoy
 *          style dishes); paraphrased instructions, not copied verbatim.
 */

const FILIPINO_FISH_RECIPES = [
  // ─────────────────────────── FRESH ONLY (raw) ────────────────────────────
  {
    id: 'kinilaw',
    name: 'Kinilaw na Isda',
    name_tagalog: 'Kinilaw na Isda',
    area: 'Filipino',
    cooking_method: 'Raw (cured in vinegar)',
    minFreshnessRank: 0,
    isRaw: true,
    species: ['Tanigue', 'Tuna', 'Maya-Maya', 'Tulingan', '*'],
    prep_time_mins: 20,
    thumbnail: 'https://upload.wikimedia.org/wikipedia/commons/6/6a/Kinilaw.jpg',
    description:
      'Fresh raw fish "cooked" in vinegar and calamansi with ginger, onion, ' +
      'and chili. Only ever prepared from very fresh, sashimi-grade fish.',
    ingredients: [
      '500g very fresh fish fillet, cubed',
      '1 cup native vinegar (sukang paombong)',
      '1/2 cup calamansi juice',
      '1 thumb ginger, julienned',
      '1 red onion, diced',
      '3 chili peppers (siling labuyo), sliced',
      'Salt and pepper to taste',
    ],
    steps: [
      'Ensure the fish is extremely fresh — clear eyes, red gills, firm flesh.',
      'Cube the fish fillet into bite-sized pieces.',
      'Rinse the cubes briefly in a little vinegar, then drain.',
      'Combine fresh vinegar and calamansi juice with the fish.',
      'Add ginger, onion, and chili. Season with salt and pepper.',
      'Let it sit 10–15 minutes until the flesh turns opaque. Serve chilled.',
    ],
  },

  // ───────────────── MODERATELY FRESH+ (light cooking) ─────────────────────
  {
    id: 'inihaw-na-isda',
    name: 'Inihaw na Isda (Grilled Fish)',
    name_tagalog: 'Inihaw na Isda',
    area: 'Filipino',
    cooking_method: 'Grilled',
    minFreshnessRank: 1,
    isRaw: false,
    species: ['Bangus', 'Tilapia', 'Maya-Maya', 'Tanigue', '*'],
    prep_time_mins: 30,
    thumbnail: 'https://upload.wikimedia.org/wikipedia/commons/1/1e/Inihaw_na_Bangus.jpg',
    description:
      'Whole fish marinated in calamansi, soy sauce, and garlic, then grilled ' +
      'over charcoal until smoky and tender.',
    ingredients: [
      '1 whole fish, cleaned and scaled',
      '1/4 cup soy sauce',
      '3 tbsp calamansi juice',
      '4 cloves garlic, minced',
      '1 tomato and 1 onion (stuffing)',
      'Salt and pepper',
    ],
    steps: [
      'Clean the fish and make diagonal slits on both sides.',
      'Marinate in soy sauce, calamansi, garlic, salt, and pepper for 20 minutes.',
      'Stuff the cavity with chopped tomato and onion.',
      'Wrap in banana leaf or foil (optional) and grill over medium charcoal.',
      'Grill 8–10 minutes per side until cooked through. Serve with soy-calamansi dip.',
    ],
  },
  {
    id: 'pinaputok-na-tilapia',
    name: 'Pinaputok na Tilapia',
    name_tagalog: 'Pinaputok na Tilapia',
    area: 'Filipino',
    cooking_method: 'Steamed / Baked in leaf',
    minFreshnessRank: 1,
    isRaw: false,
    species: ['Tilapia', 'Bangus', '*'],
    prep_time_mins: 40,
    thumbnail: 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Tilapia_fish.jpg/640px-Tilapia_fish.jpg',
    description:
      'Whole tilapia stuffed with tomato, onion, and ginger, wrapped in banana ' +
      'leaf and steamed or baked until fragrant.',
    ingredients: [
      '2 whole tilapia, cleaned',
      '2 tomatoes, diced',
      '1 onion, diced',
      '1 thumb ginger, julienned',
      'Banana leaves for wrapping',
      'Salt and pepper',
    ],
    steps: [
      'Season the cleaned fish inside and out with salt and pepper.',
      'Stuff the cavity generously with tomato, onion, and ginger.',
      'Wrap each fish tightly in wilted banana leaf.',
      'Steam for 20–25 minutes, or bake at 190°C for 30 minutes.',
      'Unwrap and serve hot with rice.',
    ],
  },
  {
    id: 'sinigang-na-isda',
    name: 'Sinigang na Isda',
    name_tagalog: 'Sinigang na Isda',
    area: 'Filipino',
    cooking_method: 'Sour soup',
    minFreshnessRank: 1,
    isRaw: false,
    species: ['Bangus', 'Maya-Maya', 'Tulingan', '*'],
    prep_time_mins: 45,
    thumbnail: 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/Sinigang.jpg/640px-Sinigang.jpg',
    description:
      'Classic sour tamarind soup with fish, kangkong, radish, and long beans. ' +
      'Comforting and light.',
    ingredients: [
      '1 whole fish, sliced into steaks',
      '1 pack sinigang sa sampalok mix (or fresh tamarind)',
      '1 radish (labanos), sliced',
      '1 bundle kangkong (water spinach)',
      '1 bunch sitaw (long beans)',
      '2 tomatoes, 1 onion',
      'Fish sauce (patis) to taste',
    ],
    steps: [
      'Boil water with tomatoes and onion until soft.',
      'Add the tamarind mix and radish; simmer 5 minutes.',
      'Add the fish and cook 5–7 minutes until just done.',
      'Add long beans and kangkong; cook 2 more minutes.',
      'Season with fish sauce. Serve hot.',
    ],
  },

  // ───────────────── LESS FRESH+ (thorough cooking, strong seasoning) ──────
  {
    id: 'paksiw-na-isda',
    name: 'Paksiw na Isda',
    name_tagalog: 'Paksiw na Isda',
    area: 'Filipino',
    cooking_method: 'Vinegar stew',
    minFreshnessRank: 2,
    isRaw: false,
    species: ['Bangus', 'Galunggong', 'Tilapia', '*'],
    prep_time_mins: 35,
    thumbnail: 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Paksiw_na_bangus.jpg/640px-Paksiw_na_bangus.jpg',
    description:
      'Fish simmered in vinegar, ginger, and garlic. The acidity and thorough ' +
      'simmering make it ideal for prompt cooking of less-fresh fish.',
    ingredients: [
      '1 whole fish, sliced',
      '1/2 cup vinegar',
      '1 thumb ginger, sliced',
      '4 cloves garlic, crushed',
      '2 finger chilies (siling haba)',
      '1 small ampalaya or eggplant (optional)',
      'Salt and peppercorns',
    ],
    steps: [
      'Inspect the fish carefully — discard if it smells sour or of ammonia.',
      'Arrange fish in a pot with ginger, garlic, and peppercorns.',
      'Pour in vinegar and a little water. Do NOT stir yet.',
      'Bring to a boil uncovered, then simmer 15–20 minutes until fully cooked.',
      'Add chilies and vegetables in the last 5 minutes. Season with salt.',
    ],
  },
  {
    id: 'pritong-isda',
    name: 'Pritong Isda (Fried Fish)',
    name_tagalog: 'Pritong Isda',
    area: 'Filipino',
    cooking_method: 'Deep fried',
    minFreshnessRank: 2,
    isRaw: false,
    species: ['Galunggong', 'Tilapia', 'Tamban', 'Bangus', '*'],
    prep_time_mins: 20,
    thumbnail: 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Fried_fish.jpg/640px-Fried_fish.jpg',
    description:
      'Simple crispy fried fish. High-heat frying thoroughly cooks the fish; ' +
      'serve with vinegar-garlic dip (sawsawan).',
    ingredients: [
      '4 pieces fish (galunggong, tilapia, or tamban)',
      'Salt',
      'Cooking oil for frying',
      'For dip: vinegar, garlic, chili',
    ],
    steps: [
      'Inspect and smell the fish; discard if it smells off.',
      'Rub with salt and let stand 10 minutes.',
      'Heat oil until hot. Fry fish until golden and crisp on both sides (thoroughly cooked).',
      'Drain on paper towel.',
      'Serve with vinegar-garlic-chili dip and rice.',
    ],
  },
  {
    id: 'escabeche',
    name: 'Escabeche (Sweet & Sour Fish)',
    name_tagalog: 'Escabeche',
    area: 'Filipino',
    cooking_method: 'Fried then sauced',
    minFreshnessRank: 2,
    isRaw: false,
    species: ['Maya-Maya', 'Tilapia', 'Tanigue', '*'],
    prep_time_mins: 45,
    thumbnail: 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Escabeche.jpg/640px-Escabeche.jpg',
    description:
      'Fried fish topped with a tangy sweet-sour sauce of vinegar, bell pepper, ' +
      'carrot, and ginger. Strong flavours suit prompt cooking.',
    ingredients: [
      '1 whole fish, fried',
      '1/2 cup vinegar',
      '3 tbsp sugar',
      '1 bell pepper, 1 carrot (julienned)',
      '1 thumb ginger, 4 cloves garlic',
      '2 tbsp cornstarch slurry',
      'Salt and pepper',
    ],
    steps: [
      'Fry the whole fish until crisp and fully cooked; set aside.',
      'Sauté garlic, ginger, then bell pepper and carrot.',
      'Add vinegar, sugar, salt, and a little water; simmer.',
      'Thicken with cornstarch slurry.',
      'Pour the sauce over the fried fish and serve immediately.',
    ],
  },
  {
    id: 'ginataang-isda',
    name: 'Ginataang Isda',
    name_tagalog: 'Ginataang Isda',
    area: 'Filipino',
    cooking_method: 'Coconut milk stew',
    minFreshnessRank: 2,
    isRaw: false,
    species: ['Tulingan', 'Galunggong', 'Bangus', '*'],
    prep_time_mins: 40,
    thumbnail: 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Coconut_milk.jpg/640px-Coconut_milk.jpg',
    description:
      'Fish simmered in rich coconut milk with ginger, garlic, and leafy greens. ' +
      'Prolonged simmering thoroughly cooks the fish.',
    ingredients: [
      '1 whole fish, sliced',
      '2 cups coconut milk (gata)',
      '1 thumb ginger, 4 cloves garlic',
      '1 bundle mustard greens or spinach',
      '2 finger chilies',
      'Fish sauce and pepper',
    ],
    steps: [
      'Inspect the fish; discard if the smell is sour or putrid.',
      'Sauté ginger and garlic, then pour in coconut milk.',
      'Simmer gently 10 minutes, stirring so it does not curdle.',
      'Add the fish and cook 12–15 minutes until fully done.',
      'Add greens and chilies; season with fish sauce. Serve hot.',
    ],
  },
];

module.exports = { FILIPINO_FISH_RECIPES };

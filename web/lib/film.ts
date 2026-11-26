/** Showcase content for The Summer I Discovered Another World */

export type ShotChapter = {
  id: string;
  label: string;
  reason: string;
  framing: string;
  camera: string;
  narration_en: string;
  narration_am: string;
};

export const FILM = {
  brand: "Heritage Short",
  title: "The Summer I Discovered Another World",
  place: "Grandfather's countryside · Ethiopia",
  author: "Lata Amenu",
  academy: "10 Academy · B2W0 Challenge",
  badge: "AI Heritage Short",
  synopsis:
    "In Grade Seven, a first visit to grandfather's countryside becomes a discovery of endless greenery, summer rain, gojo nights, and fresh milk—and a way of seeing the world that never leaves. This film is about simple living, land, and the happiness hidden in ordinary moments.",
  madeBy: "Made by Lata Amenu",
  madeWith: "Made with AI · Heritage Short pipeline",
  githubHint: "storyboard.json is the contract",
  /** Final cuts hosted on Google Drive for the Film tab. */
  drive: {
    "16x9": {
      id: "1Kjve3kvvDaxfpwNkDGznj8n1z4e-JCss",
      label: "Horizontal 16:9",
    },
    "9x16": {
      id: "1XPGSV9vY0ItxBp-kfuPQiDWo0pEcI19Q",
      label: "Vertical 9:16",
    },
  },
};

export type AspectKey = keyof typeof FILM.drive;

export function drivePreviewUrl(aspect: AspectKey): string {
  return `https://drive.google.com/file/d/${FILM.drive[aspect].id}/preview`;
}

export function driveViewUrl(aspect: AspectKey): string {
  return `https://drive.google.com/file/d/${FILM.drive[aspect].id}/view?usp=sharing`;
}

export function driveDownloadUrl(aspect: AspectKey): string {
  return `https://drive.google.com/uc?export=download&id=${FILM.drive[aspect].id}`;
}

export const SHOTS: ShotChapter[] = [
  {
    id: "shot_01",
    label: "Arrival",
    reason: "Open on the visit—Grade Seven, first time, thinking it is ordinary.",
    framing: "Medium",
    camera: "Slow push-in toward the homesteads",
    narration_en:
      "I was in Grade Seven when I first visited my grandfather's home in the countryside. I thought it was only a visit. I had no idea I was about to discover a whole new world.",
    narration_am:
      "በሰባተኛ ክፍል ነበርኩ ለመጀመሪያ ጊዜ የአያቴን የገጠር ቤት ስጎበኝ። ጉብኝት ብቻ ነው ብዬ አሰብኩ። ሙሉ አዲስ ዓለም እንደማገኝ አላወቅኩም።",
  },
  {
    id: "shot_02",
    label: "Greenery",
    reason: "Reveal the other world—endless greenery and open farmland.",
    framing: "Extreme wide",
    camera: "Very slow pan across farmland",
    narration_en:
      "Everything was different. The moment I arrived, endless greenery surrounded me—farmland, trees in the breeze, and open spaces that seemed to have no end.",
    narration_am:
      "ሁሉም ነገር የተለየ ነበር። በደረስኩበት ጊዜ ማያልቅ አረንጓዴ ከበበኝ—የእርሻ ቦታዎች፣ በንፋስ የሚወዛወዙ ዛፎች፣ መጨረሻ የሌላቸው ክፍት ቦታዎች።",
  },
  {
    id: "shot_03",
    label: "Rain",
    reason: "Summer rain—the land feels alive and different.",
    framing: "Wide",
    camera: "Slow drift through falling rain",
    narration_en:
      "Then came the summer rain. The sky slowly grew dark, the wind carried the scent of wet earth, and raindrops fell over the fields. Even the rain felt different there—peaceful, beautiful, alive.",
    narration_am:
      "ከዚያ የበጋ ዝናብ መጣ። ሰማዩ ቀስ በቀስ ጨለመ፣ ንፋሱ የእርጥብ መሬት ሽታ አመጣ፣ የዝናብ ጠብታዎች በእርሻው ላይ ወረዱ። ዝናቡም እንኳ እዚያ የተለየ ነበር—ሰላማዊ፣ ውብ፣ ሕያው።",
  },
  {
    id: "shot_04",
    label: "Work",
    reason: "Work and animals—another rhythm of life from the land.",
    framing: "Wide",
    camera: "Slow pan across people and animals",
    narration_en:
      "And then there was the work. I saw another rhythm of life—people waking early, tending land, caring for animals, working with their hands.",
    narration_am:
      "ከዚያም ሥራው ነበር። የሌላ የሕይወት ምት አየሁ—ሰዎች ጠዋት መነሳት፣ መሬት መንከባከብ፣ እንስሳት መመገብ፣ በእጅ መሥራት።",
  },
  {
    id: "shot_05",
    label: "Gojo",
    reason: "Gojo nights—potatoes, fire, family talk.",
    framing: "Medium",
    camera: "Gentle push-in on the fire circle",
    narration_en:
      "As evening arrived, we gathered inside my grandfather's traditional gojo house. A big pot of potatoes cooking over the fire. Nothing fancy—just family, food, and togetherness.",
    narration_am:
      "ማታ በአያቴ ባህላዊ ጎጆ ተሰባሰብን። በእሳቱ ላይ ትልቅ የድንች ድስት። ምንም የተራቀቀ አይደለም—ቤተሰብ፣ ምግብ እና አብሮነት ብቻ።",
  },
  {
    id: "shot_06",
    label: "Milk",
    reason: "Fresh milk—a countryside miracle.",
    framing: "Close-up",
    camera: "Slow drift on the pouring cup",
    narration_en:
      "And the fresh milk! I can still remember how special it felt to drink milk straight from the countryside.",
    narration_am:
      "እና ትኩስ ወተቱ! ከገጠር በቀጥታ ወተት መጠጣት ምን ያህል ልዩ እንደሚሰማ አሁንም አስታውሳለሁ።",
  },
  {
    id: "shot_07",
    label: "Mornings",
    reason: "Every morning becomes adventure.",
    framing: "Medium",
    camera: "Slow tracking along the path",
    narration_en:
      "Every little thing became an adventure. Every morning brought something new. Every experience left a new memory.",
    narration_am:
      "እያንዳንዱ ትንሽ ነገር ጀብዱ ሆነ። እያንዳንዱ ጠዋት አዲስ ነገር አመጣ። እያንዳንዱ ተሞክሮ አዲስ ትውስታ ትቶ ሄደ።",
  },
  {
    id: "shot_08",
    label: "Gift",
    reason: "What the visit gave—simple living and land.",
    framing: "Medium",
    camera: "Slow pull-back revealing gojo and land",
    narration_en:
      "I went there as a Grade Seven student, thinking I was just visiting my grandfather. But I came away with something much bigger.",
    narration_am:
      "እንደ ሰባተኛ ክፍል ተማሪ ሄጄ ነበር፣ አያቴን ለመጎብኘት ብቻ ብዬ አስቤ። ግን ከጉብኝት በላይ ይዤ ተመለስኩ።",
  },
  {
    id: "shot_09",
    label: "Return",
    reason: "Years pass; the summer stays.",
    framing: "Medium close",
    camera: "Ken Burns drift into firelight memory",
    narration_en:
      "Years have passed, but that summer never really left me. Sometimes the most beautiful journeys are the ones that take us back.",
    narration_am:
      "ዓመታት አለፉ፣ ያ የበጋ ወቅት ግን አልለየኝም። አንዳንድ ጊዜ ውብ ጉዞዎች ሩቅ የሚወስዱት አይደሉም—ወደ ተመለስንበት የሚመልሱት ናቸው።",
  },
];

export const PIPELINE_STAGES = [
  { id: "queued", label: "Queued" },
  { id: "script", label: "Storyboard" },
  { id: "narration", label: "Narration" },
  { id: "keyframes", label: "Keyframes" },
  { id: "shots", label: "Motion shots" },
  { id: "music", label: "Score" },
  { id: "assemble", label: "Assemble" },
  { id: "done", label: "Ready" },
] as const;

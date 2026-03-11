// 日记本配置常量

export const ANIMATION_TIMING = {
  TYPING_SPEED: 80,
  DISPLAY_DURATION: 2000,
  FADE_DURATION: 3000,
  USER_FADE_DELAY: 1500,
  USER_FADE_DURATION: 2500,
  INITIAL_GREETING_DELAY: 1500,
  FOCUS_DELAY: 100,
} as const;

export const BOOK_DIMENSIONS = {
  DEPTH_LAYERS: {
    BACK_COVER: 0,
    THICKNESS_START: 1.5,
    THICKNESS_COUNT: 3,
    MAIN_PAGE: 6,
    FRONT_COVER: 15,
  },
  Z_INDEX: {
    COVER: 100,
  },
} as const;

export const TOM_REPLIES: Record<string, string> = {
  DEFAULT: "我可以给你展示一些东西...",
  GREETING: "你好... 我是汤姆·里德尔。",
  WHO: "我是一段记忆，在日记里保存了五十年。",
  CHAMBER: "密室以前就被打开过。",
  VOLDEMORT: "伏地魔是我的过去、现在和未来。",
  HARRY: "哈利·波特... 我们终于见面了。",
  MAGIC: "我可以教你超越梦想的魔法。",
  HELP: "如果你愿意，我可以帮你。",
  DUMBLEDORE: "邓布利多... 一个愚蠢的老头。",
  HORCRUX: "你正踏入危险的领域。",
};

export const INITIAL_GREETING = "给我写点什么...";

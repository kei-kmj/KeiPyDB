import { escapeSelector, symbols, toArray } from '@unocss/core';
import { createValueHandler, getStringComponents, isInterpolatedMethod, parseCssColor, colorToString, getStringComponent } from '@unocss/rule-utils';

const PRESET_NAME = "@unocss/preset-wind4";
const CONTROL_NO_NEGATIVE = "$$mini-no-negative";
const SpecialColorKey = {
  transparent: "transparent",
  current: "currentColor",
  inherit: "inherit"
};

const directionMap = {
  "l": ["-left"],
  "r": ["-right"],
  "t": ["-top"],
  "b": ["-bottom"],
  "s": ["-inline-start"],
  "e": ["-inline-end"],
  // 'x': ['-left', '-right'],
  // 'y': ['-top', '-bottom'],
  "x": ["-inline"],
  "y": ["-block"],
  "": [""],
  "bs": ["-block-start"],
  "be": ["-block-end"],
  "is": ["-inline-start"],
  "ie": ["-inline-end"],
  "block": ["-block-start", "-block-end"],
  "inline": ["-inline-start", "-inline-end"]
};
const insetMap = {
  ...directionMap,
  x: ["-inset-inline"],
  y: ["-inset-block"],
  s: ["-inset-inline-start"],
  start: ["-inset-inline-start"],
  e: ["-inset-inline-end"],
  end: ["-inset-inline-end"],
  bs: ["-inset-block-start"],
  be: ["-inset-block-end"],
  is: ["-inset-inline-start"],
  ie: ["-inset-inline-end"],
  block: ["-inset-block-start", "-inset-block-end"],
  inline: ["-inset-inline-start", "-inset-inline-end"]
};
const cornerMap = {
  "l": ["-top-left", "-bottom-left"],
  "r": ["-top-right", "-bottom-right"],
  "t": ["-top-left", "-top-right"],
  "b": ["-bottom-left", "-bottom-right"],
  "tl": ["-top-left"],
  "lt": ["-top-left"],
  "tr": ["-top-right"],
  "rt": ["-top-right"],
  "bl": ["-bottom-left"],
  "lb": ["-bottom-left"],
  "br": ["-bottom-right"],
  "rb": ["-bottom-right"],
  "": [""],
  "bs": ["-start-start", "-start-end"],
  "be": ["-end-start", "-end-end"],
  "s": ["-end-start", "-start-start"],
  "is": ["-end-start", "-start-start"],
  "e": ["-start-end", "-end-end"],
  "ie": ["-start-end", "-end-end"],
  "ss": ["-start-start"],
  "bs-is": ["-start-start"],
  "is-bs": ["-start-start"],
  "se": ["-start-end"],
  "bs-ie": ["-start-end"],
  "ie-bs": ["-start-end"],
  "es": ["-end-start"],
  "be-is": ["-end-start"],
  "is-be": ["-end-start"],
  "ee": ["-end-end"],
  "be-ie": ["-end-end"],
  "ie-be": ["-end-end"]
};
const xyzMap = {
  "x": ["-x"],
  "y": ["-y"],
  "z": ["-z"],
  "": ["-x", "-y"]
};
const xyzArray = ["x", "y", "z"];
const basePositionMap = [
  "top",
  "top center",
  "top left",
  "top right",
  "bottom",
  "bottom center",
  "bottom left",
  "bottom right",
  "left",
  "left center",
  "left top",
  "left bottom",
  "right",
  "right center",
  "right top",
  "right bottom",
  "center",
  "center top",
  "center bottom",
  "center left",
  "center right",
  "center center"
];
const positionMap = Object.assign(
  {},
  ...basePositionMap.map((p) => ({ [p.replace(/ /, "-")]: p })),
  ...basePositionMap.map((p) => ({ [p.replace(/\b(\w)\w+/g, "$1").replace(/ /, "")]: p }))
);
const globalKeywords = [
  "inherit",
  "initial",
  "revert",
  "revert-layer",
  "unset"
];
const cssMathFnRE = /^(calc|clamp|min|max)\s*\((.+)\)(.*)/;
const cssVarFnRE = /^(var)\s*\((.+)\)(.*)/;

const numberWithUnitRE = /^(-?\d*(?:\.\d+)?)(px|pt|pc|%|r?(?:em|ex|lh|cap|ch|ic)|(?:[sld]?v|cq)(?:[whib]|min|max)|in|cm|mm|rpx)?$/i;
const numberRE = /^(-?\d*(?:\.\d+)?)$/;
const unitOnlyRE = /^(px|[sld]?v[wh])$/i;
const unitOnlyMap = {
  px: 1,
  vw: 100,
  vh: 100,
  svw: 100,
  svh: 100,
  dvw: 100,
  dvh: 100,
  lvh: 100,
  lvw: 100
};
const bracketTypeRe = /^\[(color|image|length|size|position|quoted|string|number|family):/i;
const splitComma = /,(?![^()]*\))/g;
const remRE = /(-?[.\d]+)rem/g;

const cssProps = [
  // basic props
  "color",
  "border-color",
  "background-color",
  "outline-color",
  "text-decoration-color",
  "flex-grow",
  "flex",
  "flex-shrink",
  "caret-color",
  "font",
  "gap",
  "opacity",
  "visibility",
  "z-index",
  "font-weight",
  "zoom",
  "text-shadow",
  "transform",
  "box-shadow",
  "border",
  // positions
  "background-position",
  "left",
  "right",
  "top",
  "bottom",
  "object-position",
  // sizes
  "max-height",
  "min-height",
  "max-width",
  "min-width",
  "height",
  "width",
  "border-width",
  "margin",
  "padding",
  "outline-width",
  "outline-offset",
  "font-size",
  "line-height",
  "text-indent",
  "vertical-align",
  "border-spacing",
  "letter-spacing",
  "word-spacing",
  // enhances
  "stroke",
  "filter",
  "backdrop-filter",
  "fill",
  "mask",
  "mask-size",
  "mask-border",
  "clip-path",
  "clip",
  "border-radius"
];
function round(n) {
  return +n.toFixed(10);
}
function numberWithUnit(str) {
  const match = str.match(numberWithUnitRE);
  if (!match)
    return;
  const [, n, unit] = match;
  const num = Number.parseFloat(n);
  if (unit && !Number.isNaN(num))
    return `${round(num)}${unit}`;
}
function auto(str) {
  if (str === "auto" || str === "a")
    return "auto";
}
function rem(str) {
  if (!str)
    return;
  if (unitOnlyRE.test(str))
    return `${unitOnlyMap[str]}${str}`;
  const match = str.match(numberWithUnitRE);
  if (!match)
    return;
  const [, n, unit] = match;
  const num = Number.parseFloat(n);
  if (!Number.isNaN(num)) {
    if (num === 0)
      return "0";
    return unit ? `${round(num)}${unit}` : `${round(num / 4)}rem`;
  }
}
function px(str) {
  if (unitOnlyRE.test(str))
    return `${unitOnlyMap[str]}${str}`;
  const match = str.match(numberWithUnitRE);
  if (!match)
    return;
  const [, n, unit] = match;
  const num = Number.parseFloat(n);
  if (!Number.isNaN(num))
    return unit ? `${round(num)}${unit}` : `${round(num)}px`;
}
function number(str) {
  if (!numberRE.test(str))
    return;
  const num = Number.parseFloat(str);
  if (!Number.isNaN(num))
    return round(num);
}
function percent(str) {
  if (str.endsWith("%")) {
    str = str.slice(0, -1);
  }
  const num = number(str);
  if (num != null) {
    return `${num}%`;
  }
}
function fraction(str) {
  if (!str)
    return;
  if (str === "full")
    return "100%";
  const [left, right] = str.split("/");
  const num = Number.parseFloat(left) / Number.parseFloat(right);
  if (!Number.isNaN(num)) {
    if (num === 0)
      return "0";
    return `${round(num * 100)}%`;
  }
}
function bracketWithType(str, requiredType) {
  if (str && str.startsWith("[") && str.endsWith("]")) {
    let base;
    let hintedType;
    const match = str.match(bracketTypeRe);
    if (!match) {
      base = str.slice(1, -1);
    } else {
      if (!requiredType) {
        hintedType = match[1];
      } else if (match[1] !== requiredType) {
        return;
      }
      base = str.slice(match[0].length, -1);
    }
    if (!base)
      return;
    if (base === '=""')
      return;
    if (base.startsWith("--")) {
      const [name, defaultValue] = base.slice(2).split(",");
      base = `var(--${escapeSelector(name)}${defaultValue ? `, ${defaultValue}` : ""})`;
    }
    let curly = 0;
    for (const i of base) {
      if (i === "[") {
        curly += 1;
      } else if (i === "]") {
        curly -= 1;
        if (curly < 0)
          return;
      }
    }
    if (curly)
      return;
    switch (hintedType) {
      case "string":
        return base.replace(/(^|[^\\])_/g, "$1 ").replace(/\\_/g, "_");
      case "quoted":
        return base.replace(/(^|[^\\])_/g, "$1 ").replace(/\\_/g, "_").replace(/(["\\])/g, "\\$1").replace(/^(.+)$/, '"$1"');
    }
    return base.replace(/(url\(.*?\))/g, (v) => v.replace(/_/g, "\\_")).replace(/(^|[^\\])_/g, "$1 ").replace(/\\_/g, "_").replace(/(?:calc|clamp|max|min)\((.*)/g, (match2) => {
      const vars = [];
      return match2.replace(/var\((--.+?)[,)]/g, (match3, g1) => {
        vars.push(g1);
        return match3.replace(g1, "--un-calc");
      }).replace(/(-?\d*\.?\d(?!-\d.+[,)](?![^+\-/*])\D)(?:%|[a-z]+)?|\))([+\-/*])/g, "$1 $2 ").replace(/--un-calc/g, () => vars.shift());
    });
  }
}
function bracket(str) {
  return bracketWithType(str);
}
function bracketOfColor(str) {
  return bracketWithType(str, "color");
}
function bracketOfLength(str) {
  return bracketWithType(str, "length") || bracketWithType(str, "size");
}
function bracketOfPosition(str) {
  return bracketWithType(str, "position");
}
function bracketOfFamily(str) {
  return bracketWithType(str, "family");
}
function bracketOfNumber(str) {
  return bracketWithType(str, "number");
}
function cssvar(str) {
  if (str.startsWith("var("))
    return str;
  const match = str.match(/^(?:\$|--)([^\s'"`;{}]+)$/);
  if (match) {
    const [name, defaultValue] = match[1].split(",");
    return `var(--${escapeSelector(name)}${defaultValue ? `, ${defaultValue}` : ""})`;
  }
}
function time(str) {
  const match = str.match(/^(-?[0-9.]+)(s|ms)?$/i);
  if (!match)
    return;
  const [, n, unit] = match;
  const num = Number.parseFloat(n);
  if (!Number.isNaN(num)) {
    if (num === 0 && !unit)
      return "0s";
    return unit ? `${round(num)}${unit}` : `${round(num)}ms`;
  }
}
function degree(str) {
  const match = str.match(/^(-?[0-9.]+)(deg|rad|grad|turn)?$/i);
  if (!match)
    return;
  const [, n, unit] = match;
  const num = Number.parseFloat(n);
  if (!Number.isNaN(num)) {
    if (num === 0)
      return "0";
    return unit ? `${round(num)}${unit}` : `${round(num)}deg`;
  }
}
function global(str) {
  if (globalKeywords.includes(str))
    return str;
}
function properties(str) {
  if (str.split(",").every((prop) => cssProps.includes(prop)))
    return str;
}
function position(str) {
  if (["top", "left", "right", "bottom", "center"].includes(str))
    return str;
}
function none(str) {
  if (str === "none")
    return "none";
}

const valueHandlers = {
  __proto__: null,
  auto: auto,
  bracket: bracket,
  bracketOfColor: bracketOfColor,
  bracketOfFamily: bracketOfFamily,
  bracketOfLength: bracketOfLength,
  bracketOfNumber: bracketOfNumber,
  bracketOfPosition: bracketOfPosition,
  cssvar: cssvar,
  degree: degree,
  fraction: fraction,
  global: global,
  none: none,
  number: number,
  numberWithUnit: numberWithUnit,
  percent: percent,
  position: position,
  properties: properties,
  px: px,
  rem: rem,
  time: time
};

const handler = createValueHandler(valueHandlers);
const h = handler;

function numberResolver(size, defaultValue) {
  const v = h.number(size) ?? defaultValue;
  if (v != null) {
    let num = Number(v);
    if (String(v).endsWith("%")) {
      num = Number(String(v).slice(0, -1)) / 100;
    }
    return num;
  }
}
function directionSize(propertyPrefix) {
  function parseNumberWithUnit(str) {
    const match = str.match(numberWithUnitRE);
    if (match) {
      const [, n, unit] = match;
      const num = Number.parseFloat(n);
      if (!Number.isNaN(num))
        return [num, unit];
    }
    return [void 0, void 0];
  }
  function resolveSpace(theme) {
    let base;
    let unit;
    if (theme.spacing?.DEFAULT) {
      const [v, u] = parseNumberWithUnit(theme.spacing.DEFAULT);
      if (v != null && u != null) {
        base = v;
        unit = u;
      }
    }
    return Object.entries(theme.spacing ?? {}).reduce((acc, [key, value]) => {
      const [v, u] = parseNumberWithUnit(value);
      if (v != null && u != null && u === unit) {
        acc[key] = v / base;
      } else {
        acc[key] = value;
      }
      return acc;
    }, {});
  }
  return ([_, direction, size], { theme }) => {
    if (size != null && direction != null) {
      const spaceMap = resolveSpace(theme);
      let v;
      const isNegative = size.startsWith("-");
      if (isNegative)
        size = size.slice(1);
      v = numberResolver(size, spaceMap[size]);
      if (v != null) {
        if (!Number.isNaN(v)) {
          themeTracking("spacing");
          return directionMap[direction].map((i) => [`${propertyPrefix}${i}`, `calc(var(--spacing) * ${isNegative ? "-" : ""}${v})`]);
        } else {
          themeTracking("spacing", size);
          return directionMap[direction].map((i) => [`${propertyPrefix}${i}`, isNegative ? `calc(var(--spacing-${size} * -1)` : `var(--spacing-${size})`]);
        }
      }
      v = h.bracket.cssvar.global.auto.fraction.rem(isNegative ? `-${size}` : size);
      if (v != null) {
        return directionMap[direction].map((i) => [`${propertyPrefix}${i}`, v]);
      }
    }
  };
}
function splitShorthand(body, type) {
  const [front, rest] = getStringComponent(body, "[", "]", ["/", ":"]) ?? [];
  if (front != null) {
    const match = (front.match(bracketTypeRe) ?? [])[1];
    if (match == null || match === type)
      return [front, rest];
  }
}
function parseColor(body, theme) {
  let split;
  const [front, ...rest] = getStringComponents(body, ["/", ":"], 3) ?? [];
  if (front != null) {
    const match = (front.match(bracketTypeRe) ?? [])[1];
    if (match == null || match === "color") {
      split = [front, ...rest];
    }
  }
  if (!split)
    return;
  let opacity;
  let [main, opacityOrModifier, modifier] = split;
  if (isInterpolatedMethod(opacityOrModifier) || isInterpolatedMethod(h.bracket(opacityOrModifier ?? ""))) {
    modifier = opacityOrModifier;
  } else {
    opacity = opacityOrModifier;
  }
  const colors = main.replace(/([a-z])(\d)(?![-_a-z])/g, "$1-$2").split(/-/g);
  const [name] = colors;
  if (!name)
    return;
  let parsed = parseThemeColor(theme, colors);
  if (!parsed && colors.length >= 2) {
    const last = colors.at(-1);
    const secondLast = colors.at(-2);
    if (/^\d+$/.test(last)) {
      const keys2 = colors.slice(0, -2).concat([`${secondLast}${last}`]);
      parsed = parseThemeColor(theme, keys2);
    }
  }
  let { no, keys, color } = parsed ?? {};
  if (!color) {
    const bracket = h.bracketOfColor(main);
    const bracketOrMain = bracket || main;
    if (h.numberWithUnit(bracketOrMain))
      return;
    if (/^#[\da-f]+$/i.test(bracketOrMain))
      color = bracketOrMain;
    else if (/^hex-[\da-fA-F]+$/.test(bracketOrMain))
      color = `#${bracketOrMain.slice(4)}`;
    else if (main.startsWith("$"))
      color = h.cssvar(main);
    color = color || bracket;
  }
  return {
    opacity,
    modifier: modifier && h.bracket.cssvar(modifier) || modifier,
    name,
    no,
    color: color ?? SpecialColorKey[name],
    alpha: h.bracket.cssvar.percent(opacity ?? ""),
    /**
     * Keys means the color is from theme object.
     */
    keys,
    get cssColor() {
      return parseCssColor(this.color);
    }
  };
}
function parseThemeColor(theme, keys) {
  let color;
  let no;
  let key;
  const colorData = getThemeByKey(theme, "colors", keys);
  if (typeof colorData === "object") {
    if ("DEFAULT" in colorData) {
      color = colorData.DEFAULT;
      no = "DEFAULT";
      key = [...keys, no];
    }
  } else if (typeof colorData === "string") {
    color = colorData;
    key = keys;
    no = keys.at(-1);
  }
  if (!color)
    return;
  return {
    color,
    no,
    keys: key
  };
}
function getThemeByKey(theme, themeKey, keys) {
  const obj = theme[themeKey];
  function deepGet(current, path) {
    if (!current || typeof current !== "object")
      return void 0;
    if (path.length === 0)
      return current;
    for (let i = path.length; i > 0; i--) {
      const flatKey = path.slice(0, i).join("-");
      if (flatKey in current) {
        const v = current[flatKey];
        if (i === path.length)
          return v;
        return deepGet(v, path.slice(i));
      }
    }
    return void 0;
  }
  return deepGet(obj, keys);
}
function colorCSSGenerator(data, property, varName, ctx) {
  if (!data)
    return;
  const { color, keys, alpha, modifier } = data;
  const rawColorComment = ctx?.generator.config.envMode === "dev" && color ? ` /* ${color} */` : "";
  const css = {};
  if (color) {
    const result = [css];
    if (Object.values(SpecialColorKey).includes(color)) {
      css[property] = color;
    } else {
      const alphaKey = `--un-${varName}-opacity`;
      const value = keys ? generateThemeVariable("colors", keys) : color;
      let method = modifier ?? (keys ? "in srgb" : "in oklab");
      if (!method.startsWith("in ") && !method.startsWith("var(")) {
        method = `in ${method}`;
      }
      css[property] = `color-mix(${method}, ${value} ${alpha ?? `var(${alphaKey})`}, transparent)${rawColorComment}`;
      result.push(defineProperty(alphaKey, { syntax: "<percentage>", initialValue: "100%" }));
      if (keys) {
        themeTracking(`colors`, keys);
        if (!modifier) {
          result.push({
            [symbols.parent]: "@supports (color: color-mix(in lab, red, red))",
            [symbols.noMerge]: true,
            [symbols.shortcutsNoMerge]: true,
            [property]: `color-mix(in oklab, ${value} ${alpha ?? `var(${alphaKey})`}, transparent)${rawColorComment}`
          });
        }
      }
      if (ctx?.theme) {
        detectThemeValue(color, ctx.theme);
      }
    }
    return result;
  }
}
function colorResolver(property, varName) {
  return ([, body], ctx) => {
    const data = parseColor(body ?? "", ctx.theme);
    if (!data)
      return;
    return colorCSSGenerator(data, property, varName, ctx);
  };
}
function colorableShadows(shadows, colorVar) {
  const colored = [];
  shadows = toArray(shadows);
  for (let i = 0; i < shadows.length; i++) {
    const components = getStringComponents(shadows[i], " ", 6);
    if (!components || components.length < 3)
      return shadows;
    let isInset = false;
    const pos = components.indexOf("inset");
    if (pos !== -1) {
      components.splice(pos, 1);
      isInset = true;
    }
    let colorVarValue = "";
    const lastComp = components.at(-1);
    if (parseCssColor(components.at(0))) {
      const color = parseCssColor(components.shift());
      if (color)
        colorVarValue = `, ${colorToString(color)}`;
    } else if (parseCssColor(lastComp)) {
      const color = parseCssColor(components.pop());
      if (color)
        colorVarValue = `, ${colorToString(color)}`;
    } else if (lastComp && cssVarFnRE.test(lastComp)) {
      const color = components.pop();
      colorVarValue = `, ${color}`;
    }
    colored.push(`${isInset ? "inset " : ""}${components.join(" ")} var(${colorVar}${colorVarValue})`);
  }
  return colored;
}
function hasParseableColor(color, theme) {
  return color != null && !!parseColor(color, theme)?.color;
}
const reLetters = /[a-z]+/gi;
const resolvedBreakpoints = /* @__PURE__ */ new WeakMap();
function resolveBreakpoints({ theme, generator }, key = "breakpoint") {
  const breakpoints = generator?.userConfig?.theme?.[key] || theme[key];
  if (!breakpoints)
    return void 0;
  if (resolvedBreakpoints.has(theme))
    return resolvedBreakpoints.get(theme);
  const resolved = Object.entries(breakpoints).sort((a, b) => Number.parseInt(a[1].replace(reLetters, "")) - Number.parseInt(b[1].replace(reLetters, ""))).map(([point, size]) => ({ point, size }));
  resolvedBreakpoints.set(theme, resolved);
  return resolved;
}
function resolveVerticalBreakpoints(context) {
  return resolveBreakpoints(context, "verticalBreakpoint");
}
function makeGlobalStaticRules(prefix, property) {
  return globalKeywords.map((keyword) => [`${prefix}-${keyword}`, { [property ?? prefix]: keyword }]);
}
function defineProperty(property, options = {}) {
  const {
    syntax = "*",
    inherits = false,
    initialValue
  } = options;
  const value = {
    [symbols.shortcutsNoMerge]: true,
    [symbols.noMerge]: true,
    [symbols.variants]: () => [
      {
        parent: "",
        layer: "properties",
        selector: () => `@property ${property}`
      }
    ],
    syntax: JSON.stringify(syntax),
    inherits: inherits ? "true" : "false"
  };
  if (initialValue != null) {
    value["initial-value"] = initialValue;
  }
  propertyTracking(property, initialValue ? String(initialValue) : "initial");
  return value;
}
function isCSSMathFn(value) {
  return value != null && cssMathFnRE.test(value);
}
function isSize(str) {
  if (str[0] === "[" && str.slice(-1) === "]")
    str = str.slice(1, -1);
  return cssMathFnRE.test(str) || numberWithUnitRE.test(str);
}
function camelize(str) {
  return str.replace(/-(\w)/g, (_, c) => c ? c.toUpperCase() : "");
}
function hyphenate(str) {
  return str.replace(/(?:^|\B)([A-Z])/g, "-$1").toLowerCase();
}
function compressCSS(css, isDev = false) {
  if (isDev)
    return css.trim();
  return css.trim().replace(/\s+/g, " ").replace(/\/\*[\s\S]*?\*\//g, "");
}

const trackedTheme = /* @__PURE__ */ new Set([]);
function themeTracking(key, props = "DEFAULT") {
  const k = `${key}:${toArray(props).join("-")}`;
  if (!trackedTheme.has(k)) {
    trackedTheme.add(k);
  }
}
function generateThemeVariable(key, props) {
  return `var(--${key}-${toArray(props).join("-")})`;
}
function detectThemeValue(value, theme) {
  if (value.startsWith("var(")) {
    const variable = value.match(/var\(--([\w-]+)(?:,.*)?\)/)?.[1];
    if (variable) {
      const [key, ...path] = variable.split("-");
      const themeValue = getThemeByKey(theme, key, path);
      if (typeof themeValue === "string") {
        themeTracking(key, path);
        detectThemeValue(themeValue, theme);
      }
    }
  }
}
const trackedProperties = /* @__PURE__ */ new Map();
function propertyTracking(property, value) {
  if (!trackedProperties.has(property)) {
    trackedProperties.set(property, value);
  }
}

export { colorCSSGenerator as A, colorResolver as B, CONTROL_NO_NEGATIVE as C, colorableShadows as D, hasParseableColor as E, resolveVerticalBreakpoints as F, makeGlobalStaticRules as G, defineProperty as H, isCSSMathFn as I, isSize as J, camelize as K, hyphenate as L, compressCSS as M, splitComma as N, bracketTypeRe as O, PRESET_NAME as P, SpecialColorKey as S, remRE as a, h as b, cornerMap as c, directionMap as d, xyzArray as e, cssMathFnRE as f, globalKeywords as g, handler as h, insetMap as i, cssVarFnRE as j, themeTracking as k, generateThemeVariable as l, detectThemeValue as m, trackedProperties as n, propertyTracking as o, positionMap as p, numberResolver as q, resolveBreakpoints as r, directionSize as s, trackedTheme as t, splitShorthand as u, valueHandlers as v, parseColor as w, xyzMap as x, parseThemeColor as y, getThemeByKey as z };

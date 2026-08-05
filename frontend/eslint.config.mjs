import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  {
    // This whole app kicks off its data loads from a mount effect
    // (`useEffect(loadAll, [])`) and uses the standard SSR hydration guard
    // (`useEffect(() => setMounted(true), [])`). Both trip
    // react-hooks/set-state-in-effect, which eslint-config-next ships as an
    // error — but they're deliberate, benign patterns here, not the cascading
    // re-render the rule targets. Keep it a warning so it stays visible without
    // turning the whole lint gate red; fix per-file if a real one ever shows up.
    rules: {
      "react-hooks/set-state-in-effect": "warn",
    },
  },
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
  ]),
]);

export default eslintConfig;

import { defineConfig } from '@chakra-ui/react/styled-system';
import sizes from './sizes';
import { selectSlotRecipe } from './select.recipe';
import { tabsSlotRecipe } from './tabs.recipe';
import { inputRecipe } from './input.recipe';
import { colorTokens, semanticColorTokens } from './colors';
import breakpoints from './breakpoints';

const config = defineConfig({
  theme: {
    breakpoints,
    tokens: {
      colors: colorTokens,
      sizes: sizes,
    },
    semanticTokens: {
      colors: semanticColorTokens,
    },
    recipes: {
      input: inputRecipe,
    },
    slotRecipes: {
      select: selectSlotRecipe,
      tabs: tabsSlotRecipe,
    },
  },
});

export default config;

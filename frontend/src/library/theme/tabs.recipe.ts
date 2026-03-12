import { defineSlotRecipe } from '@chakra-ui/react/styled-system';
import { tabsAnatomy } from '@chakra-ui/react/anatomy';

export const tabsSlotRecipe = defineSlotRecipe({
  className: 'chakra-tabs',
  slots: tabsAnatomy.keys(),
  variants: {
    variant: {
      enclosed: {
        trigger: {
          // color: 'orange.200',
          _selected: {
            // color: 'orange.400',
            bg: 'orange.300',
          },
        },
      },
    },
  },
});

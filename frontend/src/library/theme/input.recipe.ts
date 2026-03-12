import { defineRecipe } from '@chakra-ui/react/styled-system';

export const inputRecipe = defineRecipe({
  className: 'chakra-input',
  base: {
    width: 'full',
    minWidth: 0,
    outline: 0,
    appearance: 'none',
    borderRadius: 'l2',
    focusVisibleRing: 'inside',
    _disabled: {
      layerStyle: 'disabled',
    },
    _invalid: {
      borderColor: 'border.error',
    },
    _placeholder: {
      color: 'fg.muted/80',
    },
  },

  variants: {
    variant: {
      outline: {
        borderWidth: '1px',
        borderColor: 'border',
        bg: 'transparent',
        _hover: {
          borderColor: 'border.emphasized',
        },
        _focus: {
          borderColor: 'border.emphasized',
        },
      },
      subtle: {
        borderWidth: '1px',
        borderColor: 'transparent',
        bg: 'bg.muted',
      },
      strong: {
        borderWidth: '1px',
        borderColor: 'transparent',
        bg: 'form.bg.strong',
        _placeholder: {
          color: 'gray.fg',
        },
        _hover: {
          borderColor: 'brand.border',
        },
        _focus: {
          borderColor: 'brand.border',
        },
      },
    },

    size: {
      xs: {
        textStyle: 'xs',
        px: '2',
        h: '8',
      },
      sm: {
        textStyle: 'sm',
        px: '2.5',
        h: '9',
      },
      md: {
        textStyle: 'sm',
        px: '3',
        h: '10',
      },
      lg: {
        textStyle: 'md',
        px: '4',
        h: '12',
      },
    },
  },

  defaultVariants: {
    variant: 'outline',
    size: 'md',
  },
});

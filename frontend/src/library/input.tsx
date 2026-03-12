import { Input as ChakraInput, useRecipe } from '@chakra-ui/react';
import type { InputProps as ChakraInputProps } from '@chakra-ui/react';
import * as React from 'react';
import { inputRecipe } from './theme/input.recipe';

type InputVariant = 'outline' | 'subtle' | 'strong';
type InputSize = 'xs' | 'sm' | 'md' | 'lg';

export interface InputProps extends Omit<ChakraInputProps, 'variant' | 'size'> {
  variant?: InputVariant;
  size?: InputSize;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(function Input(
  { variant = 'outline', size = 'md', className, ...rest },
  ref,
) {
  const recipe = useRecipe({ recipe: inputRecipe });
  const styles = recipe({ variant, size });

  return <ChakraInput ref={ref} css={styles} className={className} {...rest} />;
});
